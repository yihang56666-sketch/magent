# Identity Catalog

This catalog is a local, Codex-specific identity repository. It summarizes patterns from public agent-role collections and maps them to installed skills in this workspace.

## Source Notes

- Anthropic Claude Code subagents document the core behavior this repository emulates: subagents have separate context windows, custom system prompts, tool permissions, and Claude can delegate based on task description. Source: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- VoltAgent `awesome-claude-code-subagents` shows broad marketplace-style organization for many specialist subagents across development, design, product, security, data, and operations. Source: https://github.com/VoltAgent/awesome-claude-code-subagents
- `0xfurai/claude-code-subagents` demonstrates a large professional role library with categories such as engineering, design, security, and operations. Source: https://github.com/0xfurai/claude-code-subagents
- AgentHub-style repositories show that a useful agent library should combine agents, skills, workflows, and commands rather than personas alone. Source pattern: https://github.com/SKB3002/agenthub
- Embedded-specific public skills influenced the local embedded mappings, but this repository keeps hardware actions gated by explicit user approval.

## Identity Families

Engineering:
- Embedded Firmware Engineer
- Hardware Bring-up Engineer
- Frontend UI Engineer
- UX and Accessibility Engineer
- Backend API Engineer
- Database Engineer
- Mobile Engineer
- Performance Engineer

Quality and risk:
- Security Engineer
- QA and Test Automation Engineer
- Code Reviewer
- Observability Engineer

Platform and operations:
- DevOps and Platform Engineer
- Technical Writer
- Product Engineer

AI and architecture:
- LLM Agent Engineer
- Software Architect
- Data and ML Engineer

## Selection Principles

- Prefer capability over title. Pick the identity whose tools and evidence loop match the task.
- Add reviewers to risky changes, failing tests, migrations, auth/security work, and external integrations.
- Add docs researchers when the answer depends on current APIs, SDKs, standards, or release behavior.
- Add embedded identities when physical protocols, firmware builds, probes, boards, or MCU debugging are mentioned.
- Keep the main agent responsible for the user, final decisions, edits, verification claims, and external actions.

## Skill Mapping Examples

- Embedded Firmware Engineer -> `gcc`, `keil`, `jlink`, `openocd`, `probe-rs`, `serial`, `can`, `workflow`
- Hardware Bring-up Engineer -> `jlink`, `openocd`, `probe-rs`, `serial`, `can`, `net`
- Frontend UI Engineer -> `playwright`, `frontend-patterns`
- Security Engineer -> `security-best-practices`, `error-handling`
- QA and Test Automation Engineer -> `tdd-workflow`, `e2e-testing`, `playwright`, `verification-loop`
- LLM Agent Engineer -> `openai-docs`, `eval-harness`, `codex-multi-agent-orchestrator`
