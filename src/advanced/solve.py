"""Advanced solution: Extract -> Resolve -> Decide, wired end to end.

One model call extracts typed claims from the posting (extract.py); everything after
it is deterministic — entity resolution against the full register with the alias
fixtures (resolve.py), then the rules engine reading floor_config (rules.py), then
the pure combinator, with the mechanical verifier (verify.py) gating every
model-sourced quote before the combinator runs. Code decides, the model extracts;
unverified evidence can only move a verdict toward UNVERIFIABLE.

Same pinned model and temperature as the frozen baseline (fairness statement,
docs/PLAN.md §4); identical inputs — requisition text, committed register snapshot,
committed floor_config.
"""

from __future__ import annotations

import csv
import functools
import gzip
import io
import json
from pathlib import Path
from typing import Any

import anthropic

from src.advanced.extract import (
    ExtractedClaims,
    build_extraction_prompt,
    parse_claims,
)
from src.advanced.resolve import (
    Ambiguous,
    Match,
    RegisterRow,
    Resolution,
    resolve_entity,
)
from src.advanced.rules import (
    CHECK_NAMES,
    SKILLED_WORKER,
    CheckOutcome,
    combine,
    salary_clears_floor,
    skilled_worker_route,
    willingness_check,
)
from src.advanced.verify import verify_and_downgrade

MODEL_ID = "claude-sonnet-4-6"
TEMPERATURE = 0.0
MAX_TOKENS = 1000

_FIXTURES = (
    Path(__file__).resolve().parent.parent.parent / "eval" / "cases" / "fixtures"
)

FLOOR: dict[str, Any] = json.loads((_FIXTURES / "floor_config.json").read_text())
ALIASES: dict[str, str] = json.loads((_FIXTURES / "aliases.json").read_text())[
    "aliases"
]
SNAPSHOT_DATE: str = sorted(_FIXTURES.glob("sponsor-register-*.csv.gz"))[-1].name[
    len("sponsor-register-") : -len(".csv.gz")
]


@functools.lru_cache(maxsize=1)
def register_rows() -> tuple[RegisterRow, ...]:
    path = sorted(_FIXTURES.glob("sponsor-register-*.csv.gz"))[-1]
    text = gzip.decompress(path.read_bytes()).decode("utf-8-sig")
    return tuple(
        RegisterRow(
            r["Organisation Name"],
            r["Town/City"],
            r["County"],
            r["Type & Rating"],
            r["Route"],
        )
        for r in csv.DictReader(io.StringIO(text))
    )


def _row_evidence(row: RegisterRow) -> dict[str, str]:
    return {
        "organisation_name": row.organisation_name,
        "town_city": row.town_city,
        "type_rating": row.type_rating,
        "route": row.route,
    }


def _register_check(resolution: Resolution) -> tuple[CheckOutcome, dict[str, Any]]:
    if isinstance(resolution, Match):
        return (
            CheckOutcome("pass", "legal_name_exact"),
            {"register_row": _row_evidence(resolution.rows[0])},
        )
    if isinstance(resolution, Ambiguous):
        return CheckOutcome("indeterminate", "ambiguous_group"), {}
    return CheckOutcome("fail", "no_match"), {}


def _route_check(resolution: Resolution) -> tuple[CheckOutcome, dict[str, Any]]:
    if not isinstance(resolution, Match):
        return CheckOutcome("indeterminate", "no_entity"), {}
    outcome = skilled_worker_route(tuple(r.route for r in resolution.rows))
    cited = next(
        (r for r in resolution.rows if r.route == SKILLED_WORKER),
        resolution.rows[0],
    )
    return outcome, {"register_row": _row_evidence(cited)}


_DETERMINING = {
    "register": "the employer could not be confirmed on the sponsor register",
    "route": "the employer's licence does not cover the Skilled Worker route",
    "willingness": "the posting rules out sponsorship for this role",
    "salary": "the advertised basic pay does not clear the applicable salary floor",
}


