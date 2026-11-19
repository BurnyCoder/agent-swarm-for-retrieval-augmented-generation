"""Regression tests for failure modes identified in the prior experiment and new protocol."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from folderrag.corpus import snapshot, FolderIndex
from folderrag.evidence import Evidence, validate, exact_match
from folderrag.ledger import Ledger, Limit
from folderrag.agents import assignments
from folderrag.evidence import parse_answer


def test_snapshot_keeps_offsets_and_rebuilds_after_changes(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    path = source / "notes.md"
    path.write_text(
        "# Protocol\n" + "long text " * 800 + "special_answer", encoding="utf8"
    )
    (source / ".env").write_text("private", encoding="utf8")
    (source / "escape").symlink_to(tmp_path)
    folder = snapshot(source, tmp_path / "cache")
    index = FolderIndex(folder, dense=False)
    chunks = index.search("special_answer", 3)
    assert chunks and len({s["id"] for s in index.spans}) == len(index.spans)
    assert not (folder / ".env").exists() and not (folder / "escape").exists()
    for row in index.spans:
        assert path.read_text()[row["start"] : row["end"]] == row["text"]
    path.write_text("replacement", encoding="utf8")
    assert snapshot(source, tmp_path / "cache") != folder
    assert "special_answer" in (folder / "notes.md").read_text()


def test_quoted_evidence_must_have_been_delivered():
    evidence = Evidence()
    item = dict(id="p@0:12", path="p", start=0, end=12, text="a blue house", line=1)
    evidence.deliver([item])
    cite = {
        "path": "p",
        "quote": "blue house",
        "claim": "The house is blue.",
        "span_id": "p@0:12",
    }
    assert validate([cite], evidence)[0]["valid"]
    assert not validate([{**cite, "quote": "green house"}], evidence)[0]["valid"]
    assert not validate([{**cite, "span_id": "p@50:62"}], evidence)[0]["valid"]
    assert not exact_match("Yes; no", "Yes") and exact_match("THE Eagle", "eagle")


def test_atomic_budget_and_ambiguous_billing(tmp_path):
    ledger = Ledger(tmp_path / "ledger.db", {"dev": 0.50})
    with pytest.raises(ValueError):
        ledger.reserve("dev", "case", "worker", -1, 10)

    def reserve(i):
        try:
            return ledger.reserve("dev", "case", str(i), 0.30, 100)
        except Limit:
            return None

    with ThreadPoolExecutor(2) as pool:
        ids = list(pool.map(reserve, range(2)))
    assert sum(i is not None for i in ids) == 1
    assert Ledger(tmp_path / "ledger.db", {"dev": 0.50}).totals()[
        "dev"
    ] == pytest.approx(0.30)
    ledger.settle(next(i for i in ids if i is not None), 0.02, 17, {})
    assert ledger.totals()["dev"] == pytest.approx(0.02)


def test_baseline_tool_boundary_precedes_billing(tmp_path):
    import time
    from folderrag.gateway import Gateway, Trace
    from folderrag.paths import MODEL

    ledger = Ledger(tmp_path / "ledger", {"dev": 1})
    gate = Gateway(
        ledger,
        "dev",
        "q",
        "stock",
        2,
        None,
        Evidence(),
        Trace(tmp_path / "trace", False),
        "dummy",
        time.monotonic() + 30,
    )
    with pytest.raises(Limit):
        gate.tool("search", {"query": "anything"})
    with pytest.raises(ValueError, match="Hosted tools"):
        gate.request(
            {"model": MODEL, "tools": [{"type": "unregistered_hosted_tool"}]}, None
        )
    assert not ledger.totals()


def test_tool_truncation_and_gold_passage_visibility():
    import json
    from folderrag.diagnostics import visible_fragments

    e = Evidence()
    s = dict(id="p@0:12", path="p", start=0, end=12, text="a blue house", line=1)
    e.offer([s])
    cite = dict(path="p", span_id=s["id"], quote="blue house")
    assert not validate([cite], e)[0]["valid"]
    e.see_shell("Output:\n" + json.dumps([{"text": json.dumps([s])}]))
    assert validate([cite], e)[0]["valid"]
    gold = "The first five pairs of copper wires went missing on Tuesday."
    assert visible_fragments(gold, ["pairs of copper wires went missing"]) == [
        "pairs of copper wires went missing"
    ]
    assert visible_fragments(gold, ["an unrelated file name"]) == []


def test_swarm_sizes_count_the_coordinator():
    for n in (1, 2, 4, 8):
        assert len(set(assignments(n))) == n - 1


def test_cli_run_resumes_persisted_answer_without_billing(tmp_path, monkeypatch):
    import random, sys
    from types import SimpleNamespace
    from folderrag import commands, evaluate
    from folderrag.paths import save, read

    q = dict(
        id="fixture",
        question="Which one?",
        domain="news",
        answer="Green",
        folder="fixture",
        stratum="fixture",
        facts=[],
    )
    monkeypatch.setattr(evaluate, "ROOT", tmp_path)
    monkeypatch.setattr(evaluate, "BENCH", tmp_path / "benchmark")
    monkeypatch.setattr(evaluate, "DATA", tmp_path / "data")
    save(tmp_path / "protocol/splits.json", {"legacy": {"fixture": "fixture"}})
    save(evaluate.BENCH / "cases.json", {"fixture": q})
    methods = list((*evaluate.SIZES, *evaluate.BASE))
    random.Random(20261119).shuffle(methods)
    method = methods[0]
    unit = (
        ("dev-handoff-" if method in evaluate.SIZES[1:] else "dev-")
        + "fixture-"
        + method
    )
    output = evaluate.DATA / "records/dev" / (unit + ".json")
    save(
        output.with_suffix(".answer"),
        dict(
            answer="Green",
            explanation="",
            citations=[],
            returned_files=[],
            seconds=1,
            cost_upper_usd=0,
        ),
    )
    monkeypatch.setattr(
        evaluate, "index_for", lambda *args: SimpleNamespace(root=tmp_path)
    )
    monkeypatch.setattr("folderrag.sandbox.warm_arctic", lambda *args: None)
    monkeypatch.setattr(evaluate, "new_case", lambda *args: None)
    monkeypatch.setattr(
        evaluate,
        "answer",
        lambda *a, **k: pytest.fail("Resumed answer was dispatched again"),
    )
    monkeypatch.setattr(
        sys, "argv", ["folderrag", "run", "dev", "--workers", "1", "--limit", "1"]
    )
    commands.run()
    first = read(output)
    commands.run()
    assert first == read(output) and first["score"] == 1


def test_arctic_native_numeric_answer_and_line_citation(tmp_path):
    evidence = Evidence()
    (tmp_path / "schedule").write_text("Header\nCopper has 41 stops.\n")
    evidence.see_shell("corpus://folder/schedule#L2-2 Copper has 41 stops.")
    citation = {
        "path": "schedule",
        "span_id": "corpus://folder/schedule#L2-2",
        "quote": "41 stops",
        "claim": "41",
    }
    assert validate([citation], evidence, tmp_path)[0]["line"] == 2
    assert not validate(
        [{**citation, "span_id": "corpus://folder/schedule#L1-1"}], evidence, tmp_path
    )[0]["valid"]
    assert parse_answer('{"answer":41,"citations":[]}')["answer"] == "41"
