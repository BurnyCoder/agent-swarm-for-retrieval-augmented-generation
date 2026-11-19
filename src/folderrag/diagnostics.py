"""Historical bridge, fact interventions, and blinded source-support audit."""

import json
import re
import gzip
import ast
import functools
import shutil
from concurrent.futures import ThreadPoolExecutor
import httpx

from .agents import answer, direct
from .benchdata import BENCH
from .corpus import FolderIndex, snapshot
from .evaluate import index_for, judge, ledger, new_case, records, schema
from .evidence import Evidence, exact_match
from .paths import DATA, ROOT, read, save


def historical():
    splits = read(ROOT / "protocol/splits.json")
    cases = read(BENCH / "cases.json")
    for old in read(ROOT / "protocol/historical_answers.json"):
        unit = "historical-" + old["condition"] + "-" + old["id"]
        dest = DATA / "historical" / (unit + ".json")
        if dest.exists():
            continue
        q = cases[splits["legacy"][old["id"]]]
        text = old["response"]
        if q["domain"] == "news":
            lines = re.findall(r"FINAL ANSWER:\s*([^\n]+)", text, re.I)
            score = int(
                bool(lines) and exact_match(lines[-1].strip("*` "), q["answer"])
            )
        else:
            case = new_case(None, "dev", unit)
            score = sum(judge(case, q["question"], q["answer"], text).values())
        save(
            dest,
            {
                "id": old["id"],
                "arm": old["condition"],
                "domain": q["domain"],
                "score": score,
                **ledger().unit(unit),
            },
        )


def counterfactual():
    size = read(ROOT / "protocol/freeze.json")["size"]
    for domain in ("news", "code"):
        for variant, value in enumerate(("41", "73")):
            unit = f"twin-{domain}-{variant}"
            dest = DATA / "twins" / (unit + ".json")
            if dest.exists():
                continue
            source = BENCH / "twins" / unit
            source.mkdir(parents=True, exist_ok=True)
            if domain == "news":
                (source / "routing.md").write_text(
                    "The Brook service uses the copper schedule; the amber schedule is unrelated."
                )
                (source / "schedules.md").write_text(
                    f"The copper schedule has {value} stops. The amber schedule has 12 stops."
                )
                q = "How many stops are on the schedule used by the Brook service? Answer with one integer."
            else:
                # Hold every other file at the pinned development revision.
                original = index_for("requests", False).root
                shutil.copytree(original, source, dirs_exist_ok=True)
                target = source / "src/requests/adapters.py"
                content = target.read_text(encoding="utf8")
                before = "DEFAULT_POOLSIZE = 10\n"
                if content.count(before) != 1:
                    raise ValueError("The pinned Requests constant changed")
                target.write_text(
                    content.replace(before, f"DEFAULT_POOLSIZE = {value}\n"),
                    encoding="utf8",
                )
                q = "In this exact checkout, what pool_maxsize does the default HTTPS adapter mounted by a new Session receive? Answer with one integer."
            index = FolderIndex(snapshot(source))
            case = new_case(index, "diagnostics", unit)
            raw = answer(case, q, size=size)
            save(
                dest,
                {
                    "unit": unit,
                    "domain": domain,
                    "variant": variant,
                    "expected": value,
                    "source_edit": "src/requests/adapters.py DEFAULT_POOLSIZE"
                    if domain == "code"
                    else "schedules.md copper stop count",
                    "score": int(exact_match(raw["answer"], value)),
                    **raw,
                },
            )


def visible_fragments(source, outputs):
    """Recover contiguous 6-word-or-longer runs shared by a gold file and a displayed output."""
    words = re.findall(r"\S+", source)
    if len(words) < 6:
        return [source] if any(source in text for text in outputs) else []
    candidates = {}
    for i in range(len(words) - 5):
        candidates.setdefault(tuple(words[i : i + 6]), []).append(i)
    fragments = set()
    for text in outputs:
        shown = text.split()
        positions = {}
        for j in range(len(shown) - 5):
            matched = {}
            for i in candidates.get(tuple(shown[j : j + 6]), ()):
                matched[i] = positions.pop(i - 1, i)
            for end, start in positions.items():
                fragments.add(" ".join(words[start : end + 6]))
            positions = matched
        for end, start in positions.items():
            fragments.add(" ".join(words[start : end + 6]))
    return sorted(fragments, key=lambda s: (-len(s), s))


@functools.lru_cache(maxsize=128)
def code_sites(path):
    """Identify declaration lines and call expressions at exact validated citation locations."""
    if path.suffix != ".py" or not path.is_file():
        return set(), set()
    try:
        tree = ast.parse(path.read_text(encoding="utf8"))
    except (ValueError, SyntaxError, RecursionError):
        return set(), set()
    definitions, calls = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef)):
            definitions.add(node.lineno)
        elif isinstance(node, ast.Call):
            calls.add(node.lineno)
    return definitions, calls


