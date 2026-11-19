"""Describe the registered experiments with counts from the same records used for scoring."""

from collections import Counter

from .evaluate import BASE, SIZES


def experiment_inventory(data, split):
    """Count graded original runs, controls, and technical repeats under their own populations."""
    items = []
    count = Counter(
        (r["phase"], r["arm"]) for r in data["rows"] if r.get("score") is not None
    )
    legacy = len(split["legacy"])
    stages = {s["phase"]: s["state"] for s in data["stages"]}

    def add(name, kind, done, planned, purpose, phase=None):
        if planned is not None and done >= planned and planned > 0:
            status = "Completed"
        elif data.get("closeout") and phase == "test":
            status = "Closed early"
        elif data.get("closeout") and phase in {
            "diagnostics",
            "twins",
            "support",
            "retry",
        }:
            status = "Postponed"
        elif stages.get(phase) in ("budget_stop", "stopped"):
            status = "Stopped"
        elif stages.get(phase) == "finished":
            status = "Incomplete"
        elif done or stages.get(phase) == "running":
            status = "In progress"
        else:
            status = "Planned"
        items.append(
            dict(
                name=name,
                kind=kind,
                status=status,
                done=done,
                planned=planned,
                purpose=purpose,
                phase=phase,
            )
        )

    if data["pilot"]:
        n = len(data["pilot"])
        add(
            "Investigator handoff pilot",
            "Engineering pilot",
            n,
            n,
            "Check whether concurrent investigators return their findings before their turn limits.",
        )
    add(
        "Live CLI checks",
        "End-to-end checks",
        len(data["smoke"]),
        2,
        "Combine two files to answer a question, then abstain when a date is missing.",
    )
    add(
        "News passage addresses",
        "Deterministic data audit",
        int(bool(data["offset_audit"])),
        1,
        "Reproduce exact source slices and check for duplicate identifiers on long lines.",
    )
    add(
        "Historical Arctic comparison",
        "Retrospective rescoring",
        len(data["historical"]),
        2 * legacy,
        "Apply the common scorers to archived Haiku single-agent and swarm answers.",
    )
    add(
        "Development size sweep",
        "Model selection",
        sum(count["dev", a] for a in SIZES),
        len(SIZES) * legacy,
        "Compare sizes 1, 2, 4, and 8 on the same legacy questions before selecting the candidate.",
        "dev",
    )
    add(
        "Development baselines",
        "Baseline calibration",
        sum(count["dev", a] for a in BASE),
        len(BASE) * legacy,
        "Measure stock Codex, Arctic single agent, and one-shot retrieval on the development questions.",
        "dev",
    )
    if not data["freeze"] or not data["freeze"]["blocks"]:
        return items

    blocks = split["blocks"][: data["freeze"]["blocks"]]
    per_arm = sum(map(len, blocks))
    size = data["freeze"]["size"]
    selected = f"swarm{size}"
    number = {2: "Two", 4: "Four", 8: "Eight"}[size]
    methods = [
        (
            selected,
            number + "-agent swarm",
            "Confirmatory candidate",
            "Independent investigators hand verified passages to a coordinator.",
        ),
        (
            "swarm1",
            "One-agent harness",
            "Delegation comparison",
            "Use the same retrieval tools and question-level resource ceiling with one investigator.",
        ),
        (
            "stock",
            "Stock Codex",
            "File-search baseline",
            "Let stock Codex investigate the same immutable folder.",
        ),
        (
            "arctic",
            "Arctic single agent",
            "Prior-system baseline",
            "Run the earlier Arctic B2 agent with the same Luna model and effort.",
        ),
        (
            "oneshot",
            "One-shot hybrid RAG",
            "Retrieval baseline",
            "Generate one answer from a fixed set of hybrid-ranked passages.",
        ),
    ]
    for arm, name, kind, purpose in methods:
        add(name, kind, count["test", arm], per_arm, purpose, "test")

    panel = blocks[0]
    domains = Counter("news" if q.startswith("mhr_") else "code" for q in panel)
    for arm in SIZES:
        if arm not in (selected, "swarm1"):
            add(
                f"Held-out {arm[5:]}-agent swarm",
                "Swarm-size comparison",
                count["diagnostics", arm],
                len(panel),
                "Measure the other swarm sizes on the fixed first block shared by all four sizes.",
                "diagnostics",
            )
    controls = [
        (
            "closed",
            "Closed book",
            "Knowledge control",
            len(panel),
            "Answer without source files to measure what the question and model alone provide.",
        ),
        (
            "random",
            "Random passages",
            "Negative control",
            len(panel),
            "Replace relevance ranking with randomly selected passages under the same passage budget.",
        ),
        (
            "oracle",
            "Gold news evidence",
            "Retrieval diagnostic",
            data["targets"].get("oracle"),
            "Supply annotated evidence for eligible news questions to probe remaining answer errors.",
        ),
        (
            "lexical",
            "Lexical search only",
            "Retrieval ablation",
            len(panel),
            "Disable dense search in the selected swarm and retain lexical search.",
        ),
        (
            "unchecked",
            "Verification disabled",
            "Citation ablation",
            len(panel),
            "Disable the citation-repair opportunity in the selected swarm and still score the returned quotes.",
        ),
        (
            "repeat",
            "Independent repeat",
            "Run variability",
            sum(min(4, n) for n in domains.values()),
            "Rerun the selected swarm on unchanged documents and compare answers and scores.",
        ),
    ]
    for arm, name, kind, planned, purpose in controls:
        add(name, kind, count["diagnostics", arm], planned, purpose, "diagnostics")
    add(
        "Changed-fact folders",
        "Causal intervention",
        len(data["twins"]),
        4,
        "Change the decisive stop count or Requests pool-size constant in a pair of copies of each corpus.",
        "twins",
    )
    add(
        "Blinded evidence audit",
        "Grounding evaluation",
        len(data["support"]),
        data["targets"]["audit"],
        "Assess claim support, uncited assertions, gold fact exposure, and code definitions and calls.",
        "support",
    )
    if data["capacity-flags"]:
        add(
            "Provider-failure repeats",
            "Operational sensitivity",
            len(data["capacity-repeats"]),
            len(data["capacity-flags"]),
            "Repeat eligible upstream failures once within the retry budget. Primary scores keep their first attempts.",
            "retry",
        )
    return items
