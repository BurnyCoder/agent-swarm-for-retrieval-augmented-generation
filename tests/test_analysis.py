"""Synthetic panels verify primary test families, matching and completion gating."""

from folderrag.analysis import comparisons


def test_complete_panel_controls_the_primary_family():
    rows = []
    for domain, n in (("news", 32), ("code", 15)):
        for i in range(n):
            for arm in ("swarm2", "swarm1", "stock", "arctic", "oneshot"):
                score = (
                    int(arm == "swarm2")
                    if domain == "news"
                    else (100 if arm in ("swarm2", "stock") else 50)
                )
                rows.append(
                    dict(
                        arm=arm,
                        domain=domain,
                        id=f"{domain}-{i}",
                        phase="test",
                        score=score,
                        stratum=str(i % 3),
                    )
                )
    assert comparisons(rows[:-1], "swarm2", 1) == []
    comp = comparisons(rows, "swarm2", 1)
    assert len(comp) == 8
    for r in comp:
        assert r["p"] <= r["holm_p"] <= 1 and r["low"] <= r["difference"] <= r["high"]
        assert r["complete"]
        if r["domain"] == "code" and r["comparator"] == "stock":
            assert r["difference"] == 0 and r["holm_p"] == 1 and not r["positive"]
        else:
            assert r["positive"]
