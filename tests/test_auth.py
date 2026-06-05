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

    def test_token_request_uses_json_body(self):
        # 키움 REST는 JSON 본문을 요구한다(form-urlencoded는 415). 회귀 방지.
        tm = TokenManager("test_key", "test_secret", base_url="https://mock.test")
        mock_response = httpx.Response(
            200,
            json={"token": "abc123", "return_code": 0, "expires_in": 86400},
            request=httpx.Request("POST", "https://mock.test/oauth2/token"),
        )
        with patch("httpx.post", return_value=mock_response) as mock_post:
            assert tm.token == "abc123"
            _, kwargs = mock_post.call_args
            assert kwargs.get("json", {}).get("grant_type") == "client_credentials"
            assert "data" not in kwargs  # form-encoded 가 아니어야 함

    def test_auth_failure_with_200_return_code_raises(self):
        # 키움은 인증 실패도 HTTP 200 + return_code != 0 로 응답 → KeyError 가 아니라 TokenError.
        tm = TokenManager("test_key", "test_secret", base_url="https://mock.test")
        mock_response = httpx.Response(
            200,
            json={"return_code": 3, "return_msg": "인증에 실패했습니다"},
            request=httpx.Request("POST", "https://mock.test/oauth2/token"),
        )
        with patch("httpx.post", return_value=mock_response), pytest.raises(TokenError):
            _ = tm.token

    def test_token_parses_expires_dt(self):
        # 키움은 expires_dt('YYYYMMDDHHMMSS')로 만료를 준다.
        tm = TokenManager("test_key", "test_secret", base_url="https://mock.test")
        mock_response = httpx.Response(
            200,
            json={"token": "t", "return_code": 0, "expires_dt": "20261231235959"},
            request=httpx.Request("POST", "https://mock.test/oauth2/token"),
        )
        with patch("httpx.post", return_value=mock_response):
            assert tm.token == "t"
            assert tm.expires_at == datetime(2026, 12, 31, 23, 59, 59)
