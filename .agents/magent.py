#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-Agent orchestration CLI for Codex-only manual execution."""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path
from threading import Thread

if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

ROOT = Path(__file__).resolve().parent
RUNS_DIR = ROOT / "reports" / "runs"
IDENTITIES_FILE = ROOT / "skills" / "codex-agent-identity-bank" / "references" / "identities.json"
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from config_manager import get_config  # noqa: E402
from error_handler import handle_errors, safe_subprocess_run  # noqa: E402
from manual_execution import initialize_manual_run, render_next_agent_brief, sync_manual_run  # noqa: E402
from advisor import advice_json, build_advice, format_advice  # noqa: E402
from recipes import (  # noqa: E402
    RecipeError,
    format_recipe_detail,
    format_recipe_list,
    get_recipe,
    load_recipes,
    render_recipe_context,
    render_recipe_task,
)


class MultiAgentCLI:
    LEGACY_CONFIG_KEYS = {"api_key", "api_base"}

    def __init__(self):
        self.parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="magent",
            description="Codex-only Multi-Agent Orchestration Framework",
        )
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        config_parser = subparsers.add_parser("config", help="Manage local configuration")
        config_subparsers = config_parser.add_subparsers(dest="config_action")
        set_parser = config_subparsers.add_parser("set", help="Set config value")
        set_parser.add_argument("key")
        set_parser.add_argument("value")
        get_parser = config_subparsers.add_parser("get", help="Get config value")
        get_parser.add_argument("key", nargs="?")
        del_parser = config_subparsers.add_parser("delete", help="Delete config value")
        del_parser.add_argument("key")

        run_parser = subparsers.add_parser("run", help="Prepare a Codex-only agent run")
        run_parser.add_argument("--task", required=True, help="Task description")
        run_parser.add_argument("--scope", required=True, help="File scope")
        run_parser.add_argument("--context", default="", help="Extra routing context")
        run_parser.add_argument("--max", type=int, default=4, help="Maximum routed identities")
        run_parser.add_argument("--model", help="Optional local label for the Codex session")

        advise_parser = subparsers.add_parser("advise", help="Decide whether a task is worth a multi-agent run")
        advise_parser.add_argument("--task", required=True, help="Task description")
        advise_parser.add_argument("--scope", default=".", help="Files, directories, or system area")
        advise_parser.add_argument("--context", default="", help="Extra context")
        advise_parser.add_argument("--max", type=int, default=4, help="Maximum routed identities to consider")
        advise_parser.add_argument("--json", action="store_true", help="Print machine-readable advice")

        recipes_parser = subparsers.add_parser("recipes", help="List practical workflow recipes")
        recipes_parser.add_argument("recipe_id", nargs="?", help="Show details for one recipe")

        start_parser = subparsers.add_parser("start", help="Start a practical workflow recipe")
        start_parser.add_argument("recipe_id", help="Recipe id from `magent recipes`")
        start_parser.add_argument("--scope", help="Files, directories, or system area to inspect")
        start_parser.add_argument("--task", default="", help="Concrete issue, change, or goal")
        start_parser.add_argument("--context", default="", help="Extra context for the generated run")
        start_parser.add_argument("--max", type=int, help="Override maximum routed identities")
        start_parser.add_argument("--model", help="Optional local label for the Codex session")

        ui_parser = subparsers.add_parser("ui", help="Launch web dashboard")
        ui_parser.add_argument("--port", type=int, default=8080, help="Server port")
        ui_parser.add_argument("--no-browser", action="store_true", help="Don't open browser")

        status_parser = subparsers.add_parser("status", help="Refresh and show run status")
        status_parser.add_argument("run_id", nargs="?", default="latest")

        next_parser = subparsers.add_parser("next", help="Show the next pending agent brief")
        next_parser.add_argument("run_id", nargs="?", default="latest")

        step_parser = subparsers.add_parser("step", help="Sync a run and show the next pending agent")
        step_parser.add_argument("run_id", nargs="?", default="latest")

        sync_parser = subparsers.add_parser("sync", help="Refresh summary after manual Codex execution")
        sync_parser.add_argument("run_id", nargs="?", default="latest")

        subparsers.add_parser("list", help="List all runs")
        subparsers.add_parser("agents", help="List available agents")
        subparsers.add_parser("version", help="Show version")
        return parser

    def run(self, argv=None):
        args = self.parser.parse_args(argv)
        if not args.command:
            print("Magent practical workflows")
            print("==========================")
            print()
            print(format_recipe_list(load_recipes()))
            print()
            print("Use `python .agents\\magent.py ui` to launch the dashboard.")
            return 0

        return {
            "config": self.cmd_config,
            "run": self.cmd_run,
            "advise": self.cmd_advise,
            "recipes": self.cmd_recipes,
            "start": self.cmd_start,
            "ui": self.cmd_ui,
            "status": self.cmd_status,
            "next": self.cmd_next,
            "step": self.cmd_step,
            "sync": self.cmd_sync,
            "list": self.cmd_list,
            "agents": self.cmd_agents,
            "version": self.cmd_version,
        }[args.command](args)

    @handle_errors
    def cmd_config(self, args):
        config = get_config()
        if args.config_action == "set":
            if args.key in self.LEGACY_CONFIG_KEYS:
                print(f"Key '{args.key}' is no longer supported in Codex-only mode")
                return 1
            config.set(args.key, args.value)
            print(f"Set {args.key} = {args.value}")
            return 0
        if args.config_action == "get":
            if args.key:
                if args.key in self.LEGACY_CONFIG_KEYS:
                    print(f"Key '{args.key}' is ignored in Codex-only mode")
                    return 1
                value = config.get(args.key)
                if value is None:
                    print(f"Key not found: {args.key}")
                    return 1
                print(f"{args.key} = {value}")
            else:
                print(json.dumps(config.list(), ensure_ascii=False, indent=2))
            return 0
        if args.config_action == "delete":
            config.delete(args.key)
            print(f"Deleted {args.key}")
            return 0
        print("Usage: magent config [set|get|delete]")
        return 1

    @handle_errors
    def cmd_run(self, args):
        config = get_config()
        model = args.model or config.get_default_model()

        return self._prepare_run(args.task, args.scope, args.context, args.max, model)

    @handle_errors
    def cmd_advise(self, args):
        advice = build_advice(args.task, args.scope, args.context, args.max)
        print(advice_json(advice) if args.json else format_advice(advice))
        return 0

    @handle_errors
    def cmd_recipes(self, args):
        if args.recipe_id:
            print(format_recipe_detail(get_recipe(args.recipe_id)))
        else:
            print(format_recipe_list(load_recipes()))
        return 0

    @handle_errors
    def cmd_start(self, args):
        try:
            recipe = get_recipe(args.recipe_id)
        except RecipeError as exc:
            print(exc)
            return 1

        config = get_config()
        scope = args.scope or recipe["default_scope"]
        task = render_recipe_task(recipe, args.task, scope)
        context = render_recipe_context(recipe, args.context)
        max_identities = args.max or int(recipe["default_max"])
        model = args.model or config.get_default_model()

        print(f"Starting recipe: {recipe['title']} ({recipe['id']})")
        print(f"  Outcome: {recipe['outcome']}")
        print()
        return self._prepare_run(task, scope, context, max_identities, model, recipe=recipe)

    def _prepare_run(
        self,
        task: str,
        scope: str,
        context: str,
        max_identities: int,
        model: str,
        recipe: dict | None = None,
    ):
        print("Preparing Codex-only orchestration...")
        print(f"  Task:  {task}")
        print(f"  Scope: {scope}")
        print(f"  Model label: {model}")

        result = safe_subprocess_run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "spawn-team.py"),
                "--task",
                task,
                "--scope",
                scope,
                "--context",
                context,
                "--max",
                str(max_identities),
            ],
            timeout=60,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        run_id = self._extract_run_id(result.stdout)
        if not run_id:
            print("Failed to extract run_id from output")
            return 1

        run_dir = RUNS_DIR / run_id
        summary = initialize_manual_run(run_dir)

        print(f"\nPrepared run: {run_id}")
        print(f"  Agent count: {summary['total']}")
        print(f"  Prompts: {run_dir / 'agent-prompts.md'}")
        print(f"  Workflow: {run_dir / 'manual-execution.md'}")
        print("\nNext steps:")
        print(f"  1. Open {run_dir / 'agent-prompts.md'}")
        print("  2. Use the current Codex session to play each agent in order")
        print("  3. Save each answer into its matching *.output.md file")
        print(f"  4. Run: python .agents\\magent.py step {run_id}")
        print(f"  5. Repeat until all agents are complete, then run: python .agents\\scripts\\merge-results.py {run_dir}")
        if recipe:
            print("\nRecipe guidance:")
            for step in recipe["next_steps"]:
                print(f"  - {step}")
        return 0

    @handle_errors
    def cmd_ui(self, args):
        print(f"Starting dashboard on port {args.port}...")
        import os

        os.environ["PORT"] = str(args.port)
        from serve_dashboard import main as serve_main

        if not args.no_browser:
            url = f"http://localhost:{args.port}/dashboard-live.html"

            def open_browser():
                import time

                time.sleep(1)
                webbrowser.open(url)

            Thread(target=open_browser, daemon=True).start()

        try:
            serve_main()
        except KeyboardInterrupt:
            print("\nDashboard stopped")
            return 0

    @handle_errors
    def cmd_status(self, args):
        run_dir = self._resolve_run_dir(args.run_id)
        if run_dir is None:
            print("No runs found")
            return 1

        summary = sync_manual_run(run_dir)
        print(f"\nRun Status: {run_dir.name}")
        print("=" * 60)
        print(f"Total Agents: {summary['total']}")
        print(f"Completed:    {summary['completed']}")
        print(f"Pending:      {summary['pending']}")
        print(f"Failed:       {summary['failed']}")
        print("=" * 60)
        for result in summary["results"]:
            print(f"- {result['agent_id']:<32} {result['status']}")
        print()
        return 0

    @handle_errors
    def cmd_next(self, args):
        run_dir = self._resolve_run_dir(args.run_id)
        if run_dir is None:
            print("No runs found")
            return 1

        plan = json.loads((run_dir / "dispatch-plan.json").read_text(encoding="utf-8"))
        print(render_next_agent_brief(plan, run_dir))
        return 0

    @handle_errors
    def cmd_step(self, args):
        run_dir = self._resolve_run_dir(args.run_id)
        if run_dir is None:
            print("No runs found")
            return 1
        sync_manual_run(run_dir)
        plan = json.loads((run_dir / "dispatch-plan.json").read_text(encoding="utf-8"))
        print(render_next_agent_brief(plan, run_dir))
        return 0

    @handle_errors
    def cmd_sync(self, args):
        run_dir = self._resolve_run_dir(args.run_id)
        if run_dir is None:
            print("No runs found")
            return 1
        summary = sync_manual_run(run_dir)
        print(f"Synchronized {run_dir.name}: {summary['completed']}/{summary['total']} completed")
        return 0

    @handle_errors
    def cmd_list(self, args):
        if not RUNS_DIR.exists():
            print("No runs found")
            return 0
        runs = sorted(RUNS_DIR.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True)
        print(f"\nRecent Runs ({len(runs)} total)")
        print("=" * 60)
        for index, run in enumerate(runs[:10], 1):
            summary_file = run / "execution-summary.json"
            if summary_file.exists():
                summary = json.loads(summary_file.read_text(encoding="utf-8"))
                status = f"{summary.get('completed', 0)}/{summary.get('total', 0)} completed"
            else:
                status = "prepared"
            print(f"{index:2}. {run.name:<30} {status}")
        print("=" * 60)
        return 0

    @handle_errors
    def cmd_agents(self, args):
        identities_data = json.loads(IDENTITIES_FILE.read_text(encoding="utf-8"))
        identities = identities_data.get("identities", identities_data)
        print(f"\nAvailable Agents ({len(identities)} total)")
        print("=" * 80)
        for agent in identities:
            print(f"- {agent['id']:<35} {agent['title']}")
        print("=" * 80)
        return 0

    def cmd_version(self, args):
        print("Multi-Agent Orchestration Framework")
        print("Version: 1.2.0")
        print("Mode: Codex-only manual execution")
        return 0

    def _extract_run_id(self, output: str) -> str | None:
        import re

        match = re.search(r"(\d{8}-\d{6}-\d+)", output)
        return match.group(1) if match else None

    def _resolve_run_dir(self, run_id: str) -> Path | None:
        if run_id == "latest":
            latest = self._get_latest_run()
            return RUNS_DIR / latest if latest else None
        run_dir = RUNS_DIR / run_id
        return run_dir if run_dir.exists() else None

    def _get_latest_run(self) -> str | None:
        if not RUNS_DIR.exists():
            return None
        runs = sorted(RUNS_DIR.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True)
        return runs[0].name if runs else None


def main():
    cli = MultiAgentCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
