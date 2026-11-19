"""Content-addressed text views, lexical FTS5 and a Qwen cosine index over identical spans."""

import ast
import functools
import hashlib
import os
import re
import shutil
import sqlite3
import tempfile
import threading
from pathlib import Path

import numpy as np
from filelock import FileLock

from .paths import DATA, ENCODER, REVISION, now, read, save

SKIP = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".runtime",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".mypy_cache",
}
SECRET = {
    ".env",
    "credentials.json",
    "credentials",
    "id_rsa",
    "id_ed25519",
    "auth.json",
    "AGENTS.md",
    "AGENTS.override.md",
    "CLAUDE.md",
    ".npmrc",
    ".netrc",
    ".pypirc",
}


def extract(path):
    """Produce canonical UTF-8 text, including physical document locations where available."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader

        return "\n".join(
            f"[Page {i}]\n{p.extract_text() or ''}"
            for i, p in enumerate(PdfReader(path).pages, 1)
        )
    if ext == ".docx":
        from docx import Document

        doc = Document(path)
        blocks = [
            f"[Paragraph {i}] {p.text}"
            for i, p in enumerate(doc.paragraphs, 1)
            if p.text
        ]
        for i, table in enumerate(doc.tables, 1):
            blocks.extend(
                f"[Table {i} row {j}] " + " | ".join(c.text for c in r.cells)
                for j, r in enumerate(table.rows, 1)
            )
        return "\n".join(blocks)
    if ext == ".pptx":
        from pptx import Presentation

        return "\n".join(
            f"[Slide {i}]\n"
            + "\n".join(s.text for s in slide.shapes if s.has_text_frame)
            for i, slide in enumerate(Presentation(path).slides, 1)
        )
    if ext == ".xlsx":
        from openpyxl import load_workbook

        wb = load_workbook(path, read_only=True, data_only=False)
        try:
            return "\n".join(
                f"[{ws.title} row {i}] "
                + " | ".join(str(v) if v is not None else "" for v in row)
                for ws in wb
                for i, row in enumerate(ws.values, 1)
                if any(v is not None for v in row)
            )
        finally:
            wb.close()
    raw = path.read_bytes()
    if b"\0" in raw[:8192]:
        return None
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None
    if ext in {".html", ".htm"}:
        from bs4 import BeautifulSoup

        text = BeautifulSoup(text, "html.parser").get_text("\n", strip=True)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def snapshot(source, cache=None):
    """A snapshot contains regular files only. A path, extraction or text change invalidates it."""
    source = Path(source).resolve(strict=True)
    if not source.is_dir():
        raise ValueError("The corpus must be a directory")
    cache = Path(cache or DATA / "snapshots").resolve()
    cache.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="build-", dir=cache))
    digest = hashlib.sha256(b"canonical-v2")
    skipped = []
    try:
        for current, dirs, files in os.walk(source, followlinks=False):
            base = Path(current)
            dirs[:] = sorted(
                d
                for d in dirs
                if d not in SKIP
                and not d.startswith(".")
                and not (base / d).is_symlink()
                and (base / d).resolve() != cache
            )
            for name in sorted(files):
                p = base / name
                if (
                    name in SECRET
                    or name.startswith(".")
                    or p.is_symlink()
                    or not p.is_file()
                ):
                    continue
                if (
                    p.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".ipynb"}
                    or p.stat().st_size > 5_242_880
                ):
                    continue
                try:
                    text = extract(p)
                except Exception as err:
                    skipped.append([str(p.relative_to(source)), type(err).__name__])
                    continue
                if not text or not text.strip():
                    continue
                rel = p.relative_to(source)
                dest = staging / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                b = text.encode()
                dest.write_bytes(b)
                digest.update(
                    rel.as_posix().encode() + b"\0" + hashlib.sha256(b).digest()
                )
        target = cache / digest.hexdigest()
        with FileLock(str(target) + ".lock"):
            if not target.exists():
                staging.rename(target)
            if skipped:
                save(cache / (target.name + ".skipped.json"), skipped)
        return target
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def spans_for(path, text):
    """Split at line ends where possible and retain unique character offsets on long lines."""
    import bisect

    starts = [0] + [m.end() for m in re.finditer("\n", text)]
    marks = {
        i + 1: line.strip()[:150]
        for i, line in enumerate(text.splitlines())
        if line.startswith(("#", "[Page ", "[Slide ", "[Paragraph "))
    }
    if path.endswith(".py"):
        try:
            for node in ast.walk(ast.parse(text)):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    marks[node.lineno] = node.name
        except (SyntaxError, ValueError, RecursionError):
            pass
    marked = sorted(marks)
    start = 0
    while start < len(text):
        end = min(start + 1400, len(text))
        if end < len(text):
            boundary = text.rfind("\n", start + 700, end)
            if boundary != -1:
                end = boundary + 1
        line = bisect.bisect_right(starts, start)
        pos = bisect.bisect_right(marked, line) - 1
        if text[start:end].strip():
            yield {
                "id": f"{path}@{start}:{end}",
                "path": path,
                "start": start,
                "end": end,
                "line": line,
                "section": marks[marked[pos]] if pos >= 0 else "",
                "text": text[start:end],
            }
        if end == len(text):
            break
        start = max(start + 1, end - 160)


def lexical(text):
    expanded = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    return " ".join(re.findall(r"[^\W_]+", expanded.lower()))


class Encoder:
    """Last-token pooling with left padding follows the pinned official Qwen model card."""

    def __init__(self):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        local = DATA / "qwen-embedding"
        model_id = (
            str(local)
            if (local / "model.safetensors").is_file()
            and (local / "tokenizer.json").is_file()
            else ENCODER
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, revision=REVISION, padding_side="left"
        )
        self.model = (
            AutoModel.from_pretrained(
                model_id,
                revision=REVISION,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            .to(self.device)
            .eval()
        )
        save(
            DATA / "runtime" / "encoder.json",
            dict(
                model=ENCODER,
                revision=REVISION,
                device=self.device,
                accelerator=torch.cuda.get_device_name(0)
                if self.device == "cuda"
                else "CPU",
                torch=torch.__version__,
                cuda=torch.version.cuda,
                utc=now(),
            ),
        )
        self.lock = threading.Lock()

    def encode(self, texts):
        with self.lock, self.torch.inference_mode():
            batch = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(self.device)
            hidden = self.model(**batch).last_hidden_state[:, -1, :].float()
            return self.torch.nn.functional.normalize(hidden, dim=-1).cpu().numpy()

    @functools.lru_cache(maxsize=2048)
    def query(self, text):
        return self.encode(
            [
                "Instruct: Given a question, retrieve passages that provide evidence to answer it\nQuery: "
                + text
            ]
        )[0]


_encoder = None
_encoder_lock = threading.Lock()


def encoder():
    global _encoder
    with _encoder_lock:
        if _encoder is None:
            _encoder = Encoder()
        return _encoder


class FolderIndex:
    """Rank exactly the same passages with SQLite BM25 and optional local dense vectors."""

    def __init__(self, root, dense=True):
        self.root = Path(root).resolve()
        cache = self.root.parent.parent / "indexes" / (self.root.name + "-v3")
        cache.mkdir(parents=True, exist_ok=True)
        self.db = cache / "lexical.sqlite"
        with FileLock(str(cache / "build.lock")):
            if not self.db.exists():
                tmp = cache / "building.sqlite"
                tmp.unlink(missing_ok=True)
                with sqlite3.connect(tmp) as con:
                    con.execute(
                        "create table spans(i integer primary key, id, path, start, end, line, section, text)"
                    )
                    con.execute("create virtual table fts using fts5(terms)")
                    i = 0
                    for p in sorted(self.root.rglob("*")):
                        if p.is_file():
                            for s in spans_for(
                                p.relative_to(self.root).as_posix(),
                                p.read_text(encoding="utf8"),
                            ):
                                con.execute(
                                    "insert into spans values(?,?,?,?,?,?,?,?)",
                                    (i, *s.values()),
                                )
                                con.execute(
                                    "insert into fts(rowid,terms) values(?,?)",
                                    (
                                        i,
                                        lexical(
                                            s["path"]
                                            + " "
                                            + s["section"]
                                            + " "
                                            + s["text"]
                                        ),
                                    ),
                                )
                                i += 1
                # SQLite's context manager commits without closing. DrvFS requires
                # closing the old filename before opening its atomic replacement.
                con.close()
                tmp.replace(self.db)
            with sqlite3.connect(self.db) as con:
                con.row_factory = sqlite3.Row
                self.spans = [
                    dict(r)
                    for r in con.execute(
                        "select id,path,start,end,line,section,text from spans order by i"
                    )
                ]
        self.matrix = None
        if dense and self.spans:
            path = cache / (REVISION + ".npy")
            with FileLock(str(cache / "dense.lock")):
                if not path.exists():
                    temp = path.with_suffix(".partial.npy")
                    checkpoint = cache / (REVISION + ".progress.json")
                    start_at = (
                        read(checkpoint)["completed"]
                        if temp.exists() and checkpoint.exists()
                        else 0
                    )
                    vectors = np.lib.format.open_memmap(
                        temp,
                        mode="r+" if start_at else "w+",
                        dtype=np.float16,
                        shape=(len(self.spans), 1024),
                    )
                    for start in range(start_at, len(self.spans), 24):
                        batch = self.spans[start : start + 24]
                        vectors[start : start + len(batch)] = encoder().encode(
                            [
                                s["path"] + "\n" + s["section"] + "\n" + s["text"]
                                for s in batch
                            ]
                        )
                        completed = start + len(batch)
                        if completed % (24 * 32) == 0 or completed == len(self.spans):
                            vectors.flush()
                            save(
                                checkpoint,
                                dict(
                                    completed=completed,
                                    total=len(self.spans),
                                    utc=now(),
                                ),
                            )
                    vectors.flush()
                    del vectors
                    temp.replace(path)
                    checkpoint.unlink(missing_ok=True)
            self.matrix = np.load(path, mmap_mode="r")

    def search(self, query, k=5, mode="hybrid"):
        """RRF uses 1/(60+rank), with deterministic tie breaks by passage index."""
        k = min(max(int(k), 1), 20)
        words = list(dict.fromkeys(lexical(query).split()))[:48]
        lists = []
        if words:
            with sqlite3.connect(self.db) as con:
                lists.append(
                    [
                        r[0]
                        for r in con.execute(
                            "select rowid from fts where fts match ? order by rank,rowid limit ?",
                            (" OR ".join('"' + w + '"' for w in words), max(30, k)),
                        )
                    ]
                )
        if self.matrix is not None and mode == "hybrid":
            # Float32 accumulation avoids the slow CPU half-precision GEMV path.
            q = encoder().query(query)
            scores = np.einsum("ij,j->i", self.matrix, q, dtype=np.float32)
            lists.append(np.argsort(-scores, kind="stable")[: max(30, k)].tolist())
        fused = {}
        for ranked in lists:
            for rank, i in enumerate(ranked, 1):
                fused[i] = fused.get(i, 0.0) + 1 / (60 + rank)
        return [self.spans[i] for i in sorted(fused, key=lambda i: (-fused[i], i))[:k]]

    def read(self, path, start=0, length=1600):
        dest = (self.root / path.removeprefix("/work/")).resolve()
        if not dest.is_relative_to(self.root) or not dest.is_file():
            raise ValueError("Path outside corpus or missing")
        text = dest.read_text(encoding="utf8")
        start = max(0, int(start))
        end = min(len(text), start + min(max(int(length), 1), 4000))
        if end <= start:
            return []
        name = dest.relative_to(self.root).as_posix()
        return [
            dict(
                id=f"{name}@{start}:{end}",
                path=name,
                start=start,
                end=end,
                line=1 + text.count("\n", 0, start),
                section="",
                text=text[start:end],
            )
        ]
