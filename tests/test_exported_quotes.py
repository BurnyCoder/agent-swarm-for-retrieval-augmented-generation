"""A rendered citation must reproduce the exact bytes already accepted by the verifier."""

import gzip
import json

from folderrag.provenance import displayed_citations, quote_audit


def test_whitespace_offsets_and_delivered_text(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "tag.py").write_text("    TagMarkup,\n", encoding="utf8")
    markers = tmp_path / "benchmark/snapshots"
    markers.mkdir(parents=True)
    (markers / "flask.json").write_text(json.dumps({"path": str(source)}))
    archive = tmp_path / "evidence"
    archive.mkdir()
    with gzip.open(archive / "unit.json.gz", "wt", encoding="utf8") as out:
        json.dump(["    TagMarkup,\n"], out)
    citation = dict(valid=True, path="tag.py", line=1, offset=4, quote="    TagMarkup,")
    other = {**citation, "quote": "invented"}
    row = dict(id="q", unit="unit", phase="dev", citations=[citation, other])
    assert displayed_citations([citation])[0]["quote"] == "TagMarkup,"
    assert citation["quote"].startswith("    ")
    counts = quote_audit([row], {"q": {"folder": "flask"}}, tmp_path)["dev"]
    assert counts["verified"] == 2 and counts["trimmed"] == 1
    assert counts["exact_source"] == counts["delivered"] == counts["both"] == 1
