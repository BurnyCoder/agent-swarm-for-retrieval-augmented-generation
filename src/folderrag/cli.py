"""The Windows console entry forwards file paths to the same Linux implementation."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    if os.name == "nt":
        root = Path(__file__).resolve().parents[2]
        args = sys.argv[1:].copy()
        for i, value in enumerate(args[:-1]):
            if value == "--folder":
                args[i + 1] = subprocess.check_output(
                    [
                        "wsl",
                        "-d",
                        "Ubuntu",
                        "--",
                        "wslpath",
                        "-a",
                        str(Path(args[i + 1]).resolve()),
                    ],
                    text=True,
                    encoding="utf-8",
                ).strip()
        raise SystemExit(
            subprocess.call(
                [
                    "wsl",
                    "-d",
                    "Ubuntu",
                    "--cd",
                    str(root),
                    "--",
                    "sh",
                    "scripts/linux-run",
                    "folderrag",
                    *args,
                ]
            )
        )
    from .commands import run

    run()


if __name__ == "__main__":
    main()
