#!/usr/bin/env python3
"""Tests for the Codex-only manual workflow."""

from __future__ import annotations

import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents"))

import magent as magent_module  # noqa: E402
from config_manager import ConfigManager  # noqa: E402
from magent import MultiAgentCLI  # noqa: E402
from manual_execution import initialize_manual_run, render_next_agent_brief, sync_manual_run  # noqa: E402


def _make_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    plan = {
        "task": "Analyze auth flow",
        "scope": "src/auth tests/auth",
        "context": "",
        "pattern": "critic-loop",
        "primary_identity": "security-engineer",
        "dispatch_plan": [
            {
                "id": "security-engineer",
                "title": "Security Engineer",
                "identity_id": "security-engineer",
                "agent_type": "explorer",
                "execution_role": "explorer",
                "mission": "Review the auth flow",
                "prompt": "## Security Engineer",
            }
        ],
    }
    (run_dir / "dispatch-plan.json").write_text(json.dumps(plan), encoding="utf-8")
    return run_dir


def test_config_manager_hides_legacy_api_keys(tmp_path: Path):
    cfg = ConfigManager(tmp_path / ".magent")
    cfg.set("default_model", "codex-current-session")
    cfg.set("api_key", "legacy")
    cfg.set("api_base", "legacy")

    assert cfg.get_default_model() == "codex-current-session"
    assert "api_key" not in cfg.list()
    assert "api_base" not in cfg.list()


def test_initialize_manual_run_creates_prompt_and_summary(tmp_path: Path):
    run_dir = _make_run_dir(tmp_path)
    summary = initialize_manual_run(run_dir)

    assert summary["total"] == 1
    assert (run_dir / "agent-prompts.md").exists()
    assert (run_dir / "handoff-contract.md").exists()
    assert (run_dir / "manual-execution.md").exists()
    assert (run_dir / "next-agent.md").exists()
    assert (run_dir / "execution-summary.json").exists()
    workflow = (run_dir / "manual-execution.md").read_text(encoding="utf-8")
    assert "magent step <run_id>" in workflow
    assert "magent next <run_id>" not in workflow


def test_sync_manual_run_reads_outputs(tmp_path: Path):
    run_dir = _make_run_dir(tmp_path)
    initialize_manual_run(run_dir)
    (run_dir / "security-engineer.output.md").write_text(
        "## Findings\nok\n\n## Evidence\nx\n\n## Risks\nnone\n\n## Open Questions\nnone\n\n## Recommended Next Action\nship\n",
        encoding="utf-8",
    )

    summary = sync_manual_run(run_dir)
    assert summary["completed"] == 1
    assert summary["pending"] == 0


def test_render_next_agent_brief_points_to_pending_agent(tmp_path: Path):
    run_dir = _make_run_dir(tmp_path)
    initialize_manual_run(run_dir)

    brief = render_next_agent_brief(json.loads((run_dir / "dispatch-plan.json").read_text(encoding="utf-8")), run_dir)
    assert "Next pending agent" in brief
    assert "security-engineer" in brief
    assert "next-agent.md" not in brief


def test_cli_next_shows_guided_brief(tmp_path: Path):
    run_dir = _make_run_dir(tmp_path)
    initialize_manual_run(run_dir)

    cli = MultiAgentCLI()
    original_runs_dir = cli._resolve_run_dir
    cli._resolve_run_dir = lambda run_id: run_dir if run_id == "latest" else original_runs_dir(run_id)
    try:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            assert cli.cmd_next(type("Args", (), {"run_id": "latest"})()) == 0
    finally:
        cli._resolve_run_dir = original_runs_dir

    output = stdout.getvalue()
    assert "Next Agent Brief" in output
    assert "security-engineer" in output


def test_cli_recipes_lists_practical_workflows():
    cli = MultiAgentCLI()
    stdout = io.StringIO()

    with redirect_stdout(stdout):
        assert cli.cmd_recipes(type("Args", (), {"recipe_id": None})()) == 0

    output = stdout.getvalue()
    assert "Practical recipes" in output
    assert "bugfix" in output
    assert "start bugfix" in output


def test_cli_without_command_shows_practical_workflows():
    cli = MultiAgentCLI()
    stdout = io.StringIO()

    with redirect_stdout(stdout):
        assert cli.run([]) == 0

    output = stdout.getvalue()
    assert "Magent practical workflows" in output
    assert "bugfix" in output
    assert "ui" in output


def test_cli_recipe_detail_shows_outcome():
    cli = MultiAgentCLI()
    stdout = io.StringIO()

    with redirect_stdout(stdout):
        assert cli.cmd_recipes(type("Args", (), {"recipe_id": "release-readiness"})()) == 0

    output = stdout.getvalue()
    assert "Release Readiness" in output
    assert "Outcome:" in output
    assert "magent.py step latest" in output


