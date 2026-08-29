#!/usr/bin/env python3
"""Single evaluation entrypoint for frontier-2026.

Every number claimed in README.md or CHANGELOG.md must come out of this script.
Usage:
    python eval/run_eval.py --variant baseline --variant advanced --seed 42
    python eval/run_eval.py --variant advanced --repeats 5   # variance check

Writes eval/results/<timestamp>.json and <timestamp>.md. Both are committed.

The runner is domain-agnostic on purpose: it does not know what the problem is.
Wire the problem in by editing exactly two places:
  1. load_cases()  — how test cases are read
  2. VARIANTS      — how each variant is invoked on a case
Do not restructure this file; the stability of the harness is what makes the
baseline-vs-advanced comparison credible.
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.metrics import METRICS, CaseResult  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "eval" / "cases"
RESULTS_DIR = ROOT / "eval" / "results"


# --------------------------------------------------------------------------
# 1. Cases — EDIT THIS after the problem statement is published
# --------------------------------------------------------------------------


@dataclass
class Case:
    """One evaluation case. `expected` is an independently derived answer,
    never the output of the system under test (CLAUDE.md T-7)."""

    id: str
    payload: dict[str, Any]
    expected: dict[str, Any] = field(default_factory=dict)
    split: str = "dev"


def load_cases(limit: int | None = None, split: str = "dev") -> list[Case]:
    """Read cases from eval/cases/*.json.

    Each file is {"id": ..., "meta": {"split": ...}, "payload": {...}, "expected": {...}}.
    split: "dev" (default — holdout stays unread during development, docs/PLAN.md §7),
    "holdout", or "all" (the final run).
    """
    files = sorted(CASES_DIR.glob("*.json"))
    if not files:
        raise SystemExit(
            f"No cases found in {CASES_DIR}. Add at least one before running the eval."
        )
    cases = []
    for f in files:
        raw = json.loads(f.read_text())
        case_split = raw.get("meta", {}).get("split", "dev")
        if split != "all" and case_split != split:
            continue
        cases.append(
            Case(
                id=raw.get("id", f.stem),
                payload=raw["payload"],
                expected=raw.get("expected", {}),
                split=case_split,
            )
        )
    if not cases:
        raise SystemExit(f"No cases with split={split!r} in {CASES_DIR}.")
    return cases[:limit] if limit else cases


# --------------------------------------------------------------------------
# 2. Variants — EDIT THIS after the problem statement is published
# --------------------------------------------------------------------------


def run_baseline(case: Case, seed: int) -> dict[str, Any]:
    """Deliberately simple reference implementation. FROZEN — see CLAUDE.md CN-3."""
    from src.baseline.solve import solve  # noqa: PLC0415

    return solve(case.payload, seed=seed)


def run_advanced(case: Case, seed: int) -> dict[str, Any]:
    """The submitted solution."""
    from src.advanced.solve import solve  # noqa: PLC0415

    return solve(case.payload, seed=seed)


def run_self_consistency(case: Case, seed: int) -> dict[str, Any]:
    """Removed-experiment variant (DECISIONS.md 2026-08-28): 3-sample voting over
    the frozen baseline at temperature 1.0. Not in the default variant list; runs
    only when explicitly flagged, so its rejection stays reproducible."""
    from src.experiments.self_consistency import solve  # noqa: PLC0415

    return solve(case.payload, seed=seed)


def run_always_abstain(case: Case, seed: int) -> dict[str, Any]:
    """Trivial-abstention floor: UNVERIFIABLE on every case, no evidence, no model call.

    Metric-integrity reference (DECISIONS.md 2026-08-28): with this verdict mix, always
    abstaining scores verdict_utility 0.5 for free. Every results table shows that floor
    so the claim is "beats both the baseline and trivial abstention"."""
    return {
        "verdict": "UNVERIFIABLE",
        "checks": {},
        "uncertainty": "always_abstain reference variant: no checks attempted",
    }


VARIANTS: dict[str, Callable[[Case, int], dict[str, Any]]] = {
    "baseline": run_baseline,
    "always_abstain": run_always_abstain,
    "advanced": run_advanced,
    "self_consistency": run_self_consistency,
}


# --------------------------------------------------------------------------
# Runner — do not edit below this line without a reason recorded in DECISIONS.md
# --------------------------------------------------------------------------


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def git_status_porcelain() -> str:
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        )
    except Exception:
        return ""


def git_dirty() -> bool:
    return bool(git_status_porcelain().strip())


def blocking_dirt(porcelain: str) -> list[str]:
    """Dirt that makes a tagged run non-reproducible from its commit.

    Untracked files under eval/results/ are exempt: they are the harness's own
    prior outputs, never inputs, and a fresh-clone verifier accumulates them by
    following REPRODUCTION.md in order — refusing on those would break CN-2.
    """
    dirt = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        path = line[2:].strip().strip('"')
        if line.startswith("??") and path.startswith("eval/results/"):
            continue
        dirt.append(line)
    return dirt


def run_variant(name: str, cases: list[Case], seed: int) -> dict[str, Any]:
    fn = VARIANTS[name]
    results: list[CaseResult] = []
    for case in cases:
        random.seed(seed)
        started = time.perf_counter()
        error = None
        output: dict[str, Any] = {}
        try:
            output = fn(case, seed)
        except Exception as exc:  # noqa: BLE001 — a crash is a measurable outcome
            error = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - started
        results.append(
            CaseResult(
                case_id=case.id,
                output=output,
                expected=case.expected,
                seconds=elapsed,
                error=error,
                payload=case.payload,
            )
        )

    scores = {m.name: m.aggregate(results) for m in METRICS}
    return {
        "variant": name,
        "n_cases": len(cases),
        "n_errors": sum(1 for r in results if r.error),
        "metrics": scores,
        "cases": [asdict(r) for r in results],
    }


def summarize(runs: list[dict[str, Any]]) -> str:
    metric_names = [m.name for m in METRICS]
    header = "| Metric | " + " | ".join(r["variant"] for r in runs) + " |"
    if len(runs) == 2:
        header += " Delta |"
    sep = "|---" * (len(runs) + 1 + (1 if len(runs) == 2 else 0)) + "|"
    lines = [header, sep]
    for name in metric_names:
        vals = [r["metrics"][name] for r in runs]
        cells = [f"{v:.4g}" if isinstance(v, (int, float)) else str(v) for v in vals]
        row = f"| {name} | " + " | ".join(cells) + " |"
        if len(runs) == 2 and all(isinstance(v, (int, float)) for v in vals):
            row += f" {vals[1] - vals[0]:+.4g} |"
        elif len(runs) == 2:
            row += " — |"
        lines.append(row)
    return "\n".join(lines)


def variance_report(
    name: str, cases: list[Case], seed: int, repeats: int
) -> dict[str, Any]:
    """Run one variant several times so a real delta can be told apart from noise."""
    runs = [run_variant(name, cases, seed + i) for i in range(repeats)]
    out: dict[str, Any] = {}
    for m in METRICS:
        vals = [r["metrics"][m.name] for r in runs]
        if all(isinstance(v, (int, float)) for v in vals):
            out[m.name] = {
                "mean": statistics.fmean(vals),
                "stdev": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                "min": min(vals),
                "max": max(vals),
                "runs": vals,
            }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="frontier-2026 evaluation harness")
    ap.add_argument(
        "--variant",
        action="append",
        choices=list(VARIANTS),
        help="repeatable; default is baseline then advanced",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--limit", type=int, default=None, help="cap number of cases")
    ap.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="repeat each variant N times and report variance",
    )
    ap.add_argument("--tag", default="", help="label written into the results file")
    ap.add_argument(
        "--split",
        choices=["dev", "holdout", "all"],
        default="dev",
        help="dev during development (default); all for the final run "
        "(docs/PLAN.md §7 holdout discipline)",
    )
    args = ap.parse_args()

    if args.tag:
        dirt = blocking_dirt(git_status_porcelain())
        if dirt:
            print(
                "REFUSED: --tag is set and the working tree is dirty. A tagged run "
                "is a source of\nrecord and must reproduce from its commit. Commit "
                "or stash these first:"
            )
            for line in dirt:
                print(f"  {line}")
            print("No results file was written and no model call was made.")
            return 2

    variants = args.variant or ["baseline", "always_abstain", "advanced"]
    cases = load_cases(args.limit, args.split)

    runs = [run_variant(v, cases, args.seed) for v in variants]

    variance = {}
    if args.repeats > 1:
        variance = {
            v: variance_report(v, cases, args.seed, args.repeats) for v in variants
        }

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    record = {
        "timestamp_utc": stamp,
        "tag": args.tag,
        "split": args.split,
        "seed": args.seed,
        "git_sha": git_sha(),
        "git_dirty": git_dirty(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "runs": runs,
        "variance": variance,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / f"{stamp}.json").write_text(
        json.dumps(record, indent=2, default=str)
    )

    table = summarize(runs)
    md = [
        f"# Eval run {stamp}",
        "",
        f"- commit: `{record['git_sha']}`"
        + ("  **(working tree dirty)**" if record["git_dirty"] else ""),
        f"- seed: `{args.seed}` · split: `{args.split}` · cases: {len(cases)} · repeats: {args.repeats}",
        "",
        table,
        "",
    ]
    for r in runs:
        if r["n_errors"]:
            md.append(f"- `{r['variant']}`: {r['n_errors']} case(s) errored.")
    if variance:
        md.append("\n## Run-to-run variance\n")
        for v, stats in variance.items():
            md.append(f"**{v}**\n")
            md.append("| Metric | mean | stdev | min | max |")
            md.append("|---|---|---|---|---|")
            for k, s in stats.items():
                md.append(
                    f"| {k} | {s['mean']:.4g} | {s['stdev']:.4g} | {s['min']:.4g} | {s['max']:.4g} |"
                )
            md.append("")
    (RESULTS_DIR / f"{stamp}.md").write_text("\n".join(md))

    print("\n".join(md))
    print(f"\nwritten: eval/results/{stamp}.json  eval/results/{stamp}.md")
    if record["git_dirty"]:
        print(
            "WARNING: working tree is dirty — this run is not reproducible from the commit."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
