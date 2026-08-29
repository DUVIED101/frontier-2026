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

### Step 5 (cont.) — Unblocking the API key: two dead ends before a single successful call

**Agent action + tool responses, in order**

```
operator sets .env      -> HUMAN provides the key (value REDACTED here per TR-6)
git tree                -> committed the operator's pending prompts/00-bootstrap.md
                           supersession note first, so both results files record
                           git_dirty=false (evidence must be reproducible from a commit)
smoke test 1 (1 token)  -> FAILED before reaching the API: .env had the key on its own
                           line below "ANTHROPIC_API_KEY=", so sourcing set nothing and
                           zsh tried to EXECUTE the key line ("command not found",
                           printing the key into the local error trace — flagged to the
                           operator with a rotation recommendation). Repaired .env
                           programmatically without displaying it; variable then set.
smoke test 2 (1 token)  -> 400: "anthropic-workspace-id is required when authenticating
                           with an identity-linked API key". The key type demands a
                           workspace header on EVERY request.
discovery probes        -> models.list: same 400 (no unauthenticated discovery path).
                           Literal workspace id "default": 400 "must be a valid
                           workspace ID". Nothing local (no ant CLI, no workspace env
                           var, no ~/.anthropic) knows the id. Genuinely operator-only.
```

> **HUMAN: redirected** — offered two unblocks: paste the workspace ID and wire an
> optional `anthropic-workspace-id` header into the solver pre-freeze, or rotate to a
> standard workspace-scoped key (no header requirement; also retires the key that
> surfaced in the local error trace). Operator chose **rotation** — the solver stays
> untouched and minimal, which is the better shape for a baseline about to freeze.

```
REPRODUCTION.md         -> troubleshooting row added: identity-linked keys 400 on every
                           call demanding anthropic-workspace-id; use a standard
                           workspace-scoped key. A judge reproducing from an org that
                           issues identity-linked keys would hit this wall.
watcher                 -> background wait on .env mtime; smoke test re-runs on save
```

### Step 5 (cont.) — Run 1 (noise floor) complete; gate FAILED; freeze STOPPED

**Agent action + tool responses, in order**

```
run 1                   -> eval/results/20260828-224144.{json,md}: 120 calls, 0 errors,
                           ~26 min, ~$1.32. Noise floor: verdict_utility 0.1 stdev 0.0,
                           confident_wrong_rate 0.4737 stdev 0.0 across 5 repeats —
                           verdict-level metrics are perfectly stable at temperature 0;
                           check_accuracy/grounding jitter <=~0.02 across 6 passes.
                           NOTE: the run recorded git_dirty=true — the REPRODUCTION.md
                           troubleshooting row and this trajectory's own live appends
                           were uncommitted at launch (doc-only, content-inert to the
                           eval; named here for honesty). Committed before any next run.
gate check              -> operator's pre-freeze condition: baseline must FAIL cases
                           01, 07, 11, 13, 26. RESULT: 4 of 5 produced the CORRECT
                           verdict (only 26 failed as predicted). STOP condition fired:
                           no CHANGELOG [0], no freeze, run 2 withheld.
mechanism dig           -> per-check outputs revealed register fail/no_match on cases
                           whose expected reason is legal_name_exact (07,13,20,26,27).
                           First probe of register_context() printed "HIT" for those
                           cases — misleading (it tested only != NO ROWS MATCHED).
                           Second probe printed the rows actually delivered: for 07 the
                           first candidate "Integrations" substring-matched 6 unrelated
                           orgs (BI INTEGRATIONS LTD, Power Integrations UK Limited...);
                           for 20 "Payments" matched 20 payment companies. The employer
                           row NEVER reached the model; the model truthfully reported
                           the employer absent from the rows it was given.
DIAGNOSIS               -> three distinct causes behind the gate failure:
                           (a) DEFECT: first-candidate-with-hits wins + substring
                               containment lets surviving job-title segments
                               ("Integrations", "Payments", "Reporting", "ETL") shadow
                               the real employer name. By the baseline's own docstring
                               (a person Ctrl-Fs the employer's NAME) this is a bug,
                               not designed blindness. Corrupts 07/13/20/26/27; the
                               route trap in 07 was never administered (GBM rows never
                               reached the model).
                           (b) PROMPT TOO STRONG: case-11 passed legitimately — the
                               system prompt narrates BOTH thresholds plus "the higher
                               of the two applies" plus the guaranteed-basic exclusion
                               list plus reason enums: the author's expert knowledge,
                               beyond PLAN §4's "checks described in plain language".
                           (c) STRUCTURAL: case-01's false-SPONSORABLE trap requires
                               world-knowledge priors that fictional brands cannot
                               trigger; no-match -> NS collapses onto the correct
                               verdict for ANY baseline. The case discriminates at
                               check level (register pass/alias vs fail/no_match), not
                               at verdict level. A consequence of the synthetic-fixture
                               decision, discovered only under a live model.
                           Also observed: 13's wrapper trap half-failed on model
                           strength (Sonnet chose the body salary over the wrapper's
                           £45,000 even with junk register rows); 26 fired as designed
                           even with the strong prompt (RTW boilerplate -> "refused").
```

