# Codex Multi-Agent Project Instructions

This repository contains a project-local multi-agent identity bank and orchestration layer for Codex.

Before acting on a request here, read the mandatory skill gate from your local
Codex skills directory, usually `~/.codex/skills/using-superpowers/SKILL.md`.

Use .agents/skills/codex-agent-identity-bank/SKILL.md for role and skill routing.
Use .agents/skills/codex-multi-agent-orchestrator/SKILL.md for dispatch boundaries, traffic control, and synthesis.

Project-local Codex roles are wired in .codex/config.toml: explorer, reviewer, docs-researcher, traffic-controller, and implementer.

Generate deterministic routing with python .agents/scripts/spawn-team.py --task TASK --scope SCOPE.

The main Codex agent owns final decisions, verification claims, and the user response. Subagents are bounded evidence producers or delegated workers and must not claim final completion.
