"""Tests for main client classes."""

from datetime import datetime, timedelta

from pykiwoom import MOCK, REAL, AsyncPyKiwoom, PyKiwoom


class TestPyKiwoomInit:
    def test_creates_with_real_host(self):
        client = PyKiwoom(
            "test_key",
            "test_secret",
            host=REAL,
            token="preexisting",
            expires_at=datetime.now() + timedelta(hours=1),
            rate_limit=False,
        )
        assert client.token == "preexisting"
        assert client._host == REAL
        client.close()

    def test_creates_with_mock_host(self):
        client = PyKiwoom(
            "test_key",
            "test_secret",
            host=MOCK,
            token="preexisting",
            expires_at=datetime.now() + timedelta(hours=1),
            rate_limit=False,
        )
        assert client._host == MOCK
        client.close()

    def test_context_manager(self):
        with PyKiwoom(
            "test_key",
            "test_secret",
            token="tok",
            expires_at=datetime.now() + timedelta(hours=1),
            rate_limit=False,
        ) as client:
            assert client.token == "tok"


class TestAsyncPyKiwoomInit:
    def test_creates(self):
        client = AsyncPyKiwoom(
            "test_key",
            "test_secret",
            host=REAL,
            token="async_tok",
            expires_at=datetime.now() + timedelta(hours=1),
            rate_limit=False,
        )
        assert client.token == "async_tok"
