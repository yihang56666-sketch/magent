# User Guide

## What this project is

Magent is a local orchestration kit for Codex multi-agent workflows. It does not
call an external model API during the normal runtime. Instead, it helps one
Codex session behave like a disciplined team by routing work to bounded
specialist identities and generating copyable prompt packets.

## When to use it

Use Magent when a task benefits from different perspectives:

- Architecture review
- Bug triage with reviewer and QA roles
- Security-sensitive implementation planning
- Documentation and release readiness checks
- Embedded, frontend, backend, or DevOps specialist routing

For tiny one-file edits, use the main Codex session directly.

## Main workflow

1. Ask `magent advise` whether this task is worth multi-agent overhead.
2. Pick a recipe with `magent recipes`.
3. Generate a run with `magent start <recipe>`.
4. Ask for the next pending agent with `magent step`.
5. Play that bounded role in the current Codex session.
6. Save the answer into the matching output file.
7. Run `magent step` again to sync and continue.
8. Merge outputs into `synthesis.md`.
9. Let the main Codex session decide what to implement.

## Commands

```bash
python .agents/magent.py
python .agents/magent.py advise --scope "src tests" --task "..."
python .agents/magent.py recipes
python .agents/magent.py recipes bugfix
python .agents/magent.py start bugfix --scope "src tests" --task "..."
python .agents/magent.py run --task "..." --scope "..."
python .agents/magent.py next latest
python .agents/magent.py step latest
python .agents/magent.py status latest
python .agents/magent.py sync latest  # low-level refresh; `step` is the normal loop
python .agents/magent.py list
python .agents/magent.py agents
python .agents/magent.py ui --no-browser
python scripts/maturity_audit.py
python scripts/clean.py
```

## Choosing task and scope

Good tasks are concrete:

```bash
python .agents/magent.py start code-review --task "review login rate limiting" --scope "src/auth tests/auth"
```

Weak tasks are vague:

```bash
python .agents/magent.py run --task "make it better" --scope "."
```

If the scope is broad, the generated agents will be broad too. Start narrow
when you want actionable evidence.

## Recipes vs. low-level runs

Use recipes for common jobs:

- `bugfix`: root cause, patch plan, regression tests
- `code-review`: correctness, regressions, security risk
- `release-readiness`: go/no-go release gate
- `docs-polish`: onboarding and command accuracy
- `test-plan`: highest-value tests for risky work

Use low-level `run` only when no recipe fits.

## Should You Open Subagents?

Use `advise` first:

```bash
python .agents/magent.py advise --scope "src/auth tests/auth" --task "login returns 500 after password reset"
```

Subagents are usually worth it when the task has security, auth, payment,
release, migration, production, regression, or cross-module risk. Keep the work
local for typos, formatting, obvious one-file edits, or tasks where independent
review cannot change the outcome.

`advise` reports estimated manual overhead before creating any files:

- agent packets to process
- output files to fill
- whether sync and merge are needed
- suggested command to run next

## Output files

Each run folder contains:

- `dispatch-plan.json`: machine-readable routing result
- `agent-prompts.md`: all copyable bounded agent packets
- `next-agent.md`: the next pending agent packet
- `manual-execution.md`: turn-by-turn instructions
- `handoff-contract.md`: expected agent order
- `execution-summary.json`: current completion state
- `<agent-id>.output.md`: one result file per agent
- `synthesis.md`: merged evidence after completion

## Dashboard

Start the local dashboard:

```bash
python .agents/magent.py ui
```

Then open:

- `http://localhost:8080/dashboard.html`
- `http://localhost:8080/dashboard-live.html`

The dashboard reads local files only.

## Safety model

- Generated agents are advisory unless explicitly delegated write authority.
- External side effects are out of scope by default.
- The main Codex session owns final decisions and verification claims.
- Do not paste secrets, credentials, or private production data into public
  issue reports or shared run artifacts.
