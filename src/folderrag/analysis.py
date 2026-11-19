"""Paired confirmatory estimates. Development and held-out measurements never share a test."""

import collections
import numpy as np
from scipy.stats import binomtest


def means(rows):
    groups = collections.defaultdict(list)
    for row in rows:
        groups[(row["phase"], row["domain"], row["arm"])].append(row)
    result = []
    for (phase, domain, arm), rs in sorted(groups.items()):
        xs = [r["score"] for r in rs if r.get("score") is not None]
        if not xs:
            continue
        rng = np.random.default_rng(20261119)
        if domain == "news":
            interval = binomtest(int(sum(xs)), len(xs)).proportion_ci(method="wilson")
            low, high = float(interval.low), float(interval.high)
        else:
            boot = np.mean(rng.choice(xs, size=(4000, len(xs))), axis=1)
            low, high = map(float, np.quantile(boot, [0.025, 0.975]))
        times = [r["seconds"] for r in rs]
        result.append(
            dict(
                phase=phase,
                domain=domain,
                arm=arm,
                n=len(rs),
                graded=len(xs),
                mean=float(np.mean(xs)),
                low=low,
                high=high,
                cost=float(np.mean([r["cost_upper_usd"] for r in rs])),
                p50=float(np.median(times)),
                p95=float(np.quantile(times, 0.95)),
                failures=sum(bool(r.get("error")) for r in rs),
                requested=sum(r.get("workers_requested", 0) for r in rs),
                completed=sum(r.get("workers_completed", 0) for r in rs),
                contributing=sum(r.get("workers_contributing", 0) for r in rs),
            )
        )
    return result


def comparisons(rows, selected, target_blocks, stopped=False):
    test = {
        (r["id"], r["arm"]): r
        for r in rows
        if r["phase"] == "test" and r.get("score") is not None
    }
    if not target_blocks or (
        not stopped
        and sum(r["phase"] == "test" for r in rows) < target_blocks * (32 + 15) * 5
    ):
        return []
    out = []
    for domain in ("news", "code"):
        for comp in ("stock", "arctic", "oneshot", "swarm1"):
            pairs = [
                (a, test[qid, comp])
                for (qid, arm), a in test.items()
                if a["domain"] == domain and arm == selected and (qid, comp) in test
            ]
            if not pairs:
                continue
            rng = np.random.default_rng(20261119)
            d = np.array([a["score"] - b["score"] for a, b in pairs], float)
            strata = collections.defaultdict(list)
            for (a, b), x in zip(pairs, d):
                strata[a["stratum"]].append(x)
            boot = sum(
                rng.choice(x, (6000, len(x))).sum(axis=1) for x in strata.values()
            ) / len(d)
            if domain == "news":
                discord = int(np.count_nonzero(d))
                p = (
                    float(binomtest(int(sum(d > 0)), discord).pvalue)
                    if discord
                    else 1.0
                )
            else:
                obs = abs(d.sum())
                extreme = 0
                for _ in range(20):
                    sims = (rng.choice([-1, 1], (1000, len(d))) * d).sum(axis=1)
                    extreme += int((np.abs(sims) >= obs - 1e-9).sum())
                p = (extreme + 1) / 20001
            row = dict(
                domain=domain,
                comparator=comp,
                n=len(d),
                difference=float(d.mean()),
                low=float(np.quantile(boot, 0.025)),
                high=float(np.quantile(boot, 0.975)),
                p=p,
                complete=len(d) == target_blocks * (32 if domain == "news" else 15),
            )
            if domain == "code":
                cluster = [np.mean(g) for g in strata.values()]
                samples = rng.choice(cluster, (6000, len(cluster))).mean(axis=1)
                row["repository_ci"] = np.quantile(samples, [0.025, 0.975]).tolist()
            out.append(row)
    for single, count in ((False, 6), (True, 2)):
        items = sorted(
            [r for r in out if (r["comparator"] == "swarm1") == single],
            key=lambda r: r["p"],
        )
        previous = 0.0
        for rank, row in enumerate(items):
            previous = max(previous, min(1.0, (count - rank) * row["p"]))
            row["holm_p"] = previous
            row["positive"] = (
                row["complete"] and previous < 0.05 and row["difference"] > 0
            )
    return out
