# Codex Native Subagent Orchestrator: Design

## Goal

Replace Magent's manual prompt-pack runtime with a single, installable Codex
Skill that helps the main Codex agent decide when to delegate work, create
bounded native subagents, and synthesize their evidence efficiently.

The target is general software and knowledge-work tasks, not a domain-specific
agent framework.

## Product Boundary

The repository ships one portable Skill directory:

```text
codex-native-subagent-orchestrator/
  SKILL.md
  references/
    delegation-rubric.md
    role-catalog.md
    dispatch-contract.md
    workflow-patterns.md
  examples/
    bugfix.md
    code-review.md
    research.md
```

Users install or copy that directory into `~/.codex/skills/`. The Skill uses
Codex's native subagent facility; it is not an agent runtime, CLI, dashboard,
state store, or prompt-copy workflow.

## Responsibilities

The Skill directs the main agent through this sequence:

1. Assess delegation value from complexity, uncertainty, risk, independent
   work, and expected coordination cost.
2. Keep small, obvious, or tightly coupled tasks local.
3. Select the smallest effective team, normally one to three subagents.
4. Select a role from the catalog or create a bounded temporary specialist
   where the catalog has no adequate role.
5. Choose one execution pattern: parallel evidence gathering, critic loop,
   sequential handoff, or supervisor-led analysis.
6. Send native subagents complete, read-only dispatch packets.
7. Continue useful main-agent work while agents run, then reconcile their
   results as evidence rather than commands.
8. Let the main agent make all edits, run final verification, and communicate
   completion to the user.

## Authority Model

All dispatched subagents are read-only. They may inspect files, run safe
diagnostics and tests, research public documentation when authorized, and make
recommendations. They must not change files, stage or commit code, publish,
push, modify third-party resources, or claim overall task completion.

The main Codex agent is the sole writer and task owner. It independently checks
important claims before relying on them.

## Team Sizing And Patterns

Default maximum: three subagents. A fourth is permitted only for a security
sensitive task or a clearly cross-domain task where its scope is independent.

| Situation | Pattern | Default team |
| --- | --- | --- |
| Unknown codebase or broad investigation | Parallel evidence gathering | Explorer + domain analyst + reviewer |
| Bug or regression | Critic loop | Investigator + test analyst + reviewer |
| Security-sensitive change | Parallel review | Domain analyst + security reviewer + test analyst; optional fourth reviewer |
| Design, migration, or architecture choice | Supervisor-led analysis | Explorer + architect + critic |
| Dependent research steps | Sequential handoff | Researcher followed by reviewer |

No subagents are launched for a narrow single-file change, an obvious request,
or work where the cost of distributing context exceeds independent benefit.

## Role Strategy

The bundled catalog supplies reusable roles:

- Explorer: map the relevant code, constraints, and likely change points.
- Domain analyst: investigate a domain-specific question.
- Reviewer: challenge correctness, regressions, and assumptions.
- Test analyst: identify reproduction and verification evidence.
- Security reviewer: inspect trust boundaries and misuse paths.
- Documentation researcher: verify current public documentation and APIs.
- Architect: compare designs, dependencies, and migration risks.

For an uncovered specialty, the main agent creates a temporary role that states
its expertise, one concrete mission, allowed sources, evidence requirements,
and a stop condition. Dynamic roles inherit the same read-only and no-external-
side-effects constraints as catalog roles.

## Dispatch Contract

Every native subagent prompt contains:

- role and advisory authority;
- one concrete mission and current task context;
- explicit files, directories, commands, or sources in scope;
- read-only actions allowed;
- forbidden writes and external side effects;
- expected evidence and concise response headings;
- conflict policy: report disagreement rather than resolving it by changing
  work;
- stop condition.

Subagents report findings, evidence, risks, open questions, and a recommended
next action. They never expose private reasoning traces.

## Failure Handling

The main agent treats missing evidence, contradictory conclusions, or scope
drift as incomplete input. It may ask one bounded follow-up of the same agent,
run a direct check, or discard the finding. It must not delegate edits to repair
a weak report. If a subagent cannot proceed, the main agent records the blocker
in its own synthesis and chooses a local next step.

## Testing And Documentation

The repository verifies the Skill as text-based product behavior:

- structural tests assert the installable file layout and required dispatch
  contract sections;
- routing fixtures cover keep-local decisions, common patterns, team-size
  limits, and temporary-role triggers;
- examples demonstrate bugfix, code review, and research delegation;
- README documents installation, activation triggers, limitations, and the
  main-agent authority model.

No test will pretend to invoke Codex-internal subagent APIs from Python.

## Non-Goals

- No Python command-line product or workflow dashboard.
- No manual prompt/output file lifecycle.
- No model API client, telemetry, hosted service, or external action executor.
- No subagent write access in the initial release.
- No assertion that delegation is always faster or better.

## Acceptance Criteria

The first release is complete when a user can install the Skill, give Codex a
general task, and obtain an explicit keep-local or bounded native-delegation
decision. Delegated agents are read-only, stay within the team-size cap, return
evidence in the defined form, and leave final edits and verification with the
main agent.
