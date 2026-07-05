# Dogfood Efficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove Magent can improve practical work by dogfooding it on itself and adding user-facing advice about when subagents are worth the overhead.

**Architecture:** Keep the manual run pipeline intact. Add a no-write advisor that reuses the existing identity router, a `step` command that reduces manual workflow friction, and documentation that records dogfood evidence without overstating efficiency.

**Tech Stack:** Python standard library, existing route identity module, pytest, Markdown docs.

---

### Task 1: Dogfood With Advisory Subagents

**Files:**
- Read: `README.md`
- Read: `docs/*.md`
- Read: `.agents/magent.py`
- Read: `.agents/scripts/*.py`

- [x] Dispatch read-only product, CLI, and QA/evidence subagents.
- [x] Capture their findings and reconcile recommendations in the main agent.
- [x] Close subagents after reports are collected.

### Task 2: Add No-Write Orchestration Advice

**Files:**
- Create: `.agents/scripts/advisor.py`
- Modify: `.agents/magent.py`
- Test: `tests/test_advisor.py`
- Test: `tests/test_codex_only_workflow.py`

- [x] Implement `build_advice()` using existing identity routing.
- [x] Implement recommendations: `keep-local`, `use-recipe`, `orchestrate`.
- [x] Show manual overhead and suggested next command.
- [x] Add `magent advise`.

### Task 3: Lower Manual Workflow Friction

**Files:**
- Modify: `.agents/magent.py`
- Test: `tests/test_codex_only_workflow.py`

- [x] Add `magent step` to sync a run and print the next pending packet.
- [x] Add CLI tests for `step`.

### Task 4: Evidence And Documentation

**Files:**
- Create: `docs/EFFICIENCY_EVIDENCE.md`
- Create: `docs/DOGFOOD_REPORT.md`
- Modify: `README.md`
- Modify: `docs/USER_GUIDE.md`
- Modify: `docs/RECIPES.md`
- Modify: `docs/MATURITY_AUDIT.md`
- Modify: `scripts/maturity_audit.py`

- [x] Document when subagents are likely worth it.
- [x] Document when to keep work local.
- [x] Add paired-run efficiency evidence template.
- [x] Include dogfood/evidence docs in maturity audit.

### Task 5: Verify And Commit

**Files:**
- All changed files

- [x] Run `python scripts/verify.py`.
- [x] Run smoke tests for `magent advise`, `magent step`, and recipe flow.
- [x] Clean generated artifacts.
- [x] Commit the dogfood upgrade.
