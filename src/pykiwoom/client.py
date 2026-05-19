"""Main client classes for pykiwoom."""

from __future__ import annotations

import logging
from datetime import datetime

from .api.domestic import AsyncDomesticAPI, DomesticAPI
from .auth import TokenManager
from .constants import REAL
from .http import AsyncHTTPClient, HTTPClient
from .models.balance import Balance
from .models.portfolio import PortfolioSummary
from .ratelimit import RateLimiter


class PyKiwoom:
    """Synchronous client for Kiwoom Securities OPEN API (REST).

    Usage::

        from pykiwoom import PyKiwoom

        client = PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET")

        # Get current price
        price = client.domestic.price("005930")

        # Place buy order
        result = client.domestic.buy("005930", quantity=10, price=70000)

        # Get balance
        balance = client.domestic.balance()

        # Close session
        client.close()
    """

    def __init__(
        self,
        appkey: str,
        secretkey: str,
        *,
        token: str | None = None,
        expires_at: datetime | None = None,
        host: str = REAL,
        timeout: float = 30,
        rate_limit: bool = True,
        log_level: int | None = None,
    ):
        """Initialize PyKiwoom client.

        Args:
            appkey: Kiwoom API app key (string or file path)
            secretkey: Kiwoom API secret key (string or file path)
            token: Existing access token (optional, for reuse)
            expires_at: Token expiration datetime
            host: API host (REAL or MOCK)
            timeout: HTTP request timeout in seconds
            rate_limit: Enable API rate limiting (default: True)
            log_level: Set pykiwoom logger level (e.g., logging.DEBUG)
        """
        if log_level is not None:
            _configure_logging(log_level)

        self._host = host
        self._token_manager = TokenManager(
            appkey,
            secretkey,
            base_url=host,
            token=token,
            expires_at=expires_at,
        )
        rate_limiter = RateLimiter(host, enabled=rate_limit)
        self._http = HTTPClient(self._token_manager, base_url=host, timeout=timeout, rate_limiter=rate_limiter)

        self.domestic = DomesticAPI(self._http)

    @property
    def token(self) -> str:
        """Current access token."""
        return self._token_manager.token

    @property
    def expires_at(self) -> datetime | None:
        """Token expiration datetime."""
        return self._token_manager.expires_at

    def portfolio_summary(self) -> PortfolioSummary:
        """Get a portfolio summary from domestic balance."""
        bal = self.domestic.balance()
        return _build_portfolio(bal)

    def close(self) -> None:
        """Close the connection pool."""
        self._http.close()

    def __enter__(self) -> PyKiwoom:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncPyKiwoom:
    """Asynchronous client for Kiwoom Securities OPEN API (REST).

    Usage::

        from pykiwoom import AsyncPyKiwoom

        async def main():
            async with AsyncPyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET") as client:
                price = await client.domestic.price("005930")
                balance = await client.domestic.balance()
    """

    def __init__(
        self,
        appkey: str,
        secretkey: str,
        *,
        token: str | None = None,
        expires_at: datetime | None = None,
        host: str = REAL,
        timeout: float = 30,
        rate_limit: bool = True,
        log_level: int | None = None,
    ):
        if log_level is not None:
            _configure_logging(log_level)

        self._host = host
        self._token_manager = TokenManager(
            appkey,
            secretkey,
            base_url=host,
            token=token,
            expires_at=expires_at,
        )
        rate_limiter = RateLimiter(host, enabled=rate_limit)
        self._http = AsyncHTTPClient(self._token_manager, base_url=host, timeout=timeout, rate_limiter=rate_limiter)

        self.domestic = AsyncDomesticAPI(self._http)

    @property
    def token(self) -> str:
        return self._token_manager.token

    @property
    def expires_at(self) -> datetime | None:
        return self._token_manager.expires_at

    async def portfolio_summary(self) -> PortfolioSummary:
        bal = await self.domestic.balance()
        return _build_portfolio(bal)

    async def aclose(self) -> None:
        await self._http.aclose()

    def close(self) -> None:
        pass

    async def __aenter__(self) -> AsyncPyKiwoom:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()


def _build_portfolio(bal: Balance) -> PortfolioSummary:
    return PortfolioSummary(
        total_nav=bal.eval_total,
        cash=bal.available_cash,
        profit=bal.pnl_total,
        ror=bal.pnl_rate,
        positions=list(bal.positions),
    )


def _configure_logging(level: int) -> None:
    logger = logging.getLogger("pykiwoom")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
