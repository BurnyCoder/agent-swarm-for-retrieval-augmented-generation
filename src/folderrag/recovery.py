"""Operational recovery for provider capacity failures, separate from frozen model behavior."""

from collections import defaultdict
import datetime as dt
import hashlib
import json

import httpx

from .evaluate import api_key, ledger
from .paths import DATA, MODEL, now, read, save

COUNT_FIELDS = {
    "model",
    "input",
    "instructions",
    "previous_response_id",
    "parallel_tool_calls",
    "personality",
    "reasoning",
    "text",
    "tool_choice",
    "tools",
    "truncation",
}
GENERATION_FIELDS = {
    "client_metadata",
    "include",
    "max_output_tokens",
    "prompt_cache_key",
    "service_tier",
    "store",
    "stream",
}
COUNT_URL = "https://api.openai.com/v1/responses/input_tokens"


def count_payload(request):
    """Reproduce immutable model input using the provider's documented counting fields."""
    if request.get("model") != MODEL or request.get("service_tier") != "default":
        raise ValueError("Unknown model or service rate")
    if set(request) - COUNT_FIELDS - GENERATION_FIELDS:
        raise ValueError(
            "An unknown or mutable input parameter prevents reconciliation"
        )
    return {key: value for key, value in request.items() if key in COUNT_FIELDS}


def bound_nanodollars(input_tokens, output_limit):
    """Apply the maximum Luna rates to all certified inputs and every permitted output."""
    if type(input_tokens) is not int or not 0 < input_tokens <= 1_050_000:
        raise ValueError("Unusable input count")
    if type(output_limit) is not int or not 0 < output_limit <= 4096:
        raise ValueError("Unusable output limit")
    # $0.25/M input and $0.75/M output at the maximum long-context premium.
    return input_tokens * 250 + output_limit * 750


def overloaded(event):
    """Recognize an explicit capacity rejection in either the HTTP or streaming protocol."""
    if event.get("event") == "upstream_error" and event.get("status") == 503:
        try:
            error = json.loads(event["message"]).get("error", {})
        except (ValueError, AttributeError):
            return False
    elif (
        event.get("event") == "stream"
        and event.get("body", {}).get("type") == "response.failed"
    ):
        error = event["body"].get("response", {}).get("error") or {}
    else:
        return False
    return isinstance(error, dict) and error.get("code") == "server_is_overloaded"


def reconcile(phase, minimum_age=600):
    """Retain a reservation for every unresolved call and save its provider-certified upper bound."""
    cutoff = (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=minimum_age)
    ).isoformat()
    book = ledger()
    with book.connect() as db:
        rows = db.execute(
            "select id,unit,usd from calls where phase=? and state='reserved' and usage='{}' and utc<?",
            (phase, cutoff),
        ).fetchall()
    units = defaultdict(dict)
    for key, unit, amount in rows:
        units[unit][key] = amount
    bounded = 0
    original_total = bound_total = 0
    # Counting existing inputs is free and does not submit a generation. Preserve previous_response_id.
    # https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens
    with httpx.Client(
        headers={"Authorization": "Bearer " + api_key()}, trust_env=False, timeout=35
    ) as client:
        for unit, outstanding in units.items():
            for path in sorted((DATA / "logs" / phase).glob(unit + "-20*.jsonl")):
                with path.open("rb") as log:
                    for line in log:
                        if b'"event": "request"' not in line:
                            continue
                        item = json.loads(line)
                        key = item.get("request_id")
                        if key not in outstanding:
                            continue
                        req = item["body"]
                        certificate = DATA / "billing-certificates" / (key + ".json")
                        digest = hashlib.sha256(
                            json.dumps(req, sort_keys=True, ensure_ascii=False).encode()
                        ).hexdigest()
                        try:
                            if certificate.is_file():
                                cert = read(certificate)
                                if cert["request_sha256"] != digest:
                                    raise ValueError("Recorded request changed")
                            else:
                                counted = client.post(
                                    COUNT_URL, json=count_payload(req)
                                )
                                counted.raise_for_status()
                                result = counted.json()
                                if result.get("object") != "response.input_tokens":
                                    raise ValueError(
                                        "Unrecognized input token certificate"
                                    )
                                bound = bound_nanodollars(
                                    result["input_tokens"], req["max_output_tokens"]
                                )
                                cert = dict(
                                    utc=now(),
                                    phase=phase,
                                    unit=unit,
                                    request_id=key,
                                    request_sha256=digest,
                                    provider=COUNT_URL,
                                    original_nanodollars=outstanding[key],
                                    input_tokens=result["input_tokens"],
                                    output_limit=req["max_output_tokens"],
                                    bound_nanodollars=bound,
                                    count_request_id=counted.headers.get(
                                        "x-request-id"
                                    ),
                                )
                                save(certificate, cert)
                            upper = min(
                                cert["original_nanodollars"], cert["bound_nanodollars"]
                            )
                            # Retaining 'reserved' allows a later authoritative usage record to settle normally.
                            with book.connect() as db:
                                db.execute("begin immediate")
                                changed = db.execute(
                                    "update calls set usd=?,usage=? where id=? and state='reserved' and usage='{}' and usd>=?",
                                    (
                                        upper,
                                        json.dumps({"certified_reservation": cert}),
                                        key,
                                        upper,
                                    ),
                                ).rowcount
                            if changed:
                                bounded += 1
                                original_total += outstanding[key]
                                bound_total += upper
                        except (ValueError, httpx.HTTPError) as err:
                            print(
                                now(),
                                unit,
                                "original reservation retained",
                                type(err).__name__,
                                flush=True,
                            )
                        outstanding.pop(key, None)
    summary = dict(
        phase=phase,
        eligible=len(rows),
        certified=bounded,
        original_upper_usd=original_total / 1e9,
        certified_upper_usd=bound_total / 1e9,
    )
    print(now(), json.dumps(summary), flush=True)
    return summary
