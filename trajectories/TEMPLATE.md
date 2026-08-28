# Trajectory — <slug>

<!-- Copy to trajectories/YYYY-MM-DD-HHMM-<slug>.md at the START of a session.
     Fill it live. Reconstructing this afterwards is visible and loses the point.
     Tie-break criterion #1 is agent solution and engineering quality — this file is that evidence. -->

| Field | Value |
|---|---|
| Date (UTC) | |
| Agent | |
| Model | |
| Tools granted | |
| Instruction file | `CLAUDE.md` (+ any prompt from `prompts/`) |
| Task | |
| Expected metric impact | which metric, which direction, why |
| Commit at start | |

---

## Session

### Step 1 — <what the agent set out to do>

**Agent action**

```
<the tool call: command, file edit, search — verbatim>
```

**Tool response**

```
<what came back, verbatim, truncated only if huge and marked as truncated>
```

**What this changed about the plan**

<the feedback that shaped the next step. This sentence is the reason the file exists.>

---

### Step 2 — ...

<!-- Keep failures and retries. A trajectory where nothing went wrong reads as edited. -->

> **RETRY:** attempt 1 failed because <reason>. Changed <what> and retried.

> **HUMAN: approved** — <reason>
> **HUMAN: rejected** — <reason, and what was done instead>
> **HUMAN: redirected** — <the new instruction and why it was given>

---

## Close

**Shipped:** files created or modified
**Metric moved:** which, by how much, evidence file `eval/results/<file>.json`
**Discarded:** what was tried and dropped, and why
**Next:** what this session made obvious as the next move
