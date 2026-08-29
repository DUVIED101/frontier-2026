# Time-to-a-trustworthy-answer — measurement record

Protocol pre-registered in DECISIONS.md (2026-08-29, "Human time is measured as
time-to-a-trustworthy-answer"): three requisitions, both variants, timed to the point
the user could act on the output — including the time to verify or refute a wrong or
unsupported answer. Raw latency is not the claim; the baseline answers in about a
minute and is confidently wrong on roughly half its definitive verdicts, so acting on
it requires re-deriving it against the register.

**Scope, stated plainly:** three requisitions illustrate; the full case evaluation
(`eval/results/`, all committed runs) carries the statistical weight. The sample
covers the classes that could actually be sourced live — see the sourcing finding
below.

## Measurements

| # | Requisition | Baseline (manual process) | Advanced (`python -m src.advanced.cli`) | Notes |
|---|---|---|---|---|
| 1 | Sony Music posting (live, 2026-08-29) | **130 s** — two questions plus manual register verification | **7 s** | Same verdict. Advanced reached it for better reasons: the baseline substituted a market estimate ("£70–90k for a London SWE role") for a salary the posting does not state — §3 failure mode 1 (world-knowledge substitution) on live input, the failure the synthetic fixtures structurally cannot elicit. Advanced returned indeterminate on salary and quoted what the posting actually says. |
| 2 | Mott MacDonald posting (live, 2026-08-29) | **27 s** — and correct | **7 s** | An easy case for the manual process, and this file says so rather than flattering the comparison: the refusal sits in its own "UK Immigration" section and the register lookup is one search. Advanced: NOT_SPONSORABLE, refusal quote grounded with exact offsets across line breaks; the multi-row citation fix works on live input — the report names all three routes the entity holds and states which row the verdict rests on. |
| 3 | TODO (Sunday) | | | |

The sample so far is one case where the manual process was slow and substituted an
estimate, and one where it was fast and correct. Three requisitions illustrate; the
32-case eval carries the statistical weight.

## Sourcing finding (2026-08-29)

No live posting could be sourced that affirmatively offers sponsorship for a specific
role. That matches the domain rather than contradicting it: sponsorship is rarely
stated, and a posting that says nothing is the common case, not the edge case. This is
the empirical justification for the C3 silence policy (docs/PLAN.md §2): silence
blocks SPONSORABLE without producing NOT_SPONSORABLE, so the system's most frequent
honest output on live input is UNVERIFIABLE with a named question to ask. A policy
that read silence as refusal would reach the opposite conclusion and silently discard
viable roles.
