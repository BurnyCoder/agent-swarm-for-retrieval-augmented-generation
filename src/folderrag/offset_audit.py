"""Check both passage address formats against the same immutable news folder."""

import collections
import json
import sqlite3
from pathlib import Path
from .paths import DATA, read, save


def news_offsets():
    marker = DATA / "benchmark/snapshots/news.json"
    if not marker.exists():
        return {}
    root = Path(read(marker)["path"])
    audit = DATA / "offset-audits" / (root.name + ".json")
    if audit.exists():
        return read(audit)
    indexes = list((DATA / "arctic-index" / root.name).glob("*/chunks.jsonl"))
    db = DATA / "indexes" / (root.name + "-v3") / "lexical.sqlite"
    if not db.exists() or not indexes:
        return {}
    from arcticswarm.tools.folder_corpus import Chunk

    ids = collections.defaultdict(set)
    old_count = 0
    with indexes[0].open(encoding="utf8") as file:
        for line in file:
            c = Chunk(**json.loads(line))
            ids[c.docid].add(c.text)
            old_count += 1
    ambiguous = [key for key, texts in ids.items() if len(texts) > 1]
    checked = bad = 0
    keys = set()
    path = None
    with sqlite3.connect(db) as con:
        for key, name, start, end, body in con.execute(
            "select id,path,start,end,text from spans order by path,start"
        ):
            if name != path:
                source = (root / name).read_text(encoding="utf8")
                path = name
            checked += 1
            bad += source[start:end] != body or key != f"{name}@{start}:{end}"
            keys.add(key)
        files = con.execute("select count(distinct path) from spans").fetchone()[0]
    row = dict(
        snapshot=root.name,
        files=files,
        original_spans=old_count,
        original_ambiguous_ids=len(ambiguous),
        original_ambiguous_files=len({x.rsplit("#L", 1)[0] for x in ambiguous}),
        examples=ambiguous[:3],
        offset_spans=checked,
        duplicate_offset_ids=checked - len(keys),
        incorrect_slices=bad,
    )
    save(audit, row)
    return row
