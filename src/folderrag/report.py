"""One command regenerates the private explorer, all numerical tables, figures and PDF."""

import datetime as dt
import html
import http.server
import json
from zoneinfo import ZoneInfo

from .analysis import comparisons, means
from . import outcomes
from .evaluate import ledger, records
from .paths import DATA, ROOT, now, read, save

REPORTS = ROOT / "reports"
OUT = ROOT / "results"
SITE = ROOT / "site"


def dashboard_data():
    rows = records()
    archived = read(OUT / "metrics.json") if (OUT / "metrics.json").is_file() else {}
    if not rows and (OUT / "cases.json").is_file():
        rows = read(OUT / "cases.json")
    frozen = ROOT / "protocol/freeze.json"
    final = read(frozen) if frozen.exists() else {}
    return {
        "updated": now(),
        "budget": ledger().totals() or archived.get("budget", {}),
        "groups": means(rows),
        "rows": rows,
        "pilot": records("dev", pilots=True) or archived.get("pilot", []),
        "freeze": final,
        "comparisons": comparisons(rows, f"swarm{final['size']}", final["blocks"])
        if final
        else [],
        **{
            name: [read(p) for p in sorted((DATA / name).glob("*.json"))]
            or archived.get(name, [])
            for name in ("historical", "twins", "support", "index-timings")
        },
    }


def serve_dashboard(port):
    class Dashboard(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(SITE), **kwargs)

        def do_GET(self):
            if self.path.split("?")[0] == "/data.json":
                payload = json.dumps(dashboard_data(), ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                super().do_GET()

    print(f"Dashboard at http://127.0.0.1:{port}", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Dashboard).serve_forever()


def table(groups):
    head = "| Phase | Domain | Method | Graded / attempts | Quality [95% CI] | USD/question¹ | Median / p95 s | Errors |\n|---|---|---|---:|---:|---:|---:|---:|"
    lines = [head]
    for r in groups:
        fmt = (
            (lambda x: f"{x:.1%}") if r["domain"] == "news" else (lambda x: f"{x:.1f}")
        )
        lines.append(
            f"| {r['phase']} | {r['domain']} | {r['arm']} | {r['graded']} / {r['n']} | "
            f"{fmt(r['mean'])} [{fmt(r['low'])}, {fmt(r['high'])}] | {r['cost']:.4f} | "
            f"{r['p50']:.1f} / {r['p95']:.1f} | {r['failures']} |"
        )
    if not groups:
        lines.append("| Pending | | | | | | | |")
    return (
        "\n".join(lines)
        + "\n\n¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.\n"
    )


def conclusions(data):
    if not data["rows"]:
        return "The protocol and implementation are available. Paired experiments are pending."
    if not data["comparisons"]:
        return "The registered comparison is in progress. The available scores are descriptive."
    messages = []
    for domain in ("news", "code"):
        group = [
            r
            for r in data["comparisons"]
            if r["domain"] == domain and r["comparator"] != "swarm1"
        ]
        outcome = (
            "met the registered superiority criterion"
            if len(group) == 3 and all(r["positive"] for r in group)
            else "did not establish superiority across all three baselines"
        )
        messages.append(f"On {domain}, the selected swarm {outcome}.")
    return " ".join(messages) + " " + outcomes.operating_choices(data)


def figures(data):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    dest = REPORTS / "figures"
    dest.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 2.9), layout="constrained")
    ax.set(xlim=(0, 10), ylim=(0, 3))
    ax.axis("off")
    labels = [
        (0.1, 1.05, "Folder snapshot\nline + offset anchors"),
        (2.65, 1.05, "BM25 + Qwen\nrank fusion"),
        (5.15, 1.05, "Independent Luna\ninvestigators"),
        (7.65, 1.05, "Luna coordinator\nquote verification"),
    ]
    for i, (x, y, label) in enumerate(labels):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                2.1,
                0.85,
                boxstyle="round,pad=0.06",
                facecolor="#ecf4f2",
                edgecolor="#246459",
            )
        )
        ax.text(x + 1.05, y + 0.425, label, ha="center", va="center", fontsize=11)
        if i + 1 < len(labels):
            ax.annotate(
                "",
                (labels[i + 1][0] - 0.05, y + 0.425),
                (x + 2.17, y + 0.425),
                arrowprops={"arrowstyle": "->", "color": "#20594f"},
            )
    ax.text(
        0.1,
        0.55,
        "One shared question budget. Each investigator has a separate Codex session.",
        size=10,
        color="#4a5550",
    )
    fig.savefig(dest / "architecture.png", dpi=150)
    plt.close(fig)
    if not data["groups"]:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), layout="constrained")
    stage = "test" if any(r["phase"] == "test" for r in data["groups"]) else "dev"
    for ax, domain in zip(axes, ("news", "code")):
        rows = [
            r for r in data["groups"] if r["phase"] == stage and r["domain"] == domain
        ]
        scale = 100 if domain == "news" else 1
        for i, r in enumerate(rows):
            ax.errorbar(
                r["mean"] * scale,
                i,
                xerr=[
                    [max(0, (r["mean"] - r["low"]) * scale)],
                    [max(0, (r["high"] - r["mean"]) * scale)],
                ],
                fmt="o",
                color="#167161",
                capsize=3,
            )
        ax.set_yticks(range(len(rows)), [r["arm"] for r in rows])
        ax.set_xlim(0, 100)
        ax.set_xlabel("Exact match (%)" if domain == "news" else "Rubric score / 100")
        ax.set_title(f"{domain.capitalize()} · {stage}")
        ax.grid(axis="x", alpha=0.22)
    fig.savefig(dest / "quality.png", dpi=155)
    plt.close(fig)


