"""HTTP client with connection pooling, rate limiting, pagination, and token refresh."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from .auth import TokenManager
from .constants import BASE_URL, RETURN_CODE_TOKEN_EXPIRED
from .exceptions import APIError, RateLimitError
from .ratelimit import RateLimiter

logger = logging.getLogger("pykiwoom")

_MAX_CONTINUATION = 100
_CONTINUATION_DELAY = 0.25


class HTTPClient:
    """Synchronous HTTP client for Kiwoom REST API."""

    def __init__(
        self,
        token_manager: TokenManager,
        *,
        base_url: str = BASE_URL,
        timeout: float = 30,
        rate_limiter: RateLimiter | None = None,
    ):
        self._token_manager = token_manager
        self._base_url = base_url
        self._client = httpx.Client(base_url=base_url, timeout=timeout)
        self._rate_limiter = rate_limiter

    def request(
        self,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a single authenticated POST request.

        Args:
            endpoint: API endpoint path (e.g., "/api/dostk/price")
            api_id: API identifier (e.g., "ka10001")
            data: Request body payload
        """
        return self._do_request(endpoint, api_id, data)

    def request_until(
        self,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None = None,
        *,
        should_continue: Callable[[dict[str, Any]], bool] | None = None,
    ) -> dict[str, Any]:
        """Make paginated requests following cont-yn/next-key headers.

        Merges all list-typed fields across pages into a single dict.

        Args:
            endpoint: API endpoint path
            api_id: API identifier
            data: Request body payload
            should_continue: Callable that takes the response body and returns
                True to continue pagination, False to stop. Defaults to always continue.
        """
        if should_continue is None:
            def should_continue(_body: dict[str, Any]) -> bool:
                return True

        accumulated: dict[str, Any] | None = None
        next_key: str = ""

        for _ in range(_MAX_CONTINUATION):
            if self._rate_limiter:
                self._rate_limiter.wait()

            headers = self._build_headers(api_id)
            if next_key:
                headers["cont-yn"] = "Y"
                headers["next-key"] = next_key

            logger.debug("POST %s api_id=%s", endpoint, api_id)
            response = self._client.post(endpoint, json=data or {}, headers=headers)
            response = self._handle_token_expiry(response, endpoint, api_id, data, headers)
            self._raise_for_error(response, endpoint)

            body: dict[str, Any] = response.json()
            accumulated = _merge_page(body, accumulated)

            if not should_continue(body):
                break

            resp_cont_yn = response.headers.get("cont-yn", "N")
            next_key = response.headers.get("next-key", "")

            if resp_cont_yn != "Y" or not next_key:
                break

            time.sleep(_CONTINUATION_DELAY)

        return accumulated or {}

    def close(self) -> None:
        self._client.close()

    def _do_request(
        self,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if self._rate_limiter:
            self._rate_limiter.wait()

        headers = self._build_headers(api_id)
        logger.debug("POST %s api_id=%s data=%s", endpoint, api_id, data)

        response = self._client.post(endpoint, json=data or {}, headers=headers)
        response = self._handle_token_expiry(response, endpoint, api_id, data, headers)
        self._raise_for_error(response, endpoint)

        return response.json()  # type: ignore[no-any-return]

    def _build_headers(self, api_id: str) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": self._token_manager.authorization,
            "api-id": api_id,
        }

    def _handle_token_expiry(
        self,
        response: httpx.Response,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None,
        headers: dict[str, str],
    ) -> httpx.Response:
        body = _safe_json(response)
        if isinstance(body, dict) and body.get("return_code") == RETURN_CODE_TOKEN_EXPIRED:
            logger.info("Token expired (return_code=3), refreshing...")
            self._token_manager.refresh()
            headers["Authorization"] = self._token_manager.authorization
            time.sleep(1.0)
            return self._client.post(endpoint, json=data or {}, headers=headers)
        return response

    def _raise_for_error(self, response: httpx.Response, endpoint: str) -> None:
        if response.status_code >= 400:
            body = _safe_json(response)
            return_code = body.get("return_code") if isinstance(body, dict) else None
            raise _classify_error(
                endpoint=endpoint,
                status_code=response.status_code,
                return_code=return_code,
                response_body=body,
                retry_after=response.headers.get("Retry-After"),
            )


