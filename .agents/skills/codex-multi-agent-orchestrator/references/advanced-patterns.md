# Advanced Coordination Patterns

These patterns extend the 6 core patterns with more sophisticated multi-agent collaboration strategies.

## Pattern: Competitive

**Use when:** Multiple agents should propose different solutions and compete for selection.

**Rules:**
- Spawn N agents with the same task but independent approaches
- Each agent proposes a complete solution without seeing others
- Traffic controller scores proposals against criteria
- Main agent selects winner or hybrid approach
- Document why alternatives were rejected

**Example:**
```yaml
name: competitive-architecture
pattern: competitive
competitors: 3
judging_criteria:
  - scalability
  - maintainability
  - time_to_implement
phases:
  - independent_proposals
  - criteria_scoring
  - selection_with_rationale
```

**Failure modes:**
- All solutions similar (lack of diversity)
- Scoring criteria unclear or subjective
- Losing agents' insights ignored

---

## Pattern: Voting

**Use when:** Need consensus from multiple specialist perspectives.

**Rules:**
- Each agent independently evaluates the same artifact/decision
- Agents cast weighted votes (approve/reject/abstain)
- Voting weights based on domain relevance
- Require threshold (e.g., 2/3 approval) to pass
- Document dissenting opinions

**Example:**
```yaml
name: merge-decision-voting
pattern: voting
voters:
  - security-engineer: weight=2
  - code-reviewer: weight=1
  - qa-engineer: weight=1
threshold: 0.66
phases:
  - independent_review
  - vote_casting
  - tally_and_decision
```

**Failure modes:**
- Voting becomes popularity contest
- Minority expert opinion ignored
- No mechanism to resolve ties

---

## Pattern: Hierarchical

**Use when:** Task naturally decomposes into manager + workers with clear authority layers.

**Rules:**
- Coordinator agent creates work breakdown
- Worker agents execute bounded subtasks in parallel
- Workers report back to coordinator only
- Coordinator synthesizes and escalates to main agent
- Clear authority: workers don't make cross-cutting decisions

**Example:**
```yaml
name: large-refactor
pattern: hierarchical
coordinator: software-architect
workers:
  - backend-api-engineer: scope=src/api/
  - frontend-ui-engineer: scope=src/components/
  - database-engineer: scope=migrations/
phases:
  - plan_breakdown
  - parallel_execution
  - coordinator_synthesis
  - main_agent_approval
```

**Failure modes:**
- Coordinator becomes bottleneck
- Workers blocked waiting for coordinator
- Cross-worker dependencies not managed

---

## Pattern: Debate

**Use when:** Need to stress-test a proposal through adversarial dialogue.

**Rules:**
- Proponent agent defends a proposal
- Opponent agent attacks it with counter-evidence
- Moderator (traffic controller) tracks claims and counter-claims
- Multiple rounds until convergence or stalemate
- Main agent decides based on debate transcript

**Example:**
```yaml
name: security-trade-off-debate
pattern: debate
proponent: performance-engineer
opponent: security-engineer
moderator: traffic-controller
rounds: 3
phases:
  - initial_proposal
  - attack_round_1
  - defense_round_1
  - attack_round_2
  - defense_round_2
  - synthesis_and_decision
```

**Failure modes:**
- Debate becomes circular
- Agents too polite (no real adversarial pressure)
- Too many rounds without convergence

---

## Pattern: Incremental Consensus

**Use when:** Building agreement through iterative refinement.

**Rules:**
- Start with rough proposal from one agent
- Each subsequent agent adds constraints, corrections, or refinements
- Every agent sees cumulative history
- Converge when no agent proposes changes
- Main agent validates final consensus

**Example:**
```yaml
name: api-contract-design
pattern: incremental-consensus
sequence:
  - backend-api-engineer: draft_endpoints
  - frontend-ui-engineer: add_client_needs
  - security-engineer: add_auth_requirements
  - database-engineer: add_data_constraints
  - code-reviewer: final_consistency_check
convergence: no_changes_proposed
```

**Failure modes:**
- Early decisions lock in bad patterns
- Agents add conflicting constraints
- Never converges (endless tweaking)

---

## Pattern: Specialist Chain

**Use when:** Each agent's output becomes next agent's input with domain-specific transformations.

**Rules:**
- Strict sequential handoff (A → B → C)
- Each agent transforms input to output
- No backtracking unless main agent intervenes
- Clear artifact format at each stage
- Final agent produces deliverable

**Example:**
```yaml
name: data-pipeline-build
pattern: specialist-chain
chain:
  - data-ml-engineer: raw_data_ingestion_code
  - backend-api-engineer: rest_api_wrapper
  - frontend-ui-engineer: visualization_dashboard
  - qa-test-automation-engineer: end_to_end_tests
artifact_formats:
  - ingestion: Python script + schema
  - api: OpenAPI spec + implementation
  - dashboard: React components
  - tests: Playwright test suite
```

**Failure modes:**
- Upstream errors cascade downstream
- Intermediate artifacts poorly specified
- No feedback loop if final output is wrong

---

## Pattern Selection Matrix (Extended)

```
Need diverse competing solutions? → competitive
Need consensus from experts? → voting
Large task with clear subtask boundaries? → hierarchical
Stress-test a proposal? → debate
Build agreement iteratively? → incremental-consensus
Domain-specific transformation chain? → specialist-chain
```

---

## Combining Patterns

Patterns can be nested:

**Example: Hierarchical + Competitive**
```
Main agent
  └─ Coordinator (software-architect)
      ├─ Worker Team A (competitive proposal 1)
      │   ├─ frontend-ui-engineer
      │   └─ backend-api-engineer
      └─ Worker Team B (competitive proposal 2)
          ├─ frontend-ui-engineer
          └─ backend-api-engineer
```

**Example: Voting + Critic-Loop**
```
Implementer → draft
  → Reviewer panel (voting pattern)
      ├─ security-engineer
      ├─ code-reviewer
      └─ qa-engineer
  → If rejected: implementer revises → re-vote
```

---

## Pattern Configuration

Add to `.agents/skills/codex-multi-agent-orchestrator/references/open-source-patterns.md` and update routing logic in `render_agent_pack.py` to support these patterns.
