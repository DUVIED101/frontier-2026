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
| Python | TODO | Only if running without Docker |
| Node.js | TODO | Only if running without Docker |
| API access | TODO | Which provider, which model, which env var. **No key is included in this repo.** |
| Disk | TODO | |

Approximate cost of a full evaluation run: **TODO** (model calls: TODO, tokens: TODO).
Approximate wall-clock time: **TODO**.

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
python -m venv .venv && source .venv/bin/activate
pip install -r docker/requirements.txt
# and/or
npm ci
```

---

## 2. Configure

Copy the example environment file and fill in your own credentials:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| TODO | yes/no | TODO |

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
TODO   # pytest -q   and/or   npm test
npx tsc --noEmit      # if TypeScript
mypy --strict src     # if Python
```

All tests are expected to pass on a clean clone.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| TODO | TODO | TODO |
