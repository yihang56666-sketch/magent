#!/usr/bin/env python3
"""Checkpoint-based executor with resume capability (inspired by LangGraph)."""

import json
import time
from pathlib import Path
from typing import Any


class CheckpointManager:
    """Manage execution checkpoints for crash recovery."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.checkpoint_file = run_dir / "checkpoints.jsonl"

    def save_checkpoint(self, agent_id: str, status: str, output: str | None = None, meta: dict | None = None):
        """Save agent execution checkpoint."""
        checkpoint = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "status": status,
            "output": output,
            "meta": meta or {}
        }

        with open(self.checkpoint_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(checkpoint) + "\n")

    def load_checkpoints(self) -> dict[str, dict]:
        """Load all checkpoints and return latest state per agent."""
        if not self.checkpoint_file.exists():
            return {}

        checkpoints = {}
        with open(self.checkpoint_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cp = json.loads(line)
                    checkpoints[cp["agent_id"]] = cp

        return checkpoints

    def get_completed_agents(self) -> set[str]:
        """Get IDs of successfully completed agents."""
        checkpoints = self.load_checkpoints()
        return {aid for aid, cp in checkpoints.items() if cp["status"] == "completed"}

    def get_failed_agents(self) -> set[str]:
        """Get IDs of failed agents that need retry."""
        checkpoints = self.load_checkpoints()
        return {aid for aid, cp in checkpoints.items() if cp["status"] == "failed"}

    def should_skip(self, agent_id: str) -> bool:
        """Check if agent should be skipped (already completed)."""
        return agent_id in self.get_completed_agents()

    def get_resume_point(self) -> dict[str, Any]:
        """Get resume information."""
        checkpoints = self.load_checkpoints()
        completed = self.get_completed_agents()
        failed = self.get_failed_agents()

        return {
            "total_checkpoints": len(checkpoints),
            "completed": len(completed),
            "failed": len(failed),
            "completed_ids": list(completed),
            "failed_ids": list(failed),
            "can_resume": len(checkpoints) > 0
        }
