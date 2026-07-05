#!/usr/bin/env python3
"""Streaming helpers for manual Codex run status."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Iterator


class StreamingExecutor:
    """Append lightweight dashboard events to a JSONL stream."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.stream_file = run_dir / "stream.jsonl"

    def emit_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "data": data,
        }
        with open(self.stream_file, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def stream_agent_execution(self, agent_id: str, agent_type: str) -> Iterator[dict[str, Any]]:
        yield self.emit_event("agent_start", {"agent_id": agent_id, "agent_type": agent_type, "status": "starting"})
        yield self.emit_event("agent_thinking", {"agent_id": agent_id, "status": "analyzing"})
        for progress in (0.33, 0.66, 1.0):
            time.sleep(0.1)
            yield self.emit_event(
                "agent_progress",
                {
                    "agent_id": agent_id,
                    "progress": progress,
                    "message": f"Manual workflow placeholder {int(progress * 100)}%",
                },
            )
        yield self.emit_event("agent_complete", {"agent_id": agent_id, "status": "completed"})

    def read_stream(self) -> Iterator[dict[str, Any]]:
        if not self.stream_file.exists():
            return iter(())

        def _iter():
            with open(self.stream_file, "r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        yield json.loads(line)

        return _iter()

    def get_progress_summary(self) -> dict[str, Any]:
        events = list(self.read_stream())
        agents: dict[str, str] = {}
        for event in events:
            agent_id = event.get("data", {}).get("agent_id")
            if agent_id:
                agents[agent_id] = event["data"].get("status", "unknown")
        return {
            "total_events": len(events),
            "agents": agents,
            "completed": sum(1 for status in agents.values() if status == "completed"),
            "in_progress": sum(1 for status in agents.values() if status in {"starting", "analyzing"}),
        }


class ProgressRenderer:
    """Small terminal rendering helpers used by legacy code paths."""

    @staticmethod
    def render_progress_bar(progress: float, width: int = 40) -> str:
        filled = int(width * progress)
        return f"[{'#' * filled}{'.' * (width - filled)}] {int(progress * 100)}%"

    @staticmethod
    def render_agent_status(agents: dict[str, str]) -> str:
        lines = ["Agent Execution Status:", "=" * 60]
        for agent_id, status in agents.items():
            lines.append(f"- {agent_id:<30} {status}")
        return "\n".join(lines)

    @staticmethod
    def clear_and_render(content: str):
        os.system("cls" if os.name == "nt" else "clear")
        print(content)
