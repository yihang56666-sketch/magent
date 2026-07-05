#!/usr/bin/env python3
"""Real-time negotiation mechanism between agents for conflict resolution."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Proposal:
    """A negotiation proposal from an agent."""
    agent_id: str
    proposal: str
    reasoning: str
    priority: int  # 1-5, higher = more important
    constraints: list[str]
    accepts: list[str]  # Agent IDs that accepted
    rejects: list[str]  # Agent IDs that rejected


@dataclass
class Negotiation:
    """A negotiation session."""
    topic: str
    involved_agents: list[str]
    proposals: list[Proposal]
    resolution: str | None
    status: str  # active, resolved, deadlocked


def load_conflicts(conflicts_file: Path) -> list[dict[str, Any]]:
    """Load detected conflicts."""
    if not conflicts_file.exists():
        return []
    return json.loads(conflicts_file.read_text(encoding="utf-8")).get("conflicts", [])


def create_negotiation(conflict: dict[str, Any]) -> Negotiation:
    """Initialize negotiation from a conflict."""
    agents = conflict.get("agents", [])
    topic = conflict.get("description", "Unknown conflict")

    return Negotiation(
        topic=topic,
        involved_agents=agents,
        proposals=[],
        resolution=None,
        status="active",
    )


def auto_resolve_simple(negotiation: Negotiation) -> str | None:
    """Attempt automatic resolution for simple conflicts."""
    if len(negotiation.involved_agents) == 2:
        # Two-agent conflicts: use priority-based resolution
        if len(negotiation.proposals) == 2:
            p1, p2 = negotiation.proposals
            if p1.priority > p2.priority:
                return f"Adopted {p1.agent_id}'s proposal (higher priority: {p1.priority} vs {p2.priority})"
            elif p2.priority > p1.priority:
                return f"Adopted {p2.agent_id}'s proposal (higher priority: {p2.priority} vs {p1.priority})"

    # Check for unanimous acceptance
    for proposal in negotiation.proposals:
        if len(proposal.accepts) == len(negotiation.involved_agents) - 1:
            return f"Unanimous agreement on {proposal.agent_id}'s proposal"

    return None


def merge_compatible_proposals(proposals: list[Proposal]) -> str | None:
    """Try to merge proposals that don't contradict."""
    if len(proposals) < 2:
        return None

    # Simple heuristic: if all proposals have overlapping accepts, merge them
    all_constraints = []
    merged_reasoning = []

    for proposal in proposals:
        if proposal.rejects:
            return None  # Can't merge if any proposal was rejected

        all_constraints.extend(proposal.constraints)
        merged_reasoning.append(f"{proposal.agent_id}: {proposal.reasoning}")

    return f"Merged proposals: {', '.join(merged_reasoning)}"


def detect_deadlock(negotiation: Negotiation, max_rounds: int = 3) -> bool:
    """Detect if negotiation is deadlocked."""
    if len(negotiation.proposals) > max_rounds * len(negotiation.involved_agents):
        # Too many proposals without resolution
        return True

    # Check for circular rejections
    rejection_graph = {}
    for proposal in negotiation.proposals:
        if proposal.rejects:
            rejection_graph[proposal.agent_id] = proposal.rejects

    # Simple cycle detection
    if len(rejection_graph) == len(negotiation.involved_agents):
        return True

    return False


def negotiate(run_dir: Path) -> dict[str, Any]:
    """Execute negotiation protocol."""
    conflicts_file = run_dir / "conflicts.json"
    conflicts = load_conflicts(conflicts_file)

    if not conflicts:
        return {"status": "no_conflicts", "negotiations": []}

    negotiations = []
    for conflict in conflicts:
        if conflict.get("severity") not in ["high", "critical"]:
            continue  # Only negotiate critical conflicts

        negotiation = create_negotiation(conflict)

        # In real implementation, would invoke agents to propose solutions
        # For now, create stub proposals
        for agent_id in negotiation.involved_agents:
            proposal = Proposal(
                agent_id=agent_id,
                proposal=f"{agent_id}'s solution for: {negotiation.topic}",
                reasoning=f"Based on {agent_id}'s domain expertise",
                priority=3,
                constraints=[],
                accepts=[],
                rejects=[],
            )
            negotiation.proposals.append(proposal)

        # Try auto-resolution
        auto_resolution = auto_resolve_simple(negotiation)
        if auto_resolution:
            negotiation.resolution = auto_resolution
            negotiation.status = "resolved"
        elif detect_deadlock(negotiation):
            negotiation.status = "deadlocked"
            negotiation.resolution = "Escalated to main agent for manual resolution"
        else:
            # Try merging
            merge_resolution = merge_compatible_proposals(negotiation.proposals)
            if merge_resolution:
                negotiation.resolution = merge_resolution
                negotiation.status = "resolved"

        negotiations.append(asdict(negotiation))

    return {
        "status": "completed",
        "total_conflicts": len(conflicts),
        "negotiations": negotiations,
        "resolved": sum(1 for n in negotiations if n["status"] == "resolved"),
        "deadlocked": sum(1 for n in negotiations if n["status"] == "deadlocked"),
    }


def escalate_to_main(negotiation: dict[str, Any]) -> dict[str, Any]:
    """Prepare escalation summary for main agent."""
    return {
        "topic": negotiation["topic"],
        "involved_agents": negotiation["involved_agents"],
        "proposals": [
            {
                "agent": p["agent_id"],
                "solution": p["proposal"],
                "priority": p["priority"],
            }
            for p in negotiation["proposals"]
        ],
        "recommendation": "Manual decision required - competing priorities",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, help="Save negotiation results")
    parser.add_argument("--escalate", action="store_true", help="Generate escalation report")
    args = parser.parse_args()

    try:
        result = negotiate(args.run_dir)

        if args.escalate:
            escalations = []
            for neg in result["negotiations"]:
                if neg["status"] == "deadlocked":
                    escalations.append(escalate_to_main(neg))
            result["escalations"] = escalations

        output_json = json.dumps(result, ensure_ascii=False, indent=2)

        if args.output:
            args.output.write_text(output_json, encoding="utf-8")
            logger.info(f"✓ Saved to {args.output}")
        else:
            print(output_json)

        logger.info(f"✓ Processed {result['total_conflicts']} conflicts")
        logger.info(f"  Resolved: {result.get('resolved', 0)}")
        logger.info(f"  Deadlocked: {result.get('deadlocked', 0)}")

        return 0
    except Exception as e:
        logger.error(f"Negotiation failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
