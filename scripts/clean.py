#!/usr/bin/env python3
"""Remove local generated artifacts from the project checkout.

Dry-run is the default. Use --apply to delete files.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_TARGETS = [
    ".agents/magent.exe",
    ".agents/dist",
    ".agents/build",
    ".agents/__pycache__",
    ".agents/scripts/__pycache__",
    ".agents/skills/codex-agent-identity-bank/scripts/__pycache__",
    ".pytest_cache",
    "scripts/__pycache__",
    "tests/__pycache__",
    "tests/.manual_test",
]

RUNS_DIR = ".agents/reports/runs"
RUN_KEEP_FILES = {".gitkeep", ".keep"}


def resolve_inside_root(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    resolved_root = root.resolve()
    if target != resolved_root and resolved_root not in target.parents:
        raise ValueError(f"Refusing to clean outside project root: {target}")
    return target


def existing_targets(root: Path, include_runs: bool = False) -> list[Path]:
    targets = []
    for relative in DEFAULT_TARGETS:
        path = resolve_inside_root(root, relative)
        if path.exists():
            targets.append(path)

    if include_runs:
        runs_dir = resolve_inside_root(root, RUNS_DIR)
        if runs_dir.exists():
            for child in sorted(runs_dir.iterdir()):
                if child.name not in RUN_KEEP_FILES:
                    targets.append(child)

    return targets


def remove_target(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def print_targets(targets: Iterable[Path], root: Path, apply: bool) -> None:
    action = "Removing" if apply else "Would remove"
    for target in targets:
        print(f"{action}: {target.relative_to(root)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually delete generated files.")
    parser.add_argument("--runs", action="store_true", help="Also delete generated run folders.")
    args = parser.parse_args(argv)

    targets = existing_targets(PROJECT_ROOT, include_runs=args.runs)
    if not targets:
        print("No generated artifacts found.")
        return 0

    print_targets(targets, PROJECT_ROOT, args.apply)
    if not args.apply:
        print("\nDry run only. Re-run with --apply to delete these files.")
        return 0

    for target in targets:
        remove_target(target)
    print(f"\nRemoved {len(targets)} generated artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
