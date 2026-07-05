# Example: Complete Manual Workflow

This example shows the full lifecycle of a Magent run.

## Scenario

Task: review a login module for security and test coverage gaps.

Scope: `src/auth tests/auth`

## 1. Generate a run

```bash
python .agents/magent.py run --task "review the login module for security and test coverage gaps" --scope "src/auth tests/auth" --max 4
```

Expected result:

```text
Prepared run: <run-id>
  Agent count: 4
  Prompts: .agents/reports/runs/<run-id>/agent-prompts.md
  Workflow: .agents/reports/runs/<run-id>/manual-execution.md
```

## 2. Show the next agent

```bash
python .agents/magent.py next latest
```

The command prints a bounded packet for the next pending specialist. Copy that
packet into the current Codex session.

## 3. Save the agent output

Each agent output should use this structure:

```markdown
## Findings

## Evidence

## Risks

## Open Questions

## Recommended Next Action

## Handoff
- Next speaker: <next-agent-or-main-agent>
```

Save the answer to the matching file, for example:

```text
.agents/reports/runs/<run-id>/security-engineer.output.md
```

## 4. Sync status

```bash
python .agents/magent.py sync latest
python .agents/magent.py status latest
python .agents/magent.py next latest
```

Repeat the copy, answer, save, and sync loop until all agents are complete.

## 5. Merge results

```bash
python .agents/scripts/merge-results.py .agents/reports/runs/<run-id>
```

The generated `synthesis.md` aggregates findings, risks, questions, and
recommendations.

## 6. Main-agent decision

The main Codex session reviews `synthesis.md`, checks the evidence, resolves
conflicts, implements any accepted changes, and runs verification.

Specialist outputs are advisory. The main agent owns final decisions and any
claim that work is complete.

## Useful variations

Limit the number of agents:

```bash
python .agents/magent.py run --task "review docs release readiness" --scope "README.md docs" --max 2
```

Start the dashboard:

```bash
python .agents/magent.py ui
```
