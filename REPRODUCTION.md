# Reproduction guide

Written for someone starting from a clean environment with no prior knowledge of this project.
Every command below is meant to be copy-pasted literally, in order.

**This is the qualification gate.** A submission that cannot be run and verified is not scored.
Re-verify this document from a fresh clone before submitting — do not assume it still works.

---

## 0. What you will need

| Requirement | Version | Notes |
|---|---|---|
| Python | **3.12** | Required for the local path. **3.14 fails at `venv` creation** (Homebrew builds ship without ensurepip wheels) — use 3.12, see Troubleshooting. |
| Docker | 28.x (tested 28.4.0, 2026-08-29) | Optional alternative path. Image `python:3.12-slim-bookworm`; build + full test suite + eval harness verified in-container. |
| Node.js | — | Not used; the solution is Python-only. The `docker/Dockerfile.node` scaffold is unused and declared in README. |
| API access | Anthropic API | Model `claude-sonnet-4-6` (pinned, both variants — DECISIONS.md 2026-08-28). Env var `ANTHROPIC_API_KEY`. **No key is included in this repo.** |
| Disk | ~60 MB | Repo (~2.4 MB archive incl. the gzipped register snapshot) + venv. |

Measured cost and wall-clock per command (from the committed results files, model calls
priced at $3/$15 per MTok):

| Command | Model calls | Cost | Wall clock |
|---|---|---|---|
| Test suite (§7) | 0 | $0 | ~5 s |
| Baseline eval (§4) | 22 | ~$0.25 | ~4 min |
| Advanced eval (§5) | 22 | ~$0.07 | ~1 min |
| Full three-variant eval (§6) | 44 | ~$0.32 | ~9 min |
| Optional noise floor (`--repeats 5`, §6) | 120 | ~$1.35 | ~25 min |

---

## 1. Clone and set up

```bash
git clone <REPO_URL>
cd frontier-2026
```

