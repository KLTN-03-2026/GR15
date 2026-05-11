from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, TypeVar


T = TypeVar("T")


def run_with_timeout(fn: Callable[[], T], timeout_seconds: float) -> T:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout_seconds)
    except TimeoutError:
        future.cancel()
        raise
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


__all__ = ["TimeoutError", "run_with_timeout"]
