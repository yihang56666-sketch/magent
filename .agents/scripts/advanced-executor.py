#!/usr/bin/env python3
"""Legacy executor wrapper for Codex-only manual runs."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from manual_execution import initialize_manual_run, sync_manual_run

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--parallel", type=int, default=3, help="Ignored in Codex-only mode")
    parser.add_argument("--no-cache", action="store_true", help="Ignored in Codex-only mode")
    parser.add_argument("--refresh", action="store_true", help="Refresh summary from existing outputs")
    args = parser.parse_args()

    if not args.run_dir.exists():
        logger.error(f"Run directory not found: {args.run_dir}")
        return 1

    summary = sync_manual_run(args.run_dir) if args.refresh else initialize_manual_run(args.run_dir)
    summary["legacy_executor"] = "advanced-executor"
    summary["mode"] = "codex-only"
    (args.run_dir / "execution-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("Prepared Codex-only manual run artifacts")
    logger.info(f"Completed: {summary['completed']}/{summary['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
