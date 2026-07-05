# Open-Source Multi-Agent Patterns

These patterns adapt ideas from established open-source projects while keeping Codex as the control surface. Use them as design constraints, not as a requirement to install the frameworks.

## Project Signals

- LangGraph / LangChain multi-agent docs: Graph/state orchestration, supervisor routing, and handoff edges. Source: https://docs.langchain.com/oss/python/langchain/multi-agent/index
- CrewAI: Role/task/crew separation, sequential or hierarchical processes, manager validation, and execution logs. Source: https://docs.crewai.com/en/concepts/crews
- AutoGen AgentChat: Agents, teams, selector group chat, directed workflows, state, logging, tracing, and termination. Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html
- OpenAI Swarm: Lightweight agents and handoffs, explicitly educational and client-side. Source: https://github.com/openai/swarm
- MetaGPT: SOP-oriented software company roles; reusable phase order and deliverables prevent ad hoc collaboration. Source: https://github.com/FoundationAgents/MetaGPT
- ChatDev: Communicative software-development agents and configurable multi-agent orchestration. Source: https://github.com/OpenBMB/ChatDev
- AgentScope: Leader/worker teams, tracked planning, permission control, background task offloading, and observable agent service patterns. Source: https://github.com/agentscope-ai/agentscope
- CAMEL: Role-playing agent societies, message handling, memory, RAG, and multi-agent applications. Source: https://github.com/camel-ai/camel

## Pattern: Supervisor

Use when:
- Three or more subagents are active.
- Multiple agents may inspect overlapping evidence.
- You need one place to resolve conflicts and choose next dispatches.

Rules:
- Assign `traffic-controller` as supervisor.
- Agents do not talk to each other directly.
- Supervisor maintains relationship map, conflict register, and next merge decision.
- Main agent still owns final implementation and user response.

Failure mode to prevent:
- Supervisor becoming a second main agent. Keep it advisory and evidence-focused.

## Pattern: Handoff

Use when:
- Work naturally moves from one specialist to another.
- Example: explorer gathers evidence, implementer drafts patch, test-runner verifies, reviewer audits.

Rules:
- Every transition uses a handoff packet.
- Receiver gets accepted facts, open risks, explicit question, forbidden assumptions, and stop condition.
- Do not copy entire prior context when a concise accepted-facts bundle is enough.

Failure mode to prevent:
- Context drift where downstream agents inherit unsupported assumptions.

## Pattern: SOP Pipeline

Use when:
- The task has repeatable phases.
- Example: investigate -> design -> implement -> verify -> review -> summarize.

Rules:
- Define phase gates before dispatch.
- Each phase must produce a concrete artifact or decision.
- Do not start the next phase until required evidence exists.

Failure mode to prevent:
- Parallel agents optimizing different goals because no shared phase gate exists.

## Pattern: Group-Chat Arbitration

Use when:
- You want independent perspectives on the same question.
- Example: architecture option A vs option B, risk review, API design tradeoffs.

Rules:
- Give each agent a separate viewpoint or evidence scope.
- Assign traffic-controller to summarize agreements, disagreements, and missing evidence.
- Limit to one or two rounds unless the user explicitly wants deeper debate.

Failure mode to prevent:
- Endless debate. Terminate after a decision, unresolved question, or verification need is identified.

## Pattern: Critic Loop

Use when:
- A patch, design, migration, or security-sensitive change needs pressure testing.

Rules:
- Implementer proposes or applies the narrow change.
- Reviewer attacks correctness and risk.
- Test-runner verifies concrete behavior.
- Main agent accepts, revises, or rejects based on evidence.

Failure mode to prevent:
- Reviewer rewriting implementation instead of producing findings.

## Pattern: Stateful Observer

Use when:
- The user asks for agents to keep watching while the main agent works.

Rules:
- Prefer dormant role cards over idle live agents.
- If live observers are available, give read-only scope, explicit triggers, silence-until-needed behavior, and refresh points.
- Maintain an observation log with timestamp/order, source, and decision impact.

Failure mode to prevent:
- Passive agents accumulating stale context and later influencing decisions with obsolete assumptions.

## Pattern Selection Matrix

```markdown
Need parallel independent evidence? -> supervisor
Need sequential specialists? -> handoff
Need repeatable software-development phases? -> sop
Need compare opinions/options? -> group-chat
Need attack a proposed solution? -> critic-loop
Need "watching" agents? -> stateful-observer
```
