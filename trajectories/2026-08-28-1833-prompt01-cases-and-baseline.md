# Trajectory — prompt01-cases-and-baseline

| Field | Value |
|---|---|
| Date (UTC) | 2026-08-28 18:33 |
| Agent | Claude Code (VS Code extension) |
| Model | claude-fable-5, session model pinned by operator |
| Tools granted | Read, Write, Edit, Bash (repo-local), no network except step-3 register fetch |
| Instruction file | `CLAUDE.md` + `prompts/01-baseline.md` (discipline only; ordering amended by `docs/PLAN.md` §8) |
| Task | Fri-evening sequence: (1) case schema + compound hard-case example → HUMAN gate; (2) full ~30-case set → HUMAN label gate; (3) register snapshot + fixture rows + DATA.md; (4) metrics + DECISIONS; (5) baseline, `--repeats 5`, freeze |
| Expected metric impact | Steps 1–4 move no metric — they define the contract every metric is scored against (BP-4 statement). Step 5 establishes the baseline floor for `verdict_utility`, `confident_wrong_rate`, `check_accuracy`, `grounding_rate` and the run-to-run noise floor via `--repeats 5`. |
| Commit at start | `e4ed9a3` |

Session start notes: CLAUDE.md read in full earlier this session (QNEW). Operator instruction
overriding `prompts/01-baseline.md` ordering, verbatim: "Run prompt 01 with the amended
ordering from docs/PLAN.md §8, not the ordering in prompts/01-baseline.md — that file
predates the plan. Read it for the discipline (TDD, gates, freeze, changelog, trajectory),
ignore its sequence." Commit policy for tonight: artifacts commit after their human gate
passes, not before (the gates exist to change these files).

---

## Session

### Step 1 — Case JSON schema + the compound hard case, filled

**Agent action**

```
Write eval/cases/SCHEMA.md          (case format: field spec, enums, labelling rules)
Write eval/cases/case-01-compound-aggregator-gbm.json   (the compound hard case)
```

Design decisions taken while writing, and why:

- Uniform tri-state `status` (pass | fail | indeterminate) on every check, plus a
  per-check fine-grained `reason` enum. Scoring stays one vocabulary
  (`check_accuracy` compares status; `exact_match` subset-compares whatever
  `expected` carries), while the reason preserves the label detail the report and
  tests need. Deleting a `reason` from `expected` during the label pass relaxes
  strict scoring for that case — documented as a deliberate lever.
- `payload` carries only `requisition_text` (the whole page as a person would paste
  it, wrapper included). No `employer_hint` — extracting the employer is part of the
  task under test. Register snapshot, alias fixtures and floor config are repo-level
  fixtures shared by both variants, paths locked in SCHEMA.md so step 3 lands where
  documented.
- The compound case's brand→legal-entity tie ("Ottervale" → "Bryelock Systems Ltd")
  deliberately does NOT appear in the posting text. Resolution must come from the
  Companies House alias fixture — that is hop 1 of the two-hop trap. Hop 2 is the
  GBM-only route row. The aggregator wrapper is intentionally consistent with the
  body: the wrapper-contradiction failure belongs to its own archetype, and mixing
  it in would muddy what this case measures.
- Ground-truth subtlety recorded in the case's `design_notes`: a grep-literalist
  baseline ("Ottervale" not in CSV → NOT_SPONSORABLE) lands on the right verdict for
  the wrong reason. `verdict_utility` alone would reward it; `check_accuracy`
  (register wrongly `fail`, route wrongly `indeterminate`) and `grounding_rate` are
  what catch it. This is why per-check labels exist.

**Tool response**

```
Both files created. No collisions with existing paths (eval/cases/ held only .gitkeep).
```

**What this changed about the plan**

Two follow-ups surfaced while authoring, queued for step 3: (a) fixture register rows
must copy the real snapshot's exact column vocabulary (Route / Type & Rating strings)
at commit time, not my recollection of it; (b) an integrity check that no fictional
employer name collides with a real row in the committed snapshot
(`test_fixture_orgs_do_not_collide_with_real_register`).