class AsyncHTTPClient:
    """Asynchronous HTTP client for Kiwoom REST API."""

    def __init__(
        self,
        token_manager: TokenManager,
        *,
        base_url: str = BASE_URL,
        timeout: float = 30,
        rate_limiter: RateLimiter | None = None,
    ):
        self._token_manager = token_manager
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._rate_limiter = rate_limiter

    async def request(
        self,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._do_request(endpoint, api_id, data)

    async def request_until(
        self,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None = None,
        *,
        should_continue: Callable[[dict[str, Any]], bool] | None = None,
    ) -> dict[str, Any]:
        import asyncio

        if should_continue is None:
            def should_continue(_body: dict[str, Any]) -> bool:
                return True

        accumulated: dict[str, Any] | None = None
        next_key: str = ""

        for _ in range(_MAX_CONTINUATION):
            if self._rate_limiter:
                await self._rate_limiter.async_wait()

            headers = self._build_headers(api_id)
            if next_key:
                headers["cont-yn"] = "Y"
                headers["next-key"] = next_key

            logger.debug("POST %s api_id=%s", endpoint, api_id)
            response = await self._client.post(endpoint, json=data or {}, headers=headers)
            response = await self._handle_token_expiry(response, endpoint, api_id, data, headers)
            self._raise_for_error(response, endpoint)

            body: dict[str, Any] = response.json()
            accumulated = _merge_page(body, accumulated)

            if not should_continue(body):
                break

            resp_cont_yn = response.headers.get("cont-yn", "N")
            next_key = response.headers.get("next-key", "")

            if resp_cont_yn != "Y" or not next_key:
                break

            await asyncio.sleep(_CONTINUATION_DELAY)

        return accumulated or {}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _do_request(
        self,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if self._rate_limiter:
            await self._rate_limiter.async_wait()

        headers = self._build_headers(api_id)
        logger.debug("POST %s api_id=%s data=%s", endpoint, api_id, data)

        response = await self._client.post(endpoint, json=data or {}, headers=headers)
        response = await self._handle_token_expiry(response, endpoint, api_id, data, headers)
        self._raise_for_error(response, endpoint)

        return response.json()  # type: ignore[no-any-return]

    def _build_headers(self, api_id: str) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": self._token_manager.authorization,
            "api-id": api_id,
        }

    async def _handle_token_expiry(
        self,
        response: httpx.Response,
        endpoint: str,
        api_id: str,
        data: dict[str, Any] | None,
        headers: dict[str, str],
    ) -> httpx.Response:
        import asyncio

        body = _safe_json(response)
        if isinstance(body, dict) and body.get("return_code") == RETURN_CODE_TOKEN_EXPIRED:
            logger.info("Token expired (return_code=3), refreshing...")
            await asyncio.to_thread(self._token_manager.refresh)
            headers["Authorization"] = self._token_manager.authorization
            await asyncio.sleep(1.0)
            return await self._client.post(endpoint, json=data or {}, headers=headers)
        return response

    def _raise_for_error(self, response: httpx.Response, endpoint: str) -> None:
        if response.status_code >= 400:
            body = _safe_json(response)
            return_code = body.get("return_code") if isinstance(body, dict) else None
            raise _classify_error(
                endpoint=endpoint,
                status_code=response.status_code,
                return_code=return_code,
                response_body=body,
                retry_after=response.headers.get("Retry-After"),
            )


def _merge_page(new_page: dict[str, Any], accumulated: dict[str, Any] | None) -> dict[str, Any]:
    """Merge a new page into the accumulated result.

    List-typed fields are concatenated; scalars are overwritten with the latest page.
    """
    if accumulated is None:
        return dict(new_page)

    merged = dict(accumulated)
    for key, value in new_page.items():
        if isinstance(value, list):
            existing = merged.get(key, [])
            merged[key] = existing + value if isinstance(existing, list) else value
        else:
            merged[key] = value
    return merged


def _classify_error(
    *,
    endpoint: str,
    status_code: int,
    return_code: int | None,
    response_body: dict[str, Any] | str | None,
    retry_after: str | None = None,
) -> APIError:
    msg = f"API request failed: {endpoint} (HTTP {status_code})"
    kwargs: dict[str, Any] = dict(status_code=status_code, return_code=return_code, response_body=response_body)

    if status_code == 429:
        ra = float(retry_after) if retry_after else None
        return RateLimitError(msg, retry_after=ra, **kwargs)
    return APIError(msg, **kwargs)


def _safe_json(response: httpx.Response) -> dict[str, Any] | str:
    try:
        return response.json()  # type: ignore[no-any-return]
    except Exception:
        return response.text
