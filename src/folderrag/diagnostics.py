"""Historical bridge, fact interventions, and blinded source-support audit."""

import json
import re
import gzip

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
                (source / "settings.py").write_text(
                    f"DEFAULT = {value}\nDISABLED = 12\n"
                )
                (source / "service.py").write_text(
                    "from settings import DEFAULT\ndef capacity():\n    return DEFAULT\n"
                )
                q = "What integer does capacity() return in this checkout? Answer with one integer."
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


def support_audit():
    """Judge each citation's support independently of address validity, then audit annotated news facts."""
    ids = set(read(ROOT / "protocol/splits.json")["blocks"][0])
    cases = read(BENCH / "cases.json")
    for row in records("test"):
        if row["id"] not in ids:
            continue
        dest = DATA / "support" / (row["unit"] + ".json")
        if dest.exists():
            continue
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
        pairs = items + facts
        labels = [False] * len(pairs)
        usable = [(i, x) for i, x in enumerate(pairs) if x["evidence"]]
        if usable:
            case = new_case(None, "diagnostics", "audit-" + row["unit"])
            prompt = (
                "For each numbered claim, determine whether the provided excerpt alone supports it. Return the supported integer IDs. Question: "
                + q["question"]
                + "\n"
                + json.dumps(usable, ensure_ascii=False)
            )
            result = json.loads(
                direct(
                    case.gateway("audit", 1, Evidence(), "lexical"),
                    prompt,
                    schema(
                        {
                            "supported_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                            }
                        }
                    ),
                )
            )
            allowed = {i for i, _ in usable}
            for i in result["supported_ids"]:
                if i in allowed:
                    labels[i] = True
        save(
            dest,
            {
                "unit": row["unit"],
                "n_citations": len(cites),
                "supported": sum(labels[: len(items)]),
                "missing_citations": int(not cites),
                "gold_facts": len(facts),
                "gold_facts_supported": sum(labels[len(items) :]),
            },
        )
