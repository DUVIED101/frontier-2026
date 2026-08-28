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

---

> **HUMAN: redirected** — mid-step addition to correction 6, before fixture rows are
> appended: fixture rows must be indistinguishable from real rows **by shape** — same
> column count, capitalisation conventions, empty-field treatment, city/county values
> drawn from the vocabulary real rows actually use; after appending, sample ten real rows
> and all thirty fixture rows and confirm no field-level pattern separates them.
> Stated reason: if a solver could learn "fixture rows look like X", the register check
> passes on an artifact rather than on the data, and every register number in the eval is
> worthless. Consequence taken beyond the letter of the instruction: the real file is
> ~alphabetically sorted, so fixtures are **inserted at name-sorted positions**, not
> appended — a tail of 30 fixture rows would have been the most learnable pattern of all.

### Step 3 — Register snapshot, threshold verification, fixtures, integrity tests

**Agent action + tool responses, in order**

```
curl publication page   -> CSV asset dated 2026-08-28 (placeholder date correct, no bulk fix)
curl CSV                -> 10.9MB raw, 142,988 rows; header matches anchored columns;
                           CRLF endings; quoting only for comma-fields; County 66% empty;
                           ~24% of names ALL-CAPS; file ~sorted (not strictly)
vocabulary extraction   -> anchored strings verbatim in real vocab: Worker (A rating),
                           Worker (B rating), Skilled Worker, Global Business Mobility:
                           Senior or Specialist Worker
two-way collision scan  -> 37 fictional names (30 entities + 4 brands + 3 asserted-absent)
                           vs 142,988 rows under normalise + token-set: NONE
threshold verification  -> pay page via content API: general threshold new entrant
                           £33,400 CONFIRMED ("70% of going rate, min £33,400/yr")
                        -> going-rates table (updated 2025-07-22): SOC 2134 standard
                           £54,700; second column showed £40,000 — POTENTIAL STOP:
                           if that were the new-entrant rate, case-16's salary label
                           (£39,500, above_floor) would flip
                        -> column headers + intro extracted: "Lower going rate" applies
                           only to Health & Care visas and pre-2024-04-04 transitional
                           holders. Not this user. New entrant = 70% × 54,700 = 38,290
                           → £38,300 rounded to £100: operator figure CONFIRMED.
                           No label within £700 of the boundary. NO STOP.
venv                    -> python3.14 ensurepip broken; rebuilt on python3.12 with exact
                           pins: pytest 8.3.4, mypy 1.14.1, ruff 0.9.2
TDD                     -> tests/test_fixture_integrity.py written first; RED
                           (normalize module and fixtures absent), then implementation:
                           src/advanced/normalize.py (shared resolver/tests definition),
                           snapshot built (fixtures inserted at sorted positions, real
                           rows byte-identical, gzip mtime=0 for determinism), manifest,
                           aliases.json, floor_config.json → GREEN 8/8
gates                   -> ruff format applied (3 files reflowed); format --check clean;
                           mypy --strict src clean
shape sample            -> 10 real + all 30 fixture rows: every fixture feature-class is
                           one of the top-2 real classes (mixed/no-county/Ltd 35%,
                           mixed/county/Ltd 18%); no field separates any single fixture
                           row. Aggregate skew toward the modal class = the software-
                           sector subpopulation, stated openly.
```

**What this changed about the plan**

The £40,000 "Lower going rate" column is exactly the class of confusion the tool exists
to prevent — it goes into DATA.md as documentation and becomes candidate material for
the README/video ("even the official table has a trap column"). floor_config.json now
carries the full derivation (standard rate, 70% rule, rounding) rather than a bare
number, so the report's uncertainty statement can cite it. Sunday's REPRODUCTION.md must
document the venv-on-3.12 requirement. `git archive` size checked after commit.

---

> **HUMAN: approved** — steps 4 and 5 authorised, with instructions: report the
> `--repeats 5` variance before any comparison is drawn; the results table carries three
> lines from tonight (baseline, always_abstain, empty advanced slot); the going-rate
> column finding is elevated to a finding in DATA.md and earmarked for README and video;
> the Python 3.14 ensurepip dead end goes into REPRODUCTION.md.

### Steps 4–5 — Metrics implemented; baseline built; runs BLOCKED on the API key

**Agent action + tool responses, in order**

```
env check               -> NO ANTHROPIC_API_KEY (no .env, nothing in the shell env).
                           Build proceeds; the two eval runs are blocked at the end.
Edit docs/DATA.md       -> going-rate trap column promoted to a titled Finding
API reference loaded    -> decision-relevant: temperature is REMOVED on Opus 4.7/4.8 and
                           Fable 5 (400) but accepted on the 4.6 family. The C-6
                           temperature pin therefore fixes the model choice:
                           claude-sonnet-4-6, $3/$15 per MTok (price table recorded in
                           metrics.py). DECISIONS entry written.
TDD metrics             -> tests/test_metrics.py first: 17 tests RED (payload field and
                           problem-specific metrics absent) -> implemented
                           verdict_utility / confident_wrong_rate / check_accuracy /
                           grounding_rate / cost_per_case_usd + narrowed exact_match;
                           CaseResult gained payload (run_eval passes it through).
                           Design decision while implementing: exact_match compares a
                           PROJECTION of expected — determining_fact and
                           evidence_anchors are label-only fields solvers never echo,
                           so they are excluded (SCHEMA.md updated to say so); the
                           delete-a-reason labelling lever is preserved and tested.
TDD baseline            -> tests/test_baseline.py first: RED (stub) -> implemented
                           src/baseline/solve.py. Candidate extraction needed one
                           honest refinement: raw header segments include "Engineering"
                           and "London", which match thousands of register rows, so a
                           stopword list keeps job-title/location segments out of the
                           search — a person Ctrl-Fs the employer's name, not the words
                           "Software Engineer". The designed failures are pinned as
                           tests: test_baseline_lookup_is_blind_to_brand_aliases
                           asserts case-01 yields NO ROWS MATCHED.
DEAD END (recorded)     -> mypy --strict rejected temperature= on messages.create:
                           anthropic SDK 1.2.0 has dropped sampling parameters from the
                           typed signature entirely. The API still accepts temperature
                           on Sonnet 4.6, so the pin passes via extra_body with a
                           caveat comment — a wrong combination fails loudly (400),
                           never silently samples. anthropic==1.2.0 pinned (C-9).
gates                   -> 33/33 tests green; mypy --strict src clean; ruff clean
REPRODUCTION.md         -> prerequisites, env var, test commands, troubleshooting rows
                           filled (3.14 ensurepip dead end + temperature/SDK note)
```

**What this changed about the plan**

Nothing structural; one blocker. The two runs that close step 5 are ready to fire and
BLOCKED only on the operator providing ANTHROPIC_API_KEY:

```
.venv/bin/python eval/run_eval.py --variant baseline --repeats 5 --split dev --seed 42 --tag baseline-noise-floor
.venv/bin/python eval/run_eval.py --split dev --seed 42 --tag baseline-frozen
```

Run 1 establishes the noise floor FIRST (per instruction: variance before any
comparison). Run 2 produces the three-line reference table (baseline, always_abstain,
advanced slot empty — the stub errors by design, error_rate 1.0). After run 2:
CHANGELOG `[0]` citing the results files, baseline FREEZE (CN-3), commit. Estimated
cost of both runs ~140 Sonnet calls ≈ $2.
