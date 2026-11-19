"""Track the exact text exposed to an agent. Entailment is a separate evaluation."""

import json
import re
import string
import threading


class Evidence:
    def __init__(self):
        self.spans = {}
        self.returned_files = set()
        self.shell_outputs = []
        self.lock = threading.RLock()

    def deliver(self, spans):
        with self.lock:
            for span in spans:
                self.spans[span["id"]] = span
                self.returned_files.add(span["path"])
        return spans

    def see_shell(self, text):
        with self.lock:
            self.shell_outputs.append(text)
            self.returned_files.update(
                re.findall(r"corpus://folder/([^#\s]+)#L\d+", text)
            )


def validate(citations, evidence, root=None):
    """A quote must match a delivered span or literal shell output plus the actual file."""
    results = []
    for cite in citations:
        quote = cite.get("quote", "").strip()
        path = cite.get("path", "").removeprefix("/work/").removeprefix("./")
        key = cite.get("span_id", "")
        matches = [
            s
            for s in evidence.spans.values()
            if s["path"] == path
            and (not key or s["id"] == key)
            and quote
            and quote in s["text"]
        ]
        verified = matches[0] if matches else None
        legacy = re.fullmatch(r"corpus://folder/(.+)#L(\d+)(?:-(\d+))?", key)
        if (
            not verified
            and (not key or (legacy and legacy[1] == path))
            and root
            and quote
            and any(quote in t for t in evidence.shell_outputs)
        ):
            p = (root / path).resolve()
            if p.is_relative_to(root.resolve()) and p.is_file():
                text = p.read_text(encoding="utf8")
                if legacy:
                    lines = text.splitlines(keepends=True)
                    start = sum(map(len, lines[: int(legacy[2]) - 1]))
                    end = sum(map(len, lines[: int(legacy[3] or legacy[2])]))
                    offset = text.find(quote, start, end)
                else:
                    offset = text.find(quote)
                if offset >= 0:
                    verified = {
                        "start": offset,
                        "text": quote,
                        "line": text.count("\n", 0, offset) + 1,
                    }
        offset = verified["start"] + verified["text"].index(quote) if verified else None
        line = (
            verified["line"]
            + verified["text"][: verified["text"].index(quote)].count("\n")
            if verified
            else None
        )
        results.append(
            {
                **cite,
                "path": path,
                "valid": bool(verified),
                "offset": offset,
                "line": line,
            }
        )
    return results


def exact_match(answer, reference):
    def norm(value):
        value = str(value).lower().translate(str.maketrans("", "", string.punctuation))
        return " ".join(re.sub(r"\b(a|an|the)\b", " ", value).split())

    return bool(norm(answer)) and norm(answer) == norm(reference)


def parse_answer(text):
    """Accept an object even when an upstream tool returned a surrounding Markdown fence."""
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text or ""):
        try:
            result, _ = decoder.raw_decode(text[match.start() :])
        except ValueError:
            continue
        if (
            isinstance(result, dict)
            and type(result.get("answer")) in (str, int, float, bool)
            and isinstance(result.get("citations"), list)
        ):
            return {
                "answer": str(result["answer"]),
                "explanation": str(result.get("explanation", "")),
                "citations": [
                    c
                    for c in result["citations"]
                    if isinstance(c, dict)
                    and all(
                        isinstance(c.get(k, ""), str)
                        for k in ("claim", "path", "quote", "span_id")
                    )
                ],
            }
    raise ValueError("No well-formed answer object returned")
