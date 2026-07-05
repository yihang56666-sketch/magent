#!/usr/bin/env python3
"""Prepare or refresh a dispatch plan for Codex-only manual execution."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from manual_execution import initialize_manual_run, sync_manual_run

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="Path to run directory")
    parser.add_argument("--refresh", action="store_true", help="Refresh summary from existing output files")
    args = parser.parse_args()

    if not args.run_dir.exists():
        logger.error(f"Run directory not found: {args.run_dir}")
        return 1

    try:
        summary = sync_manual_run(args.run_dir) if args.refresh else initialize_manual_run(args.run_dir)
        logger.info(f"Prepared manual execution pack: {args.run_dir}")
        logger.info(f"Completed: {summary['completed']}/{summary['total']}, Pending: {summary['pending']}")
        return 0
    except Exception as e:
        logger.error(f"Failed to prepare manual execution: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
