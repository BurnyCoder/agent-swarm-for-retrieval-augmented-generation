"""Keep corpus snapshots, model caches and private records separate from source control."""

import datetime as dt
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(
    os.environ.get("FOLDERRAG_HOME", Path.home() / ".local/share/luna-folderrag")
)
MODEL = "gpt-6-luna"
ENCODER = "Qwen/Qwen3-Embedding-0.6B"
REVISION = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"
LIMITS = {"dev": 5.0, "test": 34.0, "diagnostics": 8.0, "retry": 3.0}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def save(path, value):
    """Replace a complete record atomically, including on resumption."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf8", dir=path.parent, delete=False
    ) as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write("\n")
    os.replace(out.name, path)
