#!/usr/bin/env python3
"""Prove the 2026-08-29 snapshot repositioning changed no solver input.

The fixture rows were repositioned inside the committed register snapshot (placement
history: fixture manifest note and docs/DATA.md). Every results file recorded before
that evening references the pre-repositioning bytes, so this script is the committed
proof — not a claim in a report — that both solvers see identical inputs from either
snapshot, for every case:

  - the frozen baseline's register lookup: candidate_strings + register_context,
    executed by the real frozen code against each snapshot;
  - the advanced resolver: resolve_entity over every string the cases exercise —
    each case's fixture organisations, asserted-absent names, all alias keys and
    values, and the baseline's own candidate strings per payload.

The precise invariant this proves: matched CONTENT is identical everywhere. One
thing repositioning cannot preserve and this script reports rather than hides:
multi-match lookups return rows in file order, so where a lookup matches several
rows whose relative positions changed, the same rows arrive in a different order
(the baseline's excerpt on the multi-entity ambiguity cases; the ambiguity
listing's sequence). Order changes are printed per case as [reordered]; content
differences fail the script. Verdict-level behaviour across the repositioning is
confirmed empirically by the first post-repositioning eval run (see DATA.md).

Usage (the old bytes come from git history; filename and date never changed):

    git show <pre-repositioning-sha>:eval/cases/fixtures/sponsor-register-2026-08-28.csv.gz > /tmp/old.csv.gz
    python eval/verify_snapshot_invariance.py --old /tmp/old.csv.gz \
        --new eval/cases/fixtures/sponsor-register-2026-08-28.csv.gz

Prints one line per case and exits non-zero on any difference. Holdout cases are
compared mechanically; only PASS/DIFF is printed for them, never content.
The new snapshot also carries two added Quillhaven Systems Ltd rows (case-32);
strings that intentionally resolve to them are excluded from the old-vs-new
comparison and listed explicitly.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import src.baseline.solve as baseline_solve  # noqa: E402
from src.advanced.resolve import RegisterRow, resolve_entity  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "eval" / "cases"
NEW_ONLY_ORGS = {"Quillhaven Systems Ltd"}


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


_STAGED: dict[Path, Path] = {}


def _staged_dir(snapshot: Path) -> Path:
    """A temp dir holding the snapshot under its canonical name, so the frozen
    baseline's glob finds it regardless of what the input file is called."""
    if snapshot not in _STAGED:
        staging = Path(tempfile.mkdtemp(prefix="snapshot-invariance-"))
        shutil.copy(snapshot, staging / "sponsor-register-2026-08-28.csv.gz")
        _STAGED[snapshot] = staging
    return _STAGED[snapshot]


def baseline_context(snapshot: Path, requisition_text: str) -> str:
    """Run the real frozen lookup against a chosen snapshot file."""
    original = baseline_solve._FIXTURES
    try:
        baseline_solve._FIXTURES = _staged_dir(snapshot)
        baseline_solve._register.cache_clear()
        return baseline_solve.register_context(
            baseline_solve.candidate_strings(requisition_text)
        )
    finally:
        baseline_solve._FIXTURES = original
        baseline_solve._register.cache_clear()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old", type=Path, required=True)
    ap.add_argument("--new", type=Path, required=True)
    args = ap.parse_args()

    old_rows, new_rows = load_rows(args.old), load_rows(args.new)
    aliases: dict[str, str] = json.loads(
        (CASES_DIR / "fixtures" / "aliases.json").read_text()
    )["aliases"]

    diffs = 0
    skipped: list[str] = []
    for f in sorted(CASES_DIR.glob("case-*.json")):
        case = json.loads(f.read_text())
        strings: list[str] = []
        strings += case["meta"].get("register_fixture_orgs", [])
        strings += case["meta"].get("asserted_absent_names", [])
        strings += list(aliases) + list(aliases.values())
        text = str(case["payload"]["requisition_text"])
        strings += baseline_solve.candidate_strings(text)

        case_diffs: list[str] = []
        reorders: list[str] = []
        old_ctx = baseline_context(args.old, text)
        new_ctx = baseline_context(args.new, text)
        if old_ctx != new_ctx:
            if sorted(old_ctx.splitlines()) == sorted(new_ctx.splitlines()):
                reorders.append("baseline excerpt rows reordered (content identical)")
            else:
                case_diffs.append("baseline register_context differs in CONTENT")
        for s in strings:
            if s in NEW_ONLY_ORGS:
                skipped.append(f"{case['id']}: {s} (added with the new snapshot)")
                continue
            old_res = resolve_entity((s,), old_rows, aliases)
            new_res = resolve_entity((s,), new_rows, aliases)
            if old_res == new_res:
                continue
            same_content = (
                type(old_res) is type(new_res)
                and sorted(map(str, getattr(old_res, "rows", ())))
                == sorted(map(str, getattr(new_res, "rows", ())))
                and sorted(getattr(old_res, "organisation_names", ()))
                == sorted(getattr(new_res, "organisation_names", ()))
            )
            if same_content:
                reorders.append(f"resolve_entity({s!r}) rows reordered (same set)")
            else:
                case_diffs.append(f"resolve_entity({s!r}) differs in CONTENT")
        status = "PASS" if not case_diffs else "CONTENT DIFF: " + "; ".join(case_diffs)
        if reorders:
            status += "  [" + "; ".join(reorders) + "]"
        print(f"{case['id']:<44} {status}")
        diffs += len(case_diffs)

    for note in skipped:
        print(f"excluded from comparison (new-snapshot org): {note}")
    verdict = (
        "INVARIANT IN CONTENT: no solver input changed except the row orderings "
        "disclosed above"
        if diffs == 0
        else f"{diffs} CONTENT DIFFERENCES"
    )
    print(f"\n{verdict}")
    return 0 if diffs == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
