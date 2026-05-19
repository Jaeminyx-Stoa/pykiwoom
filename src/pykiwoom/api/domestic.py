"""Domestic (국내) market API operations for Kiwoom OPEN API."""

from __future__ import annotations

from typing import Any

from .._validation import validate_date, validate_price, validate_quantity, validate_stock_code
from ..constants import (
    API_BALANCE,
    API_BROKER_RANKING,
    API_CURRENT_PRICE,
    API_EXECUTION_HISTORY,
    API_ORDER_BUY,
    API_ORDER_CANCEL,
    API_ORDER_MODIFY,
    API_ORDER_SELL,
    API_ORDERABLE_QTY,
    API_ORDERBOOK,
    API_STOCK_INFO,
    API_TICKER_LIST,
    DOMESTIC_ACCOUNT,
    DOMESTIC_BROKER_RANKING,
    DOMESTIC_CHART_TICK,
    DOMESTIC_MODIFY_ORDER,
    DOMESTIC_ORDER,
    DOMESTIC_ORDERBOOK,
    DOMESTIC_PRICE,
    DOMESTIC_STOCK_INFO,
    DOMESTIC_TICKER_LIST,
)
from ..http import AsyncHTTPClient, HTTPClient
from ..models.balance import Balance
from ..models.order import OrderResult
from ..models.quote import ChartData, OrderBook, StockPrice


