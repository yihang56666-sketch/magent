# Dogfood Report

This report records a real use of Magent-style bounded subagents on Magent
itself.

## Scenario

- Date: 2026-07-05
- Goal: test whether subagents make this project more useful and whether the
  project can honestly claim efficiency gains.
- Scope: README, docs, CLI, recipes, tests, maturity tooling
- Control plane: main Codex agent retained write authority; subagents were
  advisory and read-only.

## Subagents used

### Product/DX reviewer

Mission: inspect whether the project helps a practical user get work done.

Key findings:

- Recipes make the project more concrete.
- Manual copy/save/sync/merge overhead can erase efficiency on small tasks.
- Users need a "should I open subagents?" decision guide.
- The CLI should guide completion more strongly after a run starts.

Accepted actions:

- Added `magent advise` to estimate whether a task should stay local, use a
  recipe, or create a custom run.
- Added `magent step` to sync and show the next pending agent packet.
- Documented when subagents are likely worth the overhead.

### CLI/architecture reviewer

Mission: find the smallest engineering feature that improves daily usefulness.

Key findings:

- Current CLI created artifacts immediately.
- A no-write preflight is a better daily entry point.
- Advice should reuse existing routing instead of duplicating routing logic.

Accepted actions:

- Added `.agents/scripts/advisor.py`.
- Reused the identity router for pattern, identities, and skill estimates.
- Added `magent advise --task ... --scope ...` and JSON output.

### QA/evidence reviewer

Mission: define what evidence would make efficiency claims credible.

Key findings:

- Existing artifacts prove auditability, not efficiency.
- Efficiency needs paired baseline vs multi-agent comparisons.
- Useful signals include elapsed time, turns, accepted findings, verification
  commands, and rework avoided.

Accepted actions:

- Added `docs/EFFICIENCY_EVIDENCE.md`.
- Added maturity-audit requirements for dogfood and evidence docs.
- Kept efficiency language conditional instead of absolute.

### Production-readiness reviewer

Mission: inspect the dogfood upgrade before committing it.

Key findings:

- Recipe matching used raw substring checks, so `production readiness check`
  could match `code-review` through the short keyword `pr`.
- `magent advise --max 0` could produce contradictory JSON: no identities but
  sync/merge marked as required.
- Generated run guidance still promoted the older `sync` loop instead of the
  lower-friction `step` command.

Accepted actions:

- Added word-boundary recipe matching and release-readiness keywords.
- Clamped advisor routing to at least one identity.
- Updated generated workflow guidance, recipes, and docs to prefer `step`.

### Main-agent smoke testing

Mission: run the project the way a user would after the reviewer fixes.

Key findings:

- A web/auth bug with `password reset` initially routed to a hardware bring-up
  role because `reset` was interpreted as a board reset signal.
- A real `start bugfix` smoke test later routed to `assumption-mapping`
  because recipe context contained the phrase `risky assumptions`.

Accepted actions:

- Added route regression tests for password-reset auth bugs.
- Added route regression tests for bugfix recipe context.
- Added domain support rules so auth bugs keep backend, security, QA, and
  reviewer identities ahead of generic imported roles.

## Outcome

This dogfood run produced concrete product changes:

- `magent advise`: no-write ROI advice before creating a run
- `magent step`: lower-friction manual execution loop
- Cleaner role routing for auth bugfix and release-readiness tasks
- Evidence docs: a repeatable way to prove or disprove efficiency

## Remaining limits

- The normal runtime is still manual; it does not automatically dispatch real
  parallel model workers in the source-first path.
- The project has one dogfood example, not broad benchmark evidence.
- Users should still keep tiny edits local.

## Recommendation

Use Magent when independent review can catch risks that a single pass may miss.
Do not use it by default for small obvious edits.
