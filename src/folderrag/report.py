"""One command regenerates the private explorer, all numerical tables, figures and PDF."""

import datetime as dt
import html
import http.server
import json
from zoneinfo import ZoneInfo

from .analysis import comparisons, means
from . import outcomes
from .examples import matched_size_groups, render_examples, plot_swarm_sizes
from .evaluate import BASE, SIZES, ledger, records
from .benchdata import BENCH
from .paths import DATA, ROOT, now, read, save
from .provenance import displayed_citations, quote_audit

REPORTS = ROOT / "reports"
OUT = ROOT / "results"
SITE = ROOT / "site"


def dashboard_data():
    rows = records()
    archived = read(OUT / "metrics.json") if (OUT / "metrics.json").is_file() else {}
    if not rows and (OUT / "cases.json").is_file():
        rows = read(OUT / "cases.json")
    if (BENCH / "cases.json").is_file() and rows:
        references = read(BENCH / "cases.json")
        rows = [{**r, "reference": references[r["id"]]["answer"]} for r in rows]
    rows = [
        {**r, "citations": displayed_citations(r.get("citations", []))} for r in rows
    ]
    frozen = ROOT / "protocol/freeze.json"
    final = read(frozen) if frozen.exists() else {}
    split = read(ROOT / "protocol/splits.json")
    targets = {
        "dev": len(split["legacy"]) * (len(SIZES) + len(BASE)),
        "audit": len(split["blocks"][0]) * (len(BASE) + 2),
    }
    if final:
        targets["test"] = sum(len(b) for b in split["blocks"][: final["blocks"]]) * (
            len(BASE) + 2
        )
    return {
        "updated": now(),
        "budget": ledger().totals() or archived.get("budget", {}),
        "balances": ledger().balances() or archived.get("balances", {}),
        "offset_audit": archived.get("offset_audit", {}),
        "quote_audit": archived.get("quote_audit", {}),
        "encoder_runtime": read(DATA / "runtime/encoder.json")
        if (DATA / "runtime/encoder.json").exists()
        else archived.get("encoder_runtime", {}),
        "groups": means(rows),
        "size_groups": matched_size_groups(rows, set(split["blocks"][0])),
        "rows": rows,
        "pilot": records("dev", pilots=True) or archived.get("pilot", []),
        "freeze": final,
        "targets": targets,
        "comparisons": comparisons(
            rows,
            f"swarm{final['size']}",
            final["blocks"],
            (DATA / "phase-stops/test.json").exists(),
        )
        if final
        else [],
        **{
            name: [read(p) for p in sorted((DATA / name).glob("*.json"))]
            or archived.get(name, [])
            for name in (
                "historical",
                "twins",
                "support",
                "index-timings",
                "smoke",
                "stages",
            )
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
    styles["Heading2"].keepWithNext = True
    story = []

    def para(text, style="BodyText"):
        story.append(Paragraph(text, styles[style]))

    def small_table(body):
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
    para(
        "The contribution is a matched test of delegation with independently observable worker handoffs. The decoder and embedding weights are frozen. The same Luna model, reasoning setting, corpus and total resource ceilings apply to every confirmatory arm."
    )
    story.append(
        Image(str(REPORTS / "figures/architecture.png"), width=410, height=132)
    )
    para("Evaluation and falsification", "Heading2")
    para(
        "The development size sweep selects a swarm before opening held-out scores. MultiHop-RAG uses strict normalized short-answer exact match. SWE-QA uses blinded pointwise rubric grading. The preregistration requires positive paired differences against all three external baselines after Holm correction for a domain win. File recall, quoted passage delivery and entailment have distinct interpretations."
    )
    if data["freeze"]:
        f = data["freeze"]
        para(
            f"The development rule selected {f['size']} total agents and admitted {f['blocks']} balanced blocks. A block contains 32 news questions and one question from each of 15 pinned repositories. Eleven repositories were reserved outside development."
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
        small_table(body)
        para(
            "News is expressed in percent with Wilson intervals. Code uses the rubric's 100-point scale with question-level bootstrap intervals. The cost column gives the mean conservative inference charge in US dollars. Grading is included separately in the study ledger."
        )
        story.append(Image(str(REPORTS / "figures/quality.png"), width=470, height=216))
        if (REPORTS / "figures/swarm-size.png").exists():
            story.append(
                Image(str(REPORTS / "figures/swarm-size.png"), width=460, height=189)
            )
            para(
                "Within each panel, every displayed size answered the same questions. The unit on the horizontal axis includes the coordinator."
            )
    else:
        para("The first registered release precedes measured outcomes.")
    if data["comparisons"]:
        para("Paired effects", "Heading2")
        body = [
            [
                "Corpus",
                "Comparator",
                "Pairs",
                "Difference",
                "95% paired interval",
                "Holm p",
            ]
        ]
        for r in data["comparisons"]:
            scale = 100 if r["domain"] == "news" else 1
            body.append(
                [
                    r["domain"],
                    r["comparator"],
                    r["n"],
                    f"{r['difference'] * scale:+.2f}",
                    f"{r['low'] * scale:+.2f} to {r['high'] * scale:+.2f}",
                    f"{r['holm_p']:.4g}",
                ]
            )
        small_table(body)
        para(
            "Differences are percentage points for news and rubric points for code. Intervals resample matched questions within news type or repository. Code inference uses a sign-flip test. News inference uses the exact discordant-pair test. The three external comparators across two domains form the primary Holm family. The single-investigator comparison forms a separate family across domains."
        )
    if data["historical"]:
        from statistics import mean

        para("Historical bridge", "Heading2")
        body = [
            [
                "Original model",
                "Legacy condition",
                "Corpus",
                "Cases",
                "Common-scorer mean",
            ]
        ]
        for (domain, arm), group in outcomes.group_by(
            data["historical"], ["domain", "arm"]
        ):
            score = mean(r["score"] for r in group)
            body.append(
                [
                    "Haiku",
                    {"M": "Swarm M", "B2": "Single B2"}.get(arm, arm),
                    domain,
                    len(group),
                    f"{score:.1%}" if domain == "news" else f"{score:.1f}",
                ]
            )
        small_table(body)
        para(
            "The bridge reuses the archived responses. Stricter extraction of the final news label and a different code judge can change the reported scores without any change in the generated answers."
        )
    para("Discussion and limitations", "Heading2")
    para(
        "Benchmark questions predate the generator and could have entered its training data. Closed-book and counterfactual diagnostics probe dependence on file contents. The generator and code judge share a model family. Interval estimates describe the sampled tasks. Quote matching verifies textual provenance. A separate blinded support audit tests whether each passage substantiates the attached claim and whether the full answer includes uncited assertions."
    )
    if data["twins"] or data["support"]:
        para("Evidence and interventions", "Heading2")
        if data["twins"]:
            para(
                "Paired folder edits produced the following observed answers. Each changed code checkout preserves other files from the pinned Requests repository."
            )
            small_table(
                [["Corpus", "Expected", "Observed", "Exact match"]]
                + [
                    [r["domain"], r["expected"], r["answer"][:60], r["score"]]
                    for r in data["twins"]
                ]
            )
        if data["support"]:
            body = [
                [
                    "Corpus",
                    "Method",
                    "Audited",
                    "Claims supported / total",
                    "Gold facts shown / total",
                ]
            ]
            for (domain, arm), grp in outcomes.group_by(
                data["support"], ["domain", "arm"]
            ):
                agg = lambda k: sum(r.get(k, 0) for r in grp)
                body.append(
                    [
                        domain,
                        arm,
                        len(grp),
                        f"{agg('claims_supported')}/{agg('n_claims')}",
                        f"{agg('gold_facts_supported')}/{agg('gold_facts')}",
                    ]
                )
            small_table(body)
    para("Conclusions", "Heading2")
    para(html.escape(summary))
    para("Appendix · reproducible settings", "Heading2")
    if data.get("encoder_runtime"):
        h = data["encoder_runtime"]
        para(
            f"The local encoder ran on {html.escape(h['accelerator'])} with PyTorch {html.escape(h['torch'])} and device {html.escape(h['device'])}. The dollar estimates cover API generation and grading. Index setup is measured in seconds."
        )
    para(
        "Each question has 300 seconds, at most 32 model requests and 48,000 aggregate output tokens. An individual request allows up to 4,096 output tokens at medium reasoning effort. Larger swarms divide 16 requests among their investigators and reserve the rest for the coordinator. The investigator's final allocated turn requests a structured handoff. The coordinator has one citation-repair opportunity within its allowance."
    )
    para(
        "Passages contain up to 1,400 Unicode characters, with 160 characters of overlap. Exact offsets distinguish pieces of a single long line. Identifier splitting feeds SQLite FTS5 BM25. Qwen3-Embedding-0.6B uses left padding, last-token pooling and normalized cosine scores. Equal-weight reciprocal rank fusion uses a constant of 60. Original, random and annotated-evidence passages share the answer schema."
    )
    if data["groups"] and (REPORTS / "figures/examples.png").exists():
        from reportlab.platypus import KeepTogether

        picture = Image(str(REPORTS / "figures/examples.png"))
        picture.drawHeight = min(250, 470 * picture.imageHeight / picture.imageWidth)
        picture.drawWidth = (
            picture.drawHeight * picture.imageWidth / picture.imageHeight
        )
        story.append(
            KeepTogether(
                [
                    Paragraph("Fixed output examples", styles["Heading2"]),
                    picture,
                    Paragraph(
                        "The manifest order fixes the first examples in each domain. The private explorer preserves each complete answer and its citations. A dash marks unavailable measurements.",
                        styles["BodyText"],
                    ),
                ]
            )
        )
    para("Related work and reproducibility", "Heading2")
    for title, url in (
        ("MultiHop-RAG", "https://arxiv.org/abs/2401.15391"),
        ("SWE-QA", "https://aclanthology.org/2026.findings-acl.402/"),
        ("RISE", "https://arxiv.org/abs/2606.06880"),
        ("ALCE", "https://aclanthology.org/2023.emnlp-main.398/"),
        (
            "Qwen3-Embedding-0.6B model and pooling recipe",
            "https://huggingface.co/Qwen/Qwen3-Embedding-0.6B",
        ),
        (
            "Reciprocal rank fusion, Cormack et al.",
            "https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf",
        ),
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
    from .offset_audit import news_offsets

    data["offset_audit"] = news_offsets() or data.get("offset_audit", {})
    if (BENCH / "cases.json").is_file() and records():
        data["quote_audit"] = quote_audit(records(), read(BENCH / "cases.json"), DATA)
    date = dt.datetime.now(ZoneInfo("Europe/Berlin")).date().isoformat()
    summary = conclusions(data)
    figures(data)
    examples = render_examples(data, REPORTS / "figures")
    sized = plot_swarm_sizes(data, REPORTS / "figures")
    save(OUT / "metrics.json", {k: v for k, v in data.items() if k != "rows"})
    save(OUT / "cases.json", data["rows"])
    save(SITE / "data.json", data)
    md = table(data["groups"])
    card = (ROOT / "protocol/hub-card.md").read_text(encoding="utf8")
    (OUT / "hub-card.md").write_text(
        card + "\n\n## Current measurements\n\n" + summary + "\n\n" + md,
        encoding="utf8",
    )
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
        "strata": (
            "Generalization by repository and news type",
            "Rows retain the frozen strata. Repository membership records whether an earlier code question from that repository was used during development. These small-cell estimates are descriptive.",
            outcomes.strata(data),
        ),
        "coverage": (
            "Execution coverage",
            "Pending cases have no quality score. Completed generation failures receive the registered zero. Missing grader results are excluded from paired inference and block a complete-domain superiority claim.",
            outcomes.coverage(data),
        ),
        "cli-smoke": (
            "Normal Windows CLI checks",
            "Both checks use the same two-file fixture. The positive question requires combining a route choice with a stop count. The missing-date question tests abstention. These checks establish end-to-end behavior on one fixture.",
            outcomes.grid(
                [
                    "Question",
                    "Expected",
                    "Observed",
                    "Agents",
                    "Investigators completed",
                    "Verified quotes",
                    "Seconds",
                    "USD upper",
                ],
                [
                    [
                        r["question"],
                        r["expected"],
                        r["answer"],
                        r["agents"],
                        r["investigators_completed"],
                        len(r["citations"]),
                        r["seconds"],
                        r["cost_upper_usd"],
                    ]
                    for r in data["smoke"]
                ],
            ),
        ),
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
            outcomes.grounding(data)
            + "\n\n"
            + outcomes.support(data)
            + "\n\n### Independent replay of every accepted quote\n\n"
            + "For each citation, the replay checks its line and character offset in the immutable file and searches the saved model-visible passages for the exact published text. Exterior whitespace is removed as in the original verifier. Raw answers remain in the private transcript archive.\n\n"
            + outcomes.grid(
                [
                    "Phase",
                    "Answers",
                    "Accepted citations",
                    "Exterior whitespace removed",
                    "Exact file location",
                    "Text delivered",
                    "Both verified",
                    "Missing exposure archives",
                ],
                [
                    [
                        phase,
                        *(
                            counts.get(k, 0)
                            for k in (
                                "answers",
                                "verified",
                                "trimmed",
                                "exact_source",
                                "delivered",
                                "both",
                                "missing_archives",
                            )
                        ),
                    ]
                    for phase, counts in sorted(data["quote_audit"].items())
                ],
            ),
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
    audit = data["offset_audit"]
    if audit:
        pages["offsets"] = (
            "News citation address audit",
            "Both chunkers processed the same immutable canonical news texts. An ambiguous original identifier points to multiple distinct passages. Every offset-indexed slice is compared with its source bytes after UTF-8 decoding.",
            outcomes.grid(
                [
                    "Files",
                    "Original spans",
                    "Ambiguous line IDs",
                    "Affected files",
                    "Offset spans",
                    "Duplicate offset IDs",
                    "Incorrect slices",
                ],
                [
                    [
                        audit[k]
                        for k in (
                            "files",
                            "original_spans",
                            "original_ambiguous_ids",
                            "original_ambiguous_files",
                            "offset_spans",
                            "duplicate_offset_ids",
                            "incorrect_slices",
                        )
                    ]
                ],
            ),
        )
    dest = REPORTS / "experiments"
    dest.mkdir(exist_ok=True)
    if examples:
        (dest / "output-examples.md").write_text(examples, encoding="utf8")
    for slug, (title, desc, body) in pages.items():
        if slug == "swarm-sizes":
            body += "\n\n### First held-out block\n\n" + outcomes.fixed_panel(
                data, set(read(ROOT / "protocol/splits.json")["blocks"][0]), sizes=True
            )
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
            + (
                comparison
                if phase == "test"
                else "\n\n### Matched first-block differences\n\nDescriptive paired bootstrap intervals are in percentage points for news and rubric points for code.\n\n"
                + outcomes.fixed_panel(
                    data, set(read(ROOT / "protocol/splits.json")["blocks"][0])
                )
                if phase == "diagnostics"
                else ""
            ),
            encoding="utf8",
        )
    write_pdf(data, summary, date)
    doc = ROOT / "README.md"
    prefix = doc.read_text(encoding="utf8").split("<!-- generated -->")[0].rstrip()
    import re

    prefix = re.sub(
        r"\n*<!-- result-headline -->.*?<!-- /result-headline -->",
        "",
        prefix,
        flags=re.S,
    )
    if data["groups"]:
        opening, description, remainder = prefix.split("\n\n", 2)
        headline = summary
        if not data["comparisons"]:
            devnews = sorted(
                (
                    r
                    for r in data["groups"]
                    if r["phase"] == "dev"
                    and r["domain"] == "news"
                    and r["arm"].startswith("swarm")
                ),
                key=lambda r: int(r["arm"][5:]),
            )
            n_news = sum(
                i.startswith("mhr_")
                for i in read(ROOT / "protocol/splits.json")["legacy"].values()
            )
            if len(devnews) == 4 and all(r["n"] == n_news for r in devnews):
                headline = (
                    f"On the same {n_news} development news questions, exact-match accuracy was "
                    + ", ".join(
                        f"{r['mean']:.0%} with {r['arm'][5:]} agent{'s' if r['arm'] != 'swarm1' else ''}"
                        for r in devnews
                    )
                    + ". "
                    + summary
                )
        prefix = (
            opening
            + "\n\n"
            + description
            + "\n\n<!-- result-headline -->\n"
            + headline
            + " [Measured tables](results/tables.md)\n<!-- /result-headline -->\n\n"
            + remainder
        )

    def milestone(label, done):
        nonlocal prefix
        for old in ("[ ]", "[x]"):
            prefix = prefix.replace(
                "- " + old + " " + label,
                "- " + ("[x]" if done else "[ ]") + " " + label,
            )

    milestone("Complete the development sweep", bool(data["freeze"]))
    complete = {s["phase"] for s in data["stages"] if s["state"] == "finished"}
    milestone(
        "Complete the paired confirmation",
        {"test", "diagnostics"}.issubset(complete)
        and len(data["twins"]) == 4
        and len(data["support"]) == data["targets"]["audit"],
    )
    doc.write_text(
        prefix
        + "\n\n<!-- generated -->\n## Measured results\n\n"
        + summary
        + "\n\n"
        + md
        + (
            "\n![Answer quality by total Luna agent count](reports/figures/swarm-size.png)\n"
            if sized
            else ""
        )
        + (
            "\n![Scores for fixed example questions](reports/figures/examples.png)\n\n[Read the actual answers and source quotations](reports/experiments/output-examples.md)\n"
            if examples
            else ""
        )
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
