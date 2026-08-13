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

    def test_readme_uses_portable_validation_instructions(self) -> None:
        text = README.read_text(encoding="utf-8")

        self.assertNotIn("C:\\Users\\", text)
        self.assertIn("python -m unittest discover -s tests -v", text)
        self.assertIn("Test-Path", text)
        self.assertIn("already exists", text)

    def test_bugfix_example_contains_a_complete_dispatch_packet(self) -> None:
        for name in ("bugfix.md", "code-review.md", "research.md"):
            text = (SKILL / "examples" / name).read_text(encoding="utf-8")

            for heading in (
                "## Identity",
                "## Mission",
                "## Allowed Scope",
                "## Forbidden Actions",
                "## Required Evidence",
                "## Stop Condition",
            ):
                self.assertIn(heading, text, name)

    def test_repository_has_a_dependency_free_ci_check(self) -> None:
        workflow = ROOT / ".github" / "workflows" / "ci.yml"
        text = workflow.read_text(encoding="utf-8")

        self.assertIn("python -m unittest discover -s tests -v", text)
        self.assertIn("windows-latest", text)
