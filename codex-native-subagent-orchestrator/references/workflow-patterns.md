# Workflow Patterns

All patterns require applicable delegation authorization and a useful next
local step. Immediate critical-path blockers stay local when no independent
main-agent work can proceed. A pattern is not permission to spawn agents.

## Parallel evidence gathering

Use when questions have independent source scopes. Dispatch explorers,
specialists, or reviewers together and synthesize their reports.

## Critic loop

Use for bugs and risky changes. First gather root-cause and test evidence, then
ask a reviewer to challenge the proposed direction. The main agent implements.

## Sequential handoff

Use when a later question needs an earlier report, such as researching a public
API before reviewing its project integration. Do not spawn the dependent agent
until its input exists.
When that input arrives, reapply the rubric: if the dependent question now
blocks all useful main-agent work, answer it locally instead of spawning.

## Supervisor-led analysis

Use for architecture or migration choices. The main agent frames alternatives,
dispatches independent analysts, and makes the decision after comparing their
evidence.

If reports disagree, compare cited evidence, run a direct check, or make one
targeted follow-up. Do not ask agents to resolve conflicts through edits.
