#!/usr/bin/env python3
"""Audit project maturity for a source-first GitHub release."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "README.md": "first-screen project explanation",
    "LICENSE": "license clarity",
    "CONTRIBUTING.md": "contributor onboarding",
    "SECURITY.md": "vulnerability reporting",
    "CODE_OF_CONDUCT.md": "community expectations",
    "CHANGELOG.md": "release history",
    "requirements.txt": "runtime dependencies",
    "requirements-dev.txt": "developer dependencies",
    "pyproject.toml": "tool configuration",
    ".github/workflows/ci.yml": "continuous integration",
    ".github/ISSUE_TEMPLATE/bug_report.yml": "bug report guidance",
    ".github/ISSUE_TEMPLATE/feature_request.yml": "feature request guidance",
    ".github/pull_request_template.md": "review guidance",
    ".gitattributes": "cross-platform line ending policy",
    ".agents/scripts/advisor.py": "orchestration ROI advisor",
    ".agents/scripts/recipes.py": "practical recipe loader",
    ".agents/recipes/bugfix.json": "bugfix recipe",
    ".agents/recipes/code-review.json": "code review recipe",
    ".agents/recipes/release-readiness.json": "release readiness recipe",
    ".agents/recipes/docs-polish.json": "documentation polish recipe",
    ".agents/recipes/test-plan.json": "test planning recipe",
    "docs/GETTING_STARTED.md": "first-run guide",
    "docs/USER_GUIDE.md": "usage guide",
    "docs/ARCHITECTURE.md": "architecture explanation",
    "docs/RECIPES.md": "practical recipe guide",
    "docs/EFFICIENCY_EVIDENCE.md": "efficiency evidence template",
    "docs/DOGFOOD_REPORT.md": "project dogfood report",
    "docs/MAINTAINER_GUIDE.md": "maintainer operations",
    "docs/RELEASE_CHECKLIST.md": "release process",
    "scripts/doctor.py": "readiness checks",
    "scripts/verify.py": "single verification command",
    "scripts/clean.py": "safe cleanup command",
}

IGNORED_GENERATED_PATTERNS = [
    ".agents/magent.exe",
    ".agents/build/",
    ".agents/dist/",
    ".agents/reports/runs/20260705-015809-44364/",
    "tests/.manual_test/",
    "scripts/__pycache__/",
]

FORBIDDEN_LEGACY_PATHS = [
    ".agents/setup-openai-api.bat",
    ".agents/rebuild-with-openai.bat",
]

CORE_COMMANDS = [
    [sys.executable, ".agents/magent.py", "version"],
]


def run_captured(root: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def check_file(root: Path, relative: str, description: str) -> dict[str, Any]:
    exists = (root / relative).exists()
    return {
        "name": relative,
        "category": "files",
        "ok": exists,
        "detail": description if exists else "missing",
        "severity": "blocker" if not exists else "ok",
    }


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return run_captured(root, ["git", *args])


def check_git_repository(root: Path) -> dict[str, Any]:
    result = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    ok = result.returncode == 0 and result.stdout.strip() == "true"
    return {
        "name": "git repository",
        "category": "source-control",
        "ok": ok,
        "detail": "initialized" if ok else "not initialized",
        "severity": "blocker" if not ok else "ok",
    }


def check_git_has_commit(root: Path) -> dict[str, Any]:
    result = run_git(root, ["rev-parse", "--verify", "HEAD"])
    ok = result.returncode == 0
    return {
        "name": "initial commit",
        "category": "source-control",
        "ok": ok,
        "detail": "present" if ok else "missing; create a source-only commit before publishing",
        "severity": "blocker" if not ok else "ok",
    }


def check_generated_artifacts_ignored(root: Path) -> dict[str, Any]:
    result = run_git(root, ["add", "-n", "."])
    if result.returncode != 0:
        return {
            "name": "git dry-run staging",
            "category": "source-control",
            "ok": False,
            "detail": result.stderr.strip() or "git add dry-run failed",
            "severity": "blocker",
        }

    staged_preview = result.stdout.replace("\\", "/")
    leaked = [pattern for pattern in IGNORED_GENERATED_PATTERNS if pattern in staged_preview]
    return {
        "name": "generated artifact ignore rules",
        "category": "source-control",
        "ok": not leaked,
        "detail": "no generated artifacts in dry-run staging" if not leaked else ", ".join(leaked),
        "severity": "blocker" if leaked else "ok",
    }


def check_forbidden_legacy_paths(root: Path) -> dict[str, Any]:
    present = [relative for relative in FORBIDDEN_LEGACY_PATHS if (root / relative).exists()]
    return {
        "name": "legacy external API entry points",
        "category": "files",
        "ok": not present,
        "detail": "absent" if not present else ", ".join(present),
        "severity": "blocker" if present else "ok",
    }


def check_command(root: Path, command: list[str]) -> dict[str, Any]:
    result = run_captured(root, command)
    command_text = " ".join(command)
    return {
        "name": command_text,
        "category": "commands",
        "ok": result.returncode == 0,
        "detail": "exit 0" if result.returncode == 0 else (result.stderr.strip() or result.stdout.strip()),
        "severity": "blocker" if result.returncode != 0 else "ok",
    }


def check_local_artifact_warnings(root: Path) -> list[dict[str, Any]]:
    warnings = []
    for relative in [".agents/magent.exe", ".agents/dist", ".agents/build"]:
        path = root / relative
        if path.exists():
            warnings.append(
                {
                    "name": relative,
                    "category": "workspace",
                    "ok": True,
                    "detail": "present locally but ignored; run `python scripts/clean.py --apply` before packaging",
                    "severity": "warning",
                }
            )
    return warnings


def maturity_level(blockers: int, warnings: int) -> str:
    if blockers:
        return "not-ready"
    if warnings:
        return "publishable-with-local-warnings"
    return "publishable"


def build_report(root: Path) -> dict[str, Any]:
    checks = [check_git_repository(root)]
    checks.append(check_git_has_commit(root))
    checks.extend(check_file(root, path, description) for path, description in REQUIRED_FILES.items())
    checks.append(check_forbidden_legacy_paths(root))
    checks.append(check_generated_artifacts_ignored(root))
    checks.extend(check_command(root, command) for command in CORE_COMMANDS)
    checks.extend(check_local_artifact_warnings(root))

    blockers = sum(1 for check in checks if check["severity"] == "blocker")
    warnings = sum(1 for check in checks if check["severity"] == "warning")
    passed = sum(1 for check in checks if check["severity"] == "ok")
    return {
        "ok": blockers == 0,
        "level": maturity_level(blockers, warnings),
        "passed": passed,
        "warnings": warnings,
        "blockers": blockers,
        "checks": checks,
    }


def print_report(report: dict[str, Any]) -> None:
    print("Magent maturity audit")
    print("=====================")
    print(f"Level: {report['level']}")
    print(f"Passed: {report['passed']}  Warnings: {report['warnings']}  Blockers: {report['blockers']}")
    print()
    for check in report["checks"]:
        if check["severity"] == "ok":
            marker = "OK"
        elif check["severity"] == "warning":
            marker = "WARN"
        else:
            marker = "FAIL"
        print(f"{marker:<4} [{check['category']}] {check['name']}: {check['detail']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    args = parser.parse_args(argv)

    report = build_report(PROJECT_ROOT)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
