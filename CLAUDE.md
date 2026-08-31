# frontier-2026 — Agent Operating Guidelines

Entry for micro1 Frontier Engineering Challenge 2026 (Aug 28–31, 2026).

This file is the contract every coding agent works under. It is a **submission artifact**:
the challenge requires shipping "the instructions that shape each agent". Keep it accurate.

---

## 0 — Competition constraints that override everything

- **CN-1 (MUST)** Every result claim in `README.md` or `CHANGELOG.md` points at a committed
  evidence file under `eval/results/`. No unbacked numbers.
- **CN-2 (MUST)** The repo must run from a clean environment using only `REPRODUCTION.md`.
  A change that breaks clean-clone reproduction is a blocker, regardless of how good it is.
- **CN-3 (MUST)** Baseline stays runnable for the entire competition. Never delete it,
  never "upgrade" it, never let it rot. The measured delta is the submission.
- **CN-4 (MUST)** No credentials, API keys, tokens, `.env` contents, or personal data in the repo.
  Config comes from environment variables with documented names only.
- **CN-5 (MUST)** Every agent session that writes files records a trajectory in
  `trajectories/`; a plan-only session (no file writes, no tool calls) records its
  output as a committed document instead — `docs/PLAN.md` is that record for
  prompt 00. See section 6. *(Amended 2026-08-30 to what the practice actually
  became; the original read "every agent session writes a trajectory".)*
- **CN-6 (MUST)** Consequential actions (network writes, filesystem outside the repo, payments,
  external side effects) run against a sandbox or simulation, behind an explicit
  `--allow-effects` flag that defaults to off.
- **CN-7 (MUST)** Only public or synthetic data. Generated fixtures are preferred over any
  real dataset. If a dataset is used, its licence goes in `docs/DATA.md`.
- **CN-8 (MUST)** Work created before kickoff (16:00 London, 28 Aug) stays declared in the
  `Pre-existing work` section of `README.md`. Do not backdate, do not rewrite history.

---

## 1 — Before coding

- **BP-1 (MUST)** Ask clarifying questions before starting non-trivial work.
- **BP-2 (MUST)** For any task beyond a single file, produce a written plan first and wait
  for approval.
- **BP-3 (SHOULD)** If two or more approaches exist, list them with pros and cons and a
  recommendation. State the cost of being wrong.
- **BP-4 (MUST)** Before implementing, state which evaluation metric this change is expected
  to move and in which direction. If it moves nothing measurable, say so — that is a valid
  answer and usually means the change should not be made.

---

## 2 — While coding

- **C-1 (MUST)** TDD: scaffold stub → write failing test → implement until green.
- **C-2 (MUST)** Reuse the existing domain vocabulary of the codebase for names.
- **C-3 (SHOULD NOT)** Introduce classes where small testable functions suffice.
- **C-4 (SHOULD)** Prefer simple, composable, pure functions. Push I/O to the edges.
- **C-5 (MUST)** Every operation that can fail returns an explicit error value or raises a
  typed error. No silent `except: pass`, no swallowed promise rejections.
- **C-6 (MUST)** Determinism by default: seed every random source, pin every model
  temperature, freeze every clock in tests. Non-determinism must be opt-in and documented.
- **C-7 (SHOULD NOT)** Add comments except for critical caveats and non-obvious invariants.
- **C-8 (SHOULD NOT)** Extract a function unless it is reused, is the only way to unit-test
  otherwise untestable logic, or drastically clarifies an opaque block.
- **C-9 (MUST)** No dependency added without a one-line justification in the commit body.
  Every dependency is pinned to an exact version.

### TypeScript-specific *(unused — this submission is Python-only; kept from the pre-kickoff scaffold, no TS surface exists)*
- **TS-1 (MUST)** Branded types for identifiers: `type JobId = Brand<string, 'JobId'>`.
- **TS-2 (MUST)** `import type { … }` for type-only imports.
- **TS-3 (SHOULD)** Default to `type`; use `interface` only for merging or readability.
- **TS-4 (MUST)** `strict: true`. No `any`, no non-null assertions without a caveat comment.

### Python-specific
- **PY-1 (MUST)** Full type hints on every public function. `mypy --strict` passes.
- **PY-2 (MUST)** Dataclasses or Pydantic models for structured data, never bare dicts
  crossing a module boundary.
- **PY-3 (SHOULD)** `pathlib` over string paths, `logging` over `print` outside CLI output.

---

## 3 — Testing

- **T-1 (MUST)** Unit tests colocate with source (`*.spec.ts` / `test_*.py`).
- **T-2 (MUST)** Pure-logic unit tests stay separate from integration tests that touch
  I/O, a database, or a model API.
- **T-3 (SHOULD)** Prefer integration tests over heavy mocking.
- **T-4 (MUST)** Every acceptance criterion in the problem statement has at least one test
  named after it.
