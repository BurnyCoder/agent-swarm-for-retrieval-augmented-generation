"""Generate the dated README results from the same private snapshot as the paper."""

from datetime import datetime, timezone
from statistics import mean, median

from .outcomes import grid, matched_first_attempts
from .paths import LIMITS
from .closeout import scope_note


def heldout_snapshot(data):
    """Show like-for-like comparisons and distinguish primary scores from outage sensitivity."""
    held = [r for r in data["rows"] if r["phase"] == "test"]
    if not held:
        return ""
    size = data["freeze"]["size"]
    selected = f"swarm{size}"
    arms = (selected, "swarm1", "stock", "arctic", "oneshot")
    paired = matched_first_attempts(held, arms)
    flagged = {r["unit"] for r in data["capacity-flags"]} & {r["unit"] for r in held}
    clean = [q for q in paired if all(r["unit"] not in flagged for r in q.values())]
    target = data["targets"]["test"]
    when = datetime.fromisoformat(data["updated"]).astimezone(timezone.utc)
    lines = [
        "## Current held-out results",
        f"**{when:%Y-%m-%d %H:%M UTC}.** "
        + ("Closed for today. " if data.get("closeout") else "")
        + "The study has recorded "
        f"**{len(held):,}/{target:,} evaluations ({len(held) / target:.1%})**. "
        f"All five methods have scores on {len(paired):,} questions. "
        f"The development sweep selected {size} total agents, including the coordinator.",
    ]
    if data.get("closeout"):
        lines.append(
            scope_note(data["closeout"])
            + " [Cutoff and frozen question IDs](protocol/closeout.json)"
        )
        lines.append(
            "The [experiment inventory](reports/experiments/inventory.md) lists completed studies, "
            "the five comparisons closed early against their original targets, and every postponed "
            "experiment with its purpose and run counts."
        )
    table_rows = []
    for domain, title in (("news", "News"), ("code", "Code")):
        for label, panel in (("first attempts", paired), ("outage-free", clean)):
            group = [q for q in panel if q[selected]["domain"] == domain]
            if not group or (label == "outage-free" and not flagged):
                continue
            values = [
                f"{sum(q[a]['score'] for q in group):.0f}/{len(group)}"
                if domain == "news"
                else f"{mean(q[a]['score'] for q in group):.2f}"
                for a in arms
            ]
            table_rows.append([f"{title}, {label}", len(group), *values])
    if table_rows:
        lines.append(
            grid(*data["closeout_tables"]["quality"])
            if data.get("closeout_tables")
            else grid(
                [
                    "Matched panel",
                    "Questions",
                    f"{size}-agent swarm",
                    "One agent",
                    "Stock Codex",
                    "Arctic single agent",
                    "One-shot RAG",
                ],
                table_rows,
            )
        )
        note = "News cells count exact matches. Code cells give the mean blinded rubric score out of 100."
        if flagged:
            note += (
                f" The primary scores retain {len(flagged)} provider-overload "
                f"failure{'s' if len(flagged) != 1 else ''}. The outage-free scores exclude a question "
                "from all five methods whenever any arm had a recorded overload failure."
            )
        lines.append(
            note + " [Paired outage analysis](reports/experiments/availability.md)"
        )
    news = [q for q in clean if q[selected]["domain"] == "news"]
    annotated = [
        q for q in news if all(q[a].get("cited_gold_recall") is not None for a in arms)
    ]
    if annotated:
        recalls = [
            mean(q[a]["cited_gold_recall"] for q in annotated)
            for a in (selected, "swarm1", "stock")
        ]
        lines.append(
            f"Across {len(annotated)} outage-free news questions with annotated sources, "
            f"the swarm cited {recalls[0]:.1%} of the reference files per question on average. "
            f"One agent cited {recalls[1]:.1%} and stock Codex cited {recalls[2]:.1%}. "
            "[Citation and claim-support measurements](reports/experiments/grounding.md)"
        )
    if data.get("closeout_tables"):
        tables = data["closeout_tables"]
        lines.extend(
            [
                "### Cost and latency on all first attempts",
                grid(*tables["resources"]),
                "Costs are mean upper estimates for answer generation. Latencies are medians in seconds and exclude index setup. The study ledger also includes grading.",
                "### Four-agent swarm minus each comparator",
                grid(*tables["effects"]),
                "Positive differences favor the swarm. News uses percentage points and code uses rubric points out of 100. The intervals are paired and exploratory after the cutoff. Holm correction covers the six external comparisons together and the two single-agent comparisons separately.",
                "### Swarm size on development and held-out questions",
                grid(*tables["sizes"]),
                "All four sizes answered the same development questions. The one- and four-agent systems also answered the same held-out panel. The other two held-out size conditions were postponed.",
            ]
        )
    elif news:
        operating = [
            (
                median(q[a]["seconds"] for q in news),
                mean(q[a]["cost_upper_usd"] for q in news),
            )
            for a in (selected, "stock")
        ]
        (swarm_time, swarm_cost), (stock_time, stock_cost) = operating
        lines.append(
            f"On the {len(news)} matched outage-free news questions, the swarm took a median "
            f"**{swarm_time:.0f} seconds** at a mean upper cost of **${swarm_cost:.4f} per question**. "
            f"Stock Codex took **{stock_time:.0f} seconds** at **${stock_cost:.4f}**."
        )
    balances = data["balances"]
    lines.append(
        f"The study ledger shows **${balances.get('settled', 0):.2f} settled** and "
        f"**${balances.get('reserved', 0):.2f} reserved** against the ${sum(LIMITS.values()):.0f} ceiling. "
        f"The fixed semantic evidence audit has {len(data['support'])}/{data['targets']['audit']} records. "
        "[Live local dashboard](http://127.0.0.1:8765) · [Private explorer](https://huggingface.co/spaces/BurnyCoder/luna-folder-swarm-explorer)"
    )
    return "\n\n".join(lines)
