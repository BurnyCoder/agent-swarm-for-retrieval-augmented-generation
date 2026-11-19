"""Runs inside an empty Linux mount/network namespace. No upstream key enters this process."""

import http.client
import json
import select
import socket
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

SOCK = "/transport/api.sock"
PORT = 18779
MODEL = "gpt-6-luna"


class Relay(socketserver.BaseRequestHandler):
    """Bridge the sandbox loopback to a single per-agent HTTP Unix socket."""

    def handle(self):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as host:
            host.connect(SOCK)
            peers = {host: self.request, self.request: host}
            while True:
                ready, _, _ = select.select(list(peers), [], [], 310)
                if not ready:
                    return
                for src in ready:
                    buf = src.recv(65536)
                    if not buf:
                        return
                    peers[src].sendall(buf)


class Bridge(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def mcp():
    """MCP stdio transport and tools/list/call per modelcontextprotocol.io/specification."""
    tools = [
        {
            "name": "search",
            "description": "Search this folder by exact identifiers and meaning. Returns quoted spans with stable IDs.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer"}},
                "required": ["query"],
            },
        },
        {
            "name": "read",
            "description": "Read a source range by relative path and character offset. Use its exact quote and ID.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start": {"type": "integer"},
                    "length": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    ]
    for tool in tools:
        tool["annotations"] = {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
            "idempotentHint": True,
        }
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            continue
        response = {"jsonrpc": "2.0", "id": request["id"]}
        try:
            method = request["method"]
            if method == "initialize":
                result = {
                    "protocolVersion": request["params"]["protocolVersion"],
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "folder-evidence", "version": "1.0"},
                }
            elif method == "tools/list":
                result = {"tools": tools}
            elif method == "tools/call":
                # A Unix-domain connection remains scoped even when an MCP child starts its own namespace.
                conn = http.client.HTTPConnection("localhost", timeout=90)
                conn.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                conn.sock.connect(SOCK)
                params = request["params"]
                conn.request(
                    "POST",
                    "/tool",
                    json.dumps(
                        {
                            "name": params["name"],
                            "arguments": params.get("arguments", {}),
                        }
                    ),
                    {"Content-Type": "application/json"},
                )
                r = conn.getresponse()
                result = {
                    "content": [{"type": "text", "text": r.read().decode()}],
                    "isError": r.status != 200,
                }
                conn.close()
            elif method == "ping":
                result = {}
            else:
                response["error"] = {"code": -32601, "message": "Unknown method"}
                result = None
            if result is not None:
                response["result"] = result
        except Exception as e:
            response["error"] = {"code": -32603, "message": str(e)}
        print(json.dumps(response), flush=True)


def arctic(prompt):
    # Use the unmodified pinned Agent loop and tool factory; adapt only provider and external sandbox.
    sys.path.insert(0, "/arctic")
    from arcticswarm.agent import Agent
    from arcticswarm.llm_client import OpenAIResponsesLLMClient
    from arcticswarm.run_config import load_run_config

    run = load_run_config(
        [
            "/arctic/conf/bench/folder_rag.yaml",
            "/arctic/conf/bench/folder_rag_single_agent.yaml",
        ]
    )
    cfg = run.to_arcticswarm_config()
    cfg.model = MODEL
    cfg.openai_api_key = cfg.api_key = "local-broker"
    cfg.openai_base_url = f"http://127.0.0.1:{PORT}/v1"
    cfg.reasoning_effort = "medium"
    cfg.max_tokens = 4096
    cfg.max_turns = 32
    cfg.corpus_local_path = "/work"
    cfg.folder_index_dir = "/index"
    cfg.exec_backend = "local"
    cfg.exec_corpus_root = "/work"
    cfg.disable_closed_model_fallback = True

    class LunaAgent(Agent):
        def _make_llm_client(self, **kwargs):
            return OpenAIResponsesLLMClient(
                api_key="local-broker", base_url=cfg.openai_base_url, timeout=90
            )

    agent = LunaAgent(cfg)
    try:
        answer = agent.run_turn(prompt, max_turns=32)
        print(json.dumps({"final": answer}), flush=True)
    finally:
        agent.close()


def run(mode):
    bridge = Bridge(("127.0.0.1", PORT), Relay)
    threading.Thread(target=bridge.serve_forever, daemon=True).start()
    prompt = sys.stdin.read()
    if mode == "arctic":
        arctic(prompt)
        return
    cmd = [
        "/usr/bin/codex",
        "exec",
        "--model",
        MODEL,
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--json",
        "--color",
        "never",
        "--output-schema",
        "/task/answer.schema.json",
        "-o",
        "/tmp/answer",
        "-c",
        'model_provider="folder_gateway"',
        "-c",
        'model_providers.folder_gateway.name="Folder Gateway"',
        "-c",
        f'model_providers.folder_gateway.base_url="http://127.0.0.1:{PORT}/v1"',
        "-c",
        'model_providers.folder_gateway.wire_api="responses"',
        "-c",
        'model_providers.folder_gateway.env_key="FOLDER_PROXY_AUTH"',
        "-c",
        "model_providers.folder_gateway.request_max_retries=0",
        "-c",
        "model_providers.folder_gateway.stream_max_retries=0",
        "-c",
        "model_providers.folder_gateway.supports_websockets=false",
        "-c",
        'model_reasoning_effort="medium"',
        "-c",
        'web_search="disabled"',
        "-c",
        'projects."/work".trust_level="trusted"',
        "-c",
        "features.multi_agent=false",
        "-c",
        "features.shell_snapshot=false",
    ]
    if mode == "custom":
        cmd += [
            "-c",
            'mcp_servers.folder.command="/usr/bin/python3"',
            "-c",
            'mcp_servers.folder.args=["/task/runner.py","mcp"]',
            "-c",
            "mcp_servers.folder.required=true",
            "-c",
            'mcp_servers.folder.tools.search.approval_mode="approve"',
            "-c",
            'mcp_servers.folder.tools.read.approval_mode="approve"',
        ]
    rc = subprocess.run(
        cmd + ["-"], input=prompt, text=True, stdout=sys.stderr, stderr=sys.stderr
    ).returncode
    if rc or not Path("/tmp/answer").is_file():
        raise SystemExit(rc or 2)
    print(json.dumps({"final": Path("/tmp/answer").read_text()}), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "mcp":
        mcp()
    else:
        run(sys.argv[1])
