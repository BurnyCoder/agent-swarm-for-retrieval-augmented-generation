"""README comparisons must use the same original questions across all five arms."""

import json
from pathlib import Path
from statistics import mean

from folderrag.readme import heldout_snapshot


def test_matched_scores_exclude_partial_questions_and_keep_failed_first_attempts():
    arms = ("swarm4", "swarm1", "stock", "arctic", "oneshot")
    rows = [
        dict(
            phase="test",
            domain="news",
            id=q,
            arm=arm,
            unit=q + arm,
            score=int(arm != "stock" or q != "failed"),
            error="capacity" if q == "failed" and arm == "stock" else None,
            seconds=20,
            cost_upper_usd=0.02,
            cited_gold_recall=0.8,
        )
        for q in ("healthy", "failed", "partial")
        for arm in arms
        if not (q == "partial" and arm == "stock")
    ]
    data = dict(
        rows=[*rows, {**rows[0], "phase": "retry"}],
        freeze={"size": 4},
        targets={"test": 25, "audit": 5},
        updated="2026-11-19T19:30:00+00:00",
        balances={"settled": 0.82, "reserved": 0.03},
        support=[],
        twins=[],
        historical=[],
        quote_audit={},
    )
    data["capacity-flags"] = [{"unit": "failedstock"}]
    snapshot = heldout_snapshot(data)
    assert "14/25" in snapshot and "2 questions" in snapshot
    assert "| News, first attempts | 2 | 2/2 | 2/2 | 1/2 |" in snapshot
    assert "| News, outage-free | 1 | 1/1 | 1/1 | 1/1 |" in snapshot
    assert "19:30 UTC" in snapshot and "$0.82" in snapshot
    assert "1 provider" in snapshot


def test_closed_readme_leads_with_the_measured_baseline_differences():
    results = Path(__file__).resolve().parents[1] / "results"
    data = json.loads((results / "metrics.json").read_text(encoding="utf8"))
    data["rows"] = json.loads((results / "cases.json").read_text(encoding="utf8"))
    lead, _ = heldout_snapshot(data).split("## Current held-out results")
    scores = {
        (domain, arm): [
            row["score"]
            for row in data["rows"]
            if (row["phase"], row["domain"], row["arm"]) == ("test", domain, arm)
        ]
        for domain in ("news", "code")
        for arm in ("stock", "oneshot", f"swarm{data['freeze']['size']}")
    }
    swarm = f"swarm{data['freeze']['size']}"
    fewer = sum(scores["news", "stock"]) - sum(scores["news", swarm])
    gain = mean(scores["code", swarm]) - mean(scores["code", "oneshot"])
    assert f"{fewer:.0f} fewer than stock Codex" in lead
    assert f"{gain:.1f} points higher than one-shot retrieval" in lead
    assert "Arctic" in lead and "one agent" in lead and "unclear" in lead


def test_offline_refresh_preserves_measurement_timestamp(tmp_path, monkeypatch):
    from folderrag import report
    from folderrag.ledger import Ledger
    from folderrag.paths import save

    when = "2026-11-19T19:30:00+00:00"
    for path in ("ROOT", "DATA", "OUT"):
        monkeypatch.setattr(report, path, tmp_path)
    monkeypatch.setattr(report, "BENCH", tmp_path / "benchmark")
    monkeypatch.setattr(report, "records", lambda *args, **kwargs: [])
    monkeypatch.setattr(report, "ledger", lambda: Ledger(tmp_path / "empty.sqlite", {}))
    save(tmp_path / "protocol/splits.json", {"legacy": {}, "blocks": [[]]})
    save(tmp_path / "metrics.json", {"updated": when})
    assert report.dashboard_data()["updated"] == when