> **HUMAN checkpoint pending** — stop report delivered with per-case attribution and a
> recommendation (fix the shadow-candidate defect with a generic-term guard; roll the
> prompt back to basic instructions in ONE principled step, then accept the re-run's
> gate outcome without iterating — tuning the baseline down until cases fail would bend
> the eval). Freeze, run 2, CHANGELOG [0] all withheld until the ruling.

### Step 5 (cont.) — Checkpoint: rebuild approved under conditions; bar set before the number

> **HUMAN: approved** — fix the lookup defect and roll the prompt back, re-run, bring
> the new gate table before freezing. Conditions, verbatim in substance:
>
> **A — one rollback, then accept.** The prompt goes back to basic instructions ONCE.
> Whatever the re-gate produces is the baseline. If a fair prompt with correct rows
> still reads the route column right on 07, that is a finding about current models and
> those cases are re-designated check-level discriminators with a DECISIONS entry.
> No second pass.
> **B — defect fix scoped as a defect fix.** The guard encodes "this is not a name",
> never "this case needs help". No stoplist additions, no per-case tuning. Pinned by a
> test that fails on the old behaviour. The pre-fix numbers were depressed by a defect
> and are NOT the baseline — the rubric asks for gains over a FAIR baseline.
> **C — the same prompt discipline binds the advanced solution.** Coaching removed from
> the baseline does not reappear as hardcoded rules in the advanced extraction prompt.
> Going-rate logic lives in the rules engine, reading floor_config. Code decides, the
> model extracts.
> Also ordered: case-01 verdict-level limitation -> DECISIONS + README limitations
> (case stays as check-level discriminator). Problem framing rewritten — the scarce
> resource is attention/calendar time under a visa deadline, not "irreplaceable"
> applications; the 10-20 min manual cost is the author's own measurement and gets
> actually measured Sunday. Two new metrics (decisive_accuracy, decisive_rate) with a
> pre-registered target BEFORE Saturday's build: advanced must beat baseline on
> verdict_utility AND beat always_abstain on decisive_rate while holding
> decisive_accuracy high — passing verdict_utility by abstaining more is not the claim.
> Rubric inventory due with the re-gate report. Timebox: this is the last
> measurement-axis work before the advanced build.

**ACCEPTANCE CRITERION — recorded before the re-run, per Condition A.**
The re-gate runs once, on the fixed lookup and the rolled-back prompt. Its outcome is
final:
- A gate case the baseline now answers correctly WITH correct evidence is a finding
  about current models; the case is re-designated a check-level discriminator
  (DECISIONS entry + README limitations). No prompt change follows.
- A gate case answered correctly with WRONG evidence (e.g. 01 via no_match) is recorded
  as verdict-level non-discriminating, check-level discriminating.
- Gate cases that fail as designed stay verdict-level discriminators.
Predictions logged ahead of the number: 01 correct-by-coincidence (structural); 26
fails as designed (RTW misread survived even the strong prompt); 13 likely correct
legitimately (Sonnet chose the body salary over the wrapper unprompted in run 1);
07 and 11 genuinely open — they are what the re-gate decides.

### Step 5 (cont.) — Rebuild implemented under the conditions; framing corrected mid-flight

**Agent action + tool responses, in order**

```
TDD                     -> 8 tests written/revised first, all RED as intended: lookup
                           pin (case-07 employer must beat "Integrations"), hit-flood
                           pin ("Software" -> NO ROWS MATCHED), coaching-absence pin,
                           2x decisive_accuracy, 2x decisive_rate, locked-name-set.
guard design deviation  -> the sketched fix (skip candidates with >20 hits) does NOT
                           fix case-07: "Integrations" matches only 6 register orgs.
                           Any threshold separating 6 from a real name's 1-3 hits would
                           be case-tuned — forbidden by Condition B's own scope. Chosen
                           instead: specificity ordering (fewest hits wins; >cap means
                           generic). Parameter-free; recorded in DECISIONS.
implement               -> register_context rewritten; build_prompt rolled back ONCE:
                           four plain questions, floor figures as data, output
                           contract; removed reason enums, "higher of the two",
                           guaranteed-basic exclusions, verdict rules.
gates                   -> 38/38 green; mypy --strict clean; ruff clean. The alias-
                           blindness pin (case-01 -> NO ROWS MATCHED) held UNCHANGED
                           under the new lookup — blindness preserved, not widened.
delivery map (no API)   -> all 14 exact-name dev cases now deliver the employer's row
                           (case-25 delivers all 3 ambiguous-group rows); 01/15/24
                           NO_MATCH by design; 04/06 junk-or-nothing by design.
commits                 -> 150b0c8 fix(baseline), 51af9fa eval(metrics)
```

