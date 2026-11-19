"""Exercise per-answer reporting when the grading phase already is the retry allocation."""

from folderrag import report
from folderrag.ledger import Ledger
from folderrag.paths import save


def test_technical_repeat_grade_is_counted_once(tmp_path, monkeypatch):
    # One generated answer and one successful grade have independent ledger units.
    book = Ledger(tmp_path / "cost.sqlite", {"retry": 1})
    unit = "test-item-stock-capacity-repeat"
    for key, amount in ((unit, 0.02), (unit + "-grade-retry", 0.01)):
        ticket = book.reserve("retry", key, "fixture", 0.05, 50)
        book.settle(ticket, amount, 20, {})
    row = dict(
        unit=unit,
        id="item",
        phase="retry",
        domain="code",
        arm="stock",
        score=75,
        seconds=4,
        cost_upper_usd=0.05,
    )
    for path in ("ROOT", "BENCH", "DATA", "OUT"):
        monkeypatch.setattr(report, path, tmp_path)
    monkeypatch.setattr(report, "ledger", lambda: book)
    monkeypatch.setattr(
        report, "records", lambda phase=None, pilots=False: [] if pilots else [row]
    )
    save(tmp_path / "protocol/splits.json", {"legacy": {}, "blocks": [[]]})

    data = report.dashboard_data()
    assert data["rows"][0]["grading_cost_upper_usd"] == 0.01
    assert data["rows"][0]["cost_upper_usd"] == 0.02
    assert data["budget"]["retry"] == 0.03