- **T-5 (SHOULD)** Assert on the whole structure in one assertion where possible.
- **T-6 (MUST)** Parameterize inputs. Never embed unexplained literals like `42` or `"foo"`.
- **T-7 (MUST)** Compare against independent, pre-computed expectations — never against the
  function's own output.
- **T-8 (MUST)** Strong assertions: `toEqual(1)` / `== 1`, not `toBeGreaterThanOrEqual(1)`.
- **T-9 (SHOULD)** Cover edge cases, realistic input, hostile input, and value boundaries.
- **T-10 (SHOULD NOT)** Test what the type checker already guarantees.
- **T-11 (SHOULD NOT)** Add a test that cannot fail for a real defect.

---

## 4 — Repository layout

```
frontier-2026/
├── CLAUDE.md                 # this file — agent contract
├── README.md                 # submission narrative (judged)
├── REPRODUCTION.md           # clean-environment guide (qualification gate)
├── CHANGELOG.md              # Improvement Changelog (judged)
├── LICENSE                   # MIT; register data stays OGL v3 (docs/DATA.md)
├── conftest.py               # makes the repo root importable for pytest
├── src/
│   ├── baseline/             # FROZEN after first green run. Never edited again.
│   └── advanced/             # all improvement work lands here; cli.py is the demo entrypoint
├── tests/
├── eval/
│   ├── run_eval.py           # single entrypoint; flag-less default runs all three variants
│   ├── metrics.py            # metric definitions — the contract for every claim
│   ├── verify_snapshot_invariance.py  # committed proof for the snapshot rebuild
│   ├── collision_sweep.py    # designed employer strings vs the committed snapshot
│   ├── split_breakdown.py    # dev/holdout re-aggregation of a results file
│   ├── cases/                # test cases / fixtures
│   └── results/              # committed JSON + markdown, one per run
├── trajectories/             # agent session records
├── docker/                   # pinned runtimes
├── prompts/                  # reusable agent prompts
└── docs/
    ├── PLAN.md               # approved plan + dated divergence status block
    ├── DECISIONS.md          # why, not what
    ├── DATA.md               # provenance and licence of any data used
    ├── TIMING.md             # time-to-a-trustworthy-answer measurements
    └── VIDEO.md              # timed video script
```
*(Layout updated 2026-08-30 to match the shipped tree.)*

---

## 5 — Tooling gates

- **G-1 (MUST)** Formatter passes: `prettier --check .` and/or `ruff format --check .`
- **G-2 (MUST)** Type check passes: `npx tsc --noEmit` and/or `mypy --strict src`
- **G-3 (MUST)** Full test suite green before any commit that claims a result.
- **G-4 (MUST)** `python eval/run_eval.py` — flag-less, so the default three-variant
  run includes the trivial-abstention floor; the flagged two-variant form is exactly
  what left `always_abstain` out of a run of record — runs to completion before any
  `CHANGELOG.md` entry is written. *(Amended 2026-08-30.)*

---

## 6 — Trajectory capture

Non-negotiable. Tie-break criterion #1 is agent solution and engineering quality, and the
submission requires trajectories showing tool responses, the feedback that shaped the next
step, retries, and human checkpoints. These are captured live, never reconstructed.

- **TR-1 (MUST)** One file per session: `trajectories/YYYY-MM-DD-HHMM-<slug>.md`.
- **TR-2 (MUST)** Each file opens with the header block from
  `trajectories/TEMPLATE.md` — agent, model, tools granted, task, expected metric impact.
- **TR-3 (MUST)** Record every tool call and what came back, including failures. Failed
  attempts and retries are the most valuable content in the file — do not clean them up.
- **TR-4 (MUST)** Mark every human checkpoint explicitly: `> HUMAN: approved / rejected /
  redirected — <reason>`.
- **TR-5 (MUST)** Close each session with: what changed, which metric moved, what was
  discarded and why.
- **TR-6 (MUST)** Redact secrets and personal data at capture time, not later.

---

## 7 — Git

- **GH-1 (MUST)** Conventional Commits: `<type>[scope]: <description>`.
  Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `perf`, `test`, `eval`.
- **GH-2 (MUST NOT)** Reference Claude, Anthropic, or any AI tool in commit messages.
- **GH-3 (MUST NOT)** Add any AI tool as commit co-author.
- **GH-4 (MUST)** Commit after every green test run. Small commits; the history is evidence
  of process and is read by judges.
- **GH-5 (MUST NOT)** Force-push or rewrite history on `main`. The timeline is part of the
  pre-existing-work declaration.

---

## 8 — Definition of done (per improvement)

An improvement is done only when all of the following hold:

1. Tests pass, gates G-1 through G-4 pass.
2. `eval/results/` contains a fresh run comparing baseline and advanced.
3. `CHANGELOG.md` has an entry citing that results file by filename.
4. A trajectory file for the session exists in `trajectories/`.
5. `REPRODUCTION.md` still works from a clean clone — verified, not assumed.

Anything short of all five is work in progress, not an improvement.

---

## Shortcuts

