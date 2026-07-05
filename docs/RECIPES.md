# Practical Recipes

Recipes are the easiest way to use Magent. They turn common engineering jobs
into scoped multi-agent runs without requiring you to design the task packet
from scratch.

## List recipes

```bash
python .agents/magent.py recipes
```

## Start a recipe

Ask for advice first when you are unsure whether subagents are worth it:

```bash
python .agents/magent.py advise --scope "src/auth tests/auth" --task "login returns 500 after password reset"
```

```bash
python .agents/magent.py start bugfix --scope "src/auth tests/auth" --task "login returns 500 after password reset"
```

Then continue with:

```bash
python .agents/magent.py step latest
```

## Available recipes

### `bugfix`

Use when you have a bug report, failing behavior, or regression. It focuses the
run on root cause, smallest safe patch, and regression tests.

```bash
python .agents/magent.py start bugfix --scope "src tests" --task "checkout fails when coupon is expired"
```

### `code-review`

Use before merging a branch or accepting a large generated patch. It focuses on
correctness, regressions, security risk, and missing tests.

```bash
python .agents/magent.py start code-review --scope "src/auth tests/auth" --task "review login rate-limit changes"
```

### `release-readiness`

Use before publishing, tagging, or shipping. It asks specialists to look for
release blockers, documentation gaps, packaging issues, and verification
commands.

```bash
python .agents/magent.py start release-readiness --scope "." --task "prepare v1.0 release"
```

### `docs-polish`

Use when the project works but users do not know what to do. It focuses on
onboarding, examples, command accuracy, and the first-run journey.

```bash
python .agents/magent.py start docs-polish --scope "README.md docs" --task "make the project useful to new users"
```

### `test-plan`

Use when you need focused verification instead of a generic "write more tests"
request. It identifies the highest-value tests for a feature, bug, or risky
change.

```bash
python .agents/magent.py start test-plan --scope "src tests" --task "new import pipeline"
```

## When to use low-level `run`

Use `run` when none of the recipes fit:

```bash
python .agents/magent.py run --task "compare two architecture options" --scope "docs src"
```

Recipes are just practical defaults on top of the same local run pipeline.

## Efficiency Notes

Recipes improve work only when the extra review catches issues or improves
verification enough to justify the manual overhead. For evidence tracking, use
`docs/EFFICIENCY_EVIDENCE.md`.
