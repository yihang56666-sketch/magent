# Native Subagent Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Magent runtime with a portable, tested Codex Skill that delegates general tasks to bounded read-only native subagents.

**Architecture:** Ship one skill directory with a concise operational `SKILL.md`, routing, role, pattern, and dispatch-contract references, plus examples. Use Python 3.10 standard-library `unittest` structural tests; do not attempt to invoke Codex session-internal APIs.

**Tech Stack:** Markdown, YAML, Python 3.10 standard-library `unittest`.

---

## File Structure

```text
codex-native-subagent-orchestrator/
  SKILL.md
  agents/openai.yaml
  references/delegation-rubric.md
  references/role-catalog.md
  references/dispatch-contract.md
  references/workflow-patterns.md
  examples/bugfix.md
  examples/code-review.md
  examples/research.md
tests/test_skill_contract.py
README.md
```

### Task 1: Establish a failing contract test

**Files:** Create `tests/test_skill_contract.py`.

- [ ] Write a test that checks `SKILL.md` frontmatter, current-session tool
  language (for example `create_thread`), all four reference files,
  `agents/openai.yaml`, the phrases `read-only`, `one to three`, `fourth`, and
  `main agent`.
- [ ] Run `python -m unittest tests.test_skill_contract -v` and observe failure
  because the new Skill is absent.

### Task 2: Implement the portable skill

**Files:** Create every file in `codex-native-subagent-orchestrator/` listed
above.

- [ ] Make `SKILL.md` decide keep-local versus delegation, choose the smallest
  team and pattern, construct packets, create native subagents only for
  independent read-only work, and require main-agent synthesis and edits.
- [ ] Add catalog roles: explorer, domain analyst, reviewer, test analyst,
  security reviewer, documentation researcher, and architect. Dynamic roles
  require one mission, explicit scope, evidence needs, and a stop condition.
- [ ] Require dispatch headings: Identity, Mission, Current Situation, Allowed
  Scope, Allowed Actions, Forbidden Actions, Required Evidence, Output
  Contract, Conflict Policy, Stop Condition. Require no writes, no external
  side effects, no global completion claim, and at most one repair follow-up.
- [ ] Add concise bugfix, code-review, and research packet examples.
- [ ] Run `python -m unittest tests.test_skill_contract -v`; expect PASS.

### Task 3: Replace the legacy repository surface

**Files:** Delete legacy Magent runtime files under `.agents/`, `.claude/`,
`.codex/`, `scripts/`, legacy `tests/`, legacy product docs, `EXAMPLE.md`,
`CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `pyproject.toml`,
`requirements.txt`, and `requirements-dev.txt`. Preserve `.git/`,
`.gitattributes`, `.gitignore`, `AGENTS.md`, `LICENSE`, `CODE_OF_CONDUCT.md`,
the approved specification, and this plan.

- [ ] Replace `README.md` with installation, trigger scope, read-only policy,
  team limits, and explicit non-goals.
- [ ] Remove only obsolete tracked Magent artifacts after the new Skill and
  tests exist. Leave user-owned untracked plans untouched.
- [ ] Run `python -m unittest discover -s tests -v`; expect all tests passing.

### Task 4: Validate distribution readiness

- [ ] Run `python <user-home>/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex-native-subagent-orchestrator`; expect success.
- [ ] Run `git diff --check` and inspect `git status --short` for only intended
  conversion changes.
- [ ] Commit the conversion with `git add -A` and
  `git commit -m "feat: ship native subagent orchestration skill"`.
