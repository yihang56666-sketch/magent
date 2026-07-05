#!/usr/bin/env python3
"""Error handling helpers for the Codex-only multi-agent workflow."""

from __future__ import annotations

import functools
import subprocess
import sys
from typing import Callable


class MagentError(Exception):
    """Base exception for magent errors."""


class ConfigError(MagentError):
    """Configuration error."""


class ExecutionError(MagentError):
    """Subprocess or workflow execution error."""


class TimeoutError(MagentError):
    """Timeout error."""


def handle_errors(func: Callable) -> Callable:
    """Decorator for consistent user-facing error output."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except subprocess.TimeoutExpired as exc:
            print(f"\nExecution timed out after {exc.timeout}s.")
            print("Tip: narrow the task scope or rerun the step manually.")
            return 1
        except FileNotFoundError as exc:
            print(f"\nFile not found: {exc.filename}")
            print("Tip: check that the run directory and required files exist.")
            return 1
        except PermissionError as exc:
            print(f"\nPermission denied: {exc.filename}")
            print("Tip: close any program locking the file and try again.")
            return 1
        except KeyError as exc:
            print(f"\nMissing required field: {exc}")
            print("Tip: regenerate the dispatch plan for this run.")
            return 1
        except ValueError as exc:
            print(f"\nInvalid value: {exc}")
            print("Tip: review the command arguments and configuration.")
            return 1
        except ConfigError as exc:
            print(f"\nConfiguration error: {exc}")
            print("Tip: this project only needs local magent settings and the current Codex session.")
            return 1
        except ExecutionError as exc:
            print(f"\nExecution error: {exc}")
            return 1
        except TimeoutError as exc:
            print(f"\nOperation timed out: {exc}")
            print("Tip: rerun `python .agents/magent.py step` to refresh the run and continue.")
            return 1
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            print("Tip: rerun the command or refresh status with `python .agents/magent.py status`.")
            return 130
        except Exception as exc:
            print(f"\nUnexpected error: {type(exc).__name__}: {exc}")
            print("Tip: inspect the generated run folder and retry the current workflow step.")
            if "--debug" in sys.argv:
                import traceback

                print("\nDebug traceback:")
                traceback.print_exc()
            return 1

    return wrapper


def safe_subprocess_run(cmd: list[str], timeout: int = 300, **kwargs):
    """Run a subprocess and raise workflow-specific exceptions on failure."""

    try:
        return subprocess.run(cmd, timeout=timeout, check=True, **kwargs)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"Command timed out after {timeout}s") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        details = stderr.strip() if isinstance(stderr, str) and stderr.strip() else "no stderr captured"
        raise ExecutionError(f"Command failed: {' '.join(cmd)} ({details})") from exc


def print_friendly_error(error_type: str, message: str, tip: str = "") -> None:
    print(f"\n{error_type}: {message}")
    if tip:
        print(f"Tip: {tip}")
