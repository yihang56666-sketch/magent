# Contributing

Thanks for improving Magent. The project is intentionally local, source-first,
and conservative about external side effects.

## Development setup

```bash
git clone <repository-url>
cd <repository>
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Run the readiness check:

```bash
python scripts/doctor.py
```

Run the full local verification sequence:

```bash
python scripts/verify.py
```

## Pull request checklist

- [ ] `python scripts/verify.py` passes.
- [ ] Documentation is updated for user-facing changes.
- [ ] Generated run folders and binary artifacts are not committed.
- [ ] New identities, workflows, or presets are validated.
- [ ] Security-sensitive behavior is documented and bounded.

## Adding a specialist identity

1. Add the identity to
   `.agents/skills/codex-agent-identity-bank/references/identities.json`.
2. Add a matching card under `.agents/identities/<category>/<identity-id>.md`.
3. Run:

```bash
python .agents/scripts/validate-identities.py
python .agents/skills/codex-agent-identity-bank/scripts/route_identity.py --task "example task" --scope "example scope"
```

Identity entries should include:

- stable `id`
- human-readable `title`
- routing `keywords`
- supporting `skills`
- clear mission
- explicit boundaries
- expected output focus

## Adding a workflow

Create a file under `.agents/workflows/` with:

```yaml
name: example-workflow
pattern: critic-loop
default_identities:
  - code-reviewer
  - qa-test-automation-engineer
phases:
  - inspect
  - test
  - review
exit_criteria:
  - findings are evidence-backed
  - verification command is documented
```

Then run:

```bash
python .agents/scripts/validate-identities.py
```

## Adding a preset

Create `.agents/presets/<preset-id>.json` with a small, focused team:

```json
{
  "id": "example-team",
  "max_identities": 3,
  "identities": ["software-architect", "code-reviewer"],
  "skills": ["architecture", "testing"],
  "default_pattern": "critic-loop",
  "policy": "Use for example review tasks."
}
```

## Code style

- Prefer Python standard-library code unless a dependency already exists.
- Use explicit errors and helpful user-facing tips.
- Keep generated artifacts out of source commits.
- Keep the normal workflow Codex-only and local.
- Do not hardcode secrets or API credentials.

## Commit and PR style

Use conventional commit-style titles when practical:

- `feat: add release readiness doctor`
- `fix: correct identity routing tie breaker`
- `docs: update first-run workflow`
- `test: cover manual execution summary`

PR descriptions should include:

- What changed
- Why it changed
- How it was verified
- Any remaining risk or follow-up