class DomesticAPI:
    """Domestic (국내) market operations — sync."""

    def __init__(self, http: HTTPClient):
        self._http = http

    # ── Trading ──

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        *,
        order_type: str = "00",
    ) -> OrderResult:
        """Place a buy order.

        Args:
            stock_code: Stock code (e.g., "005930")
            quantity: Number of shares to buy
            price: Order price. 0 for market order.
            order_type: "00"=limit (default), "03"=market
        """
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        validate_price(price)
        data = {
            "stk_cd": stock_code,
            "ord_qty": quantity,
            "ord_pric": price,
            "ord_tp": order_type,
        }
        result = self._http.request(DOMESTIC_ORDER, API_ORDER_BUY, data)
        return OrderResult.from_api(result)

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        *,
        order_type: str = "00",
    ) -> OrderResult:
        """Place a sell order.

        Args:
            stock_code: Stock code (e.g., "005930")
            quantity: Number of shares to sell
            price: Order price. 0 for market order.
            order_type: "00"=limit (default), "03"=market
        """
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        validate_price(price)
        data = {
            "stk_cd": stock_code,
            "ord_qty": quantity,
            "ord_pric": price,
            "ord_tp": order_type,
        }
        result = self._http.request(DOMESTIC_ORDER, API_ORDER_SELL, data)
        return OrderResult.from_api(result)

    def modify(
        self,
        order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
    ) -> OrderResult:
        """Modify an existing order.

        Args:
            order_no: Original order number
            stock_code: Stock code
            quantity: New quantity
            price: New price
        """
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        data = {
            "org_ord_no": order_no,
            "stk_cd": stock_code,
            "ord_qty": quantity,
            "ord_pric": price,
        }
        result = self._http.request(DOMESTIC_MODIFY_ORDER, API_ORDER_MODIFY, data)
        return OrderResult.from_api(result)

    def cancel(self, order_no: str, stock_code: str, quantity: int) -> OrderResult:
        """Cancel an existing order.

        Args:
            order_no: Original order number
            stock_code: Stock code
            quantity: Quantity to cancel
        """
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        data = {
            "org_ord_no": order_no,
            "stk_cd": stock_code,
            "ord_qty": quantity,
        }
        result = self._http.request(DOMESTIC_MODIFY_ORDER, API_ORDER_CANCEL, data)
        return OrderResult.from_api(result)

    # ── Balance & Account ──

    def balance(self) -> Balance:
        """Get domestic stock balance (잔고조회)."""
        result = self._http.request_until(DOMESTIC_ACCOUNT, API_BALANCE)
        return Balance.from_api(result)

    def execution_history(self, start: str, end: str) -> list[dict[str, Any]]:
        """Get execution history (체결내역) for a date range.

        Args:
            start: Start date (YYYYMMDD)
            end: End date (YYYYMMDD)
        """
        validate_date(start, label="start")
        validate_date(end, label="end")
        data = {"start_dt": start, "end_dt": end}
        result = self._http.request_until(DOMESTIC_ACCOUNT, API_EXECUTION_HISTORY, data)
        for key in ("exec_list", "list"):
            if key in result and isinstance(result[key], list):
                return result[key]  # type: ignore[no-any-return]
        return []

    def orderable_quantity(self, stock_code: str, price: int) -> dict[str, Any]:
        """Get orderable quantity for a stock.

        Args:
            stock_code: Stock code
            price: Order price
        """
        validate_stock_code(stock_code)
        validate_price(price)
        data = {"stk_cd": stock_code, "ord_pric": price}
        return self._http.request(DOMESTIC_ACCOUNT, API_ORDERABLE_QTY, data)

    # ── Quote ──

    def price(self, stock_code: str) -> StockPrice:
        """Get current stock price (현재가).

        Args:
            stock_code: Stock code (e.g., "005930")
        """
        validate_stock_code(stock_code)
        data = {"stk_cd": stock_code}
        result = self._http.request(DOMESTIC_PRICE, API_CURRENT_PRICE, data)
        return StockPrice.from_api(result)

    def order_book(self, stock_code: str) -> OrderBook:
        """Get order book (호가).

        Args:
            stock_code: Stock code (e.g., "005930")
        """
        validate_stock_code(stock_code)
        data = {"stk_cd": stock_code}
        result = self._http.request(DOMESTIC_ORDERBOOK, API_ORDERBOOK, data)
        return OrderBook.from_api(result)

    def stock_info(self, stock_code: str) -> dict[str, Any]:
        """Get stock info (종목정보).

        Args:
            stock_code: Stock code (e.g., "005930")
        """
        validate_stock_code(stock_code)
        data = {"mrkt_tp": "0", "stk_cd": stock_code}
        return self._http.request(DOMESTIC_STOCK_INFO, API_STOCK_INFO, data)

    def tickers(self, *, market_type: str = "0") -> list[dict[str, Any]]:
        """Get stock tickers list (종목리스트).

        Args:
            market_type: "0"=all (default)
        """
        data = {"mrkt_tp": market_type}
        result = self._http.request_until(DOMESTIC_TICKER_LIST, API_TICKER_LIST, data)
        for key in ("stk_list", "list"):
            if key in result and isinstance(result[key], list):
                return result[key]  # type: ignore[no-any-return]
        return []

    def broker_ranking(
        self,
        broker_code: str,
        *,
        trade_type: str = "1",
        period: str = "0",
        exchange: str = "3",
    ) -> list[dict[str, Any]]:
        """Get broker trading ranking (증권사별매매상위).

        Args:
            broker_code: Broker code (e.g., "063" for eBest)
            trade_type: "1"=net buy, "2"=net sell
            period: "0"=today
            exchange: "3"=all
        """
        data = {
            "mmcm_cd": broker_code,
            "trde_qty_tp": "0",
            "trde_tp": trade_type,
            "dt": period,
            "stex_tp": exchange,
        }
        result = self._http.request_until(DOMESTIC_BROKER_RANKING, API_BROKER_RANKING, data)
        for key in ("sec_trde_upper", "list"):
            if key in result and isinstance(result[key], list):
                return result[key]  # type: ignore[no-any-return]
        return []

    # ── Chart ──

    def chart(
        self,
        stock_code: str,
        *,
        period: str = "day",
        start: str = "",
        end: str = "",
    ) -> ChartData:
        """Get chart data (차트).

        Args:
            stock_code: Stock code (uses ATS unified code format, e.g., "005930_AL")
            period: "tick", "min", "day"
            start: Start date (YYYYMMDD)
            end: End date (YYYYMMDD)
        """
        validate_stock_code(stock_code)
        if start:
            validate_date(start, label="start")
        if end:
            validate_date(end, label="end")

        api_id = _chart_api_id(period)
        data: dict[str, Any] = {"code": stock_code}
        if start:
            data["start"] = start
        if end:
            data["end"] = end

        list_key = _chart_list_key(period, ctype="stock")
        result = self._http.request_until(DOMESTIC_CHART_TICK, api_id, data)
        return ChartData.from_api(result, list_key=list_key)


