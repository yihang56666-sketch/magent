#!/usr/bin/env python3
"""Codex-only executor that prepares manual workflow artifacts and refreshes status."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

from checkpoint_executor import CheckpointManager
from manual_execution import initialize_manual_run, sync_manual_run
from streaming_executor import StreamingExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _emit_summary_events(run_dir: Path, summary: dict) -> None:
    stream = StreamingExecutor(run_dir)
    checkpoint = CheckpointManager(run_dir)

    for result in summary["results"]:
        checkpoint.save_checkpoint(
            result["agent_id"],
            result["status"],
            None,
            {"identity_id": result["identity_id"], "output_file": result["output_file"]},
        )
        stream.emit_event(
            "agent_status",
            {
                "agent_id": result["agent_id"],
                "agent_type": result["agent_type"],
                "status": result["status"],
            },
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--resume", action="store_true", help="Refresh an existing run instead of recreating artifacts")
    parser.add_argument("--mode", choices=["parallel", "group-chat"], default="parallel")
    parser.add_argument("--model", default="codex-current-session")
    parser.add_argument("--budget", type=int, help="Unused in Codex-only mode; kept for CLI compatibility")
    args = parser.parse_args()

    if not args.run_dir.exists():
        logger.error(f"Run directory not found: {args.run_dir}")
        return 1

    start_time = time.time()
    summary = sync_manual_run(args.run_dir) if args.resume else initialize_manual_run(args.run_dir)
    _emit_summary_events(args.run_dir, summary)
    elapsed = time.time() - start_time

    full_summary = {
        **summary,
        "elapsed_seconds": round(elapsed, 1),
        "total_tokens": 0,
        "budget_status": {
            "mode": "codex-only",
            "note": "No external API budget is consumed by this executor.",
        },
        "mode": args.mode,
        "model": args.model,
    }

    (args.run_dir / "execution-summary.json").write_text(
        json.dumps(full_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("Prepared Codex-only execution artifacts")
    logger.info(f"Run: {args.run_dir.name}")
    logger.info(f"Completed: {full_summary['completed']}/{full_summary['total']}")
    logger.info(f"Pending: {full_summary['pending']}")
    logger.info("Use the current Codex session to complete pending agent outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
