# Prompts

Reusable agent prompts. Created before kickoff; contain no problem-specific content.

| File | When | Purpose |
|---|---|---|
| `00-bootstrap.md` | Fri 16:00, immediately after the problem PDF | Analysis only, no code. Produces the plan everything else runs on. |
| `01-baseline.md` | Fri evening | Build the baseline, define cases and metrics, measure the noise floor, freeze. |
| `02-improve-loop.md` | Sat, once per improvement | Plan → implement → review → measure → log → trace → commit. |
| `03-hardening.md` | Sun morning | Break it before the judges do. Reproducibility is the qualification gate. |
| `04-submission.md` | Sun evening / Mon | Assemble the package and the video script. |

Shortcuts (`QNEW`, `QPLAN`, `QCODE`, `QCHECK`, `QEVAL`, `QLOG`, `QTRACE`, `QREPRO`, `QGIT`,
`QORCHESTRATE`) are defined in `CLAUDE.md`.
