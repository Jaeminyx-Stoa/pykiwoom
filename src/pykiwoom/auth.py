"""OAuth2 token management for Kiwoom OPEN API."""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timedelta
from typing import Any

import httpx

from .constants import BASE_URL, OAUTH_TOKEN_URL
from .exceptions import TokenError

logger = logging.getLogger("pykiwoom")

_TOKEN_REFRESH_MARGIN_MINUTES = 10
_MAX_TOKEN_RETRIES = 3
_RETRY_WAIT_SECONDS = 5


def _read_key(value: str) -> str:
    """Read a key value — if it's a file path, read the file contents."""
    if os.path.isfile(value):
        return open(value).read().strip()
    return value


class TokenManager:
    """Manages OAuth2 token lifecycle for Kiwoom OPEN API."""

    def __init__(
        self,
        appkey: str,
        secretkey: str,
        *,
        base_url: str = BASE_URL,
        token: str | None = None,
        expires_at: datetime | None = None,
    ):
        self._appkey = _read_key(appkey)
        self._secretkey = _read_key(secretkey)
        self._base_url = base_url
        self._token = token
        self._expires_at = expires_at
        self._lock = threading.Lock()

    @property
    def token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if not self._is_valid():
            with self._lock:
                if not self._is_valid():
                    self._request_token()
        return self._token  # type: ignore[return-value]

    @property
    def expires_at(self) -> datetime | None:
        return self._expires_at

    @property
    def authorization(self) -> str:
        """Return the Authorization header value."""
        return f"Bearer {self.token}"

    def _is_valid(self) -> bool:
        if not self._token or not self._expires_at:
            return False
        return datetime.now() + timedelta(minutes=_TOKEN_REFRESH_MARGIN_MINUTES) < self._expires_at

    def refresh(self) -> None:
        """Force token refresh."""
        with self._lock:
            self._request_token()

    def _request_token(self) -> None:
        # 키움 REST OAuth는 JSON 본문을 요구한다(form-urlencoded는 415). 또한 인증 실패도
        # HTTP 200 + return_code != 0 로 응답하므로 본문 코드를 반드시 확인해야 한다.
        payload = {
            "grant_type": "client_credentials",
            "appkey": self._appkey,
            "secretkey": self._secretkey,
        }

        last_error: Exception | None = None
        for attempt in range(1, _MAX_TOKEN_RETRIES + 1):
            try:
                logger.debug("Requesting access token (attempt %d/%d)", attempt, _MAX_TOKEN_RETRIES)
                response = httpx.post(f"{self._base_url}{OAUTH_TOKEN_URL}", json=payload, timeout=30)
                response.raise_for_status()
                token_data: dict[str, Any] = response.json()

                return_code = token_data.get("return_code")
                token = token_data.get("token")
                if (return_code not in (0, None)) or not token:
                    # 인증 실패(예: return_code=3) — 재시도해도 동일하므로 즉시 전파
                    raise TokenError(
                        token_data.get("return_msg") or "Kiwoom rejected the token request",
                        status_code=response.status_code,
                        response_body=token_data,
                    )

                self._token = token
                self._expires_at = _parse_token_expiry(token_data)
                logger.info("Access token obtained, valid until %s", self._expires_at)
                return
            except httpx.HTTPStatusError as e:
                last_error = e
                body = _safe_json(e.response)
                logger.warning(
                    "Token request failed (attempt %d): status=%d body=%s",
                    attempt,
                    e.response.status_code,
                    body,
                )
            except httpx.HTTPError as e:
                last_error = e
                logger.warning("Token request failed (attempt %d): %s", attempt, e)

            if attempt < _MAX_TOKEN_RETRIES:
                import time

                time.sleep(_RETRY_WAIT_SECONDS * attempt)

        final_status_code = None
        final_body: dict[str, Any] | str | None = None
        if isinstance(last_error, httpx.HTTPStatusError):
            final_status_code = last_error.response.status_code
            final_body = _safe_json(last_error.response)

        raise TokenError(
            f"Failed to obtain access token after {_MAX_TOKEN_RETRIES} attempts",
            status_code=final_status_code,
            response_body=final_body,
        )


def _parse_token_expiry(token_data: dict[str, Any]) -> datetime:
    """토큰 만료 시각 파싱.

    키움은 `expires_dt`('YYYYMMDDHHMMSS')로 만료를 준다. 없으면 `expires_in`(초),
    그것도 없으면 24시간을 기본값으로 쓴다.
    """
    raw = token_data.get("expires_dt")
    if isinstance(raw, str) and len(raw) == 14 and raw.isdigit():
        try:
            return datetime.strptime(raw, "%Y%m%d%H%M%S")
        except ValueError:
            pass
    try:
        return datetime.now() + timedelta(seconds=int(token_data.get("expires_in", 86400)))
    except (TypeError, ValueError):
        return datetime.now() + timedelta(seconds=86400)


def _safe_json(response: httpx.Response) -> dict[str, Any] | str:
    try:
        return response.json()  # type: ignore[no-any-return]
    except Exception:
        return response.text
