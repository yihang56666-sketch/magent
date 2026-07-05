# Codex Multi-Agent Project

This directory is the project-local multi-agent control plane.

## Layout

```text
.agents/
  skills/       Codex skills loaded by the agent runtime
  identities/   Human-readable specialist identity cards
  workflows/    Repeatable task workflows
  presets/      Reusable specialist teams
  reports/      Generated run artifacts
  scripts/      Project-level helpers
```

## Runtime Flow

1. Route the task through `codex-agent-identity-bank`.
2. Select identities, supporting skills, and orchestration pattern.
3. Use `codex-multi-agent-orchestrator` to dispatch, isolate, merge, and verify.
4. Store run artifacts under `.agents/reports/runs/<run-id>/`.

## Main Rule

The main Codex agent owns final decisions, file edits, verification claims, and the user response. Specialist agents are bounded workers or explorers.
