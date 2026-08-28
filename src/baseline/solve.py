"""Baseline solution — deliberately simple reference implementation.

FROZEN after its first green evaluation run (CLAUDE.md CN-3). Do not edit, do not
refactor, do not share code with src/advanced/. Every reported improvement is measured
against this file exactly as it stands.

One direct prompt with basic instructions (docs/PLAN.md §4): a single pinned-model call
carrying the requisition text plus a naive register lookup — rows whose Organisation
Name contains one of the posting's header-line name candidates, case-insensitively,
capped at 20, or the literal line NO ROWS MATCHED. That is the honest automation of the
manual process (read the header, Ctrl-F the CSV); a small stopword list keeps job-title
and location segments out of the search because a person searches the employer's name,
not the words "Software Engineer" or "London". The lookup's blindness to trading names,
routes, ratings and negations is the measured failure surface, not a defect. No retries,
no tools, no verification, no second pass.
"""

from __future__ import annotations

import csv
import functools
import gzip
import io
import json
from pathlib import Path
from typing import Any, Sequence, cast

import anthropic

MODEL_ID = "claude-sonnet-4-6"
TEMPERATURE = 0.0
MAX_TOKENS = 2000
MAX_REGISTER_ROWS = 20
NO_MATCH = "NO ROWS MATCHED"
HEADER_LINES = 6

_FIXTURES = (
    Path(__file__).resolve().parent.parent.parent / "eval" / "cases" / "fixtures"
)

FLOOR: dict[str, Any] = json.loads((_FIXTURES / "floor_config.json").read_text())
SNAPSHOT_DATE: str = sorted(_FIXTURES.glob("sponsor-register-*.csv.gz"))[-1].name[
    len("sponsor-register-") : -len(".csv.gz")
]

_SPLIT_TOKENS = ("·", "—", "›", "|", ",")
# Words a person scanning a posting header reads as job title / location / page chrome,
# not as the employer's name. A candidate whose every token is in this list is skipped.
_NOISE_TOKENS = frozenset(
    """software engineer engineers developer development backend frontend full-stack
    platform devops data machine learning ml sre site reliability graduate junior
    senior associate founding contract early careers london manchester glasgow bristol
    leeds cambridge edinburgh bath reading brighton uk hybrid remote full-time
    part-time entry mid-senior mid level posted days ago applicants apply on the a an
    engineering""".split()
)


def candidate_strings(text: str) -> list[str]:
    """Employer-name candidates from the posting's header lines, in reading order."""
    candidates: list[str] = []
    lines = [line for line in text.splitlines() if line.strip()][:HEADER_LINES]
    for line in lines:
        segments = [line]
        for token in _SPLIT_TOKENS:
            segments = [part for seg in segments for part in seg.split(token)]
        segments = [part for seg in segments for part in seg.split(" at ")]
        for seg in segments:
            s = seg.strip().strip(".()[]")
            if not (1 < len(s) < 60 and any(c.isalpha() for c in s)):
                continue
            tokens = {t.strip(".,()£0123456789") for t in s.casefold().split()}
            if tokens <= _NOISE_TOKENS:
                continue
            if s not in candidates:
                candidates.append(s)
    return candidates


@functools.lru_cache(maxsize=1)
def _register() -> tuple[tuple[str, str], ...]:
    path = sorted(_FIXTURES.glob("sponsor-register-*.csv.gz"))[-1]
    text = gzip.decompress(path.read_bytes()).decode("utf-8-sig")
    rows: list[tuple[str, str]] = []
    for r in csv.DictReader(io.StringIO(text)):
        line = ",".join(
            [
                r["Organisation Name"],
                r["Town/City"],
                r["County"],
                r["Type & Rating"],
                r["Route"],
            ]
        )
        rows.append((r["Organisation Name"].casefold(), line))
    return tuple(rows)


