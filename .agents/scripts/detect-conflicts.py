#!/usr/bin/env python3
"""Detect conflicts in subagent outputs."""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_agent_outputs(run_dir: Path) -> dict[str, str]:
    """Load all agent output files."""
    outputs = {}
    for output_file in run_dir.glob("*.output.md"):
        agent_id = output_file.stem.replace(".output", "")
        outputs[agent_id] = output_file.read_text(encoding="utf-8")
    return outputs


def extract_file_mentions(content: str) -> set[str]:
    """Extract file paths mentioned in content."""
    # Match common file path patterns
    patterns = [
        r'`([a-zA-Z0-9_/\\\-\.]+\.[a-zA-Z0-9]+)`',  # `path/to/file.ext`
        r'([a-zA-Z0-9_/\\\-\.]+\.(?:py|ts|js|go|rs|md|json|yaml))',  # standalone paths
    ]
    files = set()
    for pattern in patterns:
        files.update(re.findall(pattern, content))
    return files


def detect_file_conflicts(outputs: dict[str, str]) -> list[dict[str, Any]]:
    """Detect if multiple agents mention modifying the same files."""
    agent_files = {}
    for agent_id, content in outputs.items():
        files = extract_file_mentions(content)
        agent_files[agent_id] = files

    conflicts = []
    agents = list(agent_files.keys())

    for i, agent_a in enumerate(agents):
        for agent_b in agents[i + 1:]:
            common_files = agent_files[agent_a] & agent_files[agent_b]
            if common_files:
                conflicts.append({
                    "type": "file_overlap",
                    "agents": [agent_a, agent_b],
                    "files": sorted(common_files),
                    "severity": "medium",
                    "description": f"Both {agent_a} and {agent_b} reference the same files",
                })

    return conflicts


def detect_contradicting_claims(outputs: dict[str, str]) -> list[dict[str, Any]]:
    """Detect potentially contradicting recommendations."""
    contradictions = []

    # Look for opposing keywords
    negative_patterns = [
        r'\b(do not|don\'t|should not|avoid|remove|delete)\b',
        r'\b(不要|不应该|避免|删除|移除)\b',
    ]
    positive_patterns = [
        r'\b(should|must|add|create|implement)\b',
        r'\b(应该|必须|添加|创建|实现)\b',
    ]

    agents_negative = {}
    agents_positive = {}

    for agent_id, content in outputs.items():
        content_lower = content.lower()
        if any(re.search(p, content_lower) for p in negative_patterns):
            agents_negative[agent_id] = content
        if any(re.search(p, content_lower) for p in positive_patterns):
            agents_positive[agent_id] = content

    if agents_negative and agents_positive:
        contradictions.append({
            "type": "opposing_recommendations",
            "agents_negative": list(agents_negative.keys()),
            "agents_positive": list(agents_positive.keys()),
            "severity": "high",
            "description": "Agents have opposing recommendations (negative vs positive actions)",
        })

    return contradictions


def detect_conflicts(run_dir: Path) -> dict[str, Any]:
    """Run all conflict detection."""
    outputs = load_agent_outputs(run_dir)

    if not outputs:
        logger.warning("No agent outputs found")
        return {"conflicts": [], "total": 0}

    file_conflicts = detect_file_conflicts(outputs)
    claim_conflicts = detect_contradicting_claims(outputs)

    all_conflicts = file_conflicts + claim_conflicts

    return {
        "conflicts": all_conflicts,
        "total": len(all_conflicts),
        "by_severity": {
            "high": sum(1 for c in all_conflicts if c["severity"] == "high"),
            "medium": sum(1 for c in all_conflicts if c["severity"] == "medium"),
            "low": sum(1 for c in all_conflicts if c["severity"] == "low"),
        },
    }


def render_conflicts(conflicts_data: dict[str, Any]) -> str:
    """Render conflicts as readable text."""
    lines = ["# Conflict Detection Report", ""]

    if conflicts_data["total"] == 0:
        lines.append("✓ No conflicts detected")
        return "\n".join(lines)

    lines.append(f"Found {conflicts_data['total']} potential conflicts:")
    lines.append("")

    for conflict in conflicts_data["conflicts"]:
        severity_marker = "⚠️" if conflict["severity"] == "high" else "ℹ️"
        lines.append(f"{severity_marker} **{conflict['type'].upper()}** (severity: {conflict['severity']})")
        lines.append(f"   {conflict['description']}")

        if "agents" in conflict:
            lines.append(f"   Agents: {', '.join(conflict['agents'])}")
        if "files" in conflict:
            lines.append(f"   Files: {', '.join(conflict['files'])}")
        if "agents_negative" in conflict:
            lines.append(f"   Negative: {', '.join(conflict['agents_negative'])}")
        if "agents_positive" in conflict:
            lines.append(f"   Positive: {', '.join(conflict['agents_positive'])}")

        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="Path to run directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.run_dir.exists():
        logger.error(f"Run directory not found: {args.run_dir}")
        return 1

    try:
        conflicts_data = detect_conflicts(args.run_dir)

        if args.json:
            print(json.dumps(conflicts_data, ensure_ascii=False, indent=2))
        else:
            print(render_conflicts(conflicts_data))

        # Save to run directory
        report_path = args.run_dir / "conflicts.json"
        report_path.write_text(json.dumps(conflicts_data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"✓ Conflict report saved: {report_path}")

        return 0 if conflicts_data["by_severity"]["high"] == 0 else 1
    except Exception as e:
        logger.error(f"Conflict detection failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
