#!/usr/bin/env python3
"""Check whether the local checkout is ready for development and release."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "requirements.txt",
    "requirements-dev.txt",
    ".agents/magent.py",
    ".agents/scripts/spawn-team.py",
    ".agents/scripts/validate-identities.py",
    ".agents/skills/codex-agent-identity-bank/SKILL.md",
    ".agents/skills/codex-multi-agent-orchestrator/SKILL.md",
    "tests",
]

REQUIRED_MODULES = {
    "yaml": "pyyaml",
    "psutil": "psutil",
    "pytest": "pytest",
}

GENERATED_ARTIFACT_HINTS = [
    ".agents/magent.exe",
    ".agents/dist",
    ".agents/build",
    ".pytest_cache",
]


def human_size(bytes_count: int) -> str:
    value = float(bytes_count)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{bytes_count} B"


def directory_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def check_python_version() -> dict[str, Any]:
    version = sys.version_info
    ok = version >= (3, 10)
    return {
        "name": "python",
        "ok": ok,
        "detail": f"{version.major}.{version.minor}.{version.micro}",
        "hint": "" if ok else "Use Python 3.10 or newer.",
    }


def check_required_paths(root: Path) -> list[dict[str, Any]]:
    checks = []
    for relative in REQUIRED_PATHS:
        exists = (root / relative).exists()
        checks.append(
            {
                "name": relative,
                "ok": exists,
                "detail": "found" if exists else "missing",
                "hint": "" if exists else "Restore this file before publishing the project.",
            }
        )
    return checks


def check_required_modules() -> list[dict[str, Any]]:
    checks = []
    for module, package in REQUIRED_MODULES.items():
        exists = importlib.util.find_spec(module) is not None
        checks.append(
            {
                "name": module,
                "ok": exists,
                "detail": "importable" if exists else "missing",
                "hint": "" if exists else f"Run `python -m pip install -r requirements-dev.txt` to install {package}.",
            }
        )
    return checks


def check_generated_artifacts(root: Path, large_threshold: int = 50 * 1024 * 1024) -> list[dict[str, Any]]:
    checks = []
    for relative in GENERATED_ARTIFACT_HINTS:
        path = root / relative
        if not path.exists():
            continue
        size = directory_size(path)
        checks.append(
            {
                "name": relative,
                "ok": size < large_threshold,
                "detail": human_size(size),
                "hint": "Generated artifact; keep ignored or rebuild locally instead of committing."
                if size >= large_threshold
                else "Generated artifact; usually not needed in source commits.",
            }
        )
    return checks


def build_report(root: Path) -> dict[str, Any]:
    checks = [check_python_version()]
    checks.extend(check_required_paths(root))
    checks.extend(check_required_modules())
    artifact_warnings = check_generated_artifacts(root)
    failures = [check for check in checks if not check["ok"]]
    warnings = [check for check in artifact_warnings if not check["ok"]]
    notes = [check for check in artifact_warnings if check["ok"]]
    return {
        "ok": not failures,
        "checks": checks,
        "warnings": warnings,
        "notes": notes,
    }


def print_report(report: dict[str, Any]) -> None:
    print("Magent project doctor")
    print("=" * 22)
    for check in report["checks"]:
        marker = "OK" if check["ok"] else "FAIL"
        print(f"{marker:<4} {check['name']}: {check['detail']}")
        if check["hint"]:
            print(f"     {check['hint']}")

    if report["warnings"]:
        print("\nWarnings")
        for warning in report["warnings"]:
            print(f"WARN {warning['name']}: {warning['detail']}")
            print(f"     {warning['hint']}")

    if report["notes"]:
        print("\nNotes")
        for note in report["notes"]:
            print(f"NOTE {note['name']}: {note['detail']}")
            print(f"     {note['hint']}")

    print("\nResult:", "ready" if report["ok"] else "needs attention")


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
