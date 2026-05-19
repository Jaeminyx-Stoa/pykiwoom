"""MCP helper utilities for pykiwoom.

1. Anthropic SDK integration — use pykiwoom MCP tools with anthropic tool runner
2. Client helpers — easily connect to pykiwoom MCP server from any app
3. Response parsing — convert MCP tool results to pykiwoom Pydantic models
"""

from __future__ import annotations

import json
from typing import Any

from ..models.balance import Balance, Position
from ..models.order import OrderResult
from ..models.quote import OrderBook, StockPrice


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Get pykiwoom tools as Anthropic API tool definitions.

    Use with `client.messages.create(tools=get_anthropic_tools())`.

    Example::

        import anthropic
        from pykiwoom.mcp.helpers import get_anthropic_tools

        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=get_anthropic_tools(),
            messages=[{"role": "user", "content": "삼성전자 현재가 알려줘"}],
        )
    """
    return [
        {
            "name": "get_stock_price",
            "description": "주식 현재가를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드 (예: '005930')"},
                },
                "required": ["stock_code"],
            },
        },
        {
            "name": "get_balance",
            "description": "주식 잔고를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_portfolio_summary",
            "description": "포트폴리오 요약을 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "place_order",
            "description": "주식 매수/매도 주문을 실행합니다. 실제 주문이므로 주의.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드"},
                    "side": {"type": "string", "enum": ["buy", "sell"], "description": "매수/매도"},
                    "quantity": {"type": "integer", "description": "주문 수량"},
                    "price": {"type": "integer", "description": "주문 가격"},
                },
                "required": ["stock_code", "side", "quantity", "price"],
            },
        },
        {
            "name": "get_order_book",
            "description": "호가(매수/매도 호가창)를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드"},
                },
                "required": ["stock_code"],
            },
        },
        {
            "name": "get_chart",
            "description": "주식 차트 데이터를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드"},
                    "period": {"type": "string", "enum": ["tick", "min", "day"], "default": "day"},
                    "start": {"type": "string", "description": "YYYYMMDD", "default": ""},
                    "end": {"type": "string", "description": "YYYYMMDD", "default": ""},
                },
                "required": ["stock_code"],
            },
        },
        {
            "name": "get_execution_history",
            "description": "체결내역을 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "시작일 YYYYMMDD"},
                    "end": {"type": "string", "description": "종료일 YYYYMMDD"},
                },
                "required": ["start", "end"],
            },
        },
    ]


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Execute a pykiwoom MCP tool locally (without MCP transport).

    Use this as the tool executor in an Anthropic API agentic loop.
    """
    from .server import (
        get_balance,
        get_chart,
        get_execution_history,
        get_order_book,
        get_portfolio_summary,
        get_stock_price,
        place_order,
    )

    executors: dict[str, Any] = {
        "get_stock_price": get_stock_price,
        "get_balance": get_balance,
        "get_portfolio_summary": get_portfolio_summary,
        "place_order": place_order,
        "get_order_book": get_order_book,
        "get_chart": get_chart,
        "get_execution_history": get_execution_history,
    }

    executor = executors.get(tool_name)
    if executor is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        result: str = executor(**tool_input)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


class KiwoomMCPClient:
    """Helper to connect to pykiwoom MCP server from any application.

    Example::

        from pykiwoom.mcp.helpers import KiwoomMCPClient

        async with KiwoomMCPClient(appkey="...", secretkey="...") as client:
            price = await client.get_stock_price("005930")
            print(price.current_price)
    """

    def __init__(
        self,
        appkey: str,
        secretkey: str,
        *,
        command: str = "pykiwoom-mcp",
        mock: bool = False,
    ):
        self._appkey = appkey
        self._secretkey = secretkey
        self._command = command
        self._mock = mock
        self._session: Any = None
        self._read: Any = None
        self._write: Any = None
        self._cm: Any = None

    async def connect(self) -> None:
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client

        env = {"KIWOOM_APPKEY": self._appkey, "KIWOOM_SECRETKEY": self._secretkey}
        if self._mock:
            env["KIWOOM_MOCK"] = "1"

        params = StdioServerParameters(command=self._command, env=env)
        self._cm = stdio_client(params)
        self._read, self._write = await self._cm.__aenter__()
        self._session = ClientSession(self._read, self._write)
        await self._session.__aenter__()
        await self._session.initialize()

    async def disconnect(self) -> None:
        if self._session:
            await self._session.__aexit__(None, None, None)
        if self._cm:
            await self._cm.__aexit__(None, None, None)

    async def call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        if not self._session:
            raise RuntimeError("Not connected. Call connect() first.")
        result = await self._session.call_tool(tool_name, kwargs)
        text = result.content[0].text if result.content else "{}"
        return json.loads(text)  # type: ignore[no-any-return]

    async def get_stock_price(self, stock_code: str) -> StockPrice:
        data = await self.call("get_stock_price", stock_code=stock_code)
        return parse_stock_price(data)

    async def get_balance(self) -> Balance:
        data = await self.call("get_balance")
        return parse_balance(data)

    async def place_order(self, stock_code: str, side: str, quantity: int, price: int) -> OrderResult:
        data = await self.call(
            "place_order", stock_code=stock_code, side=side, quantity=quantity, price=price
        )
        return parse_order_result(data)

    async def __aenter__(self) -> KiwoomMCPClient:
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.disconnect()


# ── Response parsing ──


def _ensure_dict(data: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(data, str):
        return json.loads(data)  # type: ignore[no-any-return]
    return data


def parse_stock_price(data: dict[str, Any] | str) -> StockPrice:
    """Parse MCP tool result into a StockPrice model."""
    d = _ensure_dict(data)
    return StockPrice(
        stock_code=d.get("stock_code", ""),
        stock_name=d.get("stock_name", ""),
        current_price=d.get("current_price", 0),
        change=d.get("change", 0),
        change_rate=d.get("change_rate", 0),
        volume=d.get("volume", 0),
        open_price=d.get("open", 0),
        high_price=d.get("high", 0),
        low_price=d.get("low", 0),
        raw=d,
    )


def parse_balance(data: dict[str, Any] | str) -> Balance:
    """Parse MCP tool result into a Balance model."""
    d = _ensure_dict(data)
    positions_data = d.get("positions", [])
    positions = [
        Position(
            stock_code=p.get("stock_code", ""),
            stock_name=p.get("stock_name", ""),
            quantity=p.get("quantity", 0),
            current_price=p.get("current_price", 0),
            eval_amount=p.get("eval_amount", 0),
            pnl_amount=p.get("pnl_amount", 0),
            pnl_rate=p.get("pnl_rate", 0),
        )
        for p in positions_data
    ]
    return Balance(
        deposit=d.get("deposit", 0),
        available_cash=d.get("available_cash", 0),
        eval_total=d.get("eval_total", 0),
        pnl_total=d.get("pnl_total", 0),
        pnl_rate=d.get("pnl_rate", 0),
        positions=positions,
        raw=d,
    )


def parse_order_result(data: dict[str, Any] | str) -> OrderResult:
    """Parse MCP tool result into an OrderResult model."""
    d = _ensure_dict(data)
    return OrderResult(
        success=d.get("success", False),
        order_no=d.get("order_no", ""),
        message=d.get("message", ""),
        raw=d,
    )


def parse_order_book(data: dict[str, Any] | str) -> OrderBook:
    """Parse MCP tool result into an OrderBook model."""
    d = _ensure_dict(data)
    return OrderBook.from_api(d)
