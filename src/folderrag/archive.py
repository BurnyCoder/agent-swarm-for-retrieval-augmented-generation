"""Archive private benchmark transcripts while keeping interactive user folders out of releases."""

import tarfile

from .paths import DATA


def build_archives():
    output = DATA / "archives"
    output.mkdir(parents=True, exist_ok=True)
    phases = ("dev", "test", "diagnostics", "retry")
    for phase in phases:
        files = []
        for prefix in ("logs", "records"):
            source = DATA / prefix / phase
            files.extend(
                p
                for p in source.glob("*")
                if p.is_file()
                and not p.name.startswith("ask-")
                and p.suffix in {".jsonl", ".json", ".answer", ".unrun"}
            )
        files.extend((DATA / "evidence").glob(phase + "-*.json.gz"))
        if phase == "diagnostics":
            for name in ("twins", "support"):
                files.extend((DATA / name).glob("*.json"))
        if phase == "dev":
            files.extend((DATA / "historical").glob("*.json"))
        if not files:
            continue
        path = output / (phase + ".tar.gz")
        staging = path.with_suffix(".partial")
        with tarfile.open(staging, "w:gz", compresslevel=2) as tar:
            for member in sorted(files):
                tar.add(
                    member, arcname=member.relative_to(DATA).as_posix(), recursive=False
                )
        staging.replace(path)
        print(path, len(files), "files", flush=True)
