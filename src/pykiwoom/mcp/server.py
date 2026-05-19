"""MCP server exposing Kiwoom OPEN API as tools for AI assistants.

Usage:
    # Run directly
    pykiwoom-mcp

    # Claude Desktop config (claude_desktop_config.json)
    {
        "mcpServers": {
            "kiwoom": {
                "command": "pykiwoom-mcp",
                "env": {
                    "KIWOOM_APPKEY": "your_app_key",
                    "KIWOOM_SECRETKEY": "your_secret_key"
                }
            }
        }
    }
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from pykiwoom import PyKiwoom

mcp = FastMCP(
    "Kiwoom Securities",
    instructions=(
        "키움증권 OPEN API(REST)를 통해 국내 주식 시세 조회, 잔고 확인, 매수/매도 주문을 수행할 수 있습니다. "
        "환경변수 KIWOOM_APPKEY와 KIWOOM_SECRETKEY가 설정되어 있어야 합니다."
    ),
)


def _get_client() -> PyKiwoom:
    """Lazy-initialize PyKiwoom client from env vars."""
    from pykiwoom import PyKiwoom
    from pykiwoom.constants import MOCK, REAL

    appkey = os.environ.get("KIWOOM_APPKEY", "")
    secretkey = os.environ.get("KIWOOM_SECRETKEY", "")
    if not appkey or not secretkey:
        raise ValueError(
            "KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables are required. "
            "Get them from https://openapi.kiwoom.com"
        )
    host = MOCK if os.environ.get("KIWOOM_MOCK", "").lower() in ("1", "true", "yes") else REAL
    return PyKiwoom(appkey=appkey, secretkey=secretkey, host=host)


# ── Stock Price ──


@mcp.tool()
def get_stock_price(stock_code: str) -> str:
    """주식 현재가를 조회합니다.

    Args:
        stock_code: 종목코드 (예: "005930")
    """
    client = _get_client()
    try:
        price = client.domestic.price(stock_code)
        return json.dumps(
            {
                "stock_code": price.stock_code,
                "stock_name": price.stock_name,
                "current_price": price.current_price,
                "change": price.change,
                "change_rate": price.change_rate,
                "volume": price.volume,
                "high": price.high_price,
                "low": price.low_price,
                "open": price.open_price,
            },
            ensure_ascii=False,
        )
    finally:
        client.close()


# ── Balance ──


@mcp.tool()
def get_balance() -> str:
    """주식 잔고를 조회합니다."""
    client = _get_client()
    try:
        bal = client.domestic.balance()
        positions = [
            {
                "stock_code": p.stock_code,
                "stock_name": p.stock_name,
                "quantity": p.quantity,
                "current_price": p.current_price,
                "eval_amount": p.eval_amount,
                "pnl_amount": p.pnl_amount,
                "pnl_rate": p.pnl_rate,
            }
            for p in bal.positions
        ]
        return json.dumps(
            {
                "deposit": bal.deposit,
                "available_cash": bal.available_cash,
                "eval_total": bal.eval_total,
                "pnl_total": bal.pnl_total,
                "pnl_rate": bal.pnl_rate,
                "positions": positions,
            },
            ensure_ascii=False,
        )
    finally:
        client.close()


# ── Portfolio Summary ──


@mcp.tool()
def get_portfolio_summary() -> str:
    """포트폴리오 요약을 조회합니다."""
    client = _get_client()
    try:
        summary = client.portfolio_summary()
        return json.dumps(summary.model_dump(), ensure_ascii=False, default=str)
    finally:
        client.close()


# ── Order ──


@mcp.tool()
def place_order(
    stock_code: str,
    side: str,
    quantity: int,
    price: int,
) -> str:
    """주식 매수/매도 주문을 실행합니다. 실제 주문이 실행되므로 주의하세요.

    Args:
        stock_code: 종목코드 (예: "005930")
        side: "buy" 또는 "sell"
        quantity: 주문 수량
        price: 주문 가격
    """
    client = _get_client()
    try:
        if side == "buy":
            result = client.domestic.buy(stock_code, quantity, price)
        elif side == "sell":
            result = client.domestic.sell(stock_code, quantity, price)
        else:
            return json.dumps({"error": f"Invalid side: {side}. Must be 'buy' or 'sell'."})

        return json.dumps(
            {
                "success": result.success,
                "order_no": result.order_no,
                "message": result.message,
            },
            ensure_ascii=False,
        )
    finally:
        client.close()


# ── Order Book ──


@mcp.tool()
def get_order_book(stock_code: str) -> str:
    """호가(매수/매도 호가창)를 조회합니다.

    Args:
        stock_code: 종목코드
    """
    client = _get_client()
    try:
        ob = client.domestic.order_book(stock_code)
        return json.dumps(ob.raw, ensure_ascii=False)
    finally:
        client.close()


# ── Chart ──


@mcp.tool()
def get_chart(
    stock_code: str,
    period: str = "day",
    start: str = "",
    end: str = "",
) -> str:
    """주식 차트 데이터를 조회합니다.

    Args:
        stock_code: 종목코드 (ATS 통합코드 형식, 예: "005930_AL")
        period: "tick", "min", "day"
        start: 시작일 (YYYYMMDD)
        end: 종료일 (YYYYMMDD)
    """
    client = _get_client()
    try:
        data = client.domestic.chart(stock_code, period=period, start=start, end=end)
        candles = [c.model_dump() for c in data.candles[:100]]
        return json.dumps(
            {"count": len(data.candles), "candles": candles},
            ensure_ascii=False,
        )
    finally:
        client.close()


# ── Execution History ──


@mcp.tool()
def get_execution_history(start: str, end: str) -> str:
    """체결내역을 조회합니다.

    Args:
        start: 시작일 (YYYYMMDD)
        end: 종료일 (YYYYMMDD)
    """
    client = _get_client()
    try:
        records = client.domestic.execution_history(start, end)
        return json.dumps(
            {"count": len(records), "records": records[:100]},
            ensure_ascii=False,
        )
    finally:
        client.close()


def run_server() -> None:
    """Entry point for pykiwoom-mcp command."""
    mcp.run(transport="stdio")
