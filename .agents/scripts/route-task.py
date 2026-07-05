#!/usr/bin/env python3
"""Route a task through the Codex identity bank."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "skills" / "codex-agent-identity-bank" / "scripts" / "route_identity.py"


def utf8_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    return env


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--scope", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--max", default="4")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(ROUTER),
        "--task",
        args.task,
        "--scope",
        args.scope,
        "--context",
        args.context,
        "--max",
        str(args.max),
    ]
    if args.json:
        cmd.append("--json")
    return subprocess.run(cmd, check=False, env=utf8_subprocess_env()).returncode


if __name__ == "__main__":
    raise SystemExit(main())
