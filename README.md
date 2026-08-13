# Codex Native Subagent Orchestrator

A portable Codex Skill for choosing, briefing, and reconciling native
subagents on general tasks.

It is a workflow layer, not a separate agent runtime. It helps the main Codex
agent decide when delegation earns its coordination cost, use a small bounded
team, and gather evidence without handing off ownership.

## Install

Copy `codex-native-subagent-orchestrator/` into your Codex skills directory:

```powershell
Copy-Item -Recurse .\codex-native-subagent-orchestrator `
  "$env:USERPROFILE\.codex\skills\codex-native-subagent-orchestrator"
```

Restart or open a new Codex task after installation.

## What It Does

The Skill activates for work that benefits from independent investigation,
specialist analysis, review, test strategy, security assessment, research, or
architecture comparison. It instructs Codex to:

1. Keep trivial, narrow, or tightly coupled work local.
2. Select one to three native subagents for independent questions.
3. Add a fourth only for a security-sensitive or clearly cross-domain task.
4. Use built-in roles or generate a tightly bounded temporary specialist.
5. Give every worker a read-only scope, evidence requirements, and stop
   condition.
6. Reconcile results before the main agent edits or makes completion claims.

## Authority

All delegated subagents are read-only. They can inspect source, run safe
diagnostics, and provide evidence-based recommendations. They must not edit,
commit, push, publish, deploy, or change third-party resources.

The main Codex agent is the only editor, verifier, and user-facing task owner.

## Repository Layout

```text
codex-native-subagent-orchestrator/
  SKILL.md                 Core workflow
  references/              Routing, roles, packets, and patterns
  examples/                Bugfix, review, and research examples
  agents/openai.yaml       Codex UI metadata
tests/                     Portable structural tests
```

## Verify

```powershell
python -m unittest discover -s tests -v
python C:\Users\35182\.codex\skills\.system\skill-creator\scripts\quick_validate.py codex-native-subagent-orchestrator
```

## Non-Goals

- No Python CLI, dashboard, local run-state store, or manual prompt-copy loop.
- No model API client or hosted service.
- No automatic external actions.
- No promise that using more agents always improves a task.

## License

MIT. See [LICENSE](LICENSE).
