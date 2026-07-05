#!/usr/bin/env python3
"""Codex-only manual execution helpers for prepared agent runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_contract import load_identity_text, specialist_label
from checkpoint_executor import CheckpointManager


def load_dispatch_plan(run_dir: Path) -> dict[str, Any]:
    plan_path = run_dir / "dispatch-plan.json"
    if not plan_path.exists():
        raise FileNotFoundError(f"Dispatch plan not found: {plan_path}")
    return json.loads(plan_path.read_text(encoding="utf-8"))


def agent_output_path(run_dir: Path, agent_id: str) -> Path:
    return run_dir / f"{agent_id}.output.md"


def get_dispatch_agent(plan: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for agent in plan.get("dispatch_plan", []):
        if agent.get("id") == agent_id:
            return agent
    return None


def get_next_pending_result(summary: dict[str, Any]) -> dict[str, Any] | None:
    for result in summary.get("results", []):
        if result.get("status") == "pending":
            return result
    return None


def build_agent_prompt(agent: dict[str, Any], plan: dict[str, Any], next_agent_id: str | None) -> str:
    identity = load_identity_text(agent)
    next_speaker = next_agent_id or "main agent"
    return "\n".join(
        [
            f"## {specialist_label(agent)} ({agent['id']})",
            "",
            "You are a bounded Codex specialist subagent, not the main agent.",
            "",
            "Identity:",
            f"- Specialist role: {agent.get('title', agent['id'])}",
            "- Authority: Advisory only unless the main agent explicitly delegates write authority.",
            "- Relationship: Report to the main agent or traffic controller.",
            "",
            "Mission:",
            f"- {agent.get('mission', 'Analyze the assigned task.')}",
            f"- Task: {plan.get('task', 'No task specified')}",
            "",
            "Scope:",
            f"- {plan.get('scope', 'Not specified')}",
            "",
            "Context:",
            f"- {plan.get('context', 'No additional context provided.') or 'No additional context provided.'}",
            "",
            "Identity card:",
            identity,
            "",
            "Output format:",
            "## Findings",
            "## Evidence",
            "## Risks",
            "## Open Questions",
            "## Recommended Next Action",
            "## Handoff",
            f"- Next speaker: {next_speaker}",
            "- Carry forward: short summary, key evidence, unresolved risks, open questions",
            "- Stop condition: end after one bounded answer; do not continue as another agent",
            "",
            "Write the final answer into the matching output file for this agent.",
        ]
    )


def render_prompt_pack(plan: dict[str, Any], run_dir: Path) -> str:
    lines = [
        "# Codex Manual Execution Pack",
        "",
        f"Task: {plan.get('task', 'Unknown')}",
        f"Pattern: {plan.get('pattern', 'Unknown')}",
        f"Primary identity: {plan.get('primary_identity', 'Unknown')}",
        "",
        "Work through the agents in order and write each final answer into the output file listed below.",
        "",
    ]

    for index, agent in enumerate(plan.get("dispatch_plan", []), 1):
        next_agent = plan.get("dispatch_plan", [])[index] if index < len(plan.get("dispatch_plan", [])) else None
        lines.extend(
            [
                f"### Agent {index}: {agent['id']}",
                "",
                f"- Role: {agent.get('agent_type', 'explorer')}",
                f"- Output file: `{agent_output_path(run_dir, agent['id']).name}`",
                "",
                build_agent_prompt(agent, plan, next_agent.get("id") if next_agent else None),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_handoff_contract(plan: dict[str, Any], run_dir: Path) -> str:
    lines = [
        "# Handoff Contract",
        "",
        "This run uses a turn-based handoff loop inspired by lightweight agent handoffs and group-chat managers.",
        "",
        "Order:",
    ]

    dispatch = plan.get("dispatch_plan", [])
    for index, agent in enumerate(dispatch, 1):
        next_agent = dispatch[index]["id"] if index < len(dispatch) else "main agent"
        lines.append(f"- {index}. {agent['id']} -> {next_agent}")

    lines.extend(
        [
            "",
            "Rules:",
            "- One agent answers at a time.",
            "- The main Codex session owns final synthesis.",
            "- Each agent ends with a handoff to the next speaker.",
            "- The last agent hands off back to the main agent.",
            "",
            f"Run directory: `{run_dir}`",
        ]
    )

    return "\n".join(lines) + "\n"


def _status_for_output(output_file: Path) -> str:
    if not output_file.exists():
        return "pending"
    content = output_file.read_text(encoding="utf-8").strip()
    if not content:
        return "pending"
    lowered = content.lower()
    if "execution failed" in lowered or lowered.startswith("# error"):
        return "failed"
    return "completed"


def build_summary(plan: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    results = []
    for agent in plan.get("dispatch_plan", []):
        output_file = agent_output_path(run_dir, agent["id"])
        status = _status_for_output(output_file)
        results.append(
            {
                "agent_id": agent["id"],
                "identity_id": agent.get("identity_id", agent["id"]),
                "agent_type": agent.get("agent_type", "explorer"),
                "execution_role": agent.get("execution_role", agent.get("agent_type", "explorer")),
                "status": status,
                "output_file": str(output_file),
                "tokens": 0,
            }
        )

    completed = sum(1 for result in results if result["status"] == "completed")
    failed = sum(1 for result in results if result["status"] == "failed")
    pending = sum(1 for result in results if result["status"] == "pending")

    return {
        "total": len(results),
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "total_tokens": 0,
        "results": results,
    }


def render_manual_workflow(plan: dict[str, Any], run_dir: Path) -> str:
    lines = [
        "# Manual Codex Workflow",
        "",
        "1. Open `agent-prompts.md`.",
        "2. Process one agent at a time with the current Codex session.",
        "3. Write each final answer into the matching `*.output.md` file.",
        "4. Run `magent step <run_id>` to refresh the run and jump to the next pending turn.",
        "5. Repeat until `step` says all agents are complete.",
        "6. Run `python .agents/scripts/merge-results.py <run_dir>` after all agents are complete.",
        "7. Use `handoff-contract.md` to keep the turn order explicit.",
        "",
        f"Run directory: `{run_dir}`",
        "",
        f"Task: {plan.get('task', 'Unknown')}",
        f"Pattern: {plan.get('pattern', 'Unknown')}",
        "",
        "Pending agent order:",
    ]

    for index, agent in enumerate(plan.get("dispatch_plan", []), 1):
        lines.append(f"- {index}. {agent['id']}")

    return "\n".join(lines) + "\n"


def render_next_agent_brief(plan: dict[str, Any], run_dir: Path) -> str:
    summary = build_summary(plan, run_dir)
    pending = get_next_pending_result(summary)

    lines = [
        "# Next Agent Brief",
        "",
        f"Run directory: `{run_dir}`",
        f"Completed: {summary['completed']}/{summary['total']}",
        f"Pending: {summary['pending']}",
        f"Failed: {summary['failed']}",
        "",
    ]

    if pending is None:
        lines.extend(
            [
                "All agents are complete.",
                "",
                "Run `python .agents/scripts/merge-results.py <run_dir>` to build the synthesis.",
            ]
        )
        return "\n".join(lines) + "\n"

    agent = get_dispatch_agent(plan, pending["agent_id"])
    if agent is None:
        lines.extend(
            [
                f"Next pending agent: `{pending['agent_id']}`",
                "",
                "The dispatch plan no longer contains this agent.",
            ]
        )
        return "\n".join(lines) + "\n"

    dispatch = plan.get("dispatch_plan", [])
    next_agent_id = "main agent"
    for index, item in enumerate(dispatch):
        if item.get("id") == agent["id"] and index + 1 < len(dispatch):
            next_agent_id = dispatch[index + 1]["id"]
            break

    lines.extend(
        [
            f"Next pending agent: `{agent['id']}`",
            f"- Role: {agent.get('title', agent['id'])}",
            f"- Output file: `{agent_output_path(run_dir, agent['id']).name}`",
            f"- Handoff target: `{next_agent_id}`",
            "",
            "## Copyable Packet",
            "",
            build_agent_prompt(agent, plan, None if next_agent_id == "main agent" else next_agent_id),
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def initialize_manual_run(run_dir: Path) -> dict[str, Any]:
    plan = load_dispatch_plan(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    for runtime_file in ("checkpoints.jsonl", "stream.jsonl"):
        path = run_dir / runtime_file
        if path.exists():
            path.unlink()

    prompts_path = run_dir / "agent-prompts.md"
    prompts_path.write_text(render_prompt_pack(plan, run_dir), encoding="utf-8")

    handoff_path = run_dir / "handoff-contract.md"
    handoff_path.write_text(render_handoff_contract(plan, run_dir), encoding="utf-8")

    workflow_path = run_dir / "manual-execution.md"
    workflow_path.write_text(render_manual_workflow(plan, run_dir), encoding="utf-8")

    synthesis_path = run_dir / "synthesis.md"
    if not synthesis_path.exists():
        synthesis_path.write_text(
            "# Synthesis\n\nAccepted facts:\n\nConflicts:\n\nNext action:\n",
            encoding="utf-8",
        )

    next_agent_path = run_dir / "next-agent.md"
    next_agent_path.write_text(render_next_agent_brief(plan, run_dir), encoding="utf-8")

    summary = build_summary(plan, run_dir)
    checkpoint = CheckpointManager(run_dir)
    for result in summary["results"]:
        checkpoint.save_checkpoint(
            result["agent_id"],
            result["status"],
            None,
            {"identity_id": result["identity_id"], "output_file": result["output_file"]},
        )

    (run_dir / "execution-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def sync_manual_run(run_dir: Path) -> dict[str, Any]:
    plan = load_dispatch_plan(run_dir)
    summary = build_summary(plan, run_dir)
    checkpoint = CheckpointManager(run_dir)

    for result in summary["results"]:
        checkpoint.save_checkpoint(
            result["agent_id"],
            result["status"],
            None,
            {"identity_id": result["identity_id"], "output_file": result["output_file"]},
        )

    (run_dir / "next-agent.md").write_text(render_next_agent_brief(plan, run_dir), encoding="utf-8")
    (run_dir / "execution-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
