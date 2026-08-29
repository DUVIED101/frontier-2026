# Reproduction guide

Written for someone starting from a clean environment with no prior knowledge of this project.
Every command below is meant to be copy-pasted literally, in order.

**This is the qualification gate.** A submission that cannot be run and verified is not scored.
Re-verify this document from a fresh clone before submitting — do not assume it still works.

---

## 0. What you will need

| Requirement | Version | Notes |
|---|---|---|
| Docker | TODO | Recommended path. Everything is pinned inside the image. |
| Python | 3.12 | Only if running without Docker. 3.14 fails on this repo's toolchain — see Troubleshooting. |
| Node.js | — | Not used; the solution is Python-only. |
| API access | Anthropic API | Model `claude-sonnet-4-6` (pinned, both variants — see DECISIONS.md). Env var `ANTHROPIC_API_KEY`. **No key is included in this repo.** |
| Disk | ~50 MB | Repo incl. the gzipped register snapshot (~2 MB). |

Approximate cost of a full evaluation run (dev split, all three variants): **~$0.25**
(20 model calls for the baseline at ~$0.011/case; `always_abstain` and the eval itself
make no model calls). A `--repeats 5` variance run adds ~120 calls ≈ **$1.35**.
Approximate wall-clock time: **~4 minutes** for a single pass, **~25 minutes** with
`--repeats 5` (calls are sequential).

---

## 1. Clone and set up

```bash
git clone <REPO_URL>
cd frontier-2026
```

### Option A — Docker (recommended)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm app bash
```

### Option B — Local

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r docker/requirements.txt
```

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

---

## 3. Data

<!-- Which data is required, where it comes from, how to obtain or generate it. -->

```bash
TODO   # e.g. python eval/generate_fixtures.py --seed 42
```

Expected output: TODO
Provenance and licence: [`docs/DATA.md`](docs/DATA.md).

---

## 4. Run the baseline

```bash
TODO
```

Expected output:

```
TODO
```

Runtime: TODO

---

## 5. Run the solution

```bash
TODO
```

Expected output:

```
TODO
```

Runtime: TODO

---

## 6. Run the evaluation

This is the command that produces every number claimed in `README.md` and `CHANGELOG.md`.

```bash
python eval/run_eval.py --variant baseline --variant advanced --seed 42
```

Expected output:

```
TODO — paste the real table here, not a paraphrase
```

Results are written to `eval/results/<timestamp>.json` and `<timestamp>.md`.

**Determinism.** With `--seed 42` the harness is deterministic except where model
non-determinism is unavoidable. Where it is, run-to-run variance is reported in the results
file and stated explicitly in `CHANGELOG.md`, so a delta can be told apart from noise.

---

## 7. Run the tests

```bash
python -m pytest tests/ -q
python -m mypy --strict src
python -m ruff format --check src/ tests/ eval/*.py conftest.py
```

All tests are expected to pass on a clean clone.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `python3 -m venv` fails at `ensurepip` | Some Python 3.14 builds (e.g. Homebrew's) ship without ensurepip wheels | Use `python3.12 -m venv .venv` — the pinned toolchain targets 3.12 |
| `400 invalid_request_error` mentioning `temperature` | The pinned model/parameter combination changed — newest models reject sampling parameters | Keep the pinned `claude-sonnet-4-6`; the temperature pin is deliberate (DECISIONS.md 2026-08-28) |
| `400` demanding `anthropic-workspace-id` on every call | Identity-linked API keys require a workspace header the code does not send | Use a standard workspace-scoped API key (created inside a Console workspace) for `ANTHROPIC_API_KEY` |
| `No cases with split=...` from `run_eval.py` | `--split` filter matched nothing | Use `--split dev` during development, `--split all` for the final run |
