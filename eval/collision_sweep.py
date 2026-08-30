#!/usr/bin/env python3
"""Collision sweep: every case's designed employer strings vs the committed snapshot.

The fixture organisations are fictional names embedded in a real 142,988-row
register. This sweep proves, mechanically and without a model call, that each case
resolves the way its label says it does — "right for the labelled reason" — and
surfaces every place a designed string collides with real register content:

  A. Each case's fixture organisations resolve exact-uniquely to exactly their
     manifest rows. An exact-phase collision with a real organisation would turn
     a designed legal_name_exact into Ambiguous.
  B. Each alias key mapping into the case's fixture orgs resolves via alias_lookup
     to the designed entity. The alias pass runs LAST, so a token-subset hit on a
     real organisation would silently resolve the wrong entity first — the most
     dangerous collision class this sweep exists to catch.
  C. Each asserted-absent name resolves to NoMatch.
  D. Ambiguity cases: the shared token stem of the fixture orgs (the designed
     group name) is resolved and the candidate set is split fixture-vs-real
     against the manifest, with the count compared to the designed entity count.
  E. Dev cases only: the register status/reason actually recorded in a committed
     eval run is compared to the labelled expected.checks.register.

Holdout cases are processed mechanically; only counts and booleans are printed for
them, never strings, labels, or reasons. Reasons that need the posting's own
wording (trading_name_stated needs the posted primary string) are marked not
mechanically checkable here; the eval's check_accuracy/exact_match cover them.

Usage:
    python eval/collision_sweep.py \
        --results eval/results/20260829-210352.json \
        --out eval/results/collision-sweep-2026-08-30.md
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.advanced.normalize import token_set  # noqa: E402
from src.advanced.resolve import (  # noqa: E402
    Ambiguous,
    Match,
    NoMatch,
    RegisterRow,
    resolve_entity,
)

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "eval" / "cases"
FIXTURES = CASES_DIR / "fixtures"
SNAPSHOT = FIXTURES / "sponsor-register-2026-08-28.csv.gz"


def load_rows(path: Path) -> tuple[RegisterRow, ...]:
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


def manifest_rows_by_org(manifest: dict[str, Any]) -> dict[str, list[RegisterRow]]:
    by_org: dict[str, list[RegisterRow]] = {}
    for r in manifest["rows"]:
        by_org.setdefault(r["organisation_name"], []).append(
            RegisterRow(
                r["organisation_name"],
                r["town_city"],
                r["county"],
                r["type_rating"],
                r["route"],
            )
        )
    return by_org


def group_stem(orgs: list[str]) -> str:
    """The designed group name: tokens shared by every fixture org in the case."""
    shared = set.intersection(*(set(token_set(o)) for o in orgs)) if orgs else set()
    return " ".join(sorted(shared))


def recorded_register(results: dict[str, Any], case_id: str) -> dict[str, Any] | None:
    for run in results.get("runs", []):
        if run["variant"] != "advanced":
            continue
        for c in run["cases"]:
            if c["case_id"] == case_id:
                reg = c["output"].get("checks", {}).get("register", {})
                return {"status": reg.get("status"), "reason": reg.get("reason")}
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = load_rows(SNAPSHOT)
    aliases: dict[str, str] = json.loads((FIXTURES / "aliases.json").read_text())[
        "aliases"
    ]
    manifest = json.loads((FIXTURES / "register_fixture_rows.json").read_text())
    fixture_rows = manifest_rows_by_org(manifest)
    fixture_orgs_all = set(fixture_rows)
    results = json.loads(args.results.read_text())

    lines: list[str] = [
        "# Collision sweep — designed employer strings vs the committed snapshot",
        "",
        f"Snapshot: `{SNAPSHOT.name}` ({len(rows)} rows). "
        f"Recorded-path column (dev only): `{args.results.name}`. "
        "Mechanical throughout — no model call. Holdout cases: counts and "
        "booleans only.",
        "",
    ]
    findings: list[str] = []

    for f in sorted(CASES_DIR.glob("case-*.json")):
        case = json.loads(f.read_text())
        cid, split = case["id"], case["meta"]["split"]
        dev = split == "dev"
        orgs: list[str] = case["meta"]["register_fixture_orgs"]
        absent: list[str] = case["meta"].get("asserted_absent_names", [])
        keys = [k for k, v in aliases.items() if v in orgs]
        expected_reg = case["expected"]["checks"]["register"]
        parts: list[str] = []

        ok_orgs = 0
        for org in orgs:
            r = resolve_entity((org,), rows, aliases)
            exact_self = (
                isinstance(r, Match)
                and r.via == "legal_name_exact"
                and r.organisation_name == org
                and sorted(map(str, r.rows)) == sorted(map(str, fixture_rows[org]))
            )
            if exact_self:
                ok_orgs += 1
            else:
                findings.append(
                    f"{cid}: fixture org does not resolve exact-uniquely to its "
                    f"manifest rows"
                    + (f" — {org!r} -> {type(r).__name__}" if dev else "")
                )
        parts.append(f"orgs {ok_orgs}/{len(orgs)} exact-self")

        ok_keys = 0
        for key in keys:
            r = resolve_entity((key,), rows, aliases)
            via_alias = (
                isinstance(r, Match)
                and r.via == "alias_lookup"
                and r.organisation_name == aliases[key]
            )
            if via_alias:
                ok_keys += 1
            else:
                via = r.via if isinstance(r, Match) else type(r).__name__
                findings.append(
                    f"{cid}: alias key resolved by an earlier phase or wrongly"
                    + (f" — {key!r} -> {via}" if dev else f" ({via})")
                )
        if keys:
            parts.append(f"aliases {ok_keys}/{len(keys)} alias_lookup")

        ok_absent = 0
        for name in absent:
            r = resolve_entity((name,), rows, aliases)
            if isinstance(r, NoMatch):
                ok_absent += 1
            else:
                findings.append(
                    f"{cid}: asserted-absent name matched the register"
                    + (f" — {name!r} -> {type(r).__name__}" if dev else "")
                )
        if absent:
            parts.append(f"absent {ok_absent}/{len(absent)} NoMatch")

        if expected_reg.get("reason") == "ambiguous_group" and len(orgs) > 1:
            stem = group_stem(orgs)
            r = resolve_entity((stem,), rows, aliases)
            if isinstance(r, Ambiguous):
                names = set(r.organisation_names)
                n_fix = len(names & fixture_orgs_all)
                n_real = len(names - fixture_orgs_all)
                parts.append(
                    f"group-stem -> Ambiguous {len(names)} orgs "
                    f"({n_fix} fixture + {n_real} real; designed {len(orgs)})"
                )
                if n_real:
                    findings.append(
                        f"{cid}: designed {len(orgs)}-entity ambiguity actually "
                        f"surfaces {len(names)} candidates — {n_real} real register "
                        f"organisation{'s' if n_real != 1 else ''} share"
                        f"{'' if n_real != 1 else 's'} the group stem"
                        + (f" {stem!r}" if dev else "")
                    )
            else:
                parts.append(f"group-stem -> {type(r).__name__}")
                findings.append(
                    f"{cid}: designed group stem did not resolve Ambiguous"
                    + (f" — {stem!r} -> {type(r).__name__}" if dev else "")
                )

        if dev:
            rec = recorded_register(results, cid)
            label = f"{expected_reg['status']}/{expected_reg.get('reason')}"
            if rec is None:
                parts.append(f"label {label}; recorded: none")
            else:
                match = rec["status"] == expected_reg["status"] and rec[
                    "reason"
                ] == expected_reg.get("reason")
                parts.append(
                    f"label {label}; recorded "
                    + ("MATCH" if match else f"{rec['status']}/{rec['reason']} DIFF")
                )
                if not match:
                    findings.append(
                        f"{cid}: recorded register path differs from label — "
                        f"labelled {label}, recorded {rec['status']}/{rec['reason']}"
                    )
        else:
            reason = str(expected_reg.get("reason"))
            mechanical = {"legal_name_exact", "alias_lookup", "no_match_confirmed"}
            checkable = reason in mechanical or bool(absent) or len(orgs) > 1
            parts.append(
                "label-consistent: "
                + (
                    str(not any(x.startswith(cid) for x in findings))
                    if checkable
                    else "final-run-only"
                )
            )
        lines.append(f"- `{cid}` ({split}): " + " · ".join(parts))

    lines.append("")
    if findings:
        lines.append(f"## Findings ({len(findings)})")
        lines.extend(f"- {x}" for x in findings)
    else:
        lines.append("## Findings: none — every case resolves for its labelled reason")
    report = "\n".join(lines) + "\n"
    args.out.write_text(report)
    print(report)
    print(f"written: {args.out}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
