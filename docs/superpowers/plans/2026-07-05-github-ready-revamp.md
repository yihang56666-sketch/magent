# GitHub Ready Revamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the local Codex multi-agent orchestration framework into a clear, source-first project that is ready to publish on GitHub.

**Architecture:** Keep the existing `.agents` runtime stable and wrap it with repository-level documentation, verification helpers, CI, and release hygiene. The revamp improves first-run experience without moving the core CLI or identity bank.

**Tech Stack:** Python 3.10+, pytest, GitHub Actions, local Codex CLI workflow, static Markdown documentation.

---

## File Structure

- Modify `README.md`: reposition the project for new GitHub visitors and document the happy path.
- Modify `CONTRIBUTING.md`: align contributor workflow with current Codex-only runtime.
- Modify `.gitignore`: keep build outputs, binary executables, caches, and run artifacts out of source commits.
- Create `pyproject.toml`: centralize pytest and lint-tool defaults.
- Create `requirements-dev.txt`: make local setup and CI install the same tools.
- Create `scripts/doctor.py`: check local readiness and warn about generated artifacts.
- Create `scripts/verify.py`: run the same validation sequence as CI.
- Create `tests/test_project_doctor.py`: protect readiness helper behavior.
- Create `.github/workflows/ci.yml`: validate the project on supported Python versions.
- Create `.github/ISSUE_TEMPLATE/*.yml`: guide useful user reports.
- Create `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`: standard open-source project metadata.
- Create `docs/GETTING_STARTED.md`, `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/RELEASE_CHECKLIST.md`: user-facing and maintainer-facing docs.

## Tasks

### Task 1: Release Hygiene

**Files:**
- Modify: `.gitignore`
- Create: `LICENSE`
- Create: `SECURITY.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `CHANGELOG.md`

- [x] Add ignore rules for local executables, PyInstaller output, test caches, and coverage output.
- [x] Add MIT license and safety/conduct metadata.
- [x] Add an unreleased changelog entry for the GitHub-readiness pass.

### Task 2: Verification Tooling

**Files:**
- Create: `pyproject.toml`
- Create: `requirements-dev.txt`
- Create: `scripts/doctor.py`
- Create: `scripts/verify.py`
- Create: `tests/test_project_doctor.py`

- [x] Configure pytest discovery and warning filters.
- [x] Add developer dependencies for pytest-based validation.
- [x] Add a doctor command that checks required files, Python version, imports, and generated artifact risk.
- [x] Add a verify command that runs doctor, identity validation, tests, and CLI smoke checks.
- [x] Add focused tests for doctor helper behavior.

### Task 3: GitHub Automation

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`

- [x] Add CI across Python 3.10, 3.11, 3.12, and 3.13.
- [x] Add issue templates that ask for task, scope, reproduction, and validation context.
- [x] Add issue templates for bug reports and feature requests.

### Task 6: Maturity Hardening

**Files:**
- Create: `scripts/maturity_audit.py`
- Create: `scripts/clean.py`
- Create: `tests/test_maturity_audit.py`
- Create: `tests/test_clean.py`
- Create: `.github/pull_request_template.md`
- Create: `docs/MAINTAINER_GUIDE.md`
- Create: `docs/MATURITY_AUDIT.md`
- Modify: `scripts/verify.py`
- Modify: `README.md`
- Modify: `docs/GETTING_STARTED.md`
- Modify: `docs/USER_GUIDE.md`
- Modify: `docs/RELEASE_CHECKLIST.md`

- [x] Add a maturity audit that checks repository shape, Git readiness, required docs, CI, PR template, ignore rules, and CLI smoke behavior.
- [x] Add a dry-run-first cleanup helper for generated artifacts and run folders.
- [x] Add tests for maturity audit and cleanup safety.
- [x] Add maintainer-facing docs and pull request guidance.
- [x] Include the maturity audit in `scripts/verify.py`.

### Task 4: User Documentation

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Create: `docs/GETTING_STARTED.md`
- Create: `docs/USER_GUIDE.md`
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/RELEASE_CHECKLIST.md`

- [x] Rewrite the README around the first-run user journey.
- [x] Explain setup, verification, run creation, manual agent turns, sync, and synthesis.
- [x] Document architecture and release readiness expectations.
- [x] Update contribution flow to match `scripts/verify.py`.

### Task 5: Verification

**Files:**
- Read only unless failures require a focused fix.

- [x] Run `python scripts/doctor.py`.
- [x] Run `python scripts/verify.py`.
- [x] Run `python .agents/magent.py run --task "review docs release readiness" --scope "README.md docs scripts tests" --max 2`.
- [x] Run `python .agents/magent.py next latest`.
- [x] Review results and record any residual risks.
