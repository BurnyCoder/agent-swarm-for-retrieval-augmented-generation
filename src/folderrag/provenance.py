"""Recheck published quotations against immutable text and archived model-visible passages."""

import gzip
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from .paths import read


def displayed_citations(citations):
    """The verifier computes offsets after discarding optional exterior whitespace."""
    return [
        {**c, "quote": c["quote"].strip()} if c.get("valid") else c for c in citations
    ]


def quote_audit(rows, cases, directory):
    """Independently count exact addresses and exact model exposure across completed arms."""

    @lru_cache(maxsize=32)
    def root(folder):
        marker = directory / "benchmark/snapshots" / (folder + ".json")
        return Path(read(marker)["path"]).resolve() if marker.is_file() else None

    @lru_cache(maxsize=64)
    def source(folder, path):
        base = root(folder)
        if base:
            file = (base / path).resolve()
            if file.is_relative_to(base) and file.is_file():
                return file.read_text(encoding="utf8")
        return None

    groups = defaultdict(Counter)
    for row in rows:
        counts = groups[row["phase"]]
        counts["answers"] += 1
        valid = [c for c in row.get("citations", []) if c.get("valid")]
        if not valid:
            continue
        file = directory / "evidence" / (row["unit"] + ".json.gz")
        visible = []
        if file.is_file():
            with gzip.open(file, "rt", encoding="utf8") as archived:
                visible = json.load(archived)
        counts["missing_archives"] += not file.is_file()
        for raw, citation in zip(valid, displayed_citations(valid)):
            quote, offset = citation["quote"], citation["offset"]
            document = source(cases[row["id"]]["folder"], citation["path"])
            exact = (
                bool(quote)
                and document is not None
                and isinstance(offset, int)
                and offset >= 0
                and document[offset : offset + len(quote)] == quote
                and 1 + document.count("\n", 0, offset) == citation["line"]
            )
            delivered = bool(quote) and any(quote in text for text in visible)
            counts["verified"] += 1
            counts["trimmed"] += raw["quote"] != quote
            counts["exact_source"] += exact
            counts["delivered"] += delivered
            counts["both"] += exact and delivered
    return {phase: dict(counts) for phase, counts in groups.items()}
