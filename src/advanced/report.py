"""The user-facing verification report. Pure renderer — no LLM in the render path.

The report is a fixed instrument (DECISIONS.md 2026-08-28): the sentences are written
once, by a human, and sameness across requisitions is a feature for comparison. It
renders the solver's output dict against the posting text: verdict first with its
determining sentence, each check with its verbatim evidence (quotes carry character
offsets into the source; register rows are reproduced field for field), the snapshot
date with an explicit age warning, an uncertainty section that names what could not
be established and what the user would have to do to establish it, and a closing
advisory line. Targets End-to-End Quality; moves no eval metric (BP-4, stated in
CHANGELOG [6]).
"""

from __future__ import annotations

from typing import Any

_CHECK_LABELS = {
    "register": "Sponsor register",
    "route": "Visa route",
    "willingness": "Sponsorship for this role",
    "salary": "Salary floor",
}
_STATUS_LABELS = {"pass": "PASS", "fail": "FAIL", "indeterminate": "UNRESOLVED"}
_VERDICT_LABELS = {
    "SPONSORABLE": "SPONSORABLE",
    "NOT_SPONSORABLE": "NOT SPONSORABLE",
    "UNVERIFIABLE": "UNVERIFIABLE",
}

# What the user would have to do to establish each unresolved check (§5b item 4).
_ACTIONS = {
    ("willingness", "silent"): (
        "ask the employer whether they will sponsor this role before investing "
        "interview time — the posting does not say"
    ),
    ("willingness", "boilerplate_ambiguous"): (
        "ask the employer directly: the right-to-work wording neither offers nor "
        "refuses sponsorship, and sponsorship itself would confer that right"
    ),
    ("willingness", "evidence_unverified"): (
        "re-read the posting yourself — the quoted evidence for this check could "
        "not be verified against the text"
    ),
    ("salary", "absent"): (
        "ask for the guaranteed basic annual salary in writing; only that figure "
        "counts toward the floor"
    ),
    ("salary", "straddles_floor"): (
        "ask where in the advertised range a real offer would land — only a "
        "guaranteed figure at or above the floor clears it"
    ),
    ("salary", "non_annual_unclear"): (
        "ask for the annualised guaranteed basic salary; day rates and OTE do not "
        "count toward the floor"
    ),
    ("register", "ambiguous_group"): (
        "ask which legal entity would employ you and issue the Certificate of "
        "Sponsorship, then check that entity's register entry"
    ),
    ("register", "no_employer_stated"): (
        "identify the employing legal entity first — the posting names no "
        "employer, so there is nothing to check against the register"
    ),
    ("route", "no_entity"): (
        "resolve the employing legal entity first — the route can only be read "
        "from that entity's register rows"
    ),
}
_FALLBACK_ACTION = "check this point by hand against the register snapshot"


def _evidence_lines(
    check: dict[str, Any],
    requisition_text: str,
    snapshot_date: str,
    cited_rows: list[dict[str, Any]],
) -> list[str]:
    evidence = check.get("evidence")
    if not isinstance(evidence, dict):
        return []
    lines = []
    quote = evidence.get("quote")
    if isinstance(quote, str) and quote:
        start = requisition_text.find(quote)
        if start >= 0:
            lines.append(f'   Posting, chars {start}-{start + len(quote)}: "{quote}"')
        else:
            lines.append(f'   Quoted, not verified against the posting: "{quote}"')
    row = evidence.get("register_row")
    if isinstance(row, dict):
        if row in cited_rows:
            lines.append("   Register row: as cited under Sponsor register above.")
        else:
            cited_rows.append(row)
            fields = " · ".join(str(v) for v in row.values() if str(v))
            lines.append(f"   Register row (snapshot {snapshot_date}): {fields}")
    rows = evidence.get("register_rows")
    if isinstance(rows, list):
        for candidate_row in rows:
            if isinstance(candidate_row, dict):
                fields = " · ".join(str(v) for v in candidate_row.values() if str(v))
                lines.append(f"   Candidate row (snapshot {snapshot_date}): {fields}")
    routes_held = evidence.get("routes_held")
    if isinstance(routes_held, list) and routes_held:
        lines.append(
            f"   Entity holds {len(routes_held)} licence routes: "
            + ", ".join(str(r) for r in routes_held)
            + ". The row cited above is the one this verdict rests on."
        )
    return lines


def render_report(result: dict[str, Any], requisition_text: str) -> str:
    verdict = _VERDICT_LABELS[str(result["verdict"])]
    snapshot_date = str(result["register_snapshot_date"])
    checks: dict[str, Any] = result["checks"]

    lines = [f"VERDICT: {verdict}", f"Why: {result['determining_fact']}", ""]

    lines.append("The four checks")
    cited_rows: list[dict[str, Any]] = []
    for i, name in enumerate(_CHECK_LABELS, start=1):
        check = checks[name]
        status = _STATUS_LABELS[str(check["status"])]
        lines.append(f"{i}. {_CHECK_LABELS[name]} — {status}")
        lines.extend(
            _evidence_lines(check, requisition_text, snapshot_date, cited_rows)
        )
    lines.append("")

    lines.append(
        f"Register snapshot dated {snapshot_date}. Sponsor licences are revoked and "
        "suspended continuously; this verdict is only as fresh as that snapshot."
    )
    lines.append("")

    unresolved = [
        (name, str(checks[name].get("reason", "")))
        for name in _CHECK_LABELS
        if checks[name]["status"] == "indeterminate"
    ]
    # Disclosures the solver recorded beyond the per-check statuses (salary as
    # stated, licence rating). Dropping these here is how a report ends up claiming
    # completeness the JSON contradicts (review fix 2026-08-29).
    notes = [str(n) for n in result.get("uncertainty_notes", [])]
    if unresolved or notes:
        lines.append("Could not be established:")
        for name, reason in unresolved:
            action = _ACTIONS.get((name, reason), _FALLBACK_ACTION)
            lines.append(f"- {_CHECK_LABELS[name]}. To resolve: {action}.")
        for note in notes:
            cleaned = note.rstrip().rstrip(".")
            lines.append(f"- {cleaned[0].upper()}{cleaned[1:]}.")
    else:
        lines.append("Nothing material was left unresolved.")
    lines.append("")

    lines.append(
        "This report is advisory. The evidence above is checkable; whether to "
        "apply is your decision."
    )
    return "\n".join(lines)
