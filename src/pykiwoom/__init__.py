"""pykiwoom — Python wrapper for Kiwoom Securities (키움증권) OPEN API (REST).

Usage::

    from pykiwoom import PyKiwoom, REAL, MOCK

    client = PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL)

    # Get current price
    price = client.domestic.price("005930")

    # Get balance
    balance = client.domestic.balance()

    # Place buy order
    result = client.domestic.buy("005930", quantity=10, price=70000)

    # Close session
    client.close()
"""

from .client import AsyncPyKiwoom, PyKiwoom
from .constants import MOCK, REAL
from .exceptions import (
    APIError,
    InsufficientBalanceError,
    InvalidOrderError,
    PyKiwoomError,
    RateLimitError,
    TokenError,
    TokenExpiredError,
    ValidationError,
    WebSocketError,
)

__all__ = [
    "PyKiwoom",
    "AsyncPyKiwoom",
    "REAL",
    "MOCK",
    "PyKiwoomError",
    "TokenError",
    "TokenExpiredError",
    "APIError",
    "RateLimitError",
    "InvalidOrderError",
    "InsufficientBalanceError",
    "WebSocketError",
    "ValidationError",
]

__version__ = "0.1.0"
