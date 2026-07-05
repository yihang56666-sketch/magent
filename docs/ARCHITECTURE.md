# Architecture

## Runtime model

Magent is intentionally local and manual. It prepares specialist prompts and run
state, but the current Codex session performs the reasoning and any code edits.

```text
user task
  |
  v
advise -> keep local, use recipe, or orchestrate
  |
  v
magent start <recipe> or magent run
  |
  v
recipes.py -> practical task/context defaults
  |
  v
route_identity.py -> dispatch-plan.json
  |
  v
manual_execution.py -> agent-prompts.md, next-agent.md, execution-summary.json
  |
  v
current Codex session fills *.output.md files
  |
  v
merge-results.py -> synthesis.md
```

## Key directories

```text
.agents/
  magent.py        CLI entry point
  identities/      human-readable specialist identity cards
  presets/         reusable team presets
  reports/runs/    generated local run folders
  scripts/         routing, execution, dashboard, validation helpers
  recipes/         practical workflow recipes
  skills/          Codex skills for routing and orchestration
  ui/              local dashboard
  workflows/       reusable workflow definitions
tests/             regression tests for routing and manual execution
scripts/           repository-level verification and readiness helpers
docs/              user, architecture, and release documentation
```

## Routing

Recipes live under `.agents/recipes/` and are loaded by
`.agents/scripts/recipes.py`. They turn common work such as `bugfix`,
`code-review`, and `release-readiness` into concrete task and context text.

`.agents/scripts/advisor.py` reuses the identity router to estimate whether a
task is worth the manual multi-agent overhead before creating a run folder.

The low-level router still handles identity selection after a recipe is
rendered.

`.agents/skills/codex-agent-identity-bank/scripts/route_identity.py` scores the
task, scope, and context against identity definitions in
`.agents/skills/codex-agent-identity-bank/references/identities.json`.

The router returns:

- orchestration pattern
- primary identity
- supporting identities
- supporting skills
- one bounded prompt per identity

## Manual execution

`.agents/scripts/manual_execution.py` turns a dispatch plan into a structured
manual run pack. It tracks completion by checking whether each
`<agent-id>.output.md` file exists and contains content.

This keeps execution auditable. Nothing is hidden in a remote worker.

## Dashboard

`.agents/scripts/serve_dashboard.py` serves local run artifacts to the HTML
dashboard under `.agents/ui/`. It is meant for localhost inspection, not as a
public web service.

## Design constraints

- Keep the normal path Codex-only and local.
- Treat subagents as bounded evidence producers, not autonomous owners.
- Preserve generated run artifacts locally, but do not commit them.
- Keep external publishing, pushing, or third-party actions behind explicit user
  approval.
- Favor source distribution over committed binary executables.
