"""Report an owner-shortened frozen prefix without changing any original answers or charges."""

from statistics import mean

from .outcomes import matched_first_attempts


def comparison_tables(data):
    """Use identical questions for each workload, resource table, and paired difference."""
    size = data["freeze"]["size"]
    arms = (f"swarm{size}", "swarm1", "stock", "arctic", "oneshot")
    names = dict(
        zip(
            arms,
            (
                f"{size}-agent swarm",
                "1-agent harness",
                "Stock Codex",
                "Arctic single agent",
                "One-shot hybrid RAG",
            ),
        )
    )
    groups = {(r["phase"], r["domain"], r["arm"]): r for r in data["groups"]}
    panel = matched_first_attempts(data["rows"], arms)
    flags = {r["unit"] for r in data["capacity-flags"]}
    clean = [q for q in panel if all(r["unit"] not in flags for r in q.values())]
    cohorts = [
        (d, [q for q in p if q[arms[0]]["domain"] == d])
        for d in ("news", "code")
        for p in (panel, clean)
    ]

    def quality(domain, values):
        if not values:
            return "—"
        if domain == "code":
            return f"{mean(values):.2f}"
        return f"{sum(values):.0f}/{len(values)} ({mean(values):.1%})"

    scores, costs = [], []
    for arm in arms:
        scores.append(
            [
                names[arm],
                *(quality(d, [q[arm]["score"] for q in p]) for d, p in cohorts),
            ]
        )
        resources = [names[arm]]
        for domain in ("news", "code"):
            g = groups["test", domain, arm]
            resources.extend([f"${g['cost']:.5f}", f"{g['p50']:.1f}"])
        costs.append(resources)
    sizes = []
    for n in (1, 2, 4, 8):
        row = [str(n)]
        for phase in ("dev", "test"):
            for domain in ("news", "code"):
                g = groups.get((phase, domain, f"swarm{n}"))
                row.append(
                    ("Postponed" if phase == "test" else "—")
                    if not g
                    else (
                        f"{round(g['mean'] * g['n'])}/{g['n']}"
                        if domain == "news"
                        else f"{g['mean']:.2f} (n={g['n']})"
                    )
                )
        sizes.append(row)
    paired = {(r["domain"], r["comparator"]): r for r in data["comparisons"]}
    effects = []
    for arm in arms[1:]:
        row = [names[arm]]
        for domain, scale in (("news", 100), ("code", 1)):
            r = paired[domain, arm]
            row.extend(
                [
                    f"{scale * r['difference']:+.2f} [{scale * r['low']:+.2f}, {scale * r['high']:+.2f}]",
                    f"{r['holm_p']:.4f}",
                ]
            )
        effects.append(row)
    return {
        "quality": [
            [
                "Method",
                *(
                    f"{s} (n={len(p)})"
                    for s, (_, p) in zip(
                        ("News", "News outage-free", "Code", "Code outage-free"),
                        cohorts,
                    )
                ),
            ],
            scores,
        ],
        "resources": [
            [
                "Method",
                "News USD / question",
                "News median s",
                "Code USD / question",
                "Code median s",
            ],
            costs,
        ],
        "sizes": [
            [
                "Agents",
                "Development news",
                "Development code",
                "Held-out news",
                "Held-out code",
            ],
            sizes,
        ],
        "effects": [
            [
                "Comparator",
                "News difference [95% CI], pp",
                "Holm p",
                "Code difference [95% CI]",
                "Holm p",
            ],
            effects,
        ],
    }


def selected_rows(rows, decision):
    """Use only question membership to select held-out attempts. Preserve development rows."""
    if not decision:
        return rows
    ids = set(decision["included_ids"])
    return [r for r in rows if r["phase"] != "test" or r["id"] in ids]


def scope_note(decision):
    return (
        f"Paid acquisition stopped at the owner's request after interim scores were visible. "
        f"Today's panel uses the first {decision['question_limit']} of the {decision['registered_questions']} questions "
        f"in the frozen order ({decision['domain_counts']['news']} news and {decision['domain_counts']['code']} code). "
        f"The archive preserves {len(decision['excluded_recorded_units'])} additional completed answers "
        f"from {decision['excluded_question_count']} later questions outside the analysis. "
        "The spending ledger includes those answers and interrupted calls. The remaining questions, "
        "controls, repeats, changed-fact tests and semantic evidence audits are postponed."
    )


def findings(data):
    """Summarize observed quality on the common panel and qualify the post-registration cutoff."""
    selected = f"swarm{data['freeze']['size']}"
    groups = {
        (g["domain"], g["arm"]): g for g in data["groups"] if g["phase"] == "test"
    }
    if ("news", selected) not in groups or ("code", selected) not in groups:
        return "The closeout contains an incomplete two-domain score export."
    news, code = groups["news", selected], groups["code", selected]
    labels = {
        "stock": "stock Codex",
        "arctic": "Arctic single agent",
        "oneshot": "one-shot RAG",
        "swarm1": "the one-agent harness",
        selected: "the selected swarm",
    }

    def best(domain):
        return min(
            (g for (d, _), g in groups.items() if d == domain),
            key=lambda g: (-g["mean"], g["cost"], g["p50"]),
        )

    best_news, best_code = best("news"), best("code")
    size_effects = [r for r in data["comparisons"] if r["comparator"] == "swarm1"]
    size_uncertainty = (
        "Both paired intervals for adding investigators include zero. "
        if len(size_effects) == 2
        and all(r["low"] <= 0 <= r["high"] for r in size_effects)
        else ""
    )
    return (
        f"The {data['freeze']['size']}-agent swarm answered {round(news['mean'] * news['n'])}/{news['n']} "
        f"news questions correctly and averaged {code['mean']:.2f}/100 on code. "
        f"The highest observed news score came from {labels[best_news['arm']]} "
        f"({round(best_news['mean'] * best_news['n'])}/{best_news['n']}). "
        f"The highest observed code score came from {labels[best_code['arm']]} ({best_code['mean']:.2f}/100). "
        f"One investigator scored {round(groups['news', 'swarm1']['mean'] * news['n'])}/{news['n']} "
        f"on news and {groups['code', 'swarm1']['mean']:.2f}/100 on code. "
        f"The swarm's code difference from one-shot retrieval was {code['mean'] - groups['code', 'oneshot']['mean']:+.2f} points. "
        + size_uncertainty
        + "The shortened panel supports exploratory paired estimates. The original full-sample superiority claim remains unresolved."
    )
