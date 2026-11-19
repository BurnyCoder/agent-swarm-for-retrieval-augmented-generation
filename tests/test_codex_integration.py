"""Offline normal-path tests use the real Codex binary and a local scripted Responses server."""

import contextlib
import http.server
import json
import socket
import subprocess
import threading
import time
import pytest

from folderrag.agents import Case, answer
from folderrag.corpus import FolderIndex, snapshot
from folderrag.gateway import Trace
from folderrag.ledger import Ledger
from folderrag.sandbox import command


class Scripted(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        text = json.dumps(
            {
                "answer": "Mallow",
                "explanation": "The codeword is Mallow.",
                "citations": [
                    {
                        "claim": "The codeword is Mallow.",
                        "path": "facts.txt",
                        "quote": "is Mallow",
                        "span_id": "facts.txt@0:23",
                    }
                ],
            }
        )
        content = {"type": "output_text", "text": text, "annotations": []}
        message = {
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "id": "msg_1",
            "content": [content],
        }
        inputs = request.get("input", [])
        if (
            isinstance(inputs, list)
            and any(x.get("type") == "additional_tools" for x in inputs)
            and not any(
                x.get("type") in {"custom_tool_call_output", "function_call_output"}
                for x in inputs
            )
        ):
            message = {
                "type": "custom_tool_call",
                "id": "ctc_fixture",
                "call_id": "call_fixture",
                "status": "completed",
                "namespace": "functions",
                "name": "exec",
                "input": 'const r=await tools.mcp__folder__search({query:"codeword",k:1}); text(r);',
            }
        resp = {
            "id": "resp_fixture",
            "object": "response",
            "model": "gpt-6-luna",
            "status": "completed",
            "output": [message],
            "usage": {
                "input_tokens": 140,
                "output_tokens": 42,
                "total_tokens": 182,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            },
        }
        if request.get("stream"):
            events = [
                {
                    "type": "response.created",
                    "response": {**resp, "output": [], "status": "in_progress"},
                },
                {
                    "type": "response.output_item.added",
                    "output_index": 0,
                    "item": message,
                },
            ]
            if message["type"] == "message":
                events.append(
                    {
                        "type": "response.output_text.delta",
                        "item_id": "msg_1",
                        "output_index": 0,
                        "content_index": 0,
                        "delta": text,
                    }
                )
            events.extend(
                [
                    {
                        "type": "response.output_item.done",
                        "output_index": 0,
                        "item": message,
                    },
                    {"type": "response.completed", "response": resp},
                ]
            )
            body = "".join(
                "event: " + e["type"] + "\ndata: " + json.dumps(e) + "\n\n"
                for e in events
            ).encode()
            mime = "text/event-stream"
        else:
            body = json.dumps(resp).encode()
            mime = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@contextlib.contextmanager
def fake_api():
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), Scripted) as server:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/v1/responses"
        finally:
            server.shutdown()
            t.join()


@pytest.mark.parametrize("size", [1, 2, 4, 8])
def test_real_codex_swarm_and_isolation(tmp_path, size):
    source = tmp_path / "input"
    source.mkdir()
    (source / "facts.txt").write_text("The codeword is Mallow.")
    snap = snapshot(source, tmp_path / "cache")
    index = FolderIndex(snap, dense=False)
    # Verify both the corpus mount and absent host/project/network access with a real child.
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(str(tmp_path / "sock"))
    cmd = command(snap, tmp_path / "sock", "custom")[:-3] + [
        "/usr/bin/python3",
        "-c",
        "import os,pathlib,socket; assert not pathlib.Path('/mnt/c').exists(); assert 'OPENAI_API_KEY' not in os.environ; "
        "assert pathlib.Path('/work/facts.txt').is_file(); assert not os.access('/work/facts.txt',os.W_OK); "
        "assert socket.socket().connect_ex(('1.1.1.1',443)) != 0",
    ]
    subprocess.run(cmd, check=True, timeout=12)
    sock.close()
    ledger = Ledger(tmp_path / "budget.sqlite", {"dev": 5})
    trace = Trace(tmp_path / "test.jsonl", False)
    with fake_api() as upstream:
        case = Case(
            index,
            ledger,
            "dev",
            "integration",
            trace,
            "test-key",
            time.monotonic() + 70,
            upstream,
        )
        result = answer(case, "What is the codeword?", size=size)
    assert result["answer"] == "Mallow", result
    assert (
        result["workers_completed"] == size - 1
        and result["peak_investigators"] == size - 1
    )
    assert (
        result["workers_contributing"] == size - 1 and result["citations"][0]["valid"]
    )


@pytest.mark.parametrize("method", ["stock", "arctic", "oneshot", "closed", "random"])
def test_baseline_entrypoints(tmp_path, method):
    source = tmp_path / "source"
    source.mkdir()
    (source / "facts.txt").write_text("The codeword is Mallow.")
    index = FolderIndex(snapshot(source, tmp_path / "cache"), dense=False)
    tracker = Ledger(tmp_path / "ledger.db", {"dev": 5})
    trace = Trace(tmp_path / "trace.jsonl", False)
    with fake_api() as upstream:
        case = Case(
            index,
            tracker,
            "dev",
            "baseline",
            trace,
            "test",
            time.monotonic() + 100,
            upstream,
        )
        result = answer(case, "What is the codeword?", method=method)
    assert result["answer"] == "Mallow"
    assert tracker.unit("baseline")["requests"] >= 1
