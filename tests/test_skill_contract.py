from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "codex-native-subagent-orchestrator"
README = ROOT / "README.md"


class SkillContractTests(unittest.TestCase):
    def test_skill_has_required_metadata_and_resources(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: codex-native-subagent-orchestrator", text)
        self.assertIn("spawn_agent", text)
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())

        for reference in (
            "delegation-rubric.md",
            "role-catalog.md",
            "dispatch-contract.md",
            "workflow-patterns.md",
        ):
            self.assertTrue((SKILL / "references" / reference).is_file())

    def test_description_is_a_short_activation_rule(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        description = next(line for line in text.splitlines() if line.startswith("description:"))

        self.assertTrue(description.startswith("description: Use when"))
        self.assertLess(len(description), 500)

    def test_skill_keeps_subagents_read_only_and_bounded(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("read-only", text)
        self.assertIn("one to three", text)
        self.assertIn("fourth", text)
        self.assertIn("main agent", text)

    def test_read_only_is_an_instruction_with_a_worktree_check(self) -> None:
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").lower().split())

        self.assertIn("cannot independently sandbox", text)
        self.assertIn("before dispatching", text)
        self.assertIn("git diff", text)

    def test_skill_checks_native_capacity_before_dispatching(self) -> None:
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())

        self.assertIn("spawn_agent is unavailable", text)
        self.assertIn("platform's available concurrency", text)

    def test_skill_preserves_preexisting_worktree_changes(self) -> None:
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())

        self.assertIn("baseline is already dirty", text)
        self.assertIn("Do not attribute pre-existing changes", text)

    def test_skill_degrades_cleanly_outside_a_git_repository(self) -> None:
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())

        self.assertIn("not a Git repository", text)
        self.assertIn("skip the Git baseline", text)

    def test_dispatch_contract_prevents_scope_expansion(self) -> None:
        text = (SKILL / "references" / "dispatch-contract.md").read_text(encoding="utf-8")

        self.assertIn("Do not expand the scope", text)
        self.assertIn("Stop after answering the mission", text)

    def test_readme_uses_portable_validation_instructions(self) -> None:
        text = README.read_text(encoding="utf-8")

        self.assertNotIn("C:\\Users\\", text)
        self.assertIn("python -m unittest discover -s tests -v", text)
        self.assertIn("Test-Path", text)
        self.assertIn("already exists", text)
        self.assertIn("New-Item -ItemType Directory", text)
        self.assertIn("mkdir -p", text)
        self.assertIn("$env:CODEX_HOME", text)

    def test_readme_states_the_native_subagent_prerequisite(self) -> None:
        text = README.read_text(encoding="utf-8")

        self.assertIn("native subagent support", text)
        self.assertIn("spawn_agent", text)

    def test_repository_guidance_requires_only_available_validators(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("python -m unittest discover -s tests -v", text)
        self.assertNotIn("bundled\n  `quick_validate.py`", text)

    def test_bugfix_example_contains_a_complete_dispatch_packet(self) -> None:
        for name in ("bugfix.md", "code-review.md", "research.md"):
            text = (SKILL / "examples" / name).read_text(encoding="utf-8")

            for heading in (
                "## Identity",
                "## Mission",
                "## Current Situation",
                "## Allowed Scope",
                "## Allowed Actions",
                "## Forbidden Actions",
                "## Required Evidence",
                "## Output Contract",
                "## Conflict Policy",
                "## Stop Condition",
            ):
                self.assertIn(heading, text, name)

            self.assertIn("read-only", text, name)
            self.assertIn("Do not modify files", text, name)
            self.assertIn("shared workspace", text, name)
            self.assertIn("Do not expand the scope", text, name)
            self.assertIn("non-mutating and non-networked", text, name)
            self.assertIn("third-party mutations", text, name)

    def test_repository_has_a_dependency_free_ci_check(self) -> None:
        workflow = ROOT / ".github" / "workflows" / "ci.yml"
        text = workflow.read_text(encoding="utf-8")

        self.assertIn("python -m unittest discover -s tests -v", text)
        self.assertIn("windows-latest", text)
        self.assertIn('"on":', text)

    def test_skill_handles_failed_or_missing_agent_results(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("fails, times out, or returns no usable result", text)
        self.assertIn("Do not wait indefinitely", text)

    def test_dispatch_contract_does_not_claim_permission_enforcement(self) -> None:
        text = (SKILL / "references" / "dispatch-contract.md").read_text(encoding="utf-8")

        self.assertIn("instructed to remain read-only", text)
        self.assertNotIn("Authority: Advisory and read-only.", text)

    def test_dispatch_contract_accounts_for_a_shared_worktree(self) -> None:
        text = (SKILL / "references" / "dispatch-contract.md").read_text(encoding="utf-8")

        self.assertIn("shared workspace", text)
        self.assertIn("Do not revert", text)

    def test_dispatch_contract_limits_diagnostics_to_safe_commands(self) -> None:
        text = " ".join(
            (SKILL / "references" / "dispatch-contract.md").read_text(encoding="utf-8").split()
        )

        self.assertIn("non-mutating and non-networked", text)
        self.assertIn("Do not run a test", text)
        self.assertIn("main agent", text)

    def test_skill_collects_started_agents_before_completion(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Collect every started agent", text)
        self.assertIn("before reporting task completion", text)

    def test_skill_has_all_recovery_and_concurrency_invariants(self) -> None:
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())

        for rule in (
            "spawn_agent is unavailable",
            "platform's available concurrency",
            "at most one narrowly scoped replacement",
            "Collect every started agent",
        ):
            self.assertIn(rule, text)
