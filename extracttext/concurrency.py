"""Concurrency utilities.

Provides a singleton *process* pool for CPU-bound tasks (e.g. OCR) so that
heavy work can execute in parallel without blocking the main interpreter.

The pool is lazy-initialised on first access to avoid unnecessary processes
for applications that never use OCR.
"""
from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, Executor
import atexit
from typing import Optional

__all__ = [
    "get_default_executor",
]

_DEFAULT_POOL: Optional[ProcessPoolExecutor] = None


def _create_pool() -> ProcessPoolExecutor:
    max_workers = os.cpu_count() or 1
    pool = ProcessPoolExecutor(max_workers=max_workers)
    # Ensure we cleanly shutdown when Python exits
    atexit.register(pool.shutdown, wait=False)
    return pool


def get_default_executor() -> Executor:
    """Return a singleton :class:`ProcessPoolExecutor` instance."""
    global _DEFAULT_POOL
    if _DEFAULT_POOL is None:
        _DEFAULT_POOL = _create_pool()
    return _DEFAULT_POOL 