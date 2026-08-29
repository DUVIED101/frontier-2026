"""Removed-experiment variant: 3-sample self-consistency voting over the baseline.

NOT part of the submission. Kept runnable so its rejection is reproducible
(DECISIONS.md 2026-08-28: the experiment must be rejected by its own numbers, not
by argument). It samples the frozen baseline's exact prompt and lookup three times
at temperature 1.0 — the one deliberate, documented departure from C-6 determinism,
because self-consistency is meaningless at temperature 0 where all samples collapse
into one. The majority verdict wins; a split without a strict majority abstains;
checks come from the first sample that voted with the majority. Imports the frozen
baseline read-only; nothing in src/baseline/ changes (CN-3).
"""

from __future__ import annotations

from typing import Any, Sequence

import anthropic

from src.baseline.solve import (
    MAX_TOKENS,
    MODEL_ID,
    build_prompt,
    candidate_strings,
    parse_response,
    register_context,
)

SAMPLES = 3
TEMPERATURE = 1.0
ABSTAIN = "UNVERIFIABLE"


def vote(verdicts: Sequence[str]) -> str:
    """Strict majority or abstain — a split must never manufacture confidence."""
    if not verdicts:
        return ABSTAIN
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts, key=lambda k: counts[k])
    return top if counts[top] * 2 > len(verdicts) else ABSTAIN


def solve(payload: dict[str, Any], *, seed: int = 42) -> dict[str, Any]:
    """`seed` is unused: the API exposes no sampling seed, so the three samples are
    deliberately non-deterministic (temperature 1.0) — that is the experiment."""
    text = str(payload["requisition_text"])
    system, user = build_prompt(text, register_context(candidate_strings(text)))
    client = anthropic.Anthropic()
    samples: list[dict[str, Any]] = []
    tokens_in = tokens_out = 0
    for _ in range(SAMPLES):
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            extra_body={"temperature": TEMPERATURE},
        )
        tokens_in += response.usage.input_tokens
        tokens_out += response.usage.output_tokens
        reply = "".join(b.text for b in response.content if b.type == "text")
        try:
            parsed = parse_response(reply)
        except ValueError:
            continue
        if parsed.get("verdict"):
            samples.append(parsed)
    verdict = vote([str(s["verdict"]) for s in samples])
    chosen = next(
        (s for s in samples if s["verdict"] == verdict),
        {
            "verdict": verdict,
            "checks": {},
            "uncertainty": (
                f"self-consistency: no majority across {len(samples)} valid samples"
            ),
        },
    )
    result = dict(chosen)
    result["verdict"] = verdict
    result["_usage"] = {
        "model": MODEL_ID,
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
    }
    return result
