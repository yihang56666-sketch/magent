# Changelog

All notable changes to this project will be documented here.

The format follows Keep a Changelog style, and this project uses semantic
versioning once tagged releases begin.

## [Unreleased]

### Added

- Practical workflow recipes for bug fixing, code review, release readiness,
  documentation polish, and test planning.
- `magent advise` for zero-write advice on whether multi-agent orchestration is worth the task overhead.
- `magent step` to sync a run and show the next pending agent in one command.
- Dogfood and efficiency evidence docs to separate measured value from claims.
- Route regression coverage for auth bugfix, release-readiness, and noisy imported-role matches.
- `magent recipes` and `magent start <recipe>` commands.
- `docs/RECIPES.md` with concrete daily-use examples.
- GitHub CI workflow for Python 3.10 through 3.13.
- Local `scripts/doctor.py` readiness check.
- Local `scripts/maturity_audit.py` maturity gate.
- Local `scripts/clean.py` cleanup helper for generated artifacts.
- Local `scripts/verify.py` command that mirrors CI.
- GitHub issue templates, security policy, code of conduct, and MIT license.
- User-facing setup, workflow, architecture, and release documentation.

### Changed

- README now focuses on first-run user experience and source-first publishing.
- Ignore rules now exclude local executable and PyInstaller build artifacts.
