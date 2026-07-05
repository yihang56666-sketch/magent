# Codex-Only Agent Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove external model API runtime paths and make the project operate through the current Codex session only.

**Architecture:** Keep the existing run-folder workflow, but replace API-backed executors with manual Codex preparation/synchronization helpers. Update the CLI, dashboard, build metadata, and docs so the default flow is local, explicit, and offline.

**Tech Stack:** Python, PyInstaller, plain Markdown docs, HTML/JS dashboard.

---

### Task 1: Runtime cleanup

**Files:**
- Modify: `.agents/magent.py`
- Modify: `.agents/scripts/config_manager.py`
- Modify: `.agents/scripts/error_handler.py`
- Modify: `.agents/scripts/api_adapter.py`
- Modify: `.agents/scripts/ultimate-executor.py`
- Modify: `.agents/scripts/execute-dispatch-plan.py`

- [x] **Step 1: Remove API-dependent settings and tips**
- [x] **Step 2: Replace legacy executors with Codex-only/manual workflow behavior**
- [x] **Step 3: Keep compatibility entry points, but make them offline**
- [x] **Step 4: Verify no runtime code imports OpenAI/Anthropic clients**

### Task 2: Packaging and docs

**Files:**
- Modify: `requirements.txt`
- Modify: `.agents/magent.spec`
- Modify: `.agents/build.bat`
- Modify: `.agents/build.sh`
- Modify: `.agents/build-simple.bat`
- Modify: `.agents/demo.bat`
- Modify: `.agents/rebuild-with-openai.bat`
- Modify: `.agents/setup-openai-api.bat`
- Modify: `README.md`
- Modify: `.agents/BUILD_MANUAL.md`
- Modify: `.agents/ui/README.md`
- Modify: `.agents/ui/dashboard.html`
- Modify: `.agents/ui/dashboard-live.html`

- [x] **Step 1: Remove external API install/build instructions**
- [x] **Step 2: Rewrite usage text around current Codex session manual execution**
- [x] **Step 3: Update dashboard copy and paths for the local run folder**

### Task 3: Tests and verification

**Files:**
- Add: `tests/test_manual_execution.py`
- Modify: `tests/test_agent_contract.py`
- Modify: `tests/test_route_identity.py`
- Modify: `tests/test_validate_identities.py`

- [x] **Step 1: Add a manual-run summary test**
- [x] **Step 2: Update existing tests for the Codex-only contract**
- [x] **Step 3: Run search-based verification for remaining API references**
- [x] **Step 4: Run the project tests and fix anything that fails**

---

### Self-Review

Coverage:
- Runtime cleanup: yes
- Packaging/docs cleanup: yes
- Test coverage: yes

Placeholder scan:
- No TBD/TODO placeholders

Type consistency:
- Manual run helpers, CLI, and tests all target the same run-folder contract