class AsyncDomesticAPI:
    """Domestic (국내) market operations — async."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    async def buy(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        *,
        order_type: str = "00",
    ) -> OrderResult:
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        validate_price(price)
        data = {
            "stk_cd": stock_code,
            "ord_qty": quantity,
            "ord_pric": price,
            "ord_tp": order_type,
        }
        result = await self._http.request(DOMESTIC_ORDER, API_ORDER_BUY, data)
        return OrderResult.from_api(result)

    async def sell(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        *,
        order_type: str = "00",
    ) -> OrderResult:
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        validate_price(price)
        data = {
            "stk_cd": stock_code,
            "ord_qty": quantity,
            "ord_pric": price,
            "ord_tp": order_type,
        }
        result = await self._http.request(DOMESTIC_ORDER, API_ORDER_SELL, data)
        return OrderResult.from_api(result)

    async def modify(
        self,
        order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
    ) -> OrderResult:
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        data = {
            "org_ord_no": order_no,
            "stk_cd": stock_code,
            "ord_qty": quantity,
            "ord_pric": price,
        }
        result = await self._http.request(DOMESTIC_MODIFY_ORDER, API_ORDER_MODIFY, data)
        return OrderResult.from_api(result)

    async def cancel(self, order_no: str, stock_code: str, quantity: int) -> OrderResult:
        validate_stock_code(stock_code)
        validate_quantity(quantity)
        data = {
            "org_ord_no": order_no,
            "stk_cd": stock_code,
            "ord_qty": quantity,
        }
        result = await self._http.request(DOMESTIC_MODIFY_ORDER, API_ORDER_CANCEL, data)
        return OrderResult.from_api(result)

    async def balance(self) -> Balance:
        result = await self._http.request_until(DOMESTIC_ACCOUNT, API_BALANCE)
        return Balance.from_api(result)

    async def execution_history(self, start: str, end: str) -> list[dict[str, Any]]:
        validate_date(start, label="start")
        validate_date(end, label="end")
        data = {"start_dt": start, "end_dt": end}
        result = await self._http.request_until(DOMESTIC_ACCOUNT, API_EXECUTION_HISTORY, data)
        for key in ("exec_list", "list"):
            if key in result and isinstance(result[key], list):
                return result[key]  # type: ignore[no-any-return]
        return []

    async def orderable_quantity(self, stock_code: str, price: int) -> dict[str, Any]:
        validate_stock_code(stock_code)
        validate_price(price)
        data = {"stk_cd": stock_code, "ord_pric": price}
        return await self._http.request(DOMESTIC_ACCOUNT, API_ORDERABLE_QTY, data)

    async def price(self, stock_code: str) -> StockPrice:
        validate_stock_code(stock_code)
        data = {"stk_cd": stock_code}
        result = await self._http.request(DOMESTIC_PRICE, API_CURRENT_PRICE, data)
        return StockPrice.from_api(result)

    async def order_book(self, stock_code: str) -> OrderBook:
        validate_stock_code(stock_code)
        data = {"stk_cd": stock_code}
        result = await self._http.request(DOMESTIC_ORDERBOOK, API_ORDERBOOK, data)
        return OrderBook.from_api(result)

    async def stock_info(self, stock_code: str) -> dict[str, Any]:
        validate_stock_code(stock_code)
        data = {"mrkt_tp": "0", "stk_cd": stock_code}
        return await self._http.request(DOMESTIC_STOCK_INFO, API_STOCK_INFO, data)

    async def tickers(self, *, market_type: str = "0") -> list[dict[str, Any]]:
        data = {"mrkt_tp": market_type}
        result = await self._http.request_until(DOMESTIC_TICKER_LIST, API_TICKER_LIST, data)
        for key in ("stk_list", "list"):
            if key in result and isinstance(result[key], list):
                return result[key]  # type: ignore[no-any-return]
        return []

    async def broker_ranking(
        self,
        broker_code: str,
        *,
        trade_type: str = "1",
        period: str = "0",
        exchange: str = "3",
    ) -> list[dict[str, Any]]:
        data = {
            "mmcm_cd": broker_code,
            "trde_qty_tp": "0",
            "trde_tp": trade_type,
            "dt": period,
            "stex_tp": exchange,
        }
        result = await self._http.request_until(DOMESTIC_BROKER_RANKING, API_BROKER_RANKING, data)
        for key in ("sec_trde_upper", "list"):
            if key in result and isinstance(result[key], list):
                return result[key]  # type: ignore[no-any-return]
        return []

    async def chart(
        self,
        stock_code: str,
        *,
        period: str = "day",
        start: str = "",
        end: str = "",
    ) -> ChartData:
        validate_stock_code(stock_code)
        if start:
            validate_date(start, label="start")
        if end:
            validate_date(end, label="end")

        api_id = _chart_api_id(period)
        data: dict[str, Any] = {"code": stock_code}
        if start:
            data["start"] = start
        if end:
            data["end"] = end

        list_key = _chart_list_key(period, ctype="stock")
        result = await self._http.request_until(DOMESTIC_CHART_TICK, api_id, data)
        return ChartData.from_api(result, list_key=list_key)


# ── Helpers ──


def _chart_api_id(period: str) -> str:
    from ..constants import API_CHART_DAY, API_CHART_MINUTE, API_CHART_TICK

    mapping = {
        "tick": API_CHART_TICK,
        "min": API_CHART_MINUTE,
        "day": API_CHART_DAY,
    }
    if period not in mapping:
        from ..exceptions import ValidationError

        raise ValidationError(f"Invalid period: {period!r}. Must be 'tick', 'min', or 'day'.")
    return mapping[period]


def _chart_list_key(period: str, *, ctype: str = "stock") -> str:
    if ctype == "stock":
        if period == "tick":
            return "stk_tick_pole_chart_qry"
        elif period == "min":
            return "stk_min_pole_chart_qry"
        else:
            return "stk_pole_chart_qry"
    else:
        if period == "tick":
            return "sect_tick_pole_chart_qry"
        elif period == "min":
            return "sect_min_pole_chart_qry"
        else:
            return "sect_pole_chart_qry"
