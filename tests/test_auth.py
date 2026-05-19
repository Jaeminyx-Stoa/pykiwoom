"""Tests for authentication / token management."""

from datetime import datetime, timedelta
from unittest.mock import patch

import httpx
import pytest

from pykiwoom.auth import TokenManager
from pykiwoom.exceptions import TokenError


class TestTokenManager:
    def test_token_triggers_request_when_missing(self):
        tm = TokenManager("test_key", "test_secret", base_url="https://mock.test")

        mock_response = httpx.Response(
            200,
            json={"token": "abc123", "expires_in": 86400},
            request=httpx.Request("POST", "https://mock.test/oauth2/token"),
        )

        with patch("httpx.post", return_value=mock_response) as mock_post:
            token = tm.token
            assert token == "abc123"
            assert mock_post.called

    def test_token_reuses_valid_token(self):
        tm = TokenManager(
            "test_key",
            "test_secret",
            base_url="https://mock.test",
            token="existing_token",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert tm.token == "existing_token"

    def test_authorization_header(self):
        tm = TokenManager(
            "test_key",
            "test_secret",
            token="mytoken",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert tm.authorization == "Bearer mytoken"

    def test_expired_token_triggers_refresh(self):
        tm = TokenManager(
            "test_key",
            "test_secret",
            base_url="https://mock.test",
            token="old_token",
            expires_at=datetime.now() - timedelta(hours=1),
        )

        mock_response = httpx.Response(
            200,
            json={"token": "new_token", "expires_in": 86400},
            request=httpx.Request("POST", "https://mock.test/oauth2/token"),
        )

        with patch("httpx.post", return_value=mock_response):
            assert tm.token == "new_token"

    def test_token_request_failure_raises(self):
        tm = TokenManager("test_key", "test_secret", base_url="https://mock.test")

        mock_response = httpx.Response(
            401,
            json={"error": "invalid_credentials"},
            request=httpx.Request("POST", "https://mock.test/oauth2/token"),
        )

        with patch("httpx.post", return_value=mock_response), pytest.raises(TokenError):
            _ = tm.token
