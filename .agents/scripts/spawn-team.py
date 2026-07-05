#!/usr/bin/env python3
"""Create a run folder containing a dispatch plan and copyable subagent prompts."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def utf8_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    return env


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "skills" / "codex-agent-identity-bank" / "scripts" / "route_identity.py"
RUNS = ROOT / "reports" / "runs"


def route(task: str, scope: str, context: str, max_identities: int) -> dict:
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROUTER),
                "--task",
                task,
                "--scope",
                scope,
                "--context",
                context,
                "--max",
                str(max_identities),
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
            errors='replace',
            env=utf8_subprocess_env(),
            encoding="utf-8",
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Route failed: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse route output: {e}")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--scope", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--max", type=int, default=4)
    args = parser.parse_args()

    try:
        plan = route(args.task, args.scope, args.context, args.max)
        run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
        run_dir = RUNS / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created run directory: {run_dir}")

        (run_dir / "dispatch-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        prompts = []
        for item in plan.get("dispatch_plan", []):
            prompts.append(f"# {item['id']} ({item['agent_type']})\n\n{item['prompt']}\n")
        (run_dir / "agent-prompts.md").write_text("\n---\n\n".join(prompts), encoding="utf-8")
        (run_dir / "synthesis.md").write_text("# Synthesis\n\nAccepted facts:\n\nConflicts:\n\nNext action:\n", encoding="utf-8")

        logger.info(f"[OK] Generated dispatch plan with {len(plan.get('dispatch_plan', []))} agents")
        print(str(run_dir))
        return 0
    except Exception as e:
        logger.error(f"Failed to spawn team: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
