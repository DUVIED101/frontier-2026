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
| Baseline eval (§4) | 20 | ~$0.22 | ~4 min |
| Advanced eval (§5) | 20 | ~$0.06 | ~1 min |
| Full three-variant eval (§6) | 40 | ~$0.28 | ~8 min |
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
  (142,988 rows, Open Government Licence v3) plus 30 fictional fixture rows, inserted at
  name-sorted positions. The fixture manifest `fixtures/register_fixture_rows.json` is
  the only marker distinguishing them.
- `fixtures/floor_config.json` — both salary thresholds with sources and effective dates.
- `fixtures/aliases.json` — synthetic trading-name→legal-entity fixtures.
- `case-*.json` — 30 hand-labelled cases (20 dev / 10 holdout).

Provenance and licence for everything: [`docs/DATA.md`](docs/DATA.md).

---

## 4. Run the baseline

```bash
python eval/run_eval.py --variant baseline --split dev --seed 42
```

Output of this exact command as recorded in `eval/results/20260829-083215.json`
(your timestamps will differ; on run-to-run variance see §6):

```
| Metric | baseline |
|---|---|
| verdict_utility | 0.425 |
| confident_wrong_rate | 0.3333 |
| decisive_accuracy | 0.6667 |
| decisive_rate | 0.8462 |
| check_accuracy | 0.85 |
| grounding_rate | 0.9612 |
| cost_per_case_usd | 0.01119 |
| exact_match | 0 |
| error_rate | 0 |
| p50_seconds | 9.566 |
| p95_seconds | 13.54 |
```

Runtime: ~4 minutes, ~$0.22.

---

## 5. Run the solution

```bash
python eval/run_eval.py --variant advanced --split dev --seed 42
```

Output as recorded in `eval/results/20260829-090246.json`:

```
| Metric | advanced |
|---|---|
| verdict_utility | 0.9 |
| confident_wrong_rate | 0.07692 |
| decisive_accuracy | 0.9231 |
| decisive_rate | 1 |
| check_accuracy | 0.9875 |
| grounding_rate | 1 |
| cost_per_case_usd | 0.003123 |
| exact_match | 0.75 |
| error_rate | 0 |
| p50_seconds | 2.094 |
| p95_seconds | 3.872 |
```

Runtime: ~1 minute, ~$0.06. The advanced pipeline reproduces these verdict-level
numbers identically across independent runs (`20260829-085330.json`,
`20260829-090246.json`, `20260829-090655.json`) — one small extraction call plus
deterministic stages.

---

## 6. Run the evaluation

This is the command that produces every number claimed in `README.md` and `CHANGELOG.md`.
With no `--variant` flag it runs all three: baseline, `always_abstain`, advanced.

```bash
python eval/run_eval.py --split dev --seed 42
```

Output of this exact command as recorded in `eval/results/20260829-090655.json`:

```
| Metric | baseline | always_abstain | advanced |
|---|---|---|---|
| verdict_utility | 0.325 | 0.5125 | 0.9 |
| confident_wrong_rate | 0.4 | 0 | 0.07692 |
| decisive_accuracy | 0.6 | 0 | 0.9231 |
| decisive_rate | 0.8462 | 0 | 1 |
| check_accuracy | 0.825 | 0 | 0.9875 |
| grounding_rate | 0.98 | 0 | 1 |
| cost_per_case_usd | 0.01111 | 0 | 0.00312 |
| exact_match | 0 | 0 | 0.75 |
| error_rate | 0 | 0 | 0 |
| p50_seconds | 9.727 | 1.67e-07 | 2.282 |
| p95_seconds | 12.64 | 3.33e-07 | 3.111 |
```

The final full-set run (all 30 cases including the 10-case holdout, Sunday only):

```bash
python eval/run_eval.py --split all --seed 42 --tag final
```

Results are written to `eval/results/<UTC timestamp>.json` and `.md`.

**Determinism and variance.** With `--seed 42` the harness is deterministic except for
model output at temperature 0. Measured across all committed runs: the **baseline's**
verdict_utility has taken three values — 0.225, 0.325 and 0.425 — so its operative
band is 0.225–0.425 (5-repeat noise floor in `eval/results/20260829-002003.json`;
single-prompt judgment flips on borderline cases). Every conservative delta claim in
`CHANGELOG.md` is computed against the top of that band. The **advanced** variant has
reproduced identical numbers across five independent runs, including one from a fresh
clone. Expect your baseline column to land inside the band rather than on the paste
above; expect your advanced column to match its paste exactly.

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

All 68 tests pass on a clean clone in ~5 s; no API key needed.

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
