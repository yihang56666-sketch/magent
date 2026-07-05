# Maturity Audit

Magent uses a source-first maturity model. A mature checkout should be easy to
understand, verify, clean, contribute to, and publish without accidentally
shipping local artifacts.

## Levels

`not-ready`: one or more blockers exist. Do not publish yet.

`publishable-with-local-warnings`: required project files, commands, and ignore
rules are in place, but local generated artifacts are still present. This is
acceptable for development as long as ignored artifacts are not committed.

`publishable`: no blockers and no local artifact warnings.

## Run the audit

```bash
python scripts/maturity_audit.py
```

Machine-readable output:

```bash
python scripts/maturity_audit.py --json
```

## What it checks

- Git repository initialization
- Initial source commit exists
- Required open-source metadata files
- CI, issue templates, and pull request template
- Cross-platform line ending policy
- Getting started, user, architecture, maintainer, and release docs
- Practical recipe docs and recipe loader
- Orchestration advice and evidence docs
- Local doctor, verify, and cleanup tools
- Legacy external API setup entry points are absent
- Dry-run staging does not include generated artifacts
- Core CLI smoke test exits successfully

## How to resolve warnings

Local generated artifacts can be cleaned with:

```bash
python scripts/clean.py --apply
```

To also remove generated run folders:

```bash
python scripts/clean.py --runs --apply
```
