"""Failing-by-design boundary tests for the verification stage (C-1).

The verifier's one move: a check whose quote is not a verbatim substring of the
source drops to indeterminate — it can push the verdict only toward UNVERIFIABLE,
never toward confidence (docs/PLAN.md §5). Saturday-evening scope; boundary pinned
now so the pipeline wires against it from the start."""

from __future__ import annotations

from src.advanced.rules import CheckOutcome
from src.advanced.verify import verify_and_downgrade

SOURCE = "We offer visa sponsorship for this role. Salary £41,000."
SUPPORTED_QUOTE = "We offer visa sponsorship"
FABRICATED_QUOTE = "We happily sponsor everyone"


def test_verifier_downgrades_unsupported_quote_to_indeterminate() -> None:
    checks = {"willingness": CheckOutcome("pass", "offered")}
    out = verify_and_downgrade(checks, {"willingness": FABRICATED_QUOTE}, SOURCE)
    assert out["willingness"].status == "indeterminate"


def test_verifier_keeps_supported_quote_untouched() -> None:
    checks = {"willingness": CheckOutcome("pass", "offered")}
    out = verify_and_downgrade(checks, {"willingness": SUPPORTED_QUOTE}, SOURCE)
    assert out["willingness"] == CheckOutcome("pass", "offered")
