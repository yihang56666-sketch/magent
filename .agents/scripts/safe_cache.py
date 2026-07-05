#!/usr/bin/env python3
"""Thread-safe LRU cache with file locking."""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from pathlib import Path
from threading import Lock
from typing import Any

# Cross-platform advisory file locking: fcntl on POSIX, msvcrt on Windows.
# Either may be absent (e.g. minimal builds); callers must still work, so the
# lock degrades to a no-op rather than raising at import time.
try:
    import fcntl  # type: ignore

    def _lock_exclusive(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_EX)

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)
except ImportError:  # pragma: no cover - platform dependent
    try:
        import msvcrt  # type: ignore

        # msvcrt locks a byte range from the current file pointer; on a freshly
        # created (empty) lock file that range may not exist yet, so treat a
        # failed lock as advisory and continue rather than crash.
        def _lock_exclusive(fd: int) -> None:
            try:
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            except OSError:
                return None

        def _unlock(fd: int) -> None:
            try:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                return None
    except ImportError:  # pragma: no cover - no OS lock available

        def _lock_exclusive(fd: int) -> None:
            return None

        def _unlock(fd: int) -> None:
            return None


class LRUCache:
    """Thread-safe LRU cache with size limit."""

    def __init__(self, max_size: int = 100):
        self.cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self.max_size = max_size
        self.lock = Lock()

    def get(self, key: str) -> str | None:
        """Get item and move to end (most recently used)."""
        with self.lock:
            if key in self.cache:
                content, timestamp = self.cache.pop(key)
                self.cache[key] = (content, timestamp)
                return content
        return None

    def set(self, key: str, content: str):
        """Set item and evict LRU if over size."""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Evict least recently used
                self.cache.popitem(last=False)

            self.cache[key] = (content, time.time())

    def clear(self):
        """Clear all entries."""
        with self.lock:
            self.cache.clear()

    def stats(self) -> dict:
        """Get cache statistics."""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "usage": f"{len(self.cache)}/{self.max_size}"
            }


class FileLock:
    """Cross-process file lock."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = None

    def __enter__(self):
        self.fd = open(self.path, "a")
        _lock_exclusive(self.fd.fileno())
        return self

    def __exit__(self, *args):
        if self.fd:
            _unlock(self.fd.fileno())
            self.fd.close()


class PersistentLRUCache:
    """LRU cache with disk persistence and file locking."""

    def __init__(self, cache_dir: Path, max_size: int = 100, ttl_days: int = 7):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = LRUCache(max_size)
        self.ttl_seconds = ttl_days * 86400
        self.lock_dir = cache_dir / ".locks"
        self.lock_dir.mkdir(exist_ok=True)

    def fingerprint(self, agent_type: str, task: str, scope: str) -> str:
        """Generate cache key."""
        key = f"{agent_type}:{task}:{scope}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def get(self, fingerprint: str) -> str | None:
        """Get with memory → disk fallback."""
        # Check memory
        content = self.memory_cache.get(fingerprint)
        if content:
            return content

        # Check disk
        cache_file = self.cache_dir / f"{fingerprint}.md"
        lock_file = self.lock_dir / f"{fingerprint}.lock"

        if cache_file.exists():
            with FileLock(lock_file):
                age = time.time() - cache_file.stat().st_mtime
                if age < self.ttl_seconds:
                    content = cache_file.read_text(encoding="utf-8")
                    # Warm memory cache
                    self.memory_cache.set(fingerprint, content)
                    return content
                else:
                    # Expired, remove
                    cache_file.unlink()

        return None

    def set(self, fingerprint: str, content: str):
        """Set in both memory and disk."""
        cache_file = self.cache_dir / f"{fingerprint}.md"
        lock_file = self.lock_dir / f"{fingerprint}.lock"

        with FileLock(lock_file):
            cache_file.write_text(content, encoding="utf-8")

        self.memory_cache.set(fingerprint, content)

    def evict_expired(self) -> int:
        """Evict expired entries from disk."""
        evicted = 0
        now = time.time()

        for cache_file in self.cache_dir.glob("*.md"):
            age = now - cache_file.stat().st_mtime
            if age > self.ttl_seconds:
                lock_file = self.lock_dir / f"{cache_file.stem}.lock"
                with FileLock(lock_file):
                    cache_file.unlink()
                    evicted += 1

        return evicted

    def stats(self) -> dict:
        """Get cache statistics."""
        disk_count = len(list(self.cache_dir.glob("*.md")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.md"))

        return {
            "memory": self.memory_cache.stats(),
            "disk_entries": disk_count,
            "disk_size_mb": round(total_size / 1024 / 1024, 2),
            "ttl_days": self.ttl_seconds / 86400
        }
