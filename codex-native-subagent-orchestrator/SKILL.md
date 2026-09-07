---
name: codex-native-subagent-orchestrator
description: Use when a Codex task needs parallel investigation, independent review, specialist analysis, test strategy, security review, research, architecture comparison, or explicit subagent delegation.
---

# Native Subagent Orchestrator

Use this Skill to turn native subagents into bounded evidence producers, not
parallel owners of a task.

## Workflow

1. Inspect the task, repository, risk, and dependencies. Identify the main
   agent's next local step. Require explicit authorization for delegation from
   the user or applicable instructions; depth, complexity, and automatic Skill
   loading alone are not authorization. Without it, keep work local.
2. Read [the delegation rubric](references/delegation-rubric.md) and decide
   `keep-local` or `delegate`. Explain the choice briefly when it affects the
   user-visible approach. Keep an immediate blocker local when no useful
   independent main-agent work can run alongside it.
3. For delegation, choose the smallest team and one pattern from
   [workflow patterns](references/workflow-patterns.md). Use one to three
   subagents by default. Add a fourth only for a security-sensitive or clearly
   cross-domain task with independent scope.
4. Select catalog roles from [the role catalog](references/role-catalog.md). If
   none fits, create one temporary specialist instructed to remain read-only,
   following that file.
5. Before dispatching, inspect whether native `spawn_agent` is available. If
   `spawn_agent is unavailable`, say that native delegation cannot run in this
   session and continue locally; do not simulate agents with prompt-copy files.
   In a Git worktree, capture `git status --short`, scoped `git diff --binary`
   and `git diff --cached --binary`, plus content fingerprints of allowed
   files, including pre-existing untracked files. Do not capture secrets or
   dependency/cache trees. If the baseline is already dirty, record it as
   pre-existing. If this is not a Git repository, skip the Git baseline and
   capture scoped content fingerprints instead. Status alone is insufficient.
6. Build every packet using [the dispatch contract](references/dispatch-contract.md).
7. Call `spawn_agent` only for independent evidence work. Give each agent one
   concrete mission and a non-overlapping question or source scope. Instruct
   every worker to remain read-only. Dispatch no more than the platform's
   available concurrency, then launch further independent work only after a
   slot becomes available.
8. Continue the identified useful local work while agents run. Do not dispatch
   an immediate blocker merely to wait on it. Waiting is appropriate when an
   existing agent later becomes the next dependency or local work is complete.
9. Reconcile returned findings as evidence. Resolve conflicts with source
   checks, one bounded follow-up, or a direct local check. In a Git worktree,
   inspect `git diff`, `git status --short` and content fingerprints against
   the captured baseline after agents return; otherwise compare scoped content.
   Stop and review any unexpected workspace
   change. The main agent alone edits files, runs final verification, and
   reports task completion.

## Collection Rule

Collect every started agent before reporting task completion. Wait only when a
result blocks the next decision or when all useful main-agent work is complete;
then collect outstanding results and account for each returned agent ID as
completed, failed, pending, or no longer needed. A wait timeout or empty poll
means pending, not a stopped agent. Inspect the same handle again; do not spawn
a replacement merely because an observation timed out.

Use the available native message tool (`send_input` when provided) for a bounded
follow-up to the original agent. Completed agents still occupy concurrency
until closed: collect their evidence, then call `close_agent` when no longer
needed. Record the close request; its returned previous status is not a new
post-close status. Recheck capacity before assigning another independent task.

## Failed Agents

If an agent has a confirmed terminal failure or returns no usable result,
record the missing question and decide whether the main agent can close the
gap locally. Do not wait indefinitely: a soft evidence deadline may end the
investigation, but does not prove the agent stopped. Close or otherwise confirm
termination of the original before any replacement. Use at most one narrowly
scoped replacement only when it can run alongside useful independent work.
If the platform can resume the original agent, prefer that for the same
context-dependent question. Never broaden the assignment to compensate.

## Dispatch Rules

- Do not delegate obvious, narrow, single-file tasks or work whose dependencies
  make parallel context distribution wasteful.
- The Skill cannot independently sandbox a native subagent. Instruct every
  subagent to remain read-only and do not delegate file writes, commits, pushes,
  publishing, deployment, credential changes, or third-party mutations. Check
  the worktree after it returns.
- In a Git worktree, compare status, staged/unstaged diffs and scoped content
  fingerprints with the captured baseline, even when a path was already dirty.
  Do not attribute pre-existing changes to a subagent, and
  do not discard or revert a change before determining whether it came from the
  user, the main agent, or a subagent.
- Keep each agent scoped to facts it can establish independently. Do not assign
  multiple agents the same broad codebase tour.
- Treat subagent reports as advisory. Verify important claims before acting.
- Inspect the current native tool schema; role names are prompt labels, not
  assumed `agent_type` values. Inherit the parent model unless the user requests
  a specific override. Do not invent budget, model, or lifecycle parameters.
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
- Read `references/acceptance-cases.md` when checking release readiness or
  demonstrating the Skill. Structure tests alone do not verify model behavior.
