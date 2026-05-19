"""Rate limiter for Kiwoom OPEN API endpoints."""

from __future__ import annotations

import asyncio
import threading
import time

from .constants import RATE_LIMIT_MOCK, RATE_LIMIT_REAL, REAL


class RateLimiter:
    """Thread-safe token bucket rate limiter.

    Kiwoom enforces global rate limits:
    - REAL server: 5 requests/second
    - MOCK server: 1 request/second
    """

    def __init__(self, host: str = REAL, *, enabled: bool = True):
        self._enabled = enabled
        rate = RATE_LIMIT_REAL if host == REAL else RATE_LIMIT_MOCK
        self._bucket = _TokenBucket(rate)

    def wait(self) -> None:
        if not self._enabled:
            return
        self._bucket.acquire()

    async def async_wait(self) -> None:
        if not self._enabled:
            return
        wait_time = self._bucket.time_until_available()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._bucket.acquire()


class _TokenBucket:
    """Simple token bucket for rate limiting."""

    def __init__(self, rate: int):
        self._rate = rate
        self._tokens = float(rate)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def acquire(self) -> None:
        with self._lock:
            self._refill()
            if self._tokens < 1:
                wait = (1 - self._tokens) / self._rate
                time.sleep(wait)
                self._refill()
            self._tokens -= 1

    def time_until_available(self) -> float:
        with self._lock:
            self._refill()
            if self._tokens >= 1:
                return 0.0
            return (1 - self._tokens) / self._rate
