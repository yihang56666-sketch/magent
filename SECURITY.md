# Security Policy

## Supported versions

This project is source-first and currently supports the latest `main` branch.

## Reporting a vulnerability

Please open a private security advisory if the repository is hosted on GitHub,
or contact the maintainer privately before publishing details. Include:

- A short description of the issue
- Reproduction steps
- Affected files or commands
- Any known workaround

Do not include API keys, private prompts, private task data, or generated run
artifacts from real projects in public issues.

## Scope

The normal workflow is local and Codex-only. Security-sensitive areas include:

- Local file reads and writes inside generated run folders
- Shell command construction in helper scripts
- Dashboard endpoints served on localhost
- User-provided task, scope, and context strings
- Handling of legacy API configuration keys

Networked tools and publishing actions should remain opt-in and require
explicit user approval.
