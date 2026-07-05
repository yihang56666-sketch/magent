# Coordination Protocols

## Relationship Map

Maintain this map whenever more than one subagent is active:

```markdown
Goal:
- <user goal>

Main Agent:
- Owns: final decision, edits, verification, user response

Agents:
- <agent id>: <role>, scope=<scope>, status=<ready|running|blocked|done>

Dependencies:
- <agent id> depends on <agent id or artifact> because <reason>

Shared Artifacts:
- <file/report/log>: owner=<agent id>, consumers=<agent ids>

Conflicts:
- <claim A> vs <claim B>, evidence=<links/files>, resolver=<main|traffic-controller>

Next Merge Decision:
- <what the main agent should do next>
```

## Control Pattern Header

Add this header before launching multiple agents:

```markdown
Control pattern:
- Pattern: <supervisor|handoff|sop|group-chat|critic-loop|stateful-observer>
- Router: <main-agent|traffic-controller>
- State owner: <main-agent|traffic-controller>
- Termination rule: <max rounds, artifact complete, verification complete, or blocked>
- Merge rule: <who reconciles outputs and what evidence is required>
```

## Standing-Watch Pattern

Use this when the user wants subagents "watching" while the main agent works.

Preferred implementation:
- Keep role cards prepared, but do not spawn idle agents unless the platform supports long-running agents cheaply.
- When the main agent reaches a decision point, dispatch the relevant role with a fresh context packet.
- Include the latest files changed, commands run, open risks, and the exact question to answer.

If long-running subagents are available:
- Give each watch agent read-only authority.
- Require them to stay silent until asked or until a predeclared trigger occurs.
- Give them a maximum observation scope and stop condition.
- Refresh their context after major plan or code changes.

## Conflict Register

Every contradiction must be recorded before synthesis:

```markdown
Conflict:
- Claim A:
- Evidence A:
- Claim B:
- Evidence B:
- Impact if A is true:
- Impact if B is true:
- Resolution needed:
- Recommended resolver:
```

Resolution rules:
- Prefer direct repo evidence over memory.
- Prefer executed verification over static reasoning.
- Prefer primary official sources over secondary summaries.
- Mark unresolved conflicts explicitly; do not hide them in the final synthesis.

## Synthesis Rules

The main agent or traffic controller must convert subagent output into:

- Accepted facts: supported by evidence and relevant to the task.
- Rejected claims: contradicted, out of scope, or unsupported.
- Follow-up checks: required before implementation or completion.
- Action decision: implement, verify, ask user, or stop.

Never merge subagent private reasoning. Merge observable evidence, concise rationale, and decisions.

## Handoff Packet

Use this when one subagent's output feeds another:

```markdown
From:
To:
Artifact:
Accepted facts:
Open risks:
Explicit question for receiver:
Forbidden assumptions:
Stop condition:
```

## Phase Gate

Use this for SOP-style work:

```markdown
Phase:
Required inputs:
Assigned role:
Expected artifact:
Evidence required:
Exit criteria:
Next phase:
```

## Observation Log

Use this for stateful observer or standing-watch patterns:

```markdown
Event:
- Order:
- Source agent:
- Observed artifact:
- Claim:
- Evidence:
- Decision impact:
- Still current: <yes|no|unknown>
```
