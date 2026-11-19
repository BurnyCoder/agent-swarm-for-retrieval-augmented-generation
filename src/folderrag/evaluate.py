"""Blinded scoring, resumable condition runs, development selection and frozen confirmation."""

import collections
import concurrent.futures
import functools
import hashlib
import json
import math
import os
import random
import subprocess
import time
from pathlib import Path

from dotenv import dotenv_values
from filelock import FileLock

from .agents import Case, answer, direct
from .benchdata import BENCH
from .corpus import FolderIndex, encoder, snapshot
from .evidence import Evidence, exact_match
from .gateway import Trace
from .ledger import Ledger
from .paths import DATA, LIMITS, ROOT, now, read, save

SCORING = ("correctness", "completeness", "relevance", "clarity", "reasoning")
SIZES = ("swarm1", "swarm2", "swarm4", "swarm8")
BASE = ("stock", "arctic", "oneshot")
FROZEN_FILES = (
    "src/folderrag/benchdata.py",
    "protocol/input-checksums.json",
    "protocol/splits.json",
    "protocol/sweqa_judge.txt",
    "reports/preregistration.md",
    "src/folderrag/agents.py",
    "src/folderrag/gateway.py",
    "src/folderrag/corpus.py",
    "src/folderrag/evidence.py",
    "src/folderrag/isolated/runner.py",
    "src/folderrag/isolated/answer.schema.json",
    "src/folderrag/evaluate.py",
    "src/folderrag/analysis.py",
    "src/folderrag/diagnostics.py",
    "src/folderrag/ledger.py",
    "src/folderrag/sandbox.py",
    "src/folderrag/paths.py",
    "uv.lock",
)
RUBRIC = (
    (ROOT / "protocol/sweqa_judge.txt").read_text(encoding="utf8").split("---", 1)[1]
)


def schema(fields):
    return {
        "type": "object",
        "properties": fields,
        "required": list(fields),
        "additionalProperties": False,
    }


def api_key():
    key = dotenv_values(ROOT / ".env").get("OPENAI_API_KEY") or os.environ.get(
        "OPENAI_API_KEY"
    )
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in the project .env")
    return key


@functools.lru_cache(maxsize=1)
def ledger():
    return Ledger(DATA / "research.sqlite", LIMITS)


@functools.lru_cache(maxsize=32)
def index_for(folder, dense=True):
    # Corpus versions are immutable inputs. Reuse the snapshot only for these pinned inputs.
    started = time.monotonic()
    marker = BENCH / "snapshots" / (folder + ".json")
    with FileLock(str(BENCH / ("snapshot-" + folder + ".lock"))):
        if marker.exists() and Path(read(marker)["path"]).is_dir():
            path = Path(read(marker)["path"])
        else:
            path = snapshot(BENCH / "sources" / folder)
            save(marker, {"path": str(path)})
    index = FolderIndex(path, dense=dense)
    if dense and index.spans:
        encoder().query("Find supporting passages")
    # Capture setup independently of the identical generation deadline for each arm.
    mode = "hybrid" if dense else "lexical"
    save(
        DATA
        / "index-timings"
        / (folder + "-" + mode + "-" + str(os.getpid()) + ".json"),
        dict(
            folder=folder,
            snapshot=path.name,
            mode=mode,
            spans=len(index.spans),
            seconds=round(time.monotonic() - started, 3),
            utc=now(),
        ),
    )
    return index


def new_case(index, phase, unit):
    trace = Trace(
        DATA / "logs" / phase / (unit + "-" + now().replace(":", "-") + ".jsonl")
    )
    return Case(index, ledger(), phase, unit, trace, api_key(), time.monotonic() + 300)


def judge(case, q, reference, candidate):
    gate = case.gateway("blind-grader", 2, Evidence(), "lexical")
    fields = {k: {"type": "integer", "minimum": 1, "maximum": 20} for k in SCORING}
    prompt = RUBRIC.format(question=q, reference=reference, candidate=candidate)
    result = json.loads(direct(gate, prompt, schema(fields)))
    if any(type(result.get(k)) != int or not 1 <= result[k] <= 20 for k in SCORING):
        raise ValueError("Incomplete rubric result")
    return result


