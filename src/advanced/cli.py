"""Run the advanced pipeline on one pasted requisition and print the report.

    python -m src.advanced.cli path/to/posting.txt

The demo path (checkpoint 2026-08-29): before this, the product was exercisable only
through the eval harness — an end-to-end gap found while measuring human time by
hand. Requires ANTHROPIC_API_KEY; makes exactly one model call (~$0.003, ~2 s), then
resolution, rules and rendering run deterministically.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.advanced.report import render_report
from src.advanced.solve import solve


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m src.advanced.cli path/to/posting.txt", file=sys.stderr)
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 2
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        print(f"error: not a UTF-8 text file: {path}", file=sys.stderr)
        return 2
    result = solve({"requisition_text": text})
    print(render_report(result, text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
