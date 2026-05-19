"""Input validation helpers."""

from __future__ import annotations

import re

from .exceptions import ValidationError

_DATE_RE = re.compile(r"^\d{8}$")


def validate_stock_code(code: str, label: str = "stock_code") -> None:
    if not isinstance(code, str) or not code.strip():
        raise ValidationError(f"{label} must be a non-empty string, got {code!r}")


def validate_quantity(qty: int) -> None:
    if not isinstance(qty, int) or qty <= 0:
        raise ValidationError(f"quantity must be a positive integer, got {qty!r}")


def validate_price(price: float) -> None:
    if not isinstance(price, int | float) or price < 0:
        raise ValidationError(f"price must be a non-negative number, got {price!r}")


def validate_date(date: str, *, label: str = "date", allow_empty: bool = False) -> None:
    if allow_empty and date == "":
        return
    if not isinstance(date, str) or not _DATE_RE.match(date):
        raise ValidationError(f"{label} must be in YYYYMMDD format, got {date!r}")