> **HUMAN: approved** — gate 1 passed with four amendments: (1) salary floor is two
> thresholds (general + SOC going rate), `floor_config` carries both, reasons split into
> `below_general_threshold`/`below_going_rate`, new archetype for the between-band case,
> case-01 re-checked (£42,000 ≥ both → `above_floor` stands); (2) `register_snapshot_date`
> added to `expected` on every case — staleness warning untestable without it;
> (3) new archetype `licence_rating_blocks`, ground truth NOT_SPONSORABLE (row exists,
> rating blocks CoS) — solver sub-check stays Saturday-optional; (4) absence must verify
> both ways against the committed snapshot; test named. `determining_fact` and the three
> case-01 authoring choices explicitly confirmed.

---

### Step 2 — Apply amendments, generate the full 30-case set

**Agent action**

```
Write eval/cases/SCHEMA.md          (v2: two-threshold floor_config; salary reasons split;
                                     route reason rating_blocks_cos; expected.register_snapshot_date;
                                     meta.asserted_absent_names; both-ways integrity tests named:
                                     test_fixture_orgs_do_not_collide_with_real_register,
                                     test_asserted_absent_names_match_no_row_under_any_normalisation)
Edit eval/cases/case-01-...json     (add expected.register_snapshot_date)
Edit docs/PLAN.md ×3                (two-threshold floor; rating ground truth; archetype list)
Bash python3 generation script      (29 cases, self-checking)
```

Self-checks built into generation, so bad fixtures cannot be written silently: every
`willingness_quote`/`salary_text` anchor must be a verbatim substring of the posting;
every labelled verdict must equal the combinator applied to the four statuses; every
salary figure must sit consistently with its reason under BOTH plausible general-threshold
values (30,960 and 33,400 — margins chosen so the pending verification cannot flip a
label); trap cases must NOT leak the hidden entity name into the text
(case-04 "Ashcombe", case-24/25 group entities); absence cases must have empty
`register_fixture_orgs` and non-empty `asserted_absent_names`.

**Tool response**

```
wrote 29 cases; all asserts passed (anchors, combinator, reasons, salary bands, absence fields)
totals (incl. case-01): NS 14 · S 6 · U 10 | splits: dev 20 · holdout 10
30 fixture register orgs enumerated for step 3; asserted-absent:
Copperwaite Studio, Glimmerforth Labs, TalentBridge Recruitment
```

**What this changed about the plan**

The step-3 work-list is now machine-generated rather than hand-collected: 30 fixture rows
(28 Skilled Worker A-rated, 3 GBM-only, 1 Skilled Worker B-rated — Halcyon Consulting is
GBM within an SW group), 2 alias entries (Ottervale→Bryelock, Loopwork→Ashcombe), and 3
names that must match nothing. Decisions taken while generating, flagged for the label
pass: willingness is labelled `offered` (pass) on three doomed cases (07 GBM, 15 absent,
28 B-rated) — stated willingness is a fact about the posting even when the verdict is
NOT_SPONSORABLE; case-25 probes the C1 policy (both candidate entities SW-licensed, still
`ambiguous_group`); case-30 labels "considered for permanent conversions" as
`boilerplate_ambiguous`, not `offered`.

