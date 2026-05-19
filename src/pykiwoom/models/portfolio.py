"""Portfolio summary models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .balance import Position

__all__ = ["PortfolioSummary"]


class PortfolioSummary(BaseModel):
    """Portfolio summary across account positions."""

    total_nav: float = Field(default=0, description="Total Net Asset Value")
    cash: float = Field(default=0, description="Available cash")
    profit: float = Field(default=0, description="Total unrealized P&L")
    ror: float = Field(default=0, description="Rate of return (%)")
    positions: list[Position] = Field(default_factory=list, description="All positions")
