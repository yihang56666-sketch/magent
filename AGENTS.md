# Repository Guidance

This repository distributes a Codex Skill, not a standalone agent runtime.

- Keep `codex-native-subagent-orchestrator/SKILL.md` concise and procedural.
- Put detailed routing, role, packet, and pattern material under `references/`.
- Keep every delegated role read-only. The main agent is the only writer,
  verifier, and user-facing owner.
- Do not add a CLI, dashboard, model API dependency, telemetry, or manual
  prompt-copy lifecycle without an explicit product decision.
- Update `tests/test_skill_contract.py` when changing the public Skill contract.
- Validate with `python -m unittest discover -s tests -v` and the bundled
  `quick_validate.py` command before claiming a release is ready.