> **HUMAN: approved** — gate 2 (label-correction) passed with seven corrections. Cases 29
> and 30 stay; willingness=offered on doomed cases confirmed correct; case-25's convention
> stands. The corrections, summarised from the operator's instruction:
> 1. **always_abstain reference variant.** With 14/6/10 the strategy "always UNVERIFIABLE"
>    scores verdict_utility 0.5 for zero effort — a metric property a judge will find. Fix
>    is not rebalancing but exposure: a third zero-cost variant in run_eval.py, so every
>    table shows the trivial-abstention floor and the claim becomes "beats both floors".
>    DECISIONS entry required, before the baseline freeze.
> 2. **Holdout discipline made mechanical.** From this commit: never open/read/quote/reason
>    about meta.split=holdout files while building the solution; eval runs use --split dev
>    until the final Sunday run; --split flag added to the harness now. If holdout content
>    is recalled during design, it gets recorded here rather than silently used.
> 3. **case-25 design_notes reasoning error.** "Going-rate is entity-contract-specific" is
>    wrong (going rate is SOC- and location-determined). Label stands; justification must
>    rest only on: a CoS is issued by one specific licensed entity, so an unidentifiable
>    issuer means the licence backing any CoS cannot be established. Scan all 29 notes for
>    the same class of error (right label, wrong reason).
> 4. **£33,400 is the agent's assumption, not the operator's.** Verify against the source at
>    step 3; re-check cases 11/12 (closest to the boundary); if a verified value moves a
>    label, STOP and report rather than adjusting the case.
> 5. **Guaranteed-basic-pay rule undocumented.** Only guaranteed basic gross annual pay
>    counts toward the thresholds — bonus, profit share, equity, allowances, overtime do
>    not. Add counts_toward_floor to floor_config with source; state in SCHEMA labelling
>    conventions; baseline prompt and advanced extraction must separate base from
>    non-guaranteed components. Case-11 re-verified with it stated: base £35,500, profit
>    share ~6% ≈ £2,130 → £37,630, still £670 below the going rate — label holds either
>    way; thinnest margin in the set, noted in its design_notes.
> 6. **Submission-form constraints (new information).** Source zip hard limit 50MB; video
>    is URL-only. Register snapshot committed gzipped, never raw; report
>    `git archive HEAD | wc -c` after committing; if not comfortably inside the limit,
>    filter the snapshot to needed rows with the filter script committed and before/after
>    counts in DATA.md. DATA.md must distinguish real from fixture rows at a glance and
>    carry OGL attribution, source URL, retrieval date. Fixture rows copy the real file's
>    exact Route / Type & Rating strings. Collision check runs both directions across all
>    30 fictional names; a collision renames the fixture, not the test.
> 7. **prompts/01-baseline.md gets a supersession note** (ordering lives in docs/PLAN.md §8
>    and this trajectory; the file is kept for its discipline) — after this checkpoint is
>    recorded.

---

### Step 2a — Apply the gate-2 corrections

**Agent action**

```
Edit eval/cases/case-25-...json      (design_notes: correct ground for the convention)
Edit eval/cases/case-11-...json      (design_notes: thinnest-margin note)
Edit eval/cases/SCHEMA.md            (counts_toward_floor in floor_config; guaranteed-basic
                                      labelling convention; holdout enforcement on split)
Edit eval/run_eval.py                (always_abstain variant; --split dev|holdout|all,
                                      default dev; three-variant default; split recorded in
                                      results file)
Edit docs/DECISIONS.md               (two entries: metric-integrity floor; holdout flag —
                                      both sanction the runner edits, both pre-freeze)
Edit docs/PLAN.md                    (§6 three reference lines; §7 holdout rule in force;
                                      §8 submission constraints)
Edit prompts/01-baseline.md          (supersession note)
```

Scan result for correction 3 across all 30 design_notes: the error class (correct label,
wrong supporting reason) found only in case-25. Case-22's "£38,300 floor" phrasing is
correct under the two-threshold rule (it is the binding maximum for this SOC/basis);
case-30's no-annualisation policy and case-26's sponsorship-confers-RTW reasoning are
sound. Case-11's fact line already states the max-of-two rule.

**What this changed about the plan**

The dev-loop eval command is now `python eval/run_eval.py --split dev` and the final
Sunday command gains an explicit `--split all`; REPRODUCTION.md must show both when
written. The baseline system prompt (step 5) and the advanced extraction schema
(Saturday) must instruct base-pay-vs-extras separation per correction 5. Step 3 acquires
two verification obligations that can STOP the evening: the general-threshold source
check (correction 4) and the two-way collision check (correction 6).