### QNEW
```
Read CLAUDE.md in full. All MUST rules are binding for everything that follows.
Confirm which rules apply to the task at hand before starting.
```

### QPLAN
```
Analyze the existing codebase and produce a plan that:
- is consistent with existing patterns
- introduces minimal change
- reuses existing code
- names the eval metric it is expected to move, and in which direction
Wait for approval before implementing.
```

### QCODE
```
Implement the approved plan.
Write the failing test first, then implement until green.
Run the full test suite. Run the formatter. Run the type checker.
Do not commit until all gates pass.
```

### QCHECK
```
You are a skeptical senior engineer reviewing this change.
Check it against sections 1, 2 and 3 of CLAUDE.md.
Every MUST violation is a blocker; list each one with file and line.
Finish with exactly one of: OVERALL: APPROVED / OVERALL: CHANGES_REQUESTED
```

### QEVAL
```
Run: python eval/run_eval.py   # flag-less — the default includes the abstention floor (G-4)
Report the metric table. State whether the delta is real or within run-to-run noise,
and justify that judgment from the numbers.
If the delta is noise, say so plainly and recommend reverting.
```

### QLOG
```
Write the CHANGELOG.md entry for the change just completed.
Use the exact template at the top of CHANGELOG.md.
Cite the eval/results/ filename. Numbers must match that file exactly.
No claim without a corresponding file.
```

### QTRACE
```
Write the trajectory file for this session to trajectories/YYYY-MM-DD-HHMM-<slug>.md
using trajectories/TEMPLATE.md.
Include the failed attempts and retries. Do not sanitize them.
```

### QREPRO
```
Read REPRODUCTION.md as if you had just cloned this repo and know nothing about it.
Execute every command literally, in order, in a clean container.
Report every step where the document is wrong, incomplete, or assumes context.
This is the qualification gate — treat any gap as a blocker.
```

### QGIT
```
Stage all changes, commit, push.
Conventional Commits format. No AI tool referenced. No co-author.
```

---

## Agent orchestration

### QORCHESTRATE

On `qorchestrate: [task]`:

**Step 1 — Read context.** `CLAUDE.md`, `README.md`, `docs/DECISIONS.md`, `eval/metrics.py`,
and the latest file in `eval/results/`.

**Step 2 — Plan and chunk.** Split by layer, only the chunks the task needs. Chunks must be
independent; if one depends on another's unfinished output, sequence them instead.

| Chunk | Scope |
|-------|-------|
| `core` | `src/advanced/` — primary logic |
| `agents` | agent instruction files and prompt templates |
| `eval` | `eval/metrics.py`, `eval/cases/` — metric and case definitions |
| `tests` | `tests/` — test coverage for the change |
| `docs` | `README.md`, `CHANGELOG.md`, `REPRODUCTION.md` |

**Step 3 — Spawn one agent per chunk** with this prompt:

```
You are a senior engineer working on frontier-2026, a competition entry for the
micro1 Frontier Engineering Challenge 2026.

Before writing any code:
1. Read CLAUDE.md in full.
2. Read docs/DECISIONS.md for prior decisions and their reasoning.
3. Read eval/metrics.py — this is the contract every claim is measured against.
4. Read existing files in your chunk's directory and match their patterns.

Your chunk: [CHUNK]
Your task: [TASK]

Rules:
- Only touch files inside your chunk's scope.
- Every MUST rule in CLAUDE.md is a blocker.
- Never edit src/baseline/ — it is frozen (CN-3).
- Seed every random source; the run must be deterministic (C-6).
- Failing test first, then implement (C-1).
- Run the formatter and type checker on everything you touch.

Report exactly one of:
DONE: [files created/modified] + [which metric this should move, and why]
BLOCKED: [specific reason]
```

**Step 4 — Review agent.** After all chunks report DONE:

```
You are a skeptical senior engineer reviewing this change set for frontier-2026.

Review every changed file against:
1. CLAUDE.md — every MUST rule. Each violation is a blocker.
2. Correctness — no broken imports, types consistent across boundaries, no
   non-determinism, no secrets, src/baseline/ untouched.
3. Evidence — does any claim exist that eval/results/ does not support?

Per file:
  APPROVED: [filename]
  or
  CHANGES_REQUESTED: [filename]
    - Line X: [issue]

Final line: OVERALL: APPROVED  or  OVERALL: CHANGES_REQUESTED
```

**Step 5 — Loop or proceed.**
- `CHANGES_REQUESTED` → route specific feedback back to the owning chunk agent.
  Maximum 2 iterations, then stop and output `NEEDS HUMAN REVIEW: [file] — [reason]`.
- `APPROVED` → run gates G-1 to G-4, then QEVAL, then QLOG, then QTRACE, then QGIT.

**Step 6 — Record.** If the change involved a real decision (a tradeoff, a rejected
alternative, a constraint discovered), append it to `docs/DECISIONS.md`. If an experiment
was tried and discarded, record it there too — the submission video explicitly asks for one
experiment that was removed.
