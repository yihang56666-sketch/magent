#!/usr/bin/env python3
"""Agent memory system for cross-run learning and context retention."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MEMORY_DIR = Path(__file__).resolve().parents[1] / "reports" / "memory"


@dataclass
class AgentMemory:
    """Memory entry for an agent across runs."""
    agent_id: str
    task_pattern: str
    success_count: int = 0
    failure_count: int = 0
    avg_completion_time: float = 0.0
    common_findings: list[str] = None
    common_risks: list[str] = None
    lessons_learned: list[str] = None
    last_updated: str = ""

    def __post_init__(self):
        if self.common_findings is None:
            self.common_findings = []
        if self.common_risks is None:
            self.common_risks = []
        if self.lessons_learned is None:
            self.lessons_learned = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


def load_memory(agent_id: str) -> AgentMemory | None:
    """Load memory for a specific agent."""
    memory_file = MEMORY_DIR / f"{agent_id}.json"
    if not memory_file.exists():
        return None

    try:
        data = json.loads(memory_file.read_text(encoding="utf-8"))
        return AgentMemory(**data)
    except Exception as e:
        logger.error(f"Failed to load memory for {agent_id}: {e}")
        return None


def save_memory(memory: AgentMemory) -> None:
    """Save agent memory to disk."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    memory_file = MEMORY_DIR / f"{memory.agent_id}.json"

    memory.last_updated = datetime.now().isoformat()
    memory_file.write_text(json.dumps(asdict(memory), ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"✓ Saved memory for {memory.agent_id}")


def update_from_run(run_dir: Path) -> None:
    """Update agent memories from a completed run."""
    summary_file = run_dir / "execution-summary.json"
    if not summary_file.exists():
        logger.error("Execution summary not found")
        return

    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    plan_file = run_dir / "dispatch-plan.json"
    plan = json.loads(plan_file.read_text(encoding="utf-8"))

    task_pattern = plan.get("pattern", "unknown")

    for result in summary.get("results", []):
        agent_id = result["agent_id"]
        status = result["status"]

        # Load or create memory
        memory = load_memory(agent_id) or AgentMemory(agent_id=agent_id, task_pattern=task_pattern)

        # Update success/failure counts
        if status == "completed":
            memory.success_count += 1
        else:
            memory.failure_count += 1

        # Extract learnings from output
        output_file = Path(result.get("output_file", ""))
        if output_file.exists():
            content = output_file.read_text(encoding="utf-8")
            findings = extract_section(content, "Findings")
            risks = extract_section(content, "Risks")

            if findings:
                memory.common_findings.append(findings[:200])  # Keep recent, truncate
                memory.common_findings = memory.common_findings[-10:]  # Keep last 10

            if risks:
                memory.common_risks.append(risks[:200])
                memory.common_risks = memory.common_risks[-10:]

        save_memory(memory)


def extract_section(content: str, section: str) -> str:
    """Extract a section from markdown content."""
    lines = content.split("\n")
    in_section = False
    section_lines = []

    for line in lines:
        if line.startswith(f"## {section}"):
            in_section = True
            continue
        elif line.startswith("## ") and in_section:
            break
        elif in_section and line.strip():
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def get_agent_stats(agent_id: str) -> dict[str, Any]:
    """Get performance statistics for an agent."""
    memory = load_memory(agent_id)
    if not memory:
        return {"agent_id": agent_id, "status": "no_history"}

    total = memory.success_count + memory.failure_count
    success_rate = memory.success_count / total if total > 0 else 0

    return {
        "agent_id": agent_id,
        "success_rate": round(success_rate, 2),
        "total_runs": total,
        "pattern": memory.task_pattern,
        "recent_findings": memory.common_findings[-3:],
        "recent_risks": memory.common_risks[-3:],
    }


def suggest_agents(task_keywords: list[str], top_n: int = 3) -> list[str]:
    """Suggest agents based on historical performance and task keywords."""
    if not MEMORY_DIR.exists():
        return []

    agent_scores = []
    for memory_file in MEMORY_DIR.glob("*.json"):
        memory = load_memory(memory_file.stem)
        if not memory:
            continue

        total = memory.success_count + memory.failure_count
        if total == 0:
            continue

        success_rate = memory.success_count / total
        keyword_match = sum(1 for kw in task_keywords if kw.lower() in " ".join(memory.common_findings).lower())

        score = success_rate * 0.7 + (keyword_match / max(len(task_keywords), 1)) * 0.3
        agent_scores.append((score, memory.agent_id))

    agent_scores.sort(reverse=True)
    return [agent_id for _, agent_id in agent_scores[:top_n]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Update memory from run
    update_parser = subparsers.add_parser("update", help="Update memories from completed run")
    update_parser.add_argument("run_dir", type=Path)

    # Get agent stats
    stats_parser = subparsers.add_parser("stats", help="Show agent statistics")
    stats_parser.add_argument("agent_id")

    # Suggest agents
    suggest_parser = subparsers.add_parser("suggest", help="Suggest agents for task")
    suggest_parser.add_argument("keywords", nargs="+")
    suggest_parser.add_argument("--top", type=int, default=3)

    # List all memories
    subparsers.add_parser("list", help="List all agent memories")

    args = parser.parse_args()

    try:
        if args.command == "update":
            update_from_run(args.run_dir)
        elif args.command == "stats":
            stats = get_agent_stats(args.agent_id)
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        elif args.command == "suggest":
            agents = suggest_agents(args.keywords, args.top)
            print(f"Suggested agents: {', '.join(agents)}")
        elif args.command == "list":
            if MEMORY_DIR.exists():
                for memory_file in MEMORY_DIR.glob("*.json"):
                    memory = load_memory(memory_file.stem)
                    if memory:
                        total = memory.success_count + memory.failure_count
                        rate = memory.success_count / total if total > 0 else 0
                        print(f"{memory.agent_id:40} runs={total:3d} success_rate={rate:.0%}")
            else:
                print("No memories yet")
        return 0
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