def blind_labels(unit, task, fields):
    checkpoint = DATA / "audit-labels" / (unit + ".json")
    if checkpoint.exists():
        return read(checkpoint)
    for stage in ("diagnostics", "retry"):
        case = new_case(None, stage, unit + "-" + stage)
        try:
            labels = json.loads(
                direct(
                    case.gateway("audit", 1, Evidence(), "lexical"),
                    task,
                    schema(fields),
                )
            )
            save(checkpoint, labels)
            return labels
        except (ValueError, RuntimeError, httpx.HTTPError):
            if stage == "retry" or case.trace.funding_error:
                raise


def support_audit(workers=3):
    """Judge each citation's support independently of address validity, then audit annotated news facts."""
    ids = set(read(ROOT / "protocol/splits.json")["blocks"][0])
    cases = read(BENCH / "cases.json")

    def audit(row):
        dest = DATA / "support" / (row["unit"] + ".json")
        if dest.exists():
            return
        q = cases[row["id"]]
        cites = row.get("citations", [])
        items = [
            {
                "claim": c.get("claim", ""),
                "evidence": c.get("quote", "") if c.get("valid") else "",
            }
            for c in cites
        ]
        digest = {}
        exposure = DATA / "evidence" / (row["unit"] + ".json.gz")
        if exposure.is_file() and q["facts"]:
            with gzip.open(exposure, "rt", encoding="utf8") as file:
                observed = json.load(file)
            root = index_for(q["folder"], False).root
            for path in {f["path"] for f in q["facts"] if f["path"]}:
                source = root / path
                if source.is_file():
                    digest[path] = visible_fragments(
                        source.read_text(encoding="utf8"), observed
                    )
        facts = [
            {
                "claim": f["fact"],
                "evidence": "\n".join(dict.fromkeys(digest.get(f["path"], [])))[:10000],
            }
            for f in q["facts"]
        ]
        ids_field = {"type": "array", "items": {"type": "integer"}}
        supported = set()
        claims = []
        usable = [(i, x) for i, x in enumerate(items) if x["evidence"]]
        if row.get("answer"):
            task = (
                "Answer two independent questions using only the supplied text. First, return the citation IDs whose quote supports its attached claim. "
                "Second, extract each distinct factual assertion in the entire answer and explanation, including assertions with no citation. "
                "For each assertion give the IDs of the supplied quotes that jointly substantiate it, or an empty list. "
                "Do not infer from outside knowledge. Exclude a bare abstention from factual assertions.\n"
                + json.dumps(
                    dict(
                        question=q["question"],
                        answer=row["answer"],
                        explanation=row.get("explanation", ""),
                        citations=usable,
                    ),
                    ensure_ascii=False,
                )
            )
            result = blind_labels(
                "audit-claims-" + row["unit"],
                task,
                {
                    "supported_ids": ids_field,
                    "claims": {
                        "type": "array",
                        "items": schema(
                            {"claim": {"type": "string"}, "source_ids": ids_field}
                        ),
                    },
                },
            )
            allowed = {i for i, _ in usable}
            supported = allowed & set(result["supported_ids"])
            claims = [
                {
                    "claim": c["claim"],
                    "source_ids": sorted(allowed & set(c["source_ids"])),
                }
                for c in result["claims"]
            ]
        usable_facts = [(i, x) for i, x in enumerate(facts) if x["evidence"]]
        fact_labels = set()
        if usable_facts:
            task = (
                "For each numbered reference fact, determine whether its associated displayed excerpt alone establishes it. "
                "Return the supported integer IDs.\n"
                + json.dumps(
                    dict(question=q["question"], pairs=usable_facts), ensure_ascii=False
                )
            )
            fact_labels = {i for i, _ in usable_facts} & set(
                blind_labels(
                    "audit-facts-" + row["unit"], task, {"supported_ids": ids_field}
                )["supported_ids"]
            )
        n_def = n_call = 0
        if q["domain"] == "code":
            root = index_for(q["folder"], False).root
            for c in cites:
                if c.get("valid"):
                    defs, calls = code_sites(root / c["path"])
                    lines = set(
                        range(c["line"], c["line"] + c["quote"].count("\n") + 1)
                    )
                    n_def += bool(lines & defs)
                    n_call += bool(lines & calls)
        save(
            dest,
            {
                "unit": row["unit"],
                "domain": q["domain"],
                "arm": row["arm"],
                "n_citations": len(cites),
                "supported": len(supported),
                "claims": claims,
                "n_claims": len(claims),
                "claims_supported": sum(bool(c["source_ids"]) for c in claims),
                "definition_citations": n_def,
                "call_citations": n_call,
                "missing_citations": int(not cites),
                "gold_facts": len(facts),
                "gold_facts_supported": len(fact_labels),
            },
        )

    with ThreadPoolExecutor(workers) as pool:
        for _ in pool.map(audit, (r for r in records("test") if r["id"] in ids)):
            pass
