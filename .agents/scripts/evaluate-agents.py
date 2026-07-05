#!/usr/bin/env python3
"""Evaluate agent performance and auto-select optimal agents for tasks."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
MEMORY_DIR = ROOT / "reports" / "memory"
IDENTITIES_PATH = ROOT / "skills" / "codex-agent-identity-bank" / "references" / "identities.json"


@dataclass
class AgentScore:
    """Agent performance score."""
    agent_id: str
    relevance_score: float
    performance_score: float
    reliability_score: float
    total_score: float
    reasoning: str


def load_identities() -> dict:
    """Load identity definitions."""
    return json.loads(IDENTITIES_PATH.read_text(encoding="utf-8"))


def load_agent_memory(agent_id: str) -> dict[str, Any] | None:
    """Load agent memory if exists."""
    memory_file = MEMORY_DIR / f"{agent_id}.json"
    if not memory_file.exists():
        return None
    return json.loads(memory_file.read_text(encoding="utf-8"))


def calculate_relevance(identity: dict, task: str, scope: str) -> float:
    """Calculate how relevant an agent is to the task (0-1)."""
    text = f"{task} {scope}".lower()
    keyword_hits = sum(1 for kw in identity["keywords"] if kw.lower() in text)
    return min(keyword_hits / max(len(identity["keywords"]), 1), 1.0)


def calculate_performance(memory: dict | None) -> float:
    """Calculate agent performance score from history (0-1)."""
    if not memory:
        return 0.5  # Neutral for new agents

    total = memory["success_count"] + memory["failure_count"]
    if total == 0:
        return 0.5

    success_rate = memory["success_count"] / total
    return success_rate


def calculate_reliability(memory: dict | None) -> float:
    """Calculate agent reliability (consistency) (0-1)."""
    if not memory:
        return 0.5

    total = memory["success_count"] + memory["failure_count"]
    if total < 3:
        return 0.5  # Not enough data

    # Higher total runs = more reliable data
    confidence = min(total / 20, 1.0)  # Cap at 20 runs
    success_rate = memory["success_count"] / total

    # Penalize agents with high variance (inconsistent)
    return success_rate * confidence


def evaluate_agent(identity: dict, task: str, scope: str, context: str) -> AgentScore:
    """Evaluate a single agent for a task."""
    agent_id = identity["id"]
    memory = load_agent_memory(agent_id)

    # Calculate component scores
    relevance = calculate_relevance(identity, task, scope)
    performance = calculate_performance(memory)
    reliability = calculate_reliability(memory)

    # Weighted total score
    weights = {"relevance": 0.5, "performance": 0.3, "reliability": 0.2}
    total = (
        relevance * weights["relevance"] +
        performance * weights["performance"] +
        reliability * weights["reliability"]
    )

    # Generate reasoning
    reasoning_parts = []
    if relevance > 0.7:
        reasoning_parts.append(f"high keyword match ({relevance:.0%})")
    elif relevance < 0.3:
        reasoning_parts.append(f"low relevance ({relevance:.0%})")

    if memory:
        total_runs = memory["success_count"] + memory["failure_count"]
        reasoning_parts.append(f"{total_runs} prior runs")
        if performance > 0.8:
            reasoning_parts.append(f"strong track record ({performance:.0%})")
        elif performance < 0.5:
            reasoning_parts.append(f"poor track record ({performance:.0%})")

    reasoning = ", ".join(reasoning_parts) if reasoning_parts else "new agent"

    return AgentScore(
        agent_id=agent_id,
        relevance_score=relevance,
        performance_score=performance,
        reliability_score=reliability,
        total_score=total,
        reasoning=reasoning,
    )


def rank_agents(task: str, scope: str, context: str, max_agents: int = 5) -> list[AgentScore]:
    """Rank all agents for a task."""
    data = load_identities()
    scores = []

    for identity in data["identities"]:
        score = evaluate_agent(identity, task, scope, context)
        scores.append(score)

    scores.sort(key=lambda s: s.total_score, reverse=True)
    return scores[:max_agents]


def recommend_team(task: str, scope: str, context: str, preset: str | None = None) -> dict[str, Any]:
    """Recommend optimal team for a task."""
    ranked = rank_agents(task, scope, context, max_agents=10)

    # Apply preset constraints if specified
    if preset:
        preset_file = ROOT / "presets" / f"{preset}.json"
        if preset_file.exists():
            preset_data = json.loads(preset_file.read_text(encoding="utf-8"))
            allowed_ids = set(preset_data.get("identities", []))
            ranked = [s for s in ranked if s.agent_id in allowed_ids or s.agent_id == "primary-routed-identity"]

    # Select top agents with diversity
    selected = []
    categories_used = set()

    for score in ranked:
        if len(selected) >= 4:
            break

        # Simple category: first part of agent_id
        category = score.agent_id.split("-")[0]

        # Prefer diversity, but allow same category if score is high
        if category not in categories_used or score.total_score > 0.7:
            selected.append(score)
            categories_used.add(category)

    return {
        "task": task,
        "selected_agents": [
            {
                "id": s.agent_id,
                "score": round(s.total_score, 2),
                "reasoning": s.reasoning,
            }
            for s in selected
        ],
        "alternatives": [
            {"id": s.agent_id, "score": round(s.total_score, 2)}
            for s in ranked[len(selected):len(selected) + 3]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--scope", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--preset", help="Limit to preset team")
    parser.add_argument("--max", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        if args.json:
            recommendation = recommend_team(args.task, args.scope, args.context, args.preset)
            print(json.dumps(recommendation, ensure_ascii=False, indent=2))
        else:
            ranked = rank_agents(args.task, args.scope, args.context, args.max)
            print(f"Top {len(ranked)} agents for task:\n")
            for i, score in enumerate(ranked, 1):
                print(f"{i}. {score.agent_id:40} score={score.total_score:.2f}")
                print(f"   relevance={score.relevance_score:.2f} performance={score.performance_score:.2f} reliability={score.reliability_score:.2f}")
                print(f"   {score.reasoning}")
                print()
        return 0
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
