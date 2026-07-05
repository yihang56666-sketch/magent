# Efficiency Evidence

Magent should not claim that subagents improve efficiency without evidence. Use
this template to compare a main-agent-only baseline with a recipe or
multi-agent run.

## What counts as efficiency

Separate these dimensions:

- Speed: elapsed wall-clock time
- Effort: user turns, manual copy/save/sync steps, files touched
- Quality: accepted findings, defects caught before merge, test gaps found
- Confidence: verification commands run and pass/fail result
- Cost: number of agent packets, output files, merge/synthesis steps

More agents are useful only when the quality or confidence gain is worth the
manual overhead.

## Paired-run template

```markdown
## Scenario

- Recipe:
- Task:
- Scope:
- Date:
- Baseline mode: main agent only
- Multi-agent mode: recipe or run command

## Baseline

- Elapsed time:
- User/main-agent turns:
- Files inspected:
- Findings:
- Verification commands:
- Outcome:

## Multi-agent run

- Command:
- Run directory:
- Agent count:
- Agent packets completed:
- Output files completed:
- Elapsed time:
- Findings:
- Accepted findings:
- Rejected/noisy findings:
- Verification commands:
- Outcome:

## Comparison

- Time delta:
- Effort delta:
- Defects or risks found only by agents:
- Verification improved:
- Was the overhead worth it:
- Recommendation for this task class:
```

## When subagents are likely worth it

- Security, auth, payment, data migration, release, or production risk
- Cross-module changes where one person may miss interactions
- Bug fixes where root cause is uncertain
- Pre-merge review of large generated or refactored patches
- Release readiness checks with docs, tests, packaging, and source hygiene

## When to keep work local

- Typos, formatting, small copy edits
- Single-line or single-file obvious changes
- Tasks with no meaningful independent review angle
- Work where the manual packet/output/sync loop costs more than the risk

## Current evidence status

The project has dogfood evidence that subagents found useful product, CLI, and
QA gaps in this repository. It does not yet have statistically meaningful
benchmark data across many task classes. Treat efficiency claims as conditional
until paired-run data exists.
