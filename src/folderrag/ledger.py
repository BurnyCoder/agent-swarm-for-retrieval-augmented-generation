"""Transactional cost and token limits shared by processes, investigators and coordinator."""

import json
import math
import sqlite3
import uuid
from pathlib import Path

from .paths import now


class Limit(RuntimeError):
    """The request cannot be admitted under the registered limits."""


class PendingFunds(Limit):
    """Outstanding requests temporarily occupy the remaining phase allocation."""


class Ledger:
    def __init__(self, path, limits):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.limits = limits
        with self.connect() as db:
            db.execute("""create table if not exists calls
                (id text primary key, phase text, unit text, agent text, usd integer,
                 tokens integer, state text, utc text, usage text)""")
            db.execute("create index if not exists ix_calls_unit on calls(unit)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=60)

    def reserve(self, phase, unit, agent, amount, tokens, agent_cap=32):
        with self.connect() as db:
            db.execute("begin immediate")
            used, pending = db.execute(
                "select coalesce(sum(usd),0),coalesce(sum(case when state='reserved' "
                "then usd else 0 end),0) from calls where phase=?",
                (phase,),
            ).fetchone()
            reserve = math.ceil(amount * 1e9)
            if used + reserve > round(self.limits[phase] * 1e9):
                if pending and used - pending + reserve <= round(
                    self.limits[phase] * 1e9
                ):
                    raise PendingFunds("phase budget")
                raise Limit("phase budget")
            n, out = db.execute(
                "select count(*),coalesce(sum(tokens),0) from calls where unit=? and state!='rejected'",
                (unit,),
            ).fetchone()
            own = db.execute(
                "select count(*) from calls where unit=? and agent=? and state!='rejected'",
                (unit, agent),
            ).fetchone()[0]
            if n >= 32 or own >= agent_cap or out + tokens > 48000:
                raise Limit("question or investigator budget")
            key = uuid.uuid4().hex
            db.execute(
                "insert into calls values(?,?,?,?,?,?,?,?,?)",
                (key, phase, unit, agent, reserve, tokens, "reserved", now(), "{}"),
            )
            return key

    def settle(self, key, amount, tokens, usage, state="settled"):
        with self.connect() as db:
            db.execute("begin immediate")
            row = db.execute(
                "select usd,state from calls where id=?", (key,)
            ).fetchone()
            charge = math.ceil(amount * 1e9)
            if not row or row[1] != "reserved" or charge > row[0]:
                raise RuntimeError("Unrecognized or exceeded billing reservation")
            db.execute(
                "update calls set usd=?,tokens=?,state=?,usage=? where id=?",
                (charge, tokens, state, json.dumps(usage), key),
            )

    def totals(self):
        with self.connect() as db:
            return {
                p: v / 1e9
                for p, v in db.execute(
                    "select phase,sum(usd) from calls group by phase"
                )
            }

    def unit(self, unit):
        with self.connect() as db:
            c, usd, t = db.execute(
                "select count(*),coalesce(sum(usd),0),coalesce(sum(tokens),0) from calls where unit=?",
                (unit,),
            ).fetchone()
            return {"requests": c, "cost_upper_usd": usd / 1e9, "output_tokens": t}


def charge(usage):
    """Upper charge uses the cache-write rate when the service gives no write breakdown."""
    inp = usage["input_tokens"]
    out = usage["output_tokens"]
    cached = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0)
    long = inp > 272000
    return (
        (inp - cached) * 0.125 * (2 if long else 1)
        + cached * 0.01 * (2 if long else 1)
        + out * 0.50 * (1.5 if long else 1)
    ) / 1e6
