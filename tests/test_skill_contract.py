from pathlib import Path
import os
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "codex-native-subagent-orchestrator"
README = ROOT / "README.md"

TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".toml", ".txt"}
IGNORED_DIRS = {".git", ".worktrees", ".pytest_cache", "__pycache__", "node_modules"}


def iter_text_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in TEXT_SUFFIXES:
                yield path


class SkillContractTests(unittest.TestCase):
    def test_repository_text_files_do_not_expose_machine_specific_paths(self) -> None:
        private_path = re.compile("D:" + "[\\\\/]|C:" + "[\\\\/]Users|" + "35" + "182")
        leaks = []
        for path in iter_text_files(ROOT):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if private_path.search(text):
                leaks.append(path.as_posix())

        self.assertEqual(leaks, [])

    def test_local_claude_settings_do_not_contain_broad_permissions(self) -> None:
        dangerous_patterns = (
            "rm -f",
            "del /Q",
            "os.remove",
            "pip install *",
            "pip install -q",
            "spawn-team.py",
            "magent.exe",
            "build.py",
            "--scope",
            "Bash(",
        )
        for settings in ROOT.glob(".claude/*.json"):
            text = settings.read_text(encoding="utf-8", errors="ignore")
            for pattern in dangerous_patterns:
                self.assertNotIn(pattern, text, f"{settings.name} contains {pattern!r}")

    def test_workflow_requires_authorization_and_an_immediate_local_step(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        preflight = text.split("3. For delegation", 1)[0]
        self.assertIn("explicit authorization", preflight)
        self.assertIn("next local step", preflight)
        self.assertIn("not authorization", preflight)

    def test_keep_local_covers_immediate_critical_path_blockers(self) -> None:
        text = (SKILL / "references" / "delegation-rubric.md").read_text(encoding="utf-8")
        keep_local = text.split("Delegate when", 1)[0]
        self.assertIn("immediate next step", keep_local)
        self.assertIn("no useful independent local work", keep_local)

    def test_one_critique_uses_one_specialist(self) -> None:
        text = (SKILL / "references" / "delegation-rubric.md").read_text(encoding="utf-8")
        row = next(line for line in text.splitlines() if "one needed critique" in line)
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        self.assertEqual(cells[1], "1 specialist")

    def test_pre_dispatch_baseline_captures_content_not_only_status(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        preflight = text.split("5. Before dispatching", 1)[1].split("6. Build", 1)[0]
        for evidence in ("git diff --binary", "git diff --cached --binary", "content fingerprints", "untracked"):
            self.assertIn(evidence, preflight)

    def test_collection_distinguishes_pending_results_from_failed_agents(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        collection = text.split("## Collection Rule", 1)[1].split("## Failed Agents", 1)[0]
        for invariant in ("agent ID", "pending", "wait timeout", "send_message_to_thread", "set_thread_archived"):
            self.assertIn(invariant, collection)
        self.assertIn("still occupy concurrency", collection)
        self.assertNotIn("If an agent fails, times out", text)

    def test_packet_distinguishes_completed_work_and_soft_budget(self) -> None:
        text = (SKILL / "references" / "dispatch-contract.md").read_text(encoding="utf-8")
        for field in ("## Budget", "soft budget", "complete | partial | blocked", "actually executed", "not inspected"):
            self.assertIn(field, text)
        for filename in ("bugfix.md", "code-review.md", "research.md"):
            example = (SKILL / "examples" / filename).read_text(encoding="utf-8")
            self.assertIn("## Budget", example, filename)

    def test_runtime_acceptance_cases_include_negative_paths(self) -> None:
        text = (SKILL / "references" / "acceptance-cases.md").read_text(encoding="utf-8")
        for case in ("NO-AUTH", "IMMEDIATE-BLOCKER", "ONE-CRITIQUE", "WAIT-TIMEOUT", "DIRTY-CONTENT", "MISSING-EVIDENCE", "TERMINAL-FAILURE"):
            self.assertIn(case, text)
        self.assertIn("manual native-session acceptance", text)
        self.assertIn("not proof of model behavior", text)

    def test_skill_has_required_metadata_and_resources(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: codex-native-subagent-orchestrator", text)
        self.assertIn("actually exposed in this session", text)
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())

        for reference in (
            "delegation-rubric.md",
            "role-catalog.md",
            "dispatch-contract.md",
            "workflow-patterns.md",
        ):
            self.assertTrue((SKILL / "references" / reference).is_file())

    def test_skill_discovers_native_tools_from_the_current_schema(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("actually exposed in this session", text)
        self.assertIn("create_thread", text)
        self.assertIn("send_message_to_thread", text)
        self.assertIn("set_thread_archived", text)
        self.assertNotIn("spawn_agent", text)
        self.assertNotIn("send_input", text)
        self.assertNotIn("close_agent", text)

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

        self.assertIn("no native delegation tool is exposed", text)
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
        self.assertIn("create_thread", text)

    def test_readme_uses_current_session_tool_language(self) -> None:
        text = README.read_text(encoding="utf-8")

        self.assertIn("实际会话 schema", text)
        self.assertIn("create_thread", text)
        self.assertIn("set_thread_archived", text)
        self.assertNotIn("spawn_agent", text)
        self.assertNotIn("send_input", text)
        self.assertNotIn("close_agent", text)

    def test_readme_is_a_detailed_chinese_product_guide(self) -> None:
        text = README.read_text(encoding="utf-8")

        for phrase in (
            "Codex 原生子智能体编排",
            "原生子智能体与本 Skill",
            "什么时候适合使用",
            "什么时候不应该分派",
            "完整工作流程",
            "动态临时专家",
            "失败与超时",
            "安全边界",
            "使用示例",
            "常见问题",
        ):
            self.assertIn(phrase, text)

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

    def test_openai_metadata_requires_explicit_authorization(self) -> None:
        yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("allow_implicit_invocation: false", yaml)

    def test_acceptance_record_exists_and_labels_its_limits(self) -> None:
        records = sorted((ROOT / "output" / "readiness").glob("acceptance-*.md"))
        self.assertTrue(records, "expected at least one native acceptance record")

        text = records[-1].read_text(encoding="utf-8")
        self.assertIn("真实", text)
        self.assertIn("不证明", text)
        self.assertIn("证据", text)

    def test_skill_handles_failed_or_missing_agent_results(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("confirmed terminal failure or returns no usable result", text)
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
            "no native delegation tool is exposed",
            "platform's available concurrency",
            "at most one narrowly scoped replacement",
            "Collect every started agent",
        ):
            self.assertIn(rule, text)


if __name__ == "__main__":
    unittest.main()
