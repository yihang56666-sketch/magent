# Maintainer Guide

This guide covers the repeatable operations that make Magent maintainable after
it is published.

## Daily development loop

```bash
python scripts/doctor.py
python scripts/maturity_audit.py
python scripts/verify.py
```

Use `doctor.py` for environment readiness, `maturity_audit.py` for repository
shape, and `verify.py` for the full CI-equivalent check.

## Cleaning local artifacts

Preview cleanup:

```bash
python scripts/clean.py
```

Apply cleanup:

```bash
python scripts/clean.py --apply
```

Also remove generated run folders:

```bash
python scripts/clean.py --runs --apply
```

The cleaner refuses to operate outside the project root and preserves
`.agents/reports/runs/.gitkeep` and `.agents/reports/runs/.keep`.

## Before opening a pull request

1. Run `python scripts/verify.py`.
2. Run `git status --short --ignored`.
3. Confirm generated artifacts are ignored.
4. Update docs for user-facing behavior changes.
5. Fill out the pull request template with verification evidence.

## Release preparation

1. Run `python scripts/clean.py --runs --apply`.
2. Run `python scripts/verify.py`.
3. Walk through `docs/RELEASE_CHECKLIST.md`.
4. Commit source files only.
5. Tag the release after CI passes.

Do not commit built executables. Attach optional binaries to GitHub Releases
with checksums and the source commit SHA.

## Triage policy

Prioritize issues in this order:

1. Security or private-data exposure
2. Broken first-run workflow
3. Routing or identity correctness
4. Documentation clarity
5. Dashboard polish
