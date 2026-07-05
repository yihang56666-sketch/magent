#!/usr/bin/env python3
"""Resource-aware executor with dynamic concurrency."""

import os
import psutil
from typing import Any


class ResourceMonitor:
    """Monitor system resources and adjust concurrency."""

    @staticmethod
    def get_available_workers() -> int:
        """Calculate safe worker count based on system resources."""
        # CPU-based limit
        cpu_count = os.cpu_count() or 4
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_available = max(1, int((100 - cpu_percent) / 100 * cpu_count))

        # Memory-based limit
        memory = psutil.virtual_memory()
        memory_available_gb = memory.available / (1024 ** 3)
        # Assume each worker needs ~500MB
        memory_workers = max(1, int(memory_available_gb / 0.5))

        # Conservative: use minimum
        safe_workers = min(cpu_available, memory_workers, cpu_count - 1)

        return max(1, safe_workers)

    @staticmethod
    def check_resources() -> dict[str, Any]:
        """Check if resources are available for execution."""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        return {
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024 ** 3), 2),
            "can_execute": cpu < 90 and memory.percent < 90,
            "reason": "High CPU" if cpu >= 90 else "Low memory" if memory.percent >= 90 else "OK"
        }

    @staticmethod
    def estimate_cost(num_agents: int, avg_tokens: int = 3000) -> dict:
        """Estimate execution cost."""
        total_tokens = num_agents * avg_tokens

        # Pricing (example: Sonnet)
        cost_per_million = 3.0
        estimated_cost = (total_tokens / 1_000_000) * cost_per_million

        return {
            "num_agents": num_agents,
            "estimated_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 3),
            "warning": "High cost" if estimated_cost > 0.5 else None
        }


class BudgetController:
    """Control execution based on token budget."""

    def __init__(self, max_tokens: int | None = None):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def can_execute(self, estimated_tokens: int) -> bool:
        """Check if we can execute within budget."""
        if self.max_tokens is None:
            return True
        return (self.used_tokens + estimated_tokens) <= self.max_tokens

    def record_usage(self, tokens: int):
        """Record token usage."""
        self.used_tokens += tokens

    def remaining(self) -> int | None:
        """Get remaining budget."""
        if self.max_tokens is None:
            return None
        return max(0, self.max_tokens - self.used_tokens)

    def status(self) -> dict:
        """Get budget status."""
        return {
            "max_tokens": self.max_tokens,
            "used_tokens": self.used_tokens,
            "remaining": self.remaining(),
            "usage_percent": round(self.used_tokens / self.max_tokens * 100, 1) if self.max_tokens else None
        }


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input."""
    # Remove control characters
    sanitized = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")

    # Truncate
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()


def redact_sensitive(data: dict) -> dict:
    """Redact sensitive fields from logs."""
    sensitive_keys = {"api_key", "token", "password", "secret", "credential"}
    redacted = {}

    for key, value in data.items():
        if any(s in key.lower() for s in sensitive_keys):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive(value)
        else:
            redacted[key] = value

    return redacted
