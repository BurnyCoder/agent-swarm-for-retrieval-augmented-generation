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
                f"{mean(r.get('requests', 0) for r in group):.1f}",
                f"{mean(r.get('output_tokens', 0) for r in group):.0f}",
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
            "Mean requests",
            "Mean output tokens",
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


def matched_first_attempts(rows, arms):
    """Return graded first attempts for questions with one observation in every arm."""
    cases = defaultdict(dict)
    for row in rows:
        if (
            row["phase"] == "test"
            and row["arm"] in arms
            and row.get("score") is not None
        ):
            cases[row["id"]][row["arm"]] = row
    return [q for q in cases.values() if all(a in q for a in arms)]


def availability(data):
    """Hold all five arms to identical question sets when describing the service interruption."""
    if not data["capacity-flags"]:
        return "Awaiting a completed capacity-failure audit."
    arms = (f"swarm{data['freeze']['size']}", "swarm1", "stock", "arctic", "oneshot")
    flagged = {r["unit"] for r in data["capacity-flags"]}
    repeats = {
        r["original"]: r["repeated_score"]
        for r in data["capacity-repeats"]
        if not r["error"] and r["repeated_score"] is not None
    }
    cases = matched_first_attempts(data["rows"], arms)
    output = []
    for domain in ("news", "code"):
        panel = [q for q in cases if q[arms[0]]["domain"] == domain]
        unaffected = [
            q for q in panel if all(r["unit"] not in flagged for r in q.values())
        ]
        restored = [
            q
            for q in panel
            if all(r["unit"] not in flagged or r["unit"] in repeats for r in q.values())
        ]

        def cell(group, arm, replace=False):
            if not group:
                return "—"
            values = [
                repeats.get(q[arm]["unit"], q[arm]["score"])
                if replace
                else q[arm]["score"]
                for q in group
            ]
            avg = mean(values)
            return (
                f"{avg:.1%}" if domain == "news" else f"{avg:.2f}"
            ) + f" (n={len(group)})"

        for arm in arms:
            output.append(
                [
                    domain,
                    arm,
                    cell(panel, arm),
                    cell(unaffected, arm),
                    cell(restored, arm, True),
                ]
            )
    return grid(
        [
            "Domain",
            "Method",
            "Primary complete pairs",
            "Without flagged questions",
            "With technical repeats",
        ],
        output,
    )


def fixed_panel(data, ids, sizes=False):
    """Compare each diagnostic with the same questions under its specified reference arm."""
    import numpy as np

    if not data["freeze"]:
        return "Awaiting the frozen selection."
    base = "swarm1" if sizes else f"swarm{data['freeze']['size']}"
    rows = [
        r
        for r in data["rows"]
        if r["id"] in ids
        and r["phase"] in ("test", "diagnostics")
        and r.get("score") is not None
    ]
    reference = {r["id"]: r for r in rows if r["arm"] == base}
    comparisons = [
        r
        for r in rows
        if r["id"] in reference
        and (r["arm"].startswith("swarm") if sizes else r["phase"] == "diagnostics")
    ]
    out = []
    for (domain, arm), group in group_by(comparisons, ["domain", "arm"]):
        pairs = [(r, reference[r["id"]]) for r in group]
        scale = 100 if domain == "news" else 1
        changes = np.asarray([scale * (a["score"] - b["score"]) for a, b in pairs])
        rng = np.random.default_rng(20261119)
        draws = rng.choice(changes, (4000, len(changes))).mean(axis=1)
        lo, hi = np.quantile(draws, [0.025, 0.975])
        out.append(
            [
                domain,
                arm,
                len(group),
                f"{scale * mean(r['score'] for r in group):.2f}",
                f"{changes.mean():+.2f} [{lo:+.2f}, {hi:+.2f}]",
                f"{mean(r['cost_upper_usd'] for r in group):.4f}",
                f"{np.median([r['seconds'] for r in group]):.1f}",
            ]
        )
    return grid(
        [
            "Domain",
            "Condition",
            "Pairs",
            "Quality",
            "Difference from " + base + " [95%]",
            "USD / question",
            "Median seconds",
        ],
        out,
    )


def coverage(data):
    plan = {s["phase"]: s["planned"] for s in data["stages"]}
    plan.update(data["targets"])
    result = []
    for phase in ("dev", "test", "diagnostics"):
        rows = [r for r in data["rows"] if r["phase"] == phase]
        n = plan.get(phase)
        errors = [r["error"] for r in rows if r.get("error")]
        result.append(
            [
                phase,
                n if n is not None else "pending",
                len(rows),
                n - len(rows) if n is not None else "—",
                len(errors),
                sum(
                    "timed out" in s.lower() or "deadline" in s.lower() for s in errors
                ),
                sum(r.get("score") is None for r in rows),
            ]
        )
    return grid(
        [
            "Phase",
            "Registered runs",
            "Completed records",
            "Pending/unrun",
            "Generation failures",
            "Timeouts",
            "Missing grade",
        ],
        result,
    )


def strata(data):
    development_repos = {
        r["stratum"]
        for r in data["rows"]
        if r["phase"] == "dev" and r["domain"] == "code"
    }
    held = [
        r for r in data["rows"] if r["phase"] == "test" and r.get("score") is not None
    ]
    rows = []
    for (domain, stratum, arm), items in group_by(held, ["domain", "stratum", "arm"]):
        score = mean(r["score"] for r in items)
        rows.append(
            [
                domain,
                stratum,
                (
                    "development repository"
                    if stratum in development_repos
                    else "new repository"
                )
                if domain == "code"
                else "news type",
                arm,
                len(items),
                f"{score:.1%}" if domain == "news" else f"{score:.2f}",
            ]
        )
    return grid(
        ["Domain", "Stratum", "Split membership", "Condition", "Graded", "Mean"], rows
    )
