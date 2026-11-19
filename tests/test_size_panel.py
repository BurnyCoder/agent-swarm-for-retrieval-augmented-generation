"""Keep live swarm-size charts comparable when cases arrive at different times."""

from folderrag.examples import matched_size_groups


def test_four_sizes_share_ids_across_confirmation_and_controls():
    def row(qid, size, score, phase):
        return dict(
            id=qid,
            phase=phase,
            domain="news",
            arm=f"swarm{size}",
            score=score,
            seconds=10,
            cost_upper_usd=0.01,
        )

    rows = [
        row(qid, size, int(size == 4), "test" if size in (1, 4) else "diagnostics")
        for qid in ("included", "outside")
        for size in (1, 2, 4, 8)
    ]
    rows.append(row("partial", 1, 1, "test"))
    panel = matched_size_groups(rows, {"included", "partial"})
    assert [(r["phase"], r["arm"], r["n"], r["mean"]) for r in panel] == [
        ("held", f"swarm{size}", 1, float(size == 4)) for size in (1, 2, 4, 8)
    ]