### Option A — Local venv (primary; every committed number was produced this way)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r docker/requirements.txt
```

### Option B — Docker (verified 2026-08-29: build, full suite and eval harness in-container)

```bash
docker compose -f docker/docker-compose.yml build app
docker compose -f docker/docker-compose.yml run --rm app bash
```

Inside the container the repo is mounted at `/app` and `.env` is loaded via
`env_file`; run the same commands as the local path, without the `.venv` activation.

---

## 2. Configure

Copy the example environment file and fill in your own credentials:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | yes | Model calls made by the baseline and advanced solvers. The `always_abstain` reference variant and the test suite run without it. |

No credential is committed to this repository. Nothing here will work without your own key.
The eval runner reads the environment, not `.env` — export the variable or source the file:

```bash
set -a; source .env; set +a
```

---

## 3. Data

**Nothing to download, generate, or fetch — the evaluation never touches the network.**
All data ships committed in `eval/cases/`:

- `fixtures/sponsor-register-2026-08-28.csv.gz` — the real Home Office register snapshot
  (142,988 rows, Open Government Licence v3) plus 32 fictional fixture rows at
  name-sorted positions (placement history and the invariance proof:
  `docs/DATA.md`, `eval/verify_snapshot_invariance.py`). The fixture manifest
  `fixtures/register_fixture_rows.json` is the only marker distinguishing them.
- `fixtures/floor_config.json` — both salary thresholds with sources and effective dates.
- `fixtures/aliases.json` — synthetic trading-name→legal-entity fixtures.
- `case-*.json` — 32 hand-labelled cases (22 dev / 10 holdout).

Provenance and licence for everything: [`docs/DATA.md`](docs/DATA.md).

---

## 4. Run the baseline

```bash
python eval/run_eval.py --variant baseline --split dev --seed 42
```

Output of this exact command as recorded in `eval/results/20260830-101719.json`
(your timestamps will differ; on run-to-run variance see §6):

```
| Metric | baseline |
|---|---|
| verdict_utility | 0.2955 |
| confident_wrong_rate | 0.4118 |
| decisive_accuracy | 0.5882 |
| decisive_rate | 0.8667 |
| check_accuracy | 0.8409 |
| grounding_rate | 0.9561 |
| cost_per_case_usd | 0.01137 |
| exact_match | 0 |
| error_rate | 0 |
| p50_seconds | 9.832 |
| p95_seconds | 13.11 |
```

Runtime: ~4 minutes, ~$0.25.

---

## 5. Run the solution

```bash
python eval/run_eval.py --variant advanced --split dev --seed 42
```

Output as recorded in `eval/results/20260830-101815.json`:

```
| Metric | advanced |
|---|---|
| verdict_utility | 0.9091 |
| confident_wrong_rate | 0.06667 |
| decisive_accuracy | 0.9333 |
| decisive_rate | 1 |
| check_accuracy | 0.9886 |
| grounding_rate | 1 |
| cost_per_case_usd | 0.003161 |
| exact_match | 0.9545 |
| error_rate | 0 |
| p50_seconds | 2.238 |
| p95_seconds | 2.885 |
```

Runtime: ~1 minute, ~$0.07. The advanced pipeline reproduces its verdict-level
numbers identically across independent runs at every case-set size it has been
measured on (dev n=20, dev n=22, and the dev columns of the full-set final run —
e.g. `20260830-101815.json`, `20260830-102249.json`, `20260830-101148.json`, and a
fresh-clone run on 2026-08-30) — one small extraction call plus deterministic
stages.

### Demo: one pasted posting (the video walkthrough path)

Save any job posting as plain text and run:

```bash
python -m src.advanced.cli path/to/posting.txt
```

One model call (~$0.003, ~2 s), then resolution against the committed snapshot, the
rules engine, and the rendered verification report on stdout. This is the product as
the user meets it — no case files, no harness.

---

## 6. Run the evaluation

This is the command that produces every number claimed in `README.md` and `CHANGELOG.md`.
With no `--variant` flag it runs all three: baseline, `always_abstain`, advanced.

```bash
python eval/run_eval.py --split dev --seed 42
```

Output of this exact command as recorded in `eval/results/20260830-102249.json`:

```
| Metric | baseline | always_abstain | advanced |
|---|---|---|---|
| verdict_utility | 0.2955 | 0.4886 | 0.9091 |
| confident_wrong_rate | 0.4118 | 0 | 0.06667 |
| decisive_accuracy | 0.5882 | 0 | 0.9333 |
| decisive_rate | 0.8667 | 0 | 1 |
| check_accuracy | 0.8409 | 0 | 0.9886 |
| grounding_rate | 0.9561 | 0 | 1 |
| cost_per_case_usd | 0.01118 | 0 | 0.003166 |
| exact_match | 0 | 0 | 0.9545 |
| error_rate | 0 | 0 | 0 |
| p50_seconds | 10.02 | 1.67e-07 | 2.049 |
| p95_seconds | 11.88 | 3.34e-07 | 3.53 |
```

The final full-set run (all 32 cases including the 10-case holdout, run once):

```bash
python eval/run_eval.py --split all --seed 42 --tag final
```

Its output as recorded in the run of record, `eval/results/20260830-101148.json`
(dev/holdout breakdown: `eval/results/final-breakdown-2026-08-30.md`):

```
| Metric | baseline | always_abstain | advanced |
|---|---|---|---|
| verdict_utility | 0.5547 | 0.4844 | 0.9375 |
| confident_wrong_rate | 0.2609 | 0 | 0.04545 |
| decisive_accuracy | 0.7391 | 0 | 0.9545 |
| decisive_rate | 0.8636 | 0 | 1 |
| check_accuracy | 0.8125 | 0 | 0.9922 |
| grounding_rate | 0.9371 | 0 | 1 |
| cost_per_case_usd | 0.01118 | 0 | 0.003142 |
| exact_match | 0 | 0 | 0.9688 |
| error_rate | 0 | 0 | 0 |
| p50_seconds | 9.652 | 1.67e-07 | 2.099 |
| p95_seconds | 12.36 | 5e-07 | 3.38 |
```

Results are written to `eval/results/<UTC timestamp>.json` and `.md`.

**Tagged runs demand a clean tree.** With `--tag` set the harness refuses to start —
before any model call — if the working tree is dirty with anything beyond your own
previous runs' untracked results files. A tagged results file is a source of record
and must reproduce from its commit. Untagged runs (the commands in §§4–6 above) only
warn.

**Determinism and variance.** With `--seed 42` the harness is deterministic except for
model output at temperature 0. The dev split grew from 20 to 22 cases on 2026-08-29
(cases 31 and 32, added after live inputs exposed fixture blind spots — CHANGELOG
[10]/[11]), so aggregates across different case counts are not directly comparable;
per-case verdicts are. Measured at n=20, the **baseline's** verdict_utility took three
values — 0.225, 0.325, 0.425 (5-repeat noise floor in
`eval/results/20260829-002003.json`); single-prompt judgment flips on borderline
cases, and conservative delta claims in `CHANGELOG.md` are computed against the worst
committed baseline figure. The **advanced** variant has reproduced identical numbers
across every independent run at each case-set size, including one from a fresh clone.
Expect your baseline column to differ from the paste above; expect your advanced
column to match its paste exactly on every verdict-level metric —
`cost_per_case_usd` can shift in its final digit with token-count jitter, and the
latency rows are your machine's (verified from a fresh clone, 2026-08-30).

**Expected warning.** From your second run onward the harness prints
`WARNING: working tree is dirty` — it is seeing your own previous run's results files,
which are untracked in your clone. Harmless for verification.

---

## 7. Run the tests

```bash
python -m pytest tests/ -q
python -m mypy --strict src
python -m ruff format --check src/ tests/ eval/*.py conftest.py
```

All 104 tests pass on a clean clone in ~5 s; no API key needed.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `python3 -m venv` fails at `ensurepip` | Some Python 3.14 builds (e.g. Homebrew's) ship without ensurepip wheels | Use `python3.12 -m venv .venv` — the pinned toolchain targets 3.12 |
| `400 invalid_request_error` mentioning `temperature` | The pinned model/parameter combination changed — newest models reject sampling parameters | Keep the pinned `claude-sonnet-4-6`; the temperature pin is deliberate (DECISIONS.md 2026-08-28) |
| `400` demanding `anthropic-workspace-id` on every call | Identity-linked API keys require a workspace header the code does not send | Use a standard workspace-scoped API key (created inside a Console workspace) for `ANTHROPIC_API_KEY` |
| `No cases with split=...` from `run_eval.py` | `--split` filter matched nothing | Use `--split dev` during development, `--split all` for the final run |
| `Cannot connect to the Docker daemon` | Docker Desktop not running | Start Docker Desktop, or use the local venv path (Option A) |
| `WARNING: working tree is dirty` after a run | Your previous run's results files are untracked in your clone | Expected; harmless for verification (see §6) |
| `REFUSED: --tag is set and the working tree is dirty` | Tagged runs must reproduce from their commit; a file beyond your own untracked results files is modified or new | Commit or stash the files it lists — prior results files alone never trigger this |
