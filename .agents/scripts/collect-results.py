#!/usr/bin/env python3
"""Summarize a generated multi-agent run directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from agent_contract import identity_id, execution_role  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    plan = json.loads((run_dir / "dispatch-plan.json").read_text(encoding="utf-8"))
    print(f"Task: {plan['task']}")
    print(f"Pattern: {plan['pattern']}")
    print(f"Primary: {plan['primary_identity']}")
    print("Agents:")
    for item in plan["dispatch_plan"]:
        print(f"- {identity_id(item)} role={execution_role(item)} skills={', '.join(item['skills'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
