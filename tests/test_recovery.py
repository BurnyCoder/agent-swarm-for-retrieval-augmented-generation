"""Bound an unknown charge without dropping a reservation or resending a generation."""

import pytest

from folderrag.recovery import count_payload, bound_nanodollars, overloaded


def test_token_count_keeps_prior_context_and_response_schema():
    request = dict(
        model="gpt-6-luna",
        input="a",
        previous_response_id="prior",
        text={"format": {"type": "json_object"}},
        tools=[],
        stream=True,
        service_tier="default",
        max_output_tokens=4096,
    )
    counted = count_payload(request)
    assert (
        counted["previous_response_id"] == "prior"
        and counted["text"] == request["text"]
    )
    assert "stream" not in counted and "max_output_tokens" not in counted
    assert bound_nanodollars(1500, 4096) == 1500 * 250 + 4096 * 750
    with pytest.raises(ValueError):
        count_payload({**request, "conversation": "mutable-history"})
    with pytest.raises(ValueError):
        count_payload({**request, "unknown_context": "cannot count"})


def test_only_explicit_provider_capacity_events_trigger_backoff():
    assert overloaded(
        {
            "event": "upstream_error",
            "status": 503,
            "message": '{"error":{"code":"server_is_overloaded"}}',
        }
    )
    assert overloaded(
        {
            "event": "stream",
            "body": {
                "type": "response.failed",
                "response": {"error": {"code": "server_is_overloaded"}},
            },
        }
    )
    assert not overloaded(
        {"event": "case_error", "error": "question or investigator budget"}
    )
    assert not overloaded(
        {"event": "upstream_error", "status": 403, "message": "denied"}
    )


def test_certificate_retains_an_idempotent_live_reservation(tmp_path, monkeypatch):
    import json
    import httpx
    from folderrag import recovery
    from folderrag.ledger import Ledger

    book = Ledger(tmp_path / "cost.sqlite", {"test": 1})
    key = book.reserve("test", "one", "reader", 0.265572, 4096)
    with book.connect() as db:
        db.execute(
            "update calls set utc='2020-01-01T00:00:00.000+00:00' where id=?", (key,)
        )
    logs = tmp_path / "logs/test"
    logs.mkdir(parents=True)
    payload = dict(
        model="gpt-6-luna",
        input="question",
        service_tier="default",
        max_output_tokens=4096,
    )
    line = json.dumps(dict(event="request", request_id=key, body=payload)) + "\n"
    (logs / "one-2026.jsonl").write_text(line)
    real_client = httpx.Client
    mock = httpx.MockTransport(
        lambda _: httpx.Response(
            200, json={"object": "response.input_tokens", "input_tokens": 100}
        )
    )
    monkeypatch.setattr(recovery, "DATA", tmp_path)
    monkeypatch.setattr(recovery, "ledger", lambda: book)
    monkeypatch.setattr(recovery, "api_key", lambda: "fixture")
    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: real_client(transport=mock, **kwargs)
    )
    assert recovery.reconcile("test")["certified"] == 1
    assert book.balances()["reserved"] == recovery.bound_nanodollars(100, 4096) / 1e9
    assert recovery.reconcile("test")["eligible"] == 0
    book.settle(key, 0.00003, 12, {"input_tokens": 100, "output_tokens": 12})
    assert book.balances() == {"settled": 0.00003}


def test_supervisor_stops_the_real_child_on_a_capacity_event(tmp_path, monkeypatch):
    import json
    import subprocess
    import sys
    from folderrag import capacity

    message = json.dumps(
        {
            "event": "upstream_error",
            "status": 503,
            "message": '{"error":{"code":"server_is_overloaded"}}',
        }
    )
    program = "import time; print(" + repr(message) + ", flush=True); time.sleep(90)"
    real_popen = subprocess.Popen
    monkeypatch.setattr(capacity, "DATA", tmp_path)
    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda _args, **kw: real_popen([sys.executable, "-c", program], **kw),
    )
    assert not capacity.execute("test", ["fixture"])
    assert (
        json.loads((tmp_path / "operations/capacity.json").read_text())["state"]
        == "provider_overload"
    )


def test_capacity_probe_is_metered_and_honors_retry_after(tmp_path, monkeypatch):
    import httpx
    from folderrag import capacity
    from folderrag.ledger import Ledger

    def service(request):
        if request.url.path.endswith("/input_tokens"):
            return httpx.Response(
                200, json={"object": "response.input_tokens", "input_tokens": 12}
            )
        return httpx.Response(
            503,
            headers={"Retry-After": "75"},
            json={"error": {"code": "server_is_overloaded"}},
        )

    book = Ledger(tmp_path / "budget.sqlite", {"retry": 1})
    real_client = httpx.Client
    mock = httpx.MockTransport(service)
    monkeypatch.setattr(capacity, "DATA", tmp_path)
    monkeypatch.setattr(capacity, "ledger", lambda: book)
    monkeypatch.setattr(capacity, "api_key", lambda: "fixture")
    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: real_client(transport=mock, **kwargs)
    )
    assert capacity.probe() == (False, 75)
    assert 0 < book.balances()["reserved"] < 0.00011
