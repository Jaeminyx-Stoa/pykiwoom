"""Order-related models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = ["OrderResult"]


class OrderResult(BaseModel):
    """Result of a buy/sell/cancel order."""

    success: bool = Field(description="Whether the order was accepted")
    order_no: str = Field(default="", description="Order number assigned by the exchange")
    message: str = Field(default="", description="Response message")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OrderResult:
        return_code = data.get("return_code", -1)
        return cls(
            success=return_code == 0,
            order_no=str(data.get("ord_no", data.get("order_no", ""))),
            message=str(data.get("return_msg", data.get("msg", ""))),
            raw=data,
        )
