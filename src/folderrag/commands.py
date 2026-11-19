"""Console entry points keep the interactive path and benchmark agent implementation identical."""

import argparse
import json
import os
import re
import subprocess
import uuid
from pathlib import Path, PureWindowsPath

from .paths import ROOT, now, read


def source_links(source, index, citations):
    """Return an original document link and the exact normalized text location for each quote."""

    def host_path(path):
        if os.environ.get("FOLDERRAG_LINKS_WINDOWS"):
            return PureWindowsPath(
                subprocess.check_output(["wslpath", "-w", str(path)], text=True).strip()
            )
        return path

    original, canonical = host_path(source), host_path(index.root)
    for citation in citations:
        if not citation["valid"]:
            continue
        path = citation["path"]
        line = citation["line"]
        citation["text_uri"] = (canonical / path).as_uri() + f"#L{line}"
        target = (original / path).as_uri()
        suffix = Path(path).suffix.lower()
        if suffix in {".pdf", ".docx", ".pptx", ".xlsx"}:
            prefix = (index.root / path).read_text(encoding="utf8")[
                : citation["offset"] + len(citation["quote"])
            ]
            labels = re.findall(
                r"(?m)^\[((?:Page |Paragraph |Table |Slide |[^\n\]]+ row )[^\n\]]+)\]",
                prefix,
            )
            if labels:
                citation["location"] = labels[-1]
                if suffix == ".pdf" and labels[-1].startswith("Page "):
                    target += "#page=" + labels[-1].split()[-1]
        else:
            target += f"#L{line}"
        citation["source_uri"] = target


def run():
    p = argparse.ArgumentParser(
        prog="folderrag",
        description="Search a folder with an evidence-checked Luna swarm.",
    )
    sub = p.add_subparsers(dest="op", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--folder", required=True, type=Path)
    ask.add_argument("--agents", type=int, choices=[1, 2, 4, 8])
    ask.add_argument("--json", action="store_true")
    ask.add_argument("--lexical-only", action="store_true")
    ask.add_argument(
        "--method", choices=["custom", "stock", "arctic", "oneshot"], default="custom"
    )
    for op in (
        "prepare",
        "freeze",
        "report",
        "historical",
        "diagnostics-audit",
        "counterfactual",
        "status",
    ):
        sub.add_parser(op)
    bench = sub.add_parser("run")
    bench.add_argument("phase", choices=["dev", "test", "diagnostics"])
    bench.add_argument("--workers", type=int, default=2)
    bench.add_argument("--limit", type=int)
    serve = sub.add_parser("dashboard")
    serve.add_argument("--port", type=int, default=8765)
    a = p.parse_args()
    if a.op == "prepare":
        from .benchdata import prepare

        prepare()
    elif a.op == "ask":
        from .agents import answer
        from .corpus import FolderIndex, snapshot
        from .evaluate import new_case

        source = a.folder.resolve()
        idx = FolderIndex(snapshot(source), dense=not a.lexical_only)
        selected = ROOT / "protocol/freeze.json"
        size = a.agents or (read(selected)["size"] if selected.exists() else 4)
        unit = "ask-" + uuid.uuid4().hex
        result = answer(
            new_case(idx, "dev", unit),
            a.question,
            a.method,
            size,
            mode="lexical" if a.lexical_only else "hybrid",
        )
        source_links(source, idx, result["citations"])
        if a.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["answer"], result["explanation"], sep="\n\n")
            for c in result["citations"]:
                if c["valid"]:
                    print(
                        f"- [{c['path']}, {c.get('location', 'line ' + str(c['line']))}]({c['source_uri']}) — {c['quote']}"
                    )
    elif a.op == "run":
        from .evaluate import run_stage

        run_stage(a.phase, a.workers, a.limit)
    elif a.op == "freeze":
        from .evaluate import freeze

        print(json.dumps(freeze(), indent=2))
    elif a.op == "historical":
        from .diagnostics import historical

        historical()
    elif a.op == "counterfactual":
        from .diagnostics import counterfactual

        counterfactual()
    elif a.op == "diagnostics-audit":
        from .diagnostics import support_audit

        support_audit()
    elif a.op == "report":
        from .report import build

        build()
    elif a.op == "dashboard":
        from .report import serve_dashboard

        serve_dashboard(a.port)
    else:
        from .evaluate import ledger, records
        from collections import Counter

        print(
            json.dumps(
                {
                    "utc": now(),
                    "completed": dict(Counter(r["phase"] for r in records())),
                    "cost_or_reserved_upper_usd": ledger().totals(),
                },
                indent=2,
            )
        )
