"""Quote (price, orderbook, chart) models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = ["StockPrice", "OrderBookLevel", "OrderBook", "ChartCandle", "ChartData"]


class StockPrice(BaseModel):
    """Current stock price information."""

    stock_code: str = Field(default="", description="Stock code")
    stock_name: str = Field(default="", description="Stock name")
    current_price: float = Field(default=0, description="Current price")
    change: float = Field(default=0, description="Price change from previous close")
    change_rate: float = Field(default=0, description="Change rate (%)")
    volume: int = Field(default=0, description="Trading volume")
    open_price: float = Field(default=0, description="Open price")
    high_price: float = Field(default=0, description="High price")
    low_price: float = Field(default=0, description="Low price")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StockPrice:
        return cls(
            stock_code=str(data.get("stk_cd", data.get("shcode", ""))),
            stock_name=str(data.get("stk_nm", data.get("hname", ""))),
            current_price=float(data.get("now_pric", data.get("price", 0)) or 0),
            change=float(data.get("change", data.get("diff", 0)) or 0),
            change_rate=float(data.get("change_rate", data.get("drate", 0)) or 0),
            volume=int(data.get("volume", data.get("vol", 0)) or 0),
            open_price=float(data.get("open_pric", data.get("open", 0)) or 0),
            high_price=float(data.get("high_pric", data.get("high", 0)) or 0),
            low_price=float(data.get("low_pric", data.get("low", 0)) or 0),
            raw=data,
        )


class OrderBookLevel(BaseModel):
    """Single price level in an order book."""

    price: float = Field(default=0, description="Price at this level")
    volume: int = Field(default=0, description="Volume at this level")


class OrderBook(BaseModel):
    """Order book (호가) data."""

    asks: list[OrderBookLevel] = Field(default_factory=list, description="Ask (sell) levels, best ask first")
    bids: list[OrderBookLevel] = Field(default_factory=list, description="Bid (buy) levels, best bid first")
    total_ask_volume: int = Field(default=0, description="Total ask volume")
    total_bid_volume: int = Field(default=0, description="Total bid volume")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data")

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OrderBook:
        asks: list[OrderBookLevel] = []
        bids: list[OrderBookLevel] = []

        for i in range(1, 11):
            ask_price = float(data.get(f"ask_pric{i}", data.get(f"offerho{i}", 0)) or 0)
            ask_vol = int(data.get(f"ask_qty{i}", data.get(f"offerrem{i}", 0)) or 0)
            if ask_price > 0 or ask_vol > 0:
                asks.append(OrderBookLevel(price=ask_price, volume=ask_vol))

            bid_price = float(data.get(f"bid_pric{i}", data.get(f"bidho{i}", 0)) or 0)
            bid_vol = int(data.get(f"bid_qty{i}", data.get(f"bidrem{i}", 0)) or 0)
            if bid_price > 0 or bid_vol > 0:
                bids.append(OrderBookLevel(price=bid_price, volume=bid_vol))

        return cls(
            asks=asks,
            bids=bids,
            total_ask_volume=int(data.get("tot_ask_qty", data.get("offer_tot", 0)) or 0),
            total_bid_volume=int(data.get("tot_bid_qty", data.get("bid_tot", 0)) or 0),
            raw=data,
        )


class ChartCandle(BaseModel):
    """Single OHLCV candle record."""

    datetime: str = Field(default="", description="Datetime (e.g., '20250901090100' for minute, '20250901' for day)")
    open: float = Field(default=0, description="Open price")
    high: float = Field(default=0, description="High price")
    low: float = Field(default=0, description="Low price")
    close: float = Field(default=0, description="Close price")
    volume: int = Field(default=0, description="Trading volume")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw candle data", exclude=True)

    @classmethod
    def from_api(cls, item: dict[str, Any]) -> ChartCandle:
        dt = str(item.get("cntr_tm", item.get("date", "")) or "")
        return cls(
            datetime=dt,
            open=float(item.get("open_pric", item.get("open", 0)) or 0),
            high=float(item.get("high_pric", item.get("high", 0)) or 0),
            low=float(item.get("low_pric", item.get("low", 0)) or 0),
            close=float(item.get("close_pric", item.get("close", 0)) or 0),
            volume=int(item.get("volume", item.get("vol", 0)) or 0),
            raw=item,
        )


class ChartData(BaseModel):
    """Chart data containing OHLCV candles."""

    candles: list[ChartCandle] = Field(default_factory=list, description="OHLCV candle records")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any], *, list_key: str = "") -> ChartData:
        items: list[dict[str, Any]] = []
        if list_key and list_key in data:
            items = data[list_key]
        else:
            for key in ("stk_min_pole_chart_qry", "stk_pole_chart_qry", "sect_min_pole_chart_qry",
                        "sect_pole_chart_qry", "chart", "list"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break

        candles = [ChartCandle.from_api(item) for item in items]
        return cls(candles=candles, raw=data)