def measure(phase, q, arm, unit=None):
    final_turn = phase == "dev" and arm in SIZES[1:]
    unit = unit or (phase + ("-handoff-" if final_turn else "-") + q["id"] + "-" + arm)
    dest = DATA / "records" / phase / (unit + ".json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(dest) + ".lock"):
        if dest.exists():
            prior = read(dest)
            if prior.get("score") is not None:
                return prior
        dense = arm not in {"stock", "arctic", "closed", "random", "oracle", "lexical"}
        index = index_for(q["folder"], dense)
        if arm == "arctic":
            from .sandbox import warm_arctic

            warm_arctic(index.root)
        case = new_case(index, phase, unit)
        result_path = dest.with_suffix(".answer")
        if result_path.exists():
            result = read(result_path)
        else:
            started = time.monotonic()
            try:
                selected = (
                    read(ROOT / "protocol/freeze.json")["size"]
                    if arm in {"lexical", "unchecked", "repeat"}
                    else 1
                )
                size = int(arm[5:]) if arm.startswith("swarm") else selected
                custom = arm.startswith("swarm") or arm in {
                    "lexical",
                    "unchecked",
                    "repeat",
                }
                result = answer(
                    case,
                    q["question"],
                    "custom" if custom else arm,
                    size,
                    q["facts"],
                    verify=arm != "unchecked",
                    mode="lexical" if arm == "lexical" else "hybrid",
                )
            except Exception as err:
                case.trace.log("case_error", error=str(err))
                if case.trace.funding_error:
                    save(
                        dest.with_suffix(".unrun"),
                        {
                            "unit": unit,
                            "reason": case.trace.funding_error,
                            **ledger().unit(unit),
                        },
                    )
                    raise RuntimeError(case.trace.funding_error) from err
                result = {
                    "answer": "",
                    "explanation": "",
                    "citations": [],
                    "returned_files": [],
                    "error": str(err),
                    "seconds": time.monotonic() - started,
                    **ledger().unit(unit),
                }
            save(result_path, result)
        row = {
            "unit": unit,
            "phase": phase,
            "id": q["id"],
            "domain": q["domain"],
            "stratum": q["stratum"],
            "arm": arm,
            "question": q["question"],
            "utc": now(),
            **result,
        }
        gradecost = 0.0
        if row.get("error"):
            row["score"] = 0
        elif q["domain"] == "news":
            row["score"] = int(exact_match(row["answer"], q["answer"]))
            gold = {f["path"] for f in q["facts"] if f["path"]}
            returned = set(row["returned_files"])
            cited = {c["path"] for c in row["citations"] if c.get("valid")}
            row["returned_gold_recall"] = (
                len(gold & returned) / len(gold) if gold else None
            )
            row["cited_gold_recall"] = len(gold & cited) / len(gold) if gold else None
        else:
            candidate = row["answer"] + "\n" + row.get("explanation", "")
            for stage in (phase, "retry"):
                grade = new_case(index, stage, unit + "-grade-" + stage)
                try:
                    row["dimensions"] = judge(
                        grade, q["question"], q["answer"], candidate
                    )
                    row["score"] = sum(row["dimensions"].values())
                    break
                except Exception as err:
                    row["grader_error"] = str(err)
                    row["score"] = None
                finally:
                    gradecost += ledger().unit(grade.unit)["cost_upper_usd"]
        row["grading_cost_upper_usd"] = gradecost
        save(dest, row)
        print(now(), phase, q["id"], arm, "complete", flush=True)
        return row


def pilot(row):
    return (
        row["phase"] == "dev"
        and row["arm"] in SIZES[1:]
        and not row["unit"].startswith("dev-handoff-")
    )


@functools.lru_cache(maxsize=5500)
def record_version(path, modified_ns):
    """Dashboard refreshes reuse immutable records until a file is atomically replaced."""
    return read(path)


def records(phase=None, pilots=False):
    root = DATA / "records"
    return [
        row
        for p in sorted(root.glob((phase or "*") + "/*.json"))
        if pilot(row := record_version(p, p.stat().st_mtime_ns)) == pilots
    ]


def run_stage(phase, workers=2, limit=None):
    splits = read(ROOT / "protocol/splits.json")
    questions = read(BENCH / "cases.json")
    jobs = []
    if phase == "dev":
        for qid in splits["legacy"].values():
            jobs.extend((questions[qid], a) for a in (*SIZES, *BASE))
    else:
        frozen = read(ROOT / "protocol/freeze.json")
        if frozen.get("file_sha256") and frozen["file_sha256"] != frozen_hashes():
            raise RuntimeError(
                "Registered prompts, scorer, inputs or implementation differ from the committed freeze"
            )
        size = f"swarm{frozen['size']}"
        if phase == "test":
            for block in splits["blocks"][: frozen["blocks"]]:
                for qid in block:
                    jobs.extend((questions[qid], a) for a in (size, "swarm1", *BASE))
        elif phase == "diagnostics":
            if frozen["blocks"] == 0:
                return
            bydomain = collections.Counter()
            for qid in splits["blocks"][0]:
                q = questions[qid]
                arms = [a for a in SIZES if a not in (size, "swarm1")] + [
                    "closed",
                    "random",
                    "lexical",
                    "unchecked",
                ]
                if (
                    q["domain"] == "news"
                    and q["facts"]
                    and not q["stratum"].startswith("null")
                ):
                    arms.append("oracle")
                if bydomain[q["domain"]] < 4:
                    arms.append("repeat")
                bydomain[q["domain"]] += 1
                jobs.extend((q, a) for a in arms)
        else:
            raise ValueError("Unknown phase " + phase)
    rng = random.Random(20261119)
    # Randomize arm order per question, preserving the prespecified question order.
    grouped = collections.defaultdict(list)
    for job in jobs:
        grouped[job[0]["id"]].append(job)
    jobs = []
    for group in grouped.values():
        rng.shuffle(group)
        jobs.extend(group)
    if limit:
        jobs = jobs[:limit]
    elif jobs:
        save(
            DATA / "stages" / (phase + ".json"),
            dict(phase=phase, planned=len(jobs), state="running", utc=now()),
        )
    # Submit only one job per worker. A funding stop cannot enqueue every remaining case.
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        pending = set()
        queue = iter(jobs)
        for _ in range(workers):
            if (job := next(queue, None)) is not None:
                pending.add(pool.submit(measure, phase, *job))
        while pending:
            done, pending = concurrent.futures.wait(
                pending, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for completed in done:
                try:
                    completed.result()
                except RuntimeError as error:
                    if "budget" in str(error).lower() or "quota" in str(error).lower():
                        save(
                            DATA / "phase-stops" / (phase + ".json"),
                            dict(reason=str(error), utc=now()),
                        )
                    raise
                if (job := next(queue, None)) is not None:
                    pending.add(pool.submit(measure, phase, *job))
    if not limit:
        save(
            DATA / "stages" / (phase + ".json"),
            dict(phase=phase, planned=len(jobs), state="finished", utc=now()),
        )


def frozen_hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in FROZEN_FILES
    }


def freeze():
    path = ROOT / "protocol/freeze.json"
    if path.exists():
        return read(path)
    split = read(ROOT / "protocol/splits.json")
    rows = records("dev")
    expected = {(q, a) for q in split["legacy"].values() for a in (*SIZES, *BASE)}
    if (
        len(rows) != len(expected)
        or {(r["id"], r["arm"]) for r in rows} != expected
        or any(r["score"] is None for r in rows)
    ):
        raise RuntimeError("Development comparisons or grading incomplete")

    def avg(items):
        return sum(items) / len(items)

    performance = {}
    for arm in SIZES:
        sample = [r for r in rows if r["arm"] == arm]
        quality = avg(
            [
                avg([r["score"] for r in sample if r["domain"] == "news"]),
                avg([r["score"] / 100 for r in sample if r["domain"] == "code"]),
            ]
        )
        performance[arm] = (
            quality,
            avg([r["cost_upper_usd"] for r in sample]),
            avg([r["seconds"] for r in sample]),
        )
    winner = min(
        SIZES[1:], key=lambda k: (-performance[k][0], *performance[k][1:], int(k[5:]))
    )
    selected = (winner, "swarm1", *BASE)
    estimate = sum(
        n
        * sum(
            avg(
                [
                    r["cost_upper_usd"] + r["grading_cost_upper_usd"]
                    for r in rows
                    if r["domain"] == domain and r["arm"] == arm
                ]
            )
            for arm in selected
        )
        for domain, n in (("news", 32), ("code", 15))
    )
    blocks = min(10, math.floor(34 / (1.25 * estimate))) if estimate > 0 else 0
    result = {
        "utc": now(),
        "size": int(winner[5:]),
        "blocks": blocks,
        "dev_performance": performance,
        "estimated_block_upper_usd": estimate,
        "source_commit": subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip(),
        "file_sha256": frozen_hashes(),
        "split_sha256": hashlib.sha256(
            (ROOT / "protocol/splits.json").read_bytes()
        ).hexdigest(),
    }
    save(path, result)
    return result
