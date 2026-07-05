# Practical Recipes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Magent feel useful by adding practical workflow recipes for common engineering jobs.

**Architecture:** Add source-controlled recipe JSON files under `.agents/recipes/`, a small loader in `.agents/scripts/recipes.py`, and two CLI commands: `magent recipes` to discover workflows and `magent start <recipe>` to create a guided run. Keep the existing `run` command as the low-level escape hatch.

**Tech Stack:** Python standard library, JSON recipe definitions, pytest, existing Codex-only run pipeline.

---

### Task 1: Recipe Data And Loader

**Files:**
- Create: `.agents/recipes/bugfix.json`
- Create: `.agents/recipes/code-review.json`
- Create: `.agents/recipes/release-readiness.json`
- Create: `.agents/recipes/docs-polish.json`
- Create: `.agents/recipes/test-plan.json`
- Create: `.agents/scripts/recipes.py`
- Test: `tests/test_recipes.py`

- [x] **Step 1: Add recipe JSON files**

Create practical recipes with `id`, `title`, `summary`, `task_template`, `context`, `default_scope`, `default_max`, `outcome`, and `next_steps`.

- [x] **Step 2: Add the loader**

Implement `load_recipes()`, `get_recipe()`, `render_recipe_task()`, `render_recipe_context()`, and formatting helpers in `.agents/scripts/recipes.py`.

- [x] **Step 3: Add focused tests**

Run: `python -m pytest tests/test_recipes.py -q`

Expected: tests pass and prove recipe loading, rendering, and unknown-recipe handling.

### Task 2: CLI Integration

**Files:**
- Modify: `.agents/magent.py`
- Modify: `tests/test_codex_only_workflow.py`

- [x] **Step 1: Add `recipes` command**

Show recipe IDs, titles, summaries, outcomes, and example `start` command.

- [x] **Step 2: Add `start <recipe>` command**

Render a recipe into the existing run pipeline and print recipe-specific next steps.

- [x] **Step 3: Add CLI tests**

Run: `python -m pytest tests/test_codex_only_workflow.py -q`

Expected: tests prove recipe listing output and recipe rendering path.

- [x] **Step 4: Make no-argument CLI useful**

Run: `python .agents/magent.py`

Expected: shows practical recipes instead of launching a blocking dashboard.

### Task 3: Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/GETTING_STARTED.md`
- Modify: `docs/USER_GUIDE.md`
- Create: `docs/RECIPES.md`
- Modify: `CHANGELOG.md`
- Modify: `scripts/maturity_audit.py`

- [x] **Step 1: Make recipes the first-run path**

Update docs so the default user journey starts with `python .agents/magent.py recipes` and `python .agents/magent.py start bugfix ...`.

- [x] **Step 2: Include recipes in maturity audit**

Require `docs/RECIPES.md`, `.agents/scripts/recipes.py`, and at least the core recipe JSON files.

- [x] **Step 3: Verify and commit**

Run: `python scripts/verify.py`

Expected: doctor ready, maturity audit publishable, identity validation passes, pytest passes, CLI smoke test passes.
