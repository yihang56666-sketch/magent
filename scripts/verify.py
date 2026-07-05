#!/usr/bin/env python3
"""Run the same local checks expected by CI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_step(label: str, command: list[str]) -> int:
    print(f"\n== {label} ==", flush=True)
    print("$ " + " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    if completed.returncode != 0:
        print(f"{label} failed with exit code {completed.returncode}")
    return completed.returncode


def main() -> int:
    python = sys.executable
    steps = [
        ("Project doctor", [python, "scripts/doctor.py"]),
        ("Maturity audit", [python, "scripts/maturity_audit.py"]),
        ("Identity validation", [python, ".agents/scripts/validate-identities.py"]),
        ("Test suite", [python, "-m", "pytest"]),
        ("CLI smoke test", [python, ".agents/magent.py", "version"]),
    ]

    for label, command in steps:
        code = run_step(label, command)
        if code:
            return code

    print("\nAll verification steps passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