> **HUMAN: redirected (mid-implementation)** — human-time claim corrected before it
> reaches README: the 10–20-minute figure described CSV-era manual work, not the
> author's actual process (one prompt against a chat with the register loaded, ~1 min —
> which is exactly what the baseline implements). Consequences ordered: (1) README
> states the baseline is a faithful reproduction of the manual process in use today —
> the brief's own legitimate-baseline category, qualifying literally; (2) human time is
> measured as TIME-TO-A-TRUSTWORTHY-ANSWER — Sunday protocol: three requisitions, both
> variants, timed to the act-on-it point INCLUDING verification of wrong/unsupported
> answers; (3) "10–20 minutes" banned from the repo outside this record. PLAN §1
> rewritten (attention under a visa deadline, form-cheap/process-expensive,
> asymmetric-and-unauditable errors); DECISIONS entry pre-registers the protocol.

### Step 5 (cont.) — Re-gate under the pre-set bar: 3 of 5 fire; outcome accepted

**Agent action + tool responses, in order**

```
run 1v2                 -> eval/results/20260829-002003.{json,md}, clean tree, 120
                           calls, 0 errors. Noise floor v2 — REAL this time:
                           verdict_utility mean 0.265 stdev 0.049 (0.225-0.325),
                           confident_wrong_rate mean 0.44 stdev 0.033,
                           check_accuracy 0.8075 stdev 0.020, grounding 0.964. The
                           basic-instructions prompt is less stable than the coached
                           one (borderline cases flip across repeats): Saturday deltas
                           on verdict_utility must clear ~0.1 (2 sigma) to be real.
re-gate (seed-42 pass)  -> 07 FIRES: false SPONSORABLE — model read the "Worker
                           (A rating)" Type & Rating column as covering the Skilled
                           Worker route while the Route column says GBM (§3 failure 2,
                           exactly as designed, worst-direction error).
                           11 FIRES: false SPONSORABLE — salary check itself FAILED,
                           and without combination rules the model waved the failing
                           check through to a SPONSORABLE verdict.
                           26 FIRES: RTW boilerplate -> "refused" -> NOT_SPONSORABLE,
                           robust across both prompt strengths.
                           01: correct-by-coincidence via no_match, exactly as the
                           pre-registered prediction stated — check-level evidence
                           chain wrong (register fail/route fail vs expected
                           pass/fail). Stays check-level per FINDING (c).
                           13: correct WITH correct evidence — Sonnet chose the body's
                           £29,000 over the wrapper's £45,000 unprompted, second time.
                           Acceptance criterion applied: re-designated regression
                           guard; DECISIONS entry written.
                           Also newly honest failures: 20 clean-silent -> SPONSORABLE
                           (silence read optimistically), 29 straddle -> SPONSORABLE,
                           28 rating-blind -> SPONSORABLE, 04/06 now abstain (U)
                           instead of wrong-NS.
metrics                 -> baseline utility 0.265 sits 0.25 BELOW the always_abstain
                           floor (0.5125): today's manual process scores worse on
                           utility than not asking at all, while decisive_rate 0.846
                           (stdev 0) shows it answers almost everything. The
                           reframed §1 sentence is now a measured number.
run 2                   -> three-line reference table launched (tag baseline-frozen)
```

### Step 5 (cont.) — Reference table produced; own process error repeated and corrected

**Agent action + tool responses, in order**

```
run 2                   -> eval/results/20260829-002446.{json,md}: the three-line
                           table. baseline 0.225 / always_abstain 0.5125 / advanced
                           error_rate 1.0 (stub, the deliberate empty slot). decisive
                           pair behaves exactly as designed: abstain scores
                           decisive_rate 0, baseline 0.846.
PROCESS ERROR (repeat)  -> the run recorded git_dirty=true AGAIN: the DECISIONS and
                           trajectory appends written while the run launched were
                           uncommitted — the same mistake that dirtied the first
                           noise-floor run, made twice in one night despite being
                           named the first time. The freeze-anchor evidence file must
                           not carry a dirty flag. Correction: ALL doc edits committed
                           first (including REPRODUCTION cost figures), then a clean
                           re-run replaces the reference table; 20260829-002446 stays
                           committed as an honest superseded intermediate. Lesson
                           recorded: commit BEFORE launching a run, and touch nothing
                           until it exits.
```
