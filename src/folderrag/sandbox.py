"""Mount an immutable corpus in a new Linux namespace with only a per-agent broker socket."""

import json
import os
import signal
import subprocess
import sys
import time
import tempfile
from pathlib import Path

from .paths import DATA, ROOT

TASK = Path(__file__).with_name("isolated")


def command(root, sock, mode):
    cmd = [
        "bwrap",
        "--die-with-parent",
        "--unshare-all",
        "--new-session",
        "--clearenv",
        "--ro-bind",
        "/usr",
        "/usr",
        "--symlink",
        "usr/bin",
        "/bin",
        "--symlink",
        "usr/sbin",
        "/sbin",
        "--symlink",
        "usr/lib",
        "/lib",
        "--symlink",
        "usr/lib64",
        "/lib64",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
        "--dir",
        "/home/agent/.codex",
        "--dir",
        "/etc",
        "--ro-bind",
        "/etc/passwd",
        "/etc/passwd",
        "--ro-bind",
        "/etc/group",
        "/etc/group",
        "--dir",
        "/transport",
        "--ro-bind",
        str(sock),
        "/transport/api.sock",
        "--ro-bind",
        str(root),
        "/work",
        "--ro-bind",
        str(TASK),
        "/task",
        "--chdir",
        "/work",
        "--setenv",
        "HOME",
        "/home/agent",
        "--setenv",
        "CODEX_HOME",
        "/home/agent/.codex",
        "--setenv",
        "LANG",
        "C.UTF-8",
        "--setenv",
        "PATH",
        "/usr/local/bin:/usr/bin:/bin",
        "--setenv",
        "FOLDER_PROXY_AUTH",
        "local-broker",
        "--setenv",
        "OPENBLAS_NUM_THREADS",
        "1",
        "--setenv",
        "OMP_NUM_THREADS",
        "1",
    ]
    python = "/usr/bin/python3"
    if mode == "arctic":
        cache = DATA / "arctic-index" / root.name
        cache.mkdir(parents=True, exist_ok=True)
        cmd += [
            "--ro-bind",
            os.environ.get("FOLDERRAG_ARCTIC_VENV", sys.prefix),
            "/venv",
            "--ro-bind",
            str(ROOT / "vendor/arctic/arcticswarm"),
            "/arctic/arcticswarm",
            "--ro-bind",
            str(ROOT / "vendor/arctic/conf"),
            "/arctic/conf",
            "--bind",
            str(cache),
            "/index",
            "--setenv",
            "OPENAI_API_KEY",
            "local-broker",
            "--setenv",
            "PYTHONPATH",
            "/arctic",
        ]
        python = "/venv/bin/python"
    return cmd + [python, "/task/runner.py", mode]


def execute(root, sock, mode, prompt, deadline, trace, agent):
    proc = subprocess.Popen(
        command(root, sock, mode),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf8",
        errors="replace",
        start_new_session=True,
    )
    import threading

    def log():
        for line in proc.stderr:
            trace.log("process", agent=agent, line=line.rstrip("\n"))

    thread = threading.Thread(target=log, daemon=True)
    thread.start()
    try:
        proc.stdin.write(prompt)
        proc.stdin.close()
        # stdout contains the final JSON envelope only; collect concurrently with the deadline.
        outs = []
        t = threading.Thread(
            target=lambda: outs.append(proc.stdout.read()), daemon=True
        )
        t.start()
        proc.wait(timeout=max(0.1, deadline - time.monotonic()))
        t.join(5)
        if proc.returncode:
            raise RuntimeError(f"{mode} exited {proc.returncode}; see process records")
        for line in reversed("".join(outs).splitlines()):
            if line.startswith('{"final":'):
                return json.loads(line)["final"]
        raise ValueError("Agent returned no final answer")
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        thread.join(3)


def warm_arctic(root):
    """Build the pinned comparator's index under its actual mount path before timing queries."""
    from filelock import FileLock
    from .paths import now, save

    marker = DATA / "index-timings" / ("arctic-" + root.name + ".json")
    marker.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(marker) + ".lock"):
        if marker.is_file():
            return
        start = time.monotonic()
        with tempfile.NamedTemporaryFile() as unused_broker:
            argv = command(root, unused_broker.name, "arctic")
            subprocess.run([*argv[:-1], "arctic-index"], check=True)
        save(
            marker,
            dict(
                snapshot=root.name,
                mode="arctic",
                seconds=round(time.monotonic() - start, 3),
                utc=now(),
            ),
        )
