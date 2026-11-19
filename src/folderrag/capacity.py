"""Supervise frozen experiments through upstream overloads without changing their prompts or scorers."""

import json
import subprocess
import sys
import threading
import time
from email.utils import parsedate_to_datetime

import httpx

from .evaluate import api_key, ledger, measure, records
from .gateway import Trace
from .ledger import charge
from .paths import DATA, MODEL, now, read, save
from .recovery import COUNT_URL, bound_nanodollars, count_payload, overloaded, reconcile


def operation(action, state, **details):
    """Expose the current incident locally and retain an append-only timestamped history."""
    event = dict(utc=now(), action=action, state=state, **details)
    save(DATA / "operations/capacity.json", event)
    with (DATA / "operations/capacity-history.jsonl").open("a", encoding="utf8") as log:
        log.write(json.dumps(event) + "\n")
    print(event["utc"], action, state, details, flush=True)


def retry_after(value):
    """Retry-After can specify seconds or an HTTP date under RFC 9110 section 10.2.3."""
    if not value:
        return 0
    try:
        return max(0, int(value))
    except ValueError:
        try:
            return max(
                0, int(parsedate_to_datetime(value).timestamp() - time.time()) + 1
            )
        except (ValueError, TypeError, OverflowError):
            return 0


def probe():
    """One small, metered Luna inference tests capacity. Certified bounds cover missing usage."""
    stamp = now().replace(":", "-")
    unit = "capacity-probe-" + stamp
    trace = Trace(DATA / "logs/retry" / (unit + "-" + stamp + ".jsonl"))
    payload = dict(
        model=MODEL,
        input="Reply with OK.",
        reasoning={"effort": "medium"},
        max_output_tokens=128,
        store=False,
        service_tier="default",
    )
    with httpx.Client(
        headers={"Authorization": "Bearer " + api_key()}, trust_env=False, timeout=35
    ) as client:
        try:
            count = client.post(COUNT_URL, json=count_payload(payload))
        except httpx.TransportError:
            return False, 0
        if count.status_code in (429, 500, 502, 503, 504):
            return False, retry_after(count.headers.get("retry-after"))
        count.raise_for_status()
        bound = bound_nanodollars(
            count.json()["input_tokens"], payload["max_output_tokens"]
        )
        book = ledger()
        key = book.reserve("retry", unit, "capacity-probe", bound / 1e9, 128, 1)
        trace.log("request", agent="capacity-probe", request_id=key, body=payload)
        try:
            response = client.post("https://api.openai.com/v1/responses", json=payload)
        except httpx.TransportError as err:
            trace.log("gateway_error", agent="capacity-probe", error=type(err).__name__)
            return False, 0
        if response.status_code != 200:
            trace.log(
                "upstream_error",
                agent="capacity-probe",
                status=response.status_code,
                message=response.text,
            )
            if response.status_code in (500, 502, 503, 504, 408):
                return False, retry_after(response.headers.get("retry-after"))
            if 400 <= response.status_code < 500:
                book.settle(key, 0, 0, {}, "rejected")
            error = response.json().get("error", {})
            if (
                response.status_code == 429
                and isinstance(error, dict)
                and error.get("code") in ("rate_limit_exceeded", "slow_down")
            ):
                return False, retry_after(response.headers.get("retry-after"))
            response.raise_for_status()
        message = response.json()
        trace.log("response", agent="capacity-probe", body=message)
        usage = message.get("usage")
        if usage:
            book.settle(key, charge(usage), usage["output_tokens"], usage)
        return bool(usage and message.get("status") in ("completed", "incomplete")), 0


def execute(action, arguments):
    """Stop scheduling on the first capacity error and bound the time for active jobs to drain."""
    command = [sys.executable, "-m", "folderrag.cli", *arguments]
    interrupted = False
    timer = None
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ) as process:
        for line in process.stdout:
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
            if interrupted or b"server_is_overloaded" not in line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if overloaded(event):
                import signal

                interrupted = True
                operation(action, "provider_overload", worker_pid=process.pid)
                process.send_signal(signal.SIGINT)
                timer = threading.Timer(20, process.terminate)
                timer.start()
        code = process.wait()
    if timer:
        timer.cancel()
    if code and not interrupted:
        raise subprocess.CalledProcessError(code, command)
    return not interrupted


def guard(action, workers, after_overload=False):
    """Use small fixed ramp steps after capacity returns, retaining the original ordered jobs."""
    backoff = 60
    recovering = after_overload
    while True:
        if recovering:
            while True:
                operation(action, "checking_capacity")
                ready, advised = probe()
                if ready:
                    break
                delay = max(backoff, advised)
                operation(action, "waiting_for_capacity", retry_seconds=delay)
                time.sleep(delay)
                backoff = min(backoff * 2, 900)
            for phase in {"test", "diagnostics", "retry"}:
                reconcile(phase)
        schedule = [(workers, None)]
        if recovering and action in ("test", "diagnostics"):
            schedule = [
                (w, n) for w, n in ((1, 4), (2, 10), (4, 18)) if w < workers
            ] + schedule
        for active, extra in schedule:
            if action in ("test", "diagnostics"):
                args = ["run", action, "--workers", str(active)]
                if extra:
                    args += ["--limit", str(len(records(action)) + extra)]
            else:
                args = [action]
            operation(action, "running", question_workers=active, ramp_jobs=extra)
            if not execute(action, args):
                operation(action, "cooldown", retry_seconds=backoff)
                time.sleep(backoff)
                backoff = min(backoff * 2, 900)
                recovering = True
                break
        else:
            operation(action, "finished")
            return


def unit_overloaded(row):
    """Only provider-emitted capacity events make a failed case eligible for a technical repeat."""
    for path in (DATA / "logs" / row["phase"]).glob(row["unit"] + "-20*.jsonl"):
        with path.open("rb") as log:
            for line in log:
                if b"server_is_overloaded" in line:
                    try:
                        if overloaded(json.loads(line)):
                            return True
                    except ValueError:
                        continue
    return False


def classify_failures():
    """Materialize operational eligibility without generating answers or consulting quality scores."""
    rows = sorted(
        (
            r
            for p in ("test", "diagnostics")
            for r in records(p)
            if r.get("error") and unit_overloaded(r)
        ),
        key=lambda r: (r["utc"], r["unit"]),
    )
    for row in rows:
        save(
            DATA / "capacity-flags" / (row["unit"] + ".json"),
            {k: row[k] for k in ("unit", "id", "domain", "arm", "phase", "utc")},
        )
    return rows


def repeat_failed_capacity_cases():
    """Keep first-attempt scores and run one reported technical repeat per eligible failure."""
    cases = read(DATA / "benchmark/cases.json")
    rows = classify_failures()
    for row in rows:
        unit = row["unit"] + "-capacity-repeat"
        try:
            result = measure("retry", cases[row["id"]], row["arm"], unit)
        except RuntimeError as error:
            if "budget" not in str(error).lower() and "quota" not in str(error).lower():
                raise
            operation("capacity-retries", "retry_allocation_stop", reason=str(error))
            return
        save(
            DATA / "capacity-repeats" / (row["unit"] + ".json"),
            dict(
                original=row["unit"],
                repeat=unit,
                domain=row["domain"],
                arm=row["arm"],
                phase=row["phase"],
                original_score=row["score"],
                repeated_score=result.get("score"),
                error=result.get("error"),
                utc=now(),
            ),
        )
