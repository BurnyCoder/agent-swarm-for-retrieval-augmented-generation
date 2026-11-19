"""The Windows console entry forwards file paths to the same Linux implementation."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    if os.name == "nt":
        root = Path(__file__).resolve().parents[2]
        args = sys.argv[1:].copy()
        for i, value in enumerate(args):
            if (
                value == "--folder"
                and i + 1 < len(args)
                or value.startswith("--folder=")
            ):
                inline = value.startswith("--folder=")
                source = value.split("=", 1)[1] if inline else args[i + 1]
                # --exec preserves quotation marks and shell metacharacters in questions.
                directory = subprocess.check_output(
                    [
                        "wsl",
                        "-d",
                        "Ubuntu",
                        "--cd",
                        str(Path(source).resolve()),
                        "--exec",
                        "/bin/pwd",
                    ],
                    text=True,
                    encoding="utf8",
                ).strip()
                args[i if inline else i + 1] = (
                    "--folder=" if inline else ""
                ) + directory
        raise SystemExit(
            subprocess.call(
                [
                    "wsl",
                    "-d",
                    "Ubuntu",
                    "--cd",
                    str(root),
                    "--exec",
                    "env",
                    "FOLDERRAG_LINKS_WINDOWS=1",
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