def write_pdf(data, summary, date):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Image,
        Table,
        TableStyle,
    )

    path = REPORTS / "paper.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=44,
        bottomMargin=46,
        title="Luna swarms for retrieval over files",
        author="Libor “Burny” Burian",
    )
    styles = getSampleStyleSheet()
    story = []

    def para(text, style="BodyText"):
        story.append(Paragraph(text, styles[style]))

    para("Luna swarms for retrieval over files", "Title")
    para("Libor “Burny” Burian · " + date)
    para("Abstract", "Heading2")
    para(html.escape(summary))
    para("Motivation and method", "Heading2")
    para(
        "A reader can find the right filename and still miss the decisive passage. We compare independent Codex investigators with a coordinator, an identical single investigator, ordinary Codex, Arctic B2 and one-shot hybrid retrieval. All agents use GPT-6 Luna. Documents and code are evaluated separately."
    )
    para(
        "A content-addressed snapshot supplies exact text ranges. Identifier-aware lexical retrieval and Qwen dense retrieval rank the same passages. Investigators explore in parallel. The coordinator receives verified excerpts and may read further before synthesizing its response."
    )
    story.append(
        Image(str(REPORTS / "figures/architecture.png"), width=410, height=132)
    )
    para("Evaluation and falsification", "Heading2")
    para(
        "The development size sweep selects a swarm before opening held-out scores. MultiHop-RAG uses strict normalized short-answer exact match. SWE-QA uses blinded pointwise rubric grading. The preregistration requires positive paired differences against all three external baselines after Holm correction for a domain win. File recall, quoted passage delivery and entailment have distinct interpretations."
    )
    para("Results", "Heading2")
    if data["groups"]:
        body = [["Phase", "Domain", "Method", "N", "Mean", "95% interval", "USD/q¹"]]
        for r in data["groups"]:
            scale = 100 if r["domain"] == "news" else 1
            body.append(
                [
                    r["phase"],
                    r["domain"],
                    r["arm"],
                    str(r["n"]),
                    f"{scale * r['mean']:.1f}",
                    f"{scale * r['low']:.1f} – {scale * r['high']:.1f}",
                    f"{r['cost']:.4f}",
                ]
            )
        t = Table(body, repeatRows=1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcebe7")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f1f5f4")],
                    ),
                ]
            )
        )
        story.append(t)
        para(
            "News is expressed in percent; code uses the rubric's 100-point scale. ¹ Conservative inference cost."
        )
        story.append(Image(str(REPORTS / "figures/quality.png"), width=470, height=216))
    else:
        para("The first registered release precedes measured outcomes.")
    para("Discussion and limitations", "Heading2")
    para(
        "Benchmark questions predate the generator. Closed-book and counterfactual diagnostics test dependence on file contents. The generator and code judge share a model family. Interval estimates describe the sampled tasks. A valid quote verifies provenance; the independent support audit tests its relationship to the claim."
    )
    para("Related work and reproducibility", "Heading2")
    for title, url in (
        ("MultiHop-RAG", "https://arxiv.org/abs/2401.15391"),
        ("SWE-QA", "https://aclanthology.org/2026.findings-acl.402/"),
        ("RISE", "https://arxiv.org/abs/2606.06880"),
        ("ALCE", "https://aclanthology.org/2023.emnlp-main.398/"),
        (
            "Protocol, experiment reports and source",
            "https://github.com/BurnyCoder/agent-swarm-for-retrieval-augmented-generation",
        ),
    ):
        para(f'<link color="#156154" href="{url}">{title}</link>')
    from reportlab.platypus import KeepTogether

    story.append(
        KeepTogether(
            [
                Paragraph("AI statement", styles["Heading2"]),
                Paragraph(
                    "Codex wrote this codebase and paper. A human provided the exact specification that Codex executed. Human cleanup and rewriting are in progress.",
                    styles["BodyText"],
                ),
            ]
        )
    )

    def footer(canvas, document):
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            A4[0] - 45, 22, f"Luna folder research · {document.page}"
        )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def build():
    data = dashboard_data()
    date = dt.datetime.now(ZoneInfo("Europe/Berlin")).date().isoformat()
    summary = conclusions(data)
    figures(data)
    save(OUT / "metrics.json", {k: v for k, v in data.items() if k != "rows"})
    save(OUT / "cases.json", data["rows"])
    save(SITE / "data.json", data)
    md = table(data["groups"])
    (OUT / "tables.md").write_text(md, encoding="utf8")
    comps = data["comparisons"]
    comparison = "\n".join(
        f"- {r['domain']} against {r['comparator']}, n={r['n']}, difference {r['difference']:.4f}, "
        f"95% CI [{r['low']:.4f}, {r['high']:.4f}], Holm p={r['holm_p']:.4g}."
        for r in comps
    )
    freeze = data["freeze"]
    if freeze:
        choice = f"The frozen development choice is **{freeze['size']} agents**, including the coordinator. The cost rule admitted **{freeze['blocks']} balanced blocks**."
    else:
        choice = "Selection is pending completion of the registered development panel."
    pages = {
        "handoff-pilot": (
            "Investigator turn-limit pilot",
            "The initial size-eight development trace contained genuine concurrent searches and exhausted investigator budgets before handoff. The final allocated investigator turn now disables tools and requests a source report. The prior multi-agent cases remain below and are excluded from size selection. Single-agent and external-baseline runs used identical implementations throughout.",
            outcomes.grid(
                ["Case", "Size", "Returned / assigned", "Peak", "Score", "Seconds"],
                [
                    [
                        r["id"],
                        r["arm"],
                        f"{r.get('workers_completed', 0)}/{r.get('workers_requested', 0)}",
                        r.get("peak_investigators"),
                        r.get("score"),
                        r["seconds"],
                    ]
                    for r in data["pilot"]
                ],
            ),
        ),
        "historical": (
            "Historical bridge",
            "Saved Haiku answers receive the same strict news scorer and blinded Luna code grader used in the new study. The historical conditions are model and protocol specific.",
            outcomes.bridge(data),
        ),
        "swarm-sizes": (
            "Swarm size and participation",
            choice
            + " An investigator contributes when at least one of its source quotations passes validation. Peak concurrency counts overlapping investigator session lifetimes.",
            outcomes.swarms(data),
        ),
        "grounding": (
            "Source grounding",
            "¹ Mean per-question recall on questions with annotated files. Returned-file recall depends on path visibility in each tool interface. ² Citation support includes one failed opportunity for each answer without citations. Exact quote matching, assertion support, and annotated fact exposure have different denominators.",
            outcomes.grounding(data) + "\n\n" + outcomes.support(data),
        ),
        "counterfactuals": (
            "File interventions",
            "The two news schedules and two copies of the pinned Requests repository change one answer-determining value. Each twin uses a separate immutable snapshot and fresh swarm. These are narrow causal probes.",
            outcomes.twins(data),
        ),
        "variability": (
            "Independent repeat runs",
            "The selected method runs again on the first four registered cases per domain. Code score changes include variability in both generation and grading.",
            outcomes.repeats(data),
        ),
        "indexing": (
            "Index setup and loading",
            "Setup time includes opening an immutable corpus, constructing or loading a search index and initializing the local encoder when required. Concurrent loaders can wait on a shared build. These times are excluded from per-question latency.",
            outcomes.grid(
                ["Corpus or snapshot", "Mode", "Spans", "Seconds", "UTC"],
                [
                    [
                        r.get("folder", r.get("snapshot", "")[:12]),
                        r["mode"],
                        r.get("spans", "—"),
                        r["seconds"],
                        r["utc"],
                    ]
                    for r in data["index-timings"]
                ],
            ),
        ),
    }
    dest = REPORTS / "experiments"
    dest.mkdir(exist_ok=True)
    for slug, (title, desc, body) in pages.items():
        (dest / (slug + ".md")).write_text(
            "# " + title + "\n\n" + desc + "\n\n" + body + "\n", encoding="utf8"
        )
    linked = "\n".join(
        f"- [{title}](experiments/{slug}.md)" for slug, (title, _, _) in pages.items()
    )
    (REPORTS / "summary.md").write_text(
        "# Experiment summary\n\n"
        + summary
        + "\n\n"
        + choice
        + "\n\n"
        + md
        + "\n"
        + comparison
        + "\n\n"
        + linked
        + "\n",
        encoding="utf8",
    )
    for phase in ("dev", "test", "diagnostics"):
        subset = [r for r in data["groups"] if r["phase"] == phase]
        (dest / (phase + ".md")).write_text(
            "# "
            + phase.capitalize()
            + " experiments\n\n"
            + md_for(phase)
            + "\n\n"
            + table(subset)
            + "\n"
            + (comparison if phase == "test" else ""),
            encoding="utf8",
        )
    write_pdf(data, summary, date)
    doc = ROOT / "README.md"
    prefix = doc.read_text(encoding="utf8").split("<!-- generated -->")[0].rstrip()
    doc.write_text(
        prefix
        + "\n\n<!-- generated -->\n## Measured results\n\n"
        + summary
        + "\n\n"
        + md
        + "\n[Paper](reports/paper.pdf) · [All experiment reports](reports/summary.md)\n",
        encoding="utf8",
    )
    print("Generated", REPORTS / "paper.pdf", flush=True)


def md_for(phase):
    return {
        "dev": "The same legacy questions are used for each swarm size and baseline. These results select a size and estimate cost.",
        "test": "The frozen size and three external baselines share the same confirmatory questions. The one-agent counterpart isolates the effect of delegation.",
        "diagnostics": "The fixed first block tests the other sizes, controls, retrieval and verification ablations. Repeats quantify within-model variability.",
    }[phase]
