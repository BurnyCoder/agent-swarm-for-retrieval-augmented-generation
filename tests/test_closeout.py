"""The owner-selected cutoff keeps the frozen prefix and preserves the original design."""

from folderrag.closeout import selected_rows
from folderrag.inventory import experiment_inventory


def test_closeout_uses_frozen_ids_and_postpones_followups():
    close = {"included_ids": ["mhr_a"], "question_limit": 1}
    rows = [
        {"phase": "test", "id": "mhr_b", "arm": "swarm4", "score": 1},
        {"phase": "test", "id": "mhr_a", "arm": "swarm4", "score": 0},
        {"phase": "dev", "id": "other", "arm": "stock", "score": 1},
    ]
    selected = selected_rows(rows, close)
    assert [r["id"] for r in selected] == ["mhr_a", "other"]
    data = {
        "rows": selected,
        "closeout": close,
        "freeze": {"size": 4, "blocks": 1},
        "targets": {"audit": 10, "oracle": 1},
        "pilot": [],
        "smoke": [],
        "historical": [],
        "offset_audit": {},
        "stages": [],
        "support": [],
        "twins": [],
    }
    data.update({"capacity-flags": [], "capacity-repeats": []})
    inventory = {
        r["name"]: r
        for r in experiment_inventory(
            data, {"legacy": {}, "blocks": [["mhr_a", "mhr_b"]]}
        )
    }
    assert inventory["Four-agent swarm"]["status"] == "Closed early"
    assert inventory["Four-agent swarm"]["planned"] == 2
    assert inventory["Blinded evidence audit"]["status"] == "Postponed"


def test_stopped_study_cannot_dispatch_a_followup(tmp_path, monkeypatch):
    import sys

    import pytest

    from folderrag import commands
    from folderrag.paths import save

    save(tmp_path / "operations/owner-stop.json", {"state": "closed_for_today"})
    monkeypatch.setattr(commands, "DATA", tmp_path)
    monkeypatch.setattr(sys, "argv", ["folderrag", "guarded", "diagnostics"])
    with pytest.raises(SystemExit) as stopped:
        commands.run()
    assert stopped.value.code == 2
