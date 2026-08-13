---
name: codex-native-subagent-orchestrator
description: Route general tasks to the smallest effective set of Codex native subagents. Use when a task benefits from parallel investigation, independent review, specialist analysis, test strategy, security review, research, architecture comparison, or explicit subagent delegation. Keep small or tightly coupled tasks local. Delegate read-only evidence work only; the main agent remains the sole editor, verifier, and user-facing owner.
---

# Native Subagent Orchestrator

Use this Skill to turn native subagents into bounded evidence producers, not
parallel owners of a task.

## Workflow

1. Inspect the task, repository, risk, and dependencies.
2. Read [the delegation rubric](references/delegation-rubric.md) and decide
   `keep-local` or `delegate`. Explain the choice briefly when it affects the
   user-visible approach.
3. For delegation, choose the smallest team and one pattern from
   [workflow patterns](references/workflow-patterns.md). Use one to three
   subagents by default. Add a fourth only for a security-sensitive or clearly
   cross-domain task with independent scope.
4. Select catalog roles from [the role catalog](references/role-catalog.md). If
   none fits, create one temporary specialist instructed to remain read-only,
   following that file.
5. Before dispatching, capture `git status --short` and inspect whether native
   `spawn_agent` is available. If `spawn_agent is unavailable`, say that native
   delegation cannot run in this session and continue locally; do not simulate
   agents with prompt-copy files.
6. Build every packet using [the dispatch contract](references/dispatch-contract.md).
7. Call `spawn_agent` only for independent evidence work. Give each agent one
   concrete mission and a non-overlapping question or source scope. Instruct
   every worker to remain read-only. Dispatch no more than the platform's
   available concurrency, then launch further independent work only after a
   slot becomes available.
8. Continue useful main-agent work while agents run. Do not wait immediately
   unless their result blocks the next main-agent decision.
9. Reconcile returned findings as evidence. Resolve conflicts with source
   checks, one bounded follow-up, or a direct local check. Inspect `git diff`
   and `git status --short` after agents return; stop and review any unexpected
   workspace change. The main agent alone edits files, runs final verification,
   and reports task completion.

## Dispatch Rules

- Do not delegate obvious, narrow, single-file tasks or work whose dependencies
  make parallel context distribution wasteful.
- The Skill cannot independently sandbox a native subagent. Instruct every
  subagent to remain read-only and do not delegate file writes, commits, pushes,
  publishing, deployment, credential changes, or third-party mutations. Check
  the worktree after it returns.
- Compare the post-dispatch `git status --short` with the captured baseline.
  Do not discard or revert a change before determining whether it came from the
  user, the main agent, or a subagent.
- Keep each agent scoped to facts it can establish independently. Do not assign
  multiple agents the same broad codebase tour.
- Treat subagent reports as advisory. Verify important claims before acting.
- Ask at most one targeted follow-up from the original agent for missing
  evidence. Then proceed locally, discard the report, or state the blocker.
- Do not use a traffic-controller agent for a team of three or fewer; the main
  agent coordinates that team directly.

## Reference Selection

- Read `references/delegation-rubric.md` for keep-local decisions and size caps.
- Read `references/role-catalog.md` to select or construct roles.
- Read `references/workflow-patterns.md` to choose sequencing.
- Read `references/dispatch-contract.md` before sending a packet.
- Read one relevant file in `examples/` only when a concrete packet helps.
