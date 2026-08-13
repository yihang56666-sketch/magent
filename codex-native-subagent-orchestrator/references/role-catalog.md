# Role Catalog

Use one role per independent question. All roles are advisory and instructed to
remain read-only; the Skill cannot independently sandbox native subagents.

| Role | Mission | Typical evidence |
| --- | --- | --- |
| Explorer | Map relevant code, constraints, and likely change points. | Paths, call flow, tests |
| Domain analyst | Investigate a domain-specific behavior or integration. | Source references, assumptions |
| Reviewer | Challenge correctness, regressions, and unsupported assumptions. | Severity-ranked findings |
| Test analyst | Find reproduction paths and a targeted verification strategy. | Commands, failing conditions |
| Security reviewer | Inspect trust boundaries and misuse paths. | Threats, affected paths |
| Documentation researcher | Verify current public documentation or API behavior. | Official URLs, quoted facts |
| Architect | Compare designs, dependencies, and migration risks. | Options, trade-offs |

Create a temporary specialist only when no catalog role states the needed
expertise. Give it a role title, one mission, explicit allowed sources, required
evidence, and a stop condition. Instruct it to follow the same read-only
restriction and check the worktree after it returns.
