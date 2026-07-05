---
name: codex-agent-identity-bank
description: Auto-select bounded specialist Codex agent identities and supporting skills from a local identity repository. Use when a task needs specialist subagents, role/persona routing, choosing between embedded engineer, UI engineer, backend engineer, security reviewer, DevOps engineer, QA, docs researcher, product/architect roles, or deciding which existing Codex skill should be attached to a subagent.
---

# Codex Agent Identity Bank

## Overview

Use this skill as the identity router for multi-agent Codex work. It decides which specialist identities should exist for a task, which supporting skills each identity should load, and how to keep each identity bounded.

This skill is designed to work with `codex-multi-agent-orchestrator`: identity-bank selects specialist identities and skills; the orchestrator decides dispatch pattern, handoffs, traffic control, and evidence synthesis.

## Autopilot

Default to automatic routing. The user should not need to name roles, skills, or agent types.

1. Read the task, scope, files, tools, and risk signals.
2. Run `scripts/route_identity.py --task "<task>" --scope "<scope>" --context "<context>"` when a deterministic route is useful.
3. Use the top identity as primary and the next one to three identities as sidecar specialists.
4. Use the returned orchestration pattern as input to `codex-multi-agent-orchestrator`.
5. Attach mapped skills only when relevant and available.
6. If real subagent tools are available and the user explicitly asked for multi-agent work, dispatch bounded subagents with the generated prompts.
7. If no subagent tool exists, use the generated identity prompts as copyable dispatch packets.

## Routing Rules

- Tiny single-file edits: keep local; do not create specialist agents.
- Embedded, firmware, board, MCU, CAN, UART, J-Link, OpenOCD, Keil, GCC: route to embedded/firmware identities and attach matching hardware skills.
- UI, frontend, React, Next.js, CSS, accessibility, responsive design: route to UI/frontend identities and attach Playwright for browser verification when useful.
- API, backend, database, cache, auth, queue, payment: route to backend/API/database/security identities.
- Cloud, CI, Docker, deploy, observability, release: route to DevOps/platform/release identities.
- Bug, failing tests, regression: add QA/test-runner and reviewer identities.
- Security, secrets, auth, permissions, injection, dependency risk: add security engineer and security review skill.
- Docs, SDK, current API, latest behavior: add docs researcher and prefer primary sources.
- Architecture/options/refactor/migration: add architect and reviewer identities; use multi-agent orchestrator for group-chat, SOP, or critic-loop patterns.

## Identity Contract

Every generated identity must include:

- Identity: specific specialist role, not the main agent.
- Authority: advisory unless write authority is explicitly delegated.
- Scope: files, commands, tools, and source boundaries.
- Skills: relevant skill names to read before acting.
- Forbidden actions: no external side effects, no completion claims, no hidden chain-of-thought output.
- Output: findings, evidence, risks, open questions, recommended next action.

## Repository Files

- `references/identities.json`: machine-readable identity definitions and keyword routing.
- `references/identity-catalog.md`: human-readable role catalog and source notes.
- `scripts/route_identity.py`: deterministic identity and skill router.
- `../../identities/`: repo-level specialist identity cards grouped by domain.
- `../../workflows/`: reusable multi-agent workflow templates.
- `../../presets/`: ready-made team-size and domain presets.
- `../../scripts/spawn-team.py`: generate a run folder with dispatch plan, prompts, and synthesis file.

## Script

Auto-route a task:

```bash
python .agents/skills/codex-agent-identity-bank/scripts/route_identity.py --task "fix UART packet loss on STM32" --scope "firmware drivers tests"
```

Limit the number of identities:

```bash
python .agents/skills/codex-agent-identity-bank/scripts/route_identity.py --task "redesign the admin dashboard" --scope "src/app components tests" --max 3
```

Manual filtering remains possible with `--include-skill` when the main agent already knows a required skill.

Machine-readable dispatch plan:

```bash
python .agents/skills/codex-agent-identity-bank/scripts/route_identity.py --task "audit login auth" --scope "src/auth tests" --json
```

Create a tracked run folder:

```bash
python .agents/scripts/spawn-team.py --task "fix UART packet loss on STM32" --scope "firmware drivers tests"
```
