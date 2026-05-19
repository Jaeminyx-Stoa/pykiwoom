"""Balance response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = ["Position", "Balance"]


class Position(BaseModel):
    """A single stock position."""

    stock_code: str = Field(default="", description="Stock code")
    stock_name: str = Field(default="", description="Stock name")
    quantity: int = Field(default=0, description="Holding quantity")
    current_price: float = Field(default=0, description="Current price")
    purchase_price: float = Field(default=0, description="Average purchase price")
    purchase_amount: float = Field(default=0, description="Total purchase amount")
    eval_amount: float = Field(default=0, description="Current evaluation amount")
    pnl_amount: float = Field(default=0, description="Unrealized P&L amount")
    pnl_rate: float = Field(default=0, description="Unrealized P&L rate (%)")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Position:
        return cls(
            stock_code=str(data.get("stk_cd", data.get("shcode", ""))),
            stock_name=str(data.get("stk_nm", data.get("hname", ""))),
            quantity=int(data.get("hold_qty", data.get("janqty", 0)) or 0),
            current_price=float(data.get("now_pric", data.get("price", 0)) or 0),
            purchase_price=float(data.get("avg_pric", data.get("pamt", 0)) or 0),
            purchase_amount=float(data.get("buy_amt", data.get("mamt", 0)) or 0),
            eval_amount=float(data.get("eval_amt", data.get("appamt", 0)) or 0),
            pnl_amount=float(data.get("pnl_amt", data.get("dtsunik", 0)) or 0),
            pnl_rate=float(data.get("pnl_rate", data.get("sunikrt", 0)) or 0),
            raw=data,
        )


class Balance(BaseModel):
    """Account balance summary."""

    deposit: float = Field(default=0, description="Total deposit amount")
    available_cash: float = Field(default=0, description="Available cash for orders")
    eval_total: float = Field(default=0, description="Total evaluation amount")
    pnl_total: float = Field(default=0, description="Total unrealized P&L")
    pnl_rate: float = Field(default=0, description="Total P&L rate (%)")
    positions: list[Position] = Field(default_factory=list, description="Stock positions")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any], *, list_key: str = "") -> Balance:
        positions_data: list[dict[str, Any]] = []
        if list_key and list_key in data:
            positions_data = data[list_key]
        else:
            for key in ("balance", "janko", "list"):
                if key in data and isinstance(data[key], list):
                    positions_data = data[key]
                    break

        return cls(
            deposit=float(data.get("deposit", data.get("sunamt", 0)) or 0),
            available_cash=float(data.get("ord_able_amt", data.get("mamt", 0)) or 0),
            eval_total=float(data.get("eval_tot", data.get("appamt", 0)) or 0),
            pnl_total=float(data.get("pnl_tot", data.get("dtsunik", 0)) or 0),
            pnl_rate=float(data.get("pnl_rate", data.get("sunikrt", 0)) or 0),
            positions=[Position.from_api(p) for p in positions_data],
            raw=data,
        )
