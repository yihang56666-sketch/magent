#!/usr/bin/env python3
"""Merge subagent outputs into a unified synthesis document."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_execution_summary(run_dir: Path) -> dict[str, Any]:
    summary_path = run_dir / "execution-summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Execution summary not found: {summary_path}")
    return json.loads(summary_path.read_text(encoding="utf-8"))


def load_agent_output(output_file: Path) -> str:
    if not output_file.exists():
        return "[Output file not found]"
    return output_file.read_text(encoding="utf-8")


def extract_section(content: str, section: str) -> str:
    """Extract a section from agent output."""
    lines = content.split("\n")
    in_section = False
    section_lines = []

    for line in lines:
        if line.startswith(f"## {section}"):
            in_section = True
            continue
        elif line.startswith("## ") and in_section:
            break
        elif in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def merge_results(run_dir: Path) -> dict[str, Any]:
    """Merge all agent outputs into structured synthesis."""
    summary = load_execution_summary(run_dir)
    plan = json.loads((run_dir / "dispatch-plan.json").read_text(encoding="utf-8"))

    merged = {
        "task": plan.get("task", "Unknown"),
        "pattern": plan.get("pattern", "Unknown"),
        "agents": [],
        "accepted_facts": [],
        "conflicts": [],
        "risks": [],
        "open_questions": [],
        "recommendations": [],
        "handoffs": [],
    }

    for result in summary["results"]:
        if result["status"] != "completed":
            continue

        output_file = Path(result["output_file"])
        content = load_agent_output(output_file)

        agent_summary = {
            "id": result["agent_id"],
            "findings": extract_section(content, "Findings"),
            "evidence": extract_section(content, "Evidence"),
            "risks": extract_section(content, "Risks"),
            "questions": extract_section(content, "Open Questions"),
            "recommendation": extract_section(content, "Recommended Next Action"),
            "handoff": extract_section(content, "Handoff"),
        }

        merged["agents"].append(agent_summary)

        # Aggregate cross-agent data
        if agent_summary["risks"]:
            merged["risks"].append(f"[{agent_summary['id']}] {agent_summary['risks']}")
        if agent_summary["questions"]:
            merged["open_questions"].append(f"[{agent_summary['id']}] {agent_summary['questions']}")
        if agent_summary["recommendation"]:
            merged["recommendations"].append(f"[{agent_summary['id']}] {agent_summary['recommendation']}")
        if agent_summary["handoff"]:
            merged["handoffs"].append(f"[{agent_summary['id']}] {agent_summary['handoff']}")

    return merged


def render_synthesis_md(merged: dict[str, Any]) -> str:
    """Render merged data as Markdown."""
    lines = [
        "# Synthesis",
        "",
        f"**Task:** {merged['task']}",
        f"**Pattern:** {merged['pattern']}",
        "",
        "## Agent Summary",
        "",
    ]

    for agent in merged["agents"]:
        lines.append(f"### {agent['id']}")
        lines.append("")
        lines.append(f"**Findings:** {agent['findings'] or '(none)'}")
        lines.append(f"**Evidence:** {agent['evidence'] or '(none)'}")
        lines.append("")

    lines.extend([
        "## Accepted Facts",
        "",
        "[Main agent to populate after reviewing agent outputs]",
        "",
        "## Conflicts",
        "",
    ])

    if merged["conflicts"]:
        for conflict in merged["conflicts"]:
            lines.append(f"- {conflict}")
    else:
        lines.append("(none detected)")

    lines.extend([
        "",
        "## Aggregated Risks",
        "",
    ])

    if merged["risks"]:
        for risk in merged["risks"]:
            lines.append(f"- {risk}")
    else:
        lines.append("(none)")

    lines.extend([
        "",
        "## Open Questions",
        "",
    ])

    if merged["open_questions"]:
        for question in merged["open_questions"]:
            lines.append(f"- {question}")
    else:
        lines.append("(none)")

    lines.extend([
        "",
        "## Recommendations",
        "",
    ])

    if merged["recommendations"]:
        for rec in merged["recommendations"]:
            lines.append(f"- {rec}")
    else:
        lines.append("(none)")

    lines.extend([
        "",
        "## Handoffs",
        "",
    ])

    if merged["handoffs"]:
        for handoff in merged["handoffs"]:
            lines.append(f"- {handoff}")
    else:
        lines.append("(none)")

    lines.extend([
        "",
        "## Next Action",
        "",
        "[Main agent decision based on above synthesis]",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="Path to run directory")
    parser.add_argument("--output", type=Path, help="Output file (default: synthesis.md in run_dir)")
    args = parser.parse_args()

    if not args.run_dir.exists():
        logger.error(f"Run directory not found: {args.run_dir}")
        return 1

    try:
        merged = merge_results(args.run_dir)
        synthesis_md = render_synthesis_md(merged)

        output_path = args.output or (args.run_dir / "synthesis.md")
        output_path.write_text(synthesis_md, encoding="utf-8")

        logger.info(f"✓ Synthesis written to: {output_path}")
        logger.info(f"  Agents: {len(merged['agents'])}")
        logger.info(f"  Risks: {len(merged['risks'])}")
        logger.info(f"  Questions: {len(merged['open_questions'])}")
        return 0
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
