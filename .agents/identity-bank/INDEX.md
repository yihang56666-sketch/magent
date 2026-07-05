# Codex Multi-Agent Identity Repository

This is the repo-level control surface for specialist Codex agents.

## Layers

- `skills/`: Codex-triggerable skills.
- `identities/`: Human-readable specialist identity cards.
- `workflows/`: Reusable multi-agent workflow templates.
- `presets/`: Ready-made team compositions.
- `scripts/`: CLI helpers for routing, dispatch-plan generation, and validation.
- `reports/runs/`: Generated run artifacts.

## Default Flow

1. Use `skills/codex-agent-identity-bank` to choose identities and skills.
2. Use `skills/codex-multi-agent-orchestrator` to choose pattern and dispatch rules.
3. Use `scripts/spawn-team.py` to create a run folder with dispatch plan and prompts.
4. Main agent executes, integrates, verifies, and reports.

## Non-Negotiables

- Main agent owns final user commitments.
- Specialist agents are bounded and advisory unless explicitly delegated.
- Sidecar agents default to read-only.
- External effects require explicit approval.
- Hidden chain-of-thought is never requested; agents provide evidence and concise rationale.
