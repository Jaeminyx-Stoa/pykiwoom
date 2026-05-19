"""Tests for rate limiter."""

import time

from pykiwoom.constants import MOCK, REAL
from pykiwoom.ratelimit import RateLimiter


class TestRateLimiter:
    def test_disabled(self):
        rl = RateLimiter(REAL, enabled=False)
        rl.wait()

    def test_real_rate(self):
        rl = RateLimiter(REAL, enabled=True)
        start = time.monotonic()
        for _ in range(5):
            rl.wait()
        elapsed = time.monotonic() - start
        assert elapsed < 2.0

    def test_mock_rate(self):
        rl = RateLimiter(MOCK, enabled=True)
        start = time.monotonic()
        rl.wait()
        rl.wait()
        elapsed = time.monotonic() - start
        assert elapsed < 3.0
