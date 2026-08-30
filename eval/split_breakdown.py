#!/usr/bin/env python3
"""Re-aggregate a full-set results file by dev/holdout split.

The final run scores all 32 cases in one aggregate; the README's held-out
breakdown needs the same metrics computed over each split separately, from the
same per-case records, with the same metric definitions. Nothing is re-run and
no case content is read — only meta.split from the case files and the recorded
per-case results from the results JSON.

Usage:
    python eval/split_breakdown.py --results eval/results/20260830-101148.json \
        --out eval/results/final-breakdown-2026-08-30.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.metrics import METRICS, CaseResult  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "eval" / "cases"


def split_of_cases() -> dict[str, str]:
    return {
        (c := json.loads(f.read_text()))["id"]: c["meta"]["split"]
        for f in sorted(CASES_DIR.glob("case-*.json"))
    }


def to_case_results(run: dict[str, Any]) -> list[CaseResult]:
    return [
        CaseResult(
            case_id=c["case_id"],
            output=c["output"],
            expected=c["expected"],
            seconds=c["seconds"],
            error=c["error"],
            payload=c["payload"],
        )
        for c in run["cases"]
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    record = json.loads(args.results.read_text())
    splits = split_of_cases()

    lines = [
        "# Split breakdown — same per-case records, same metric definitions",
        "",
        f"Derived from `{args.results.name}` "
        f"(commit `{record['git_sha']}`, git_dirty={record['git_dirty']}, "
        f"tag `{record['tag']}`); nothing re-run.",
        "",
    ]
    for run in record["runs"]:
        results = to_case_results(run)
        subsets = {
            "all": results,
            "dev": [r for r in results if splits[r.case_id] == "dev"],
            "holdout": [r for r in results if splits[r.case_id] == "holdout"],
        }
        lines.append(f"## {run['variant']}")
        lines.append("")
        lines.append("| Metric | all | dev | holdout |")
        lines.append("|---|---|---|---|")
        for m in METRICS:
            cells = [
                f"{m.aggregate(subsets[s]):.4g}" for s in ("all", "dev", "holdout")
            ]
            lines.append(f"| {m.name} | " + " | ".join(cells) + " |")
        lines.append("")
        counts = {s: len(rs) for s, rs in subsets.items()}
        lines.append(
            f"Cases: {counts['all']} all / {counts['dev']} dev / {counts['holdout']} holdout."
        )
        lines.append("")

    args.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
