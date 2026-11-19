"""Materialize pinned public inputs and separate evaluator-only labels from mounted files."""

import collections
import concurrent.futures
import hashlib
import io
import json
import random
import re
import tarfile
import urllib.request
from pathlib import Path

from .paths import DATA, ROOT, read, save

NEWS = "https://huggingface.co/datasets/yixuantt/MultiHopRAG/resolve/71ac0d0bd1f951d2d6b70311f7d2ae404e1ffa82/"
SWE = "https://huggingface.co/datasets/swe-qa/SWE-QA-Benchmark/resolve/f048f07da234b39e32937f115d027c5b71acd54e/"
PINS = "https://raw.githubusercontent.com/peng-weihan/SWE-QA-Bench/c13deac7a0d99b0ca2e593e004c4739475785b08/repo_commit.txt"
BENCH = DATA / "benchmark"


def download(url):
    cache = BENCH / "downloads" / hashlib.sha256(url.encode()).hexdigest()
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            url, headers={"User-Agent": "folderrag-research/0.1"}
        )
        with urllib.request.urlopen(request, timeout=180) as resp:
            data = resp.read()
        tmp = cache.with_suffix(".partial")
        tmp.write_bytes(data)
        tmp.replace(cache)
    return cache.read_bytes()


def slug(s, n=60):
    return (
        re.sub("[^a-zA-Z0-9]+", "-", str(s)).strip("-").lower()[:n].rstrip("-")
        or "untitled"
    )


def news():
    root = BENCH / "sources/news"
    seen, paths = set(), {}
    for article in json.loads(download(NEWS + "corpus.json")):
        date = str(article.get("published_at") or "")[:10] or "undated"
        rel = f"{slug(article.get('source') or 'unknown', 30)}/{date}_{slug(article['title'])}.md"
        while rel in seen:
            rel = rel[:-3] + "_2.md"
        seen.add(rel)
        paths[article["url"]] = rel
        dest = root / rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            header = "\n".join(
                f"{k}: {article.get(v, '')}"
                for k, v in (
                    ("Source", "source"),
                    ("Author", "author"),
                    ("Published", "published_at"),
                    ("Category", "category"),
                    ("URL", "url"),
                )
            )
            dest.write_text(
                f"# {article['title']}\n\n{header}\n\n{article['body']}",
                encoding="utf8",
            )
    rows = []
    for i, q in enumerate(json.loads(download(NEWS + "MultiHopRAG.json"))):
        facts = [
            {"path": paths.get(e["url"], ""), "fact": e.get("fact", "")}
            for e in q.get("evidence_list", [])
        ]
        rows.append(
            dict(
                id=f"mhr_{i:04d}",
                domain="news",
                folder="news",
                stratum=q["question_type"],
                question=q["query"],
                answer=q["answer"],
                facts=facts,
            )
        )
    return rows


def code_repo(pin):
    url, commit = pin.split()
    repo = url.rsplit("/", 1)[-1]
    root = BENCH / "sources" / repo
    marker = BENCH / "revisions" / repo
    if not marker.exists():
        archive = download(
            f"https://codeload.github.com/{url.removeprefix('https://github.com/')}/tar.gz/{commit}"
        )
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            for member in tar:
                parts = Path(member.name).parts[1:]
                if (
                    not parts
                    or not member.isfile()
                    or ".." in parts
                    or member.size > 5_242_880
                ):
                    continue
                target = root.joinpath(*parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(commit)
    data = [
        json.loads(line)
        for line in download(SWE + repo + ".jsonl").splitlines()
        if line.strip()
    ]
    return [
        dict(
            id=f"sweqa_{repo}_{i:02d}",
            domain="code",
            folder=repo,
            stratum=repo,
            question=q["question"],
            answer=q["answer"],
            facts=[],
        )
        for i, q in enumerate(data)
    ]


def prepare():
    """Build ten deterministic blocks. Only IDs and hashes enter the public-facing protocol."""
    rows = news()
    pins = [p.strip() for p in download(PINS).decode().splitlines() if p.strip()]
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for group in pool.map(code_repo, pins):
            rows.extend(group)
    archive_inputs(pins)
    byid = {r["id"]: r for r in rows}
    dev = read(ROOT / "protocol/development.json")
    normalized = lambda q: " ".join(re.findall(r"\w+", q.casefold()))
    lookup = {normalized(r["question"]): r["id"] for r in rows}
    legacy = {r["id"]: lookup[normalized(r["question"])] for r in dev}
    seen = {normalized(r["question"]) for r in dev}
    rng = random.Random(20261119)
    strata = collections.defaultdict(list)
    for row in rows:
        k = normalized(row["question"])
        if k not in seen:
            strata[(row["domain"], row["stratum"])].append(row["id"])
            seen.add(k)
    for key in sorted(strata):
        rng.shuffle(strata[key])
    types = sorted(k for k in strata if k[0] == "news")
    counts = {k: len(strata[k]) for k in types}
    used = collections.Counter()
    blocks = []
    for block in range(10):
        ids = []
        for j in range(32):
            k = max(
                types,
                key=lambda g: (
                    (block * 32 + j + 1) * counts[g] / sum(counts.values()) - used[g]
                ),
            )
            ids.append(strata[k].pop())
            used[k] += 1
        ids.extend(strata[k].pop() for k in sorted(strata) if k[0] == "code")
        rng.shuffle(ids)
        blocks.append(ids)
    assert len({q for b in blocks for q in b}) == 470 and not set(
        legacy.values()
    ).intersection(q for b in blocks for q in b)
    save(BENCH / "cases.json", byid)
    save(
        ROOT / "protocol/splits.json",
        {
            "seed": 20261119,
            "legacy": legacy,
            "blocks": blocks,
            "pins": pins,
            "questions_sha256": hashlib.sha256(
                json.dumps([(r["id"], r["question"]) for r in rows]).encode()
            ).hexdigest(),
        },
    )
    print(
        "Prepared",
        len(rows),
        "questions and",
        len(blocks),
        "balanced blocks.",
        flush=True,
    )


def archive_inputs(pins):
    """Fingerprint upstream downloads without exposing benchmark contents to any answering agent."""
    urls = [PINS, NEWS + "corpus.json", NEWS + "MultiHopRAG.json"]
    for pin in pins:
        repo, rev = pin.split()
        urls.extend(
            [
                SWE + repo.rsplit("/", 1)[-1] + ".jsonl",
                f"https://codeload.github.com/{repo.removeprefix('https://github.com/')}/tar.gz/{rev}",
            ]
        )
    manifest = {}
    for url in urls:
        raw = download(url)
        row = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        if url.startswith("https://codeload.github.com/"):
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
                commit = archive.pax_headers.get("comment", "")
                if re.fullmatch(r"[0-9a-f]{40}", commit):
                    row["commit"] = commit
        manifest[url] = row
    save(ROOT / "protocol/input-checksums.json", manifest)


if __name__ == "__main__":
    prepare()
