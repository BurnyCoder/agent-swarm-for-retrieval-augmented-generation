"""Keep diagnostic targets and technical repeats separate from first-attempt comparisons."""

from folderrag.inventory import experiment_inventory


def test_inventory_tracks_independent_stages_and_frozen_denominators():
    split = {"legacy": {"old": "old"}, "blocks": [["mhr_a", "sweqa_b", "mhr_c"]]}
    data = {
        "rows": [
            {"phase": "test", "arm": "swarm4", "score": 0},
            {"phase": "retry", "arm": "swarm4", "score": 1},
            {"phase": "diagnostics", "arm": "closed", "score": 0},
        ],
        "freeze": {"size": 4, "blocks": 1},
        "targets": {"oracle": 1, "audit": 15},
        "historical": [],
        "pilot": [],
        "smoke": [],
        "offset_audit": {},
        "support": [],
        "twins": [],
        "stages": [],
        "capacity-flags": [{"unit": "test-item"}],
        "capacity-repeats": [],
    }
    items = {r["name"]: r for r in experiment_inventory(data, split)}
    assert (
        items["Four-agent swarm"]["done"],
        items["Four-agent swarm"]["planned"],
    ) == (1, 3)
    assert items["Four-agent swarm"]["status"] == "In progress"
    assert items["Gold news evidence"]["planned"] == 1
    assert items["Independent repeat"]["planned"] == 3
    assert items["Provider-failure repeats"]["done"] == 0
    assert items["Blinded evidence audit"]["planned"] == 15