def test_cli_advise_shows_keep_local_for_tiny_task():
    cli = MultiAgentCLI()
    stdout = io.StringIO()

    with redirect_stdout(stdout):
        assert cli.cmd_advise(
            type("Args", (), {"task": "fix typo", "scope": "README.md", "context": "", "max": 4, "json": False})()
        ) == 0

    output = stdout.getvalue()
    assert "Recommendation: keep-local" in output
    assert "Estimated overhead:" in output


def test_cli_step_syncs_and_shows_next_agent(tmp_path: Path):
    run_dir = _make_run_dir(tmp_path)
    initialize_manual_run(run_dir)

    cli = MultiAgentCLI()
    original_runs_dir = cli._resolve_run_dir
    cli._resolve_run_dir = lambda run_id: run_dir if run_id == "latest" else original_runs_dir(run_id)
    try:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            assert cli.cmd_step(type("Args", (), {"run_id": "latest"})()) == 0
    finally:
        cli._resolve_run_dir = original_runs_dir

    output = stdout.getvalue()
    assert "Next Agent Brief" in output
    assert (run_dir / "execution-summary.json").exists()


def test_prepare_run_guidance_prefers_step(tmp_path: Path):
    run_id = "20260705-120000-12345"
    runs_dir = tmp_path / "runs"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "dispatch-plan.json").write_text(
        json.dumps(
            {
                "task": "Analyze auth flow",
                "scope": "src/auth tests/auth",
                "pattern": "critic-loop",
                "dispatch_plan": [
                    {
                        "id": "security-engineer",
                        "title": "Security Engineer",
                        "identity_id": "security-engineer",
                        "agent_type": "explorer",
                        "execution_role": "explorer",
                        "mission": "Review the auth flow",
                        "prompt": "## Security Engineer",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    class Result:
        stdout = f"Created run: {run_id}\n"

    original_runs_dir = magent_module.RUNS_DIR
    original_safe_subprocess_run = magent_module.safe_subprocess_run
    magent_module.RUNS_DIR = runs_dir
    magent_module.safe_subprocess_run = lambda *args, **kwargs: Result()
    try:
        cli = MultiAgentCLI()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            assert cli._prepare_run("Analyze auth flow", "src/auth tests/auth", "", 4, "codex-current-session") == 0
    finally:
        magent_module.RUNS_DIR = original_runs_dir
        magent_module.safe_subprocess_run = original_safe_subprocess_run

    output = stdout.getvalue()
    assert f"python .agents\\magent.py step {run_id}" in output
    assert f"python .agents\\magent.py sync {run_id}" not in output


def test_sync_manual_run_refreshes_next_agent_brief(tmp_path: Path):
    run_dir = _make_run_dir(tmp_path)
    initialize_manual_run(run_dir)
    (run_dir / "security-engineer.output.md").write_text(
        "## Findings\nok\n\n## Evidence\nx\n\n## Risks\nnone\n\n## Open Questions\nnone\n\n## Recommended Next Action\nship\n\n## Handoff\n- Next speaker: main agent\n",
        encoding="utf-8",
    )

    sync_manual_run(run_dir)
    brief = (run_dir / "next-agent.md").read_text(encoding="utf-8")
    assert "All agents are complete." in brief


def run():
    tests = [
        ("config_manager_hides_legacy_api_keys", test_config_manager_hides_legacy_api_keys),
        ("initialize_manual_run_creates_prompt_and_summary", test_initialize_manual_run_creates_prompt_and_summary),
        ("sync_manual_run_reads_outputs", test_sync_manual_run_reads_outputs),
        ("render_next_agent_brief_points_to_pending_agent", test_render_next_agent_brief_points_to_pending_agent),
        ("cli_next_shows_guided_brief", test_cli_next_shows_guided_brief),
        ("cli_recipes_lists_practical_workflows", test_cli_recipes_lists_practical_workflows),
        ("cli_without_command_shows_practical_workflows", test_cli_without_command_shows_practical_workflows),
        ("cli_recipe_detail_shows_outcome", test_cli_recipe_detail_shows_outcome),
        ("cli_advise_shows_keep_local_for_tiny_task", test_cli_advise_shows_keep_local_for_tiny_task),
        ("cli_step_syncs_and_shows_next_agent", test_cli_step_syncs_and_shows_next_agent),
        ("prepare_run_guidance_prefers_step", test_prepare_run_guidance_prefers_step),
        ("sync_manual_run_refreshes_next_agent_brief", test_sync_manual_run_refreshes_next_agent_brief),
    ]

    passed = 0
    failed = 0
    for name, test_func in tests:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_func(Path(temp_dir))
            print(f"OK  {name}")
            passed += 1
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
            failed += 1
        except Exception as exc:
            print(f"ERR  {name}: {type(exc).__name__}: {exc}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
