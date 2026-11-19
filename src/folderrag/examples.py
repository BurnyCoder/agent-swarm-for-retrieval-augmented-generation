"""Fixed-order examples: selection depends on registered identifiers, never answer quality."""

from .analysis import means
from .paths import ROOT, read


def matched_size_groups(rows, first_block):
    """Use the common four-size question set for each domain and study phase."""
    arms = ("swarm1", "swarm2", "swarm4", "swarm8")
    panels = []
    for domain in ("news", "code"):
        for phase in ("dev", "held"):
            candidates = [
                r
                for r in rows
                if r["domain"] == domain
                and r["arm"] in arms
                and r.get("score") is not None
                and (
                    r["phase"] == "dev"
                    if phase == "dev"
                    else r["id"] in first_block
                    and r["phase"] in ("test", "diagnostics")
                )
            ]
            common = set.intersection(
                *[{r["id"] for r in candidates if r["arm"] == arm} for arm in arms]
            )
            panels.extend(
                {**r, "phase": phase} for r in candidates if r["id"] in common
            )
    return means(panels)


def plot_swarm_sizes(data, directory):
    """Only compare sizes on questions completed by all four systems within each panel."""
    import matplotlib.pyplot as plt
    import numpy as np

    sizes = (1, 2, 4, 8)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.7), layout="constrained", sharey=True)
    plotted = False
    for ax, domain in zip(axes, ("news", "code")):
        for phase, label, offset, color in (
            ("dev", "Development", -0.065, "#276b5d"),
            ("held", "Held-out block", 0.065, "#a44d2b"),
        ):
            rows = [
                g
                for g in data["size_groups"]
                if g["phase"] == phase and g["domain"] == domain
            ]
            if not rows:
                continue
            plotted = True
            scale = 100 if domain == "news" else 1
            ys = np.asarray([r["mean"] * scale for r in rows])
            lo = np.maximum(0, ys - np.asarray([r["low"] * scale for r in rows]))
            hi = np.maximum(0, np.asarray([r["high"] * scale for r in rows]) - ys)
            ax.errorbar(
                np.arange(4) + offset,
                ys,
                yerr=[lo, hi],
                fmt="o-",
                markersize=4,
                capsize=3,
                color=color,
                label=f"{label} (n={rows[0]['n']})",
            )
        ax.set(
            xticks=range(4),
            xticklabels=sizes,
            xlabel="Total agents, including coordinator",
            ylim=(-2, 102),
            title="News exact match (%)"
            if domain == "news"
            else "Code rubric score / 100",
        )
        ax.grid(axis="y", alpha=0.2)
        if ax.lines:
            ax.legend(frameon=False, fontsize=8)
    if plotted:
        fig.savefig(directory / "swarm-size.png", dpi=155)
    plt.close(fig)
    return plotted


def selected_examples(data, per_domain=2):
    split = read(ROOT / "protocol/splits.json")
    held = any(r["phase"] == "test" for r in data["rows"])
    ids = split["blocks"][0] if held else list(split["legacy"].values())
    ids = [
        i
        for prefix in ("mhr_", "sweqa_")
        for i in [q for q in ids if q.startswith(prefix)][:per_domain]
    ]
    rows = [
        r
        for r in data["rows"]
        if r["id"] in ids
        and (r["phase"] in ("test", "diagnostics") if held else r["phase"] == "dev")
    ]
    return ids, rows


def render_examples(data, directory):
    import numpy as np
    import matplotlib.pyplot as plt

    ids, rows = selected_examples(data)
    if not rows:
        return ""
    methods = sorted({r["arm"] for r in rows})
    values = np.full((len(methods), len(ids)), np.nan)
    for r in rows:
        if r.get("score") is not None:
            values[methods.index(r["arm"]), ids.index(r["id"])] = r["score"] * (
                100 if r["domain"] == "news" else 1
            )
    fig, ax = plt.subplots(
        figsize=(9, max(3.2, len(methods) * 0.34 + 1.35)), layout="constrained"
    )
    cmap = plt.get_cmap("cividis").copy()
    cmap.set_bad("#e5e8e6")
    ax.imshow(values, vmin=0, vmax=100, cmap=cmap, aspect="auto")
    for i, method in enumerate(methods):
        for j, qid in enumerate(ids):
            value = values[i, j]
            label = (
                "—"
                if np.isnan(value)
                else (
                    ("correct" if value else "miss")
                    if qid.startswith("mhr_")
                    else f"{value:.0f}"
                )
            )
            ax.text(
                j,
                i,
                label,
                ha="center",
                va="center",
                color="white" if value < 55 else "#192a2a",
                fontsize=9,
            )
    ax.set_xticks(
        range(len(ids)), [x.replace("sweqa_", "").replace("mhr_", "news ") for x in ids]
    )
    ax.set_yticks(range(len(methods)), methods)
    ax.set_title("Fixed examples in registered order")
    fig.savefig(directory / "examples.png", dpi=155)
    plt.close(fig)
    sections = [
        "# Fixed output examples",
        "Cases are selected in the split manifest's stored order. A dash in the figure denotes an unobserved condition. News cells show strict exact match and code cells show the score out of 100.",
        "![Question outcomes across conditions](../figures/examples.png)",
    ]
    for qid in ids:
        subset = [r for r in rows if r["id"] == qid]
        if subset:
            sections.extend(["## " + qid, subset[0]["question"]])
            if subset[0].get("reference"):
                sections.extend(["**Benchmark reference**", subset[0]["reference"]])
        for r in sorted(subset, key=lambda x: x["arm"]):
            sections.extend(
                [
                    "### " + r["arm"],
                    f"Recorded score {r.get('score', 'pending')} / {1 if r['domain'] == 'news' else 100}.",
                    r["answer"] or r.get("error", "No answer"),
                    r.get("explanation", ""),
                ]
            )
            for c in r.get("citations", []):
                sections.append(
                    f"> {c.get('quote', '').strip()}\n\n{c.get('path', '')} · "
                    + ("verified" if c.get("valid") else "unverified")
                )
    return "\n\n".join(sections) + "\n"