def assemble(
    claims: ExtractedClaims,
    resolution: Resolution,
    floor_config: dict[str, Any],
    snapshot_date: str,
    requisition_text: str,
) -> dict[str, Any]:
    """Pure assembly of the output contract from typed stage results.

    Model-sourced quotes pass the mechanical verifier before the combinator runs:
    a quote that is not a verbatim substring of the posting downgrades its check to
    indeterminate and never appears as evidence — the verdict can only move toward
    UNVERIFIABLE, never toward confidence (docs/PLAN.md §5)."""
    register_outcome, register_ev = _register_check(resolution)
    route_outcome, route_ev = _route_check(resolution)
    willingness_outcome = willingness_check(claims.stance.stance)
    salary_outcome = salary_clears_floor(
        claims.salary.basic_annual_min_gbp,
        claims.salary.basic_annual_max_gbp,
        floor_config,
    )
    outcomes = {
        "register": register_outcome,
        "route": route_outcome,
        "willingness": willingness_outcome,
        "salary": salary_outcome,
    }
    quotes: dict[str, str | None] = {"willingness": claims.stance.quote}
    verified = verify_and_downgrade(outcomes, quotes, requisition_text)
    downgraded = {n for n in outcomes if verified[n] != outcomes[n]}
    outcomes = verified
    verdict = combine(outcomes)

    checks: dict[str, Any] = {}
    for name in CHECK_NAMES:
        entry: dict[str, Any] = {
            "status": outcomes[name].status,
            "reason": outcomes[name].reason,
        }
        evidence: dict[str, Any] = {}
        if name == "register":
            evidence.update(register_ev)
        if name == "route":
            evidence.update(route_ev)
        if name == "willingness" and claims.stance.quote and name not in downgraded:
            evidence["quote"] = claims.stance.quote
        if evidence:
            entry["evidence"] = evidence
        checks[name] = entry

    failed = [n for n in CHECK_NAMES if outcomes[n].status == "fail"]
    unresolved = [n for n in CHECK_NAMES if outcomes[n].status == "indeterminate"]
    if verdict == "NOT_SPONSORABLE":
        determining = f"Not sponsorable because {_DETERMINING[failed[0]]}."
    elif verdict == "SPONSORABLE":
        determining = (
            "All four checks pass against the register snapshot and floor config."
        )
    else:
        determining = (
            "Cannot be verified because the following could not be established: "
            + ", ".join(unresolved)
            + "."
        )

    uncertainty_bits = [f"{n}: {outcomes[n].reason}" for n in unresolved]
    if claims.salary.note:
        uncertainty_bits.append(f"salary as stated: {claims.salary.note}")
    # The B-rating sub-check is cut by scope ruling (2026-08-29): the rating never
    # changes a verdict here, but a non-A rating must not disappear into "nothing
    # unresolved" — a sponsor rated below A cannot issue a CoS until its action
    # plan completes.
    cited_rating = str(route_ev.get("register_row", {}).get("type_rating", ""))
    if cited_rating and "(A rating)" not in cited_rating:
        uncertainty_bits.append(
            f"licence rating not assessed: the register shows {cited_rating}; "
            "a sponsor rated below A cannot issue a Certificate of Sponsorship "
            "until its action plan completes"
        )
    uncertainty = (
        "; ".join(uncertainty_bits)
        if uncertainty_bits
        else "nothing material left unresolved"
    )

    return {
        "verdict": verdict,
        "determining_fact": determining,
        "checks": checks,
        "uncertainty": uncertainty,
        "register_snapshot_date": snapshot_date,
    }


def solve(payload: dict[str, Any], *, seed: int = 42) -> dict[str, Any]:
    """Extract (one model call) -> resolve -> rules -> assemble. `seed` is unused:
    determinism comes from TEMPERATURE=0.0 and the pinned MODEL_ID (C-6)."""
    text = str(payload["requisition_text"])
    system, user = build_extraction_prompt(text)
    client = anthropic.Anthropic()
    # anthropic 1.2.0 dropped sampling params from the typed signature; the API
    # accepts temperature on this model, so the C-6 pin goes through extra_body —
    # a wrong model/param combination fails with a 400, never silently samples.
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
        extra_body={"temperature": TEMPERATURE},
    )
    reply = "".join(b.text for b in response.content if b.type == "text")
    claims = parse_claims(reply)
    resolution = resolve_entity(claims.employer_strings, register_rows(), ALIASES)
    result = assemble(claims, resolution, FLOOR, SNAPSHOT_DATE, text)
    result["_usage"] = {
        "model": MODEL_ID,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return result
