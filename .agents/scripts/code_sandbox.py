#!/usr/bin/env python3
"""Code execution sandbox for agent validation (inspired by AutoGen + MetaGPT)."""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Any


class CodeSandbox:
    """Execute code in isolated environment for validation."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def execute_python(self, code: str) -> dict[str, Any]:
        """Execute Python code in sandbox."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timeout ({self.timeout}s)"
            }
        finally:
            os.unlink(temp_file)

    def validate_fix(self, original_code: str, fixed_code: str, test_code: str) -> dict[str, Any]:
        """Validate that a fix actually works."""
        # Test original (should fail)
        original_result = self.execute_python(original_code + "\n\n" + test_code)

        # Test fixed (should pass)
        fixed_result = self.execute_python(fixed_code + "\n\n" + test_code)

        return {
            "original_failed": not original_result["success"],
            "fixed_passed": fixed_result["success"],
            "fix_valid": not original_result["success"] and fixed_result["success"],
            "original_output": original_result,
            "fixed_output": fixed_result
        }

    def execute_shell(self, command: str, cwd: Path | None = None) -> dict[str, Any]:
        """Execute shell command safely."""
        # Blocklist dangerous commands
        blocklist = ['rm -rf', 'dd', 'mkfs', ':(){ :|:& };:', 'shutdown', 'reboot']
        if any(danger in command for danger in blocklist):
            return {
                "success": False,
                "error": "Blocked dangerous command"
            }

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=cwd
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timeout ({self.timeout}s)"
            }


class AgentToolkit:
    """Extended tools for agents (file ops, search, execution)."""

    def __init__(self, work_dir: Path, sandbox: CodeSandbox):
        self.work_dir = work_dir
        self.sandbox = sandbox

    def read_file(self, path: str) -> str:
        """Read file contents."""
        full_path = self.work_dir / path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return full_path.read_text(encoding='utf-8')

    def search_code(self, pattern: str, file_pattern: str = "**/*.py") -> list[dict]:
        """Search code for pattern."""
        import re
        results = []

        for file in self.work_dir.glob(file_pattern):
            content = file.read_text(encoding='utf-8')
            for i, line in enumerate(content.split('\n'), 1):
                if re.search(pattern, line):
                    results.append({
                        "file": str(file.relative_to(self.work_dir)),
                        "line": i,
                        "content": line.strip()
                    })

        return results

    def run_tests(self, test_pattern: str = "test_*.py") -> dict[str, Any]:
        """Run test suite."""
        result = self.sandbox.execute_shell(
            f"python -m pytest {test_pattern} -v --tb=short",
            cwd=self.work_dir
        )

        # Parse output for pass/fail counts
        stdout = result.get("stdout", "")
        import re
        passed = len(re.findall(r'PASSED', stdout))
        failed = len(re.findall(r'FAILED', stdout))

        return {
            "success": result["success"],
            "passed": passed,
            "failed": failed,
            "output": stdout
        }

    def validate_syntax(self, file_path: str) -> dict[str, Any]:
        """Check Python syntax."""
        result = self.sandbox.execute_shell(
            f"python -m py_compile {file_path}",
            cwd=self.work_dir
        )

        return {
            "valid": result["success"],
            "error": result.get("stderr", "")
        }
