"""Report an owner-shortened frozen prefix without changing any original answers or charges."""


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
    return (
        f"The {data['freeze']['size']}-agent swarm answered {round(news['mean'] * news['n'])}/{news['n']} "
        f"news questions correctly and averaged {code['mean']:.2f}/100 on code. "
        f"The highest observed news score came from {labels[best_news['arm']]} "
        f"({round(best_news['mean'] * best_news['n'])}/{best_news['n']}). "
        f"The highest observed code score came from {labels[best_code['arm']]} ({best_code['mean']:.2f}/100). "
        f"One investigator scored {round(groups['news', 'swarm1']['mean'] * news['n'])}/{news['n']} "
        f"on news and {groups['code', 'swarm1']['mean']:.2f}/100 on code. "
        f"The swarm's code difference from one-shot retrieval was {code['mean'] - groups['code','oneshot']['mean']:+.2f} points. "
        "The shortened panel supports exploratory paired estimates. The original full-sample superiority claim remains unresolved."
    )