def register_context(candidates: Sequence[str]) -> str:
    """Naive lookup: first candidate with case-insensitive substring hits wins."""
    for candidate in candidates:
        needle = candidate.casefold().strip()
        if not needle:
            continue
        hits = [line for name, line in _register() if needle in name]
        if hits:
            return "\n".join(hits[:MAX_REGISTER_ROWS])
    return NO_MATCH


def build_prompt(requisition_text: str, register_excerpt: str) -> tuple[str, str]:
    general = int(FLOOR["general_threshold_gbp"]["amount"])
    going = int(FLOOR["going_rate_gbp"]["amount"])
    system = f"""You assess whether a UK job requisition can lead to a Skilled Worker \
Certificate of Sponsorship for an early-career software engineer (SOC 2134, \
new-entrant basis). Four checks decide it:

1. "register": the employer appears on the Home Office sponsor register. You are given \
the register rows a name search found for this posting, or the line {NO_MATCH}.
2. "route": the employer's register rows cover the Skilled Worker route specifically.
3. "willingness": the posting itself is willing to sponsor this role.
4. "salary": the advertised salary must clear BOTH the general threshold (£{general:,}) \
AND the SOC 2134 new-entrant going rate (£{going:,}) — the higher of the two applies. \
Only guaranteed basic gross annual pay counts; bonuses, profit share, equity, options, \
allowances and overtime do not.

Each check gets a "status": "pass", "fail" or "indeterminate", and a short "reason" \
from: register: legal_name_exact|trading_name_stated|alias_lookup|no_match|\
ambiguous_group; route: skilled_worker|gbm_only|other_routes_only|rating_blocks_cos|\
no_entity; willingness: offered|refused|silent|boilerplate_ambiguous; salary: \
above_floor|below_general_threshold|below_going_rate|straddles_floor|absent|\
non_annual_unclear.

Verdict rules: any failed check means "NOT_SPONSORABLE"; all four passing means \
"SPONSORABLE"; otherwise "UNVERIFIABLE".

The register snapshot is dated {SNAPSHOT_DATE}.

Reply with ONLY one JSON object, no other text, in exactly this shape:
{{"verdict": "...", "determining_fact": "one sentence", "checks": {{"register": \
{{"status": "...", "reason": "...", "evidence": {{"quote": "verbatim from the posting \
(optional)", "register_row": {{"organisation_name": "...", "town_city": "...", \
"type_rating": "...", "route": "..."}}}}}}, "route": {{...}}, "willingness": {{...}}, \
"salary": {{...}}}}, "uncertainty": "what could not be established", \
"register_snapshot_date": "{SNAPSHOT_DATE}"}}

Evidence quotes must be verbatim substrings of the posting; cited register rows must be \
copied exactly from the rows you were given."""
    user = (
        f"Requisition (as pasted):\n{requisition_text}\n\n"
        f"Register lookup result (naive name search):\n{register_excerpt}"
    )
    return system, user


def parse_response(reply: str) -> dict[str, Any]:
    start, end = reply.find("{"), reply.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("baseline: model reply contains no JSON object")
    try:
        parsed = json.loads(reply[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"baseline: model reply is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("baseline: model reply is not a JSON object")
    return cast(dict[str, Any], parsed)


def solve(payload: dict[str, Any], *, seed: int = 42) -> dict[str, Any]:
    """One direct prompt. `seed` is unused: the API exposes no sampling seed, so
    determinism comes from TEMPERATURE=0.0 and the pinned MODEL_ID (C-6)."""
    text = str(payload["requisition_text"])
    system, user = build_prompt(text, register_context(candidate_strings(text)))
    client = anthropic.Anthropic()
    # anthropic 1.2.0 removed sampling params from the typed signature (newest models
    # reject them); the API still accepts temperature on this model, so the C-6 pin
    # goes through extra_body — a wrong model/param combination fails with a 400
    # rather than silently sampling at the default temperature.
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
        extra_body={"temperature": TEMPERATURE},
    )
    reply = "".join(b.text for b in response.content if b.type == "text")
    result = parse_response(reply)
    result["_usage"] = {
        "model": MODEL_ID,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return result
