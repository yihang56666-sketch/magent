#!/usr/bin/env python3
"""Build script for the Codex-only magent executable."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def build() -> bool:
    print("Building magent.exe...")

    for directory in ["build", "dist"]:
        path = Path(directory)
        if path.exists():
            shutil.rmtree(path)
    if Path("magent.exe").exists():
        Path("magent.exe").unlink()

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "magent.spec"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("BUILD FAILED:")
        print(result.stderr)
        return False

    dist_exe = Path("dist/magent.exe")
    if not dist_exe.exists():
        print("ERROR: dist/magent.exe not found")
        return False

    shutil.move(str(dist_exe), "magent.exe")
    print("SUCCESS: magent.exe created")

    test_result = subprocess.run(["magent.exe", "version"], capture_output=True, text=True)
    if test_result.returncode == 0:
        print("Test passed:")
        print(test_result.stdout)
    else:
        print("Test failed:")
        print(test_result.stderr)
    return True


if __name__ == "__main__":
    sys.exit(0 if build() else 1)
