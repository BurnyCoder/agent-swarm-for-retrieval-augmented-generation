"""Derive reportable counts and design diagnostics from persistent experiment records."""

from collections import defaultdict
from statistics import mean


def group_by(rows, fields):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(f) for f in fields)].append(row)
    return sorted(groups.items())


def ratio(n, d):
    return f"{n}/{d} ({n / d:.1%})" if d else "—"


def grid(headers, rows):
    def line(values):
        return "| " + " | ".join(str(x).replace("|", "\\|") for x in values) + " |"

    return "\n".join(
        [line(headers), line(["---"] * len(headers)), *(line(r) for r in rows)]
    )


def grounding(data):
    result = []
    for (phase, domain, arm), rows in group_by(
        data["rows"], ["phase", "domain", "arm"]
    ):
        cites = [c for row in rows for c in row.get("citations", [])]
        coverage = [
            row[k]
            for row in rows
            for k in ["returned_gold_recall"]
            if row.get(k) is not None
        ]
        citedgold = [
            row["cited_gold_recall"]
            for row in rows
            if row.get("cited_gold_recall") is not None
        ]
        result.append(
            [
                phase,
                domain,
                arm,
                len(rows),
                ratio(sum(bool(c.get("valid")) for c in cites), len(cites)),
                ratio(sum(bool(r.get("citations")) for r in rows), len(rows)),
                f"{mean(coverage):.1%}" if coverage else "—",
                f"{mean(citedgold):.1%}" if citedgold else "—",
            ]
        )
    return grid(
        [
            "Phase",
            "Domain",
            "Method",
            "Answers",
            "Literal quotes valid",
            "Answers with citations",
            "Gold files returned¹",
            "Gold files cited¹",
        ],
        result,
    )


def support(data):
    result = []
    for (domain, arm), rows in group_by(data["support"], ["domain", "arm"]):

        def total(k):
            return sum(r.get(k, 0) for r in rows)

        result.append(
            [
                domain,
                arm,
                len(rows),
                ratio(
                    total("supported"),
                    total("n_citations") + total("missing_citations"),
                ),
                ratio(total("claims_supported"), total("n_claims")),
                total("missing_citations"),
                ratio(total("gold_facts_supported"), total("gold_facts")),
                total("definition_citations"),
                total("call_citations"),
            ]
        )
    return grid(
        [
            "Domain",
            "Method",
            "Audited",
            "Citation support²",
            "Factual assertions supported",
            "Answers without citations",
            "Gold facts shown",
            "Definition citations",
            "Call citations",
        ],
        result,
    )


def bridge(data):
    return grid(
        [
            "Original generator",
            "Historical condition",
            "Domain",
            "N",
            "Common-scorer mean",
        ],
        [
            [
                "Haiku",
                arm,
                domain,
                len(rows),
                f"{mean(r['score'] for r in rows):.1%}"
                if domain == "news"
                else f"{mean(r['score'] for r in rows):.1f}",
            ]
            for (domain, arm), rows in group_by(data["historical"], ["domain", "arm"])
        ],
    )


def swarms(data):
    rows = []
    for (phase, domain, arm), group in group_by(
        data["rows"], ["phase", "domain", "arm"]
    ):
        if not arm.startswith("swarm"):
            continue
        requested = (int(arm[5:]) - 1) * len(group)
        rows.append(
            [
                phase,
                domain,
                arm,
                len(group),
                requested,
                sum(r.get("workers_completed", 0) for r in group),
                sum(r.get("workers_contributing", 0) for r in group),
                max(r.get("peak_investigators", 0) for r in group),
                sum(r.get("duplicate_worker_spans", 0) for r in group),
            ]
        )
    return grid(
        [
            "Phase",
            "Domain",
            "Size condition",
            "Cases",
            "Investigators assigned",
            "Returned",
            "Supplied verified evidence",
            "Max simultaneous",
            "Repeated span reads",
        ],
        rows,
    )


def twins(data):
    return grid(
        [
            "Domain",
            "Intervention",
            "Expected",
            "Observed",
            "Correct",
            "Verified citations",
        ],
        [
            [
                r["domain"],
                r.get("source_edit", ""),
                r["expected"],
                r["answer"],
                r["score"],
                sum(bool(c.get("valid")) for c in r["citations"]),
            ]
            for r in data["twins"]
        ],
    )


def repeats(data):
    selected = f"swarm{data['freeze'].get('size', 0)}"
    originals = {
        r["id"]: r
        for r in data["rows"]
        if r["phase"] == "test" and r["arm"] == selected
    }
    repeated = [
        r for r in data["rows"] if r["arm"] == "repeat" and r["id"] in originals
    ]
    return grid(
        [
            "Domain",
            "Paired repeats",
            "Identical short answer",
            "Mean absolute score change",
        ],
        [
            [
                domain,
                len(group),
                ratio(
                    sum(
                        r["answer"].casefold()
                        == originals[r["id"]]["answer"].casefold()
                        for r in group
                    ),
                    len(group),
                ),
                f"{mean(abs(r['score'] - originals[r['id']]['score']) for r in group if r.get('score') is not None and originals[r['id']].get('score') is not None):.3f}",
            ]
            for (domain,), group in group_by(repeated, ["domain"])
            if any(
                r.get("score") is not None
                and originals[r["id"]].get("score") is not None
                for r in group
            )
        ],
    )


def operating_choices(data):
    groups = [g for g in data["groups"] if g["phase"] == "test"]
    out = []
    for (domain,), group in group_by(groups, ["domain"]):
        target = data["freeze"]["blocks"] * (32 if domain == "news" else 15)
        if len(group) != 5 or any(r["graded"] != target for r in group):
            continue
        best = min(group, key=lambda r: (-r["mean"], r["cost"], r["p50"]))
        out.append(
            f"For {domain}, {best['arm']} has the highest observed quality after breaking exact ties by cost and then median latency. Its conservative mean inference charge is ${best['cost']:.4f} per question."
        )
    return " ".join(out)
