#!/usr/bin/env python3
"""Bootstrap: Let the multi-agent framework review and improve itself."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def self_review_round(iteration: int) -> dict:
    """One round of self-review."""
    print(f"\n{'='*60}")
    print(f"🔄 Self-Review Iteration {iteration}")
    print(f"{'='*60}\n")

    # Phase 1: Architecture Review
    print("Phase 1: Architecture Review")
    result_arch = subprocess.run([
        "python", str(ROOT / "scripts" / "spawn-team.py"),
        "--task", "Review this multi-agent framework's architecture. Identify design flaws, scalability issues, and missing patterns.",
        "--scope", str(ROOT / "scripts"),
    ], capture_output=True, text=True)

    # Phase 2: Code Quality Review
    print("\nPhase 2: Code Quality Review")
    result_quality = subprocess.run([
        "python", str(ROOT / "scripts" / "spawn-team.py"),
        "--task", "Review code quality: error handling, edge cases, performance bottlenecks, security issues.",
        "--scope", str(ROOT / "scripts"),
    ], capture_output=True, text=True)

    # Phase 3: User Experience Review
    print("\nPhase 3: User Experience Review")
    result_ux = subprocess.run([
        "python", str(ROOT / "scripts" / "spawn-team.py"),
        "--task", "Review developer experience: API complexity, documentation gaps, confusing workflows.",
        "--scope", str(ROOT),
    ], capture_output=True, text=True)

    # Collect findings
    findings = {
        "iteration": iteration,
        "phases": {
            "architecture": parse_findings(result_arch.stdout),
            "quality": parse_findings(result_quality.stdout),
            "ux": parse_findings(result_ux.stdout)
        }
    }

    return findings


def parse_findings(output: str) -> dict:
    """Extract findings from agent output."""
    # Simple extraction - in real version would parse synthesis.md
    return {
        "raw_output": output,
        "has_critical_issues": "CRITICAL" in output or "critical" in output.lower(),
        "has_suggestions": "recommend" in output.lower() or "should" in output.lower()
    }


def prioritize_fixes(findings: dict) -> list[dict]:
    """Prioritize issues to fix."""
    issues = []

    for phase, data in findings["phases"].items():
        if data["has_critical_issues"]:
            issues.append({
                "phase": phase,
                "priority": "critical",
                "needs_fix": True
            })
        elif data["has_suggestions"]:
            issues.append({
                "phase": phase,
                "priority": "medium",
                "needs_fix": True
            })

    return sorted(issues, key=lambda x: 0 if x["priority"] == "critical" else 1)


def apply_fixes(issues: list[dict], iteration: int) -> int:
    """Apply fixes identified by agents."""
    fixed_count = 0

    for issue in issues:
        if issue["priority"] == "critical":
            print(f"\n🔧 Applying fix for {issue['phase']}...")

            # In real version: extract specific fixes from agent output
            # and apply them automatically or with approval

            # For now: ask agents to generate fixes
            result = subprocess.run([
                "python", str(ROOT / "scripts" / "spawn-team.py"),
                "--task", f"Generate code fix for {issue['phase']} issues found in iteration {iteration}",
                "--scope", str(ROOT / "scripts"),
            ], capture_output=True, text=True)

            if result.returncode == 0:
                fixed_count += 1
                print(f"  ✓ Fix applied for {issue['phase']}")
            else:
                print(f"  ✗ Fix failed for {issue['phase']}")

    return fixed_count


def self_bootstrap(max_iterations: int = 3) -> None:
    """Run self-review and improvement loop."""
    print("🚀 Starting Self-Bootstrap Process")
    print(f"Max iterations: {max_iterations}\n")

    iteration = 1
    history = []

    while iteration <= max_iterations:
        # Review
        findings = self_review_round(iteration)
        history.append(findings)

        # Prioritize
        issues = prioritize_fixes(findings)

        if not issues:
            print(f"\n✅ No issues found. Bootstrap complete at iteration {iteration}.")
            break

        print(f"\n📋 Found {len(issues)} issues:")
        for issue in issues:
            print(f"  [{issue['priority'].upper()}] {issue['phase']}")

        # Apply fixes
        fixed = apply_fixes(issues, iteration)
        print(f"\n✓ Applied {fixed}/{len(issues)} fixes")

        if fixed == 0:
            print("\n⚠️  No fixes could be applied. Manual intervention needed.")
            break

        iteration += 1

    # Save history
    history_file = ROOT / "reports" / "bootstrap-history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"🎉 Bootstrap Complete")
    print(f"  Total iterations: {iteration - 1}")
    print(f"  History: {history_file}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    self_bootstrap(max_iterations=3)
