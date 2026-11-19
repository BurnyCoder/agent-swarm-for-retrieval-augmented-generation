"""Per-agent Unix socket. It is the only route to OpenAI or host-side corpus tools."""

import contextlib
import http.server
import json
import os
import socketserver
import tempfile
import threading
import time
from pathlib import Path

import httpx

from .ledger import Limit, PendingFunds, charge
from .paths import MODEL, now

_print_lock = threading.Lock()


class Trace:
    def __init__(self, path, console=True):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.console = console
        self.funding_error = None

    def log(self, event, **values):
        if event == "gateway_error" and values.get("error") == "phase budget":
            self.funding_error = "Phase budget cannot cover the next reservation"
        if event == "upstream_error" and "insufficient_quota" in values.get(
            "message", ""
        ):
            self.funding_error = "The upstream project reported insufficient quota"
        line = json.dumps(
            {"utc": now(), "event": event, **values}, ensure_ascii=False, default=str
        )
        with _print_lock:
            with self.path.open("a", encoding="utf8") as file:
                file.write(line + "\n")
            if self.console:
                import sys

                print(line, file=sys.stderr, flush=True)


class Gateway:
    def __init__(
        self,
        ledger,
        phase,
        unit,
        agent,
        cap,
        index,
        evidence,
        trace,
        key,
        deadline,
        mode="hybrid",
        upstream=None,
    ):
        self.ledger, self.phase, self.unit, self.agent, self.cap = (
            ledger,
            phase,
            unit,
            agent,
            cap,
        )
        self.index, self.evidence, self.trace, self.key = index, evidence, trace, key
        self.deadline, self.mode, self.upstream = deadline, mode, upstream
        self.calls = 0

    def tool(self, name, args):
        if time.monotonic() > self.deadline:
            raise Limit("deadline")
        if name == "search":
            rows = self.index.search(args["query"], args.get("k", 5), self.mode)
        elif name == "read":
            rows = self.index.read(
                args["path"], args.get("start", 0), args.get("length", 1600)
            )
        else:
            raise ValueError("Unknown corpus tool")
        self.trace.log(
            "tool", agent=self.agent, name=name, arguments=args, returned=rows
        )
        return self.evidence.offer(rows)

    def request(self, payload, handler):
        if payload.get("model") != MODEL:
            raise ValueError("Unexpected model")
        blocked = {
            "web_search",
            "web_search_preview",
            "file_search",
            "computer_use_preview",
            "image_generation",
            "code_interpreter",
            "mcp",
        }
        incoming_tools = list(payload.get("tools", []))
        for item in (
            payload.get("input", []) if isinstance(payload.get("input"), list) else []
        ):
            if isinstance(item, dict) and item.get("type") == "additional_tools":
                # Swarm size is imposed by the study, including for the stock CLI comparator.
                item["tools"] = [
                    t for t in item["tools"] if t.get("name") != "collaboration"
                ]
                incoming_tools.extend(item["tools"])

        def hosted(tool):
            return tool.get("type") in blocked or any(
                hosted(t) for t in tool.get("tools", [])
            )

        if any(hosted(t) for t in incoming_tools):
            raise ValueError("Hosted tools are outside the file benchmark")
        if time.monotonic() >= self.deadline:
            raise Limit("deadline")
        payload = dict(payload)
        if self.agent == "arctic":
            schema_path = Path(__file__).with_name("isolated") / "answer.schema.json"
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "answer",
                    "strict": True,
                    "schema": json.loads(schema_path.read_text()),
                }
            }
        payload["reasoning"] = {**(payload.get("reasoning") or {}), "effort": "medium"}
        payload["service_tier"] = "default"
        payload["max_output_tokens"] = min(
            int(payload.get("max_output_tokens") or 4096), 4096
        )
        incoming = payload.get("input", [])
        if isinstance(incoming, list):
            for item in incoming:
                if isinstance(item, dict) and item.get("type") in {
                    "function_call_output",
                    "custom_tool_call_output",
                    "local_shell_call_output",
                }:
                    output = item.get("output", "")
                    if isinstance(output, list):
                        for part in output:
                            if isinstance(part, dict) and isinstance(
                                part.get("text"), str
                            ):
                                self.evidence.see_shell(part["text"])
                    else:
                        self.evidence.see_shell(
                            output
                            if isinstance(output, str)
                            else json.dumps(output, ensure_ascii=False)
                        )
        # The maximum full context and premium rates also bound server-side chained turns.
        worst = (1050000 * 0.25 + payload["max_output_tokens"] * 0.75) / 1e6
        while True:
            try:
                key = self.ledger.reserve(
                    self.phase,
                    self.unit,
                    self.agent,
                    worst,
                    payload["max_output_tokens"],
                    self.cap,
                )
                break
            except PendingFunds:
                if time.monotonic() + 1 >= self.deadline:
                    raise
                time.sleep(1)
        self.calls += 1
        self.trace.log("request", agent=self.agent, request_id=key, body=payload)
        uri = self.upstream or "https://api.openai.com/v1/responses"
        duration = max(0.1, min(120.0, self.deadline - time.monotonic()))
        with httpx.Client(trust_env=False, timeout=duration) as client:
            with client.stream(
                "POST",
                uri,
                headers={"Authorization": "Bearer " + self.key},
                json=payload,
            ) as resp:
                if resp.status_code != 200:
                    message = resp.read().decode(errors="replace")
                    if 400 <= resp.status_code < 500 and resp.status_code != 408:
                        self.ledger.settle(key, 0, 0, {}, "rejected")
                    self.trace.log(
                        "upstream_error",
                        agent=self.agent,
                        status=resp.status_code,
                        message=message,
                    )
                    handler.reply(resp.status_code, message.encode())
                    return
                if not payload.get("stream"):
                    raw = resp.read()
                    msg = json.loads(raw)
                    self.trace.log("response", agent=self.agent, body=msg)
                    if msg.get("usage"):
                        self.ledger.settle(
                            key,
                            charge(msg["usage"]),
                            msg["usage"]["output_tokens"],
                            msg["usage"],
                        )
                    handler.reply(200, raw)
                    return
                handler.send_response(200)
                handler.send_header("Content-Type", "text/event-stream")
                handler.send_header("Connection", "close")
                handler.end_headers()
                handler.streaming = True
                connected = True
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        value = line[6:]
                        if value != "[DONE]":
                            event = json.loads(value)
                            self.trace.log("stream", agent=self.agent, body=event)
                            if event.get("type") in {
                                "response.completed",
                                "response.incomplete",
                                "response.failed",
                            }:
                                usage = event.get("response", {}).get("usage")
                                if usage:
                                    self.ledger.settle(
                                        key,
                                        charge(usage),
                                        usage["output_tokens"],
                                        usage,
                                    )
                    if connected:
                        try:
                            handler.wfile.write((line + "\n").encode())
                            handler.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            connected = False


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.split("?")[0] in {"/v1/models", "/models"}:
            self.reply(
                200,
                json.dumps(
                    {"data": [{"id": MODEL, "object": "model"}], "models": []}
                ).encode(),
            )
        else:
            self.reply(404, b"{}")

    def do_POST(self):
        self.streaming = False
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0 or n > 16000000:
                raise ValueError("Invalid request size")
            body = json.loads(self.rfile.read(n))
            if self.path in {"/v1/responses", "/responses"}:
                self.server.gateway.request(body, self)
            elif self.path == "/tool":
                data = self.server.gateway.tool(body["name"], body["arguments"])
                self.reply(200, json.dumps(data, ensure_ascii=False).encode())
            else:
                self.reply(404, b"{}")
        except Exception as err:
            self.server.gateway.trace.log(
                "gateway_error", agent=self.server.gateway.agent, error=str(err)
            )
            if not self.streaming:
                self.reply(
                    403 if isinstance(err, Limit) else 400,
                    json.dumps({"error": {"message": str(err)}}).encode(),
                )


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


@contextlib.contextmanager
def socket_for(gateway):
    with tempfile.TemporaryDirectory(prefix="fr-") as tmp:
        path = Path(tmp) / "api.sock"
        with Server(str(path), Handler) as server:
            server.gateway = gateway
            os.chmod(path, 0o600)
            thread = threading.Thread(
                target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
            )
            thread.start()
            try:
                yield path
            finally:
                server.shutdown()
                thread.join()
