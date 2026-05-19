"""Tests for input validation helpers."""

import pytest

from pykiwoom._validation import validate_date, validate_price, validate_quantity, validate_stock_code
from pykiwoom.exceptions import ValidationError


class TestValidateStockCode:
    def test_valid(self):
        validate_stock_code("005930")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_stock_code("")

    def test_whitespace_raises(self):
        with pytest.raises(ValidationError):
            validate_stock_code("   ")

    def test_non_string_raises(self):
        with pytest.raises(ValidationError):
            validate_stock_code(123)  # type: ignore[arg-type]


class TestValidateQuantity:
    def test_valid(self):
        validate_quantity(10)

    def test_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_quantity(0)

    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            validate_quantity(-1)

    def test_float_raises(self):
        with pytest.raises(ValidationError):
            validate_quantity(1.5)  # type: ignore[arg-type]


class TestValidatePrice:
    def test_valid(self):
        validate_price(70000)
        validate_price(0)
        validate_price(100.5)

    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            validate_price(-1)


class TestValidateDate:
    def test_valid(self):
        validate_date("20250901")

    def test_invalid_format_raises(self):
        with pytest.raises(ValidationError):
            validate_date("2025-09-01")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_date("")

    def test_empty_allowed(self):
        validate_date("", allow_empty=True)
