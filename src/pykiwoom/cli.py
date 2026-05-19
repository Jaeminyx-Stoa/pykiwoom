"""CLI tool for pykiwoom — query Kiwoom Securities OPEN API from the terminal.

Usage::

    # Set credentials (one-time)
    export KIWOOM_APPKEY="your_app_key"
    export KIWOOM_SECRETKEY="your_secret_key"

    # Commands
    pykiwoom price 005930              # 삼성전자 현재가
    pykiwoom balance                   # 잔고 조회
    pykiwoom portfolio                 # 포트폴리오 요약
    pykiwoom buy 005930 10 70000       # 삼성전자 10주 70000원 매수
    pykiwoom sell 005930 5 72000       # 삼성전자 5주 72000원 매도
    pykiwoom history 20250901 20250930 # 체결내역 조회
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pykiwoom",
        description="Kiwoom Securities (키움증권) OPEN API CLI",
    )
    parser.add_argument("--appkey", default=os.environ.get("KIWOOM_APPKEY"), help="App key (or set KIWOOM_APPKEY)")
    parser.add_argument(
        "--secretkey", default=os.environ.get("KIWOOM_SECRETKEY"), help="Secret key (or set KIWOOM_SECRETKEY)"
    )
    parser.add_argument("--mock", action="store_true", help="Use mock (paper-trading) server")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # price
    p_price = sub.add_parser("price", help="Get current stock price")
    p_price.add_argument("stock_code", help="Stock code (e.g., 005930)")

    # balance
    sub.add_parser("balance", help="Get account balance")

    # portfolio
    sub.add_parser("portfolio", help="Get portfolio summary")

    # buy
    p_buy = sub.add_parser("buy", help="Place a buy order")
    p_buy.add_argument("stock_code", help="Stock code")
    p_buy.add_argument("quantity", type=int, help="Number of shares")
    p_buy.add_argument("price", type=int, help="Order price")

    # sell
    p_sell = sub.add_parser("sell", help="Place a sell order")
    p_sell.add_argument("stock_code", help="Stock code")
    p_sell.add_argument("quantity", type=int, help="Number of shares")
    p_sell.add_argument("price", type=int, help="Order price")

    # history
    p_hist = sub.add_parser("history", help="Get execution history")
    p_hist.add_argument("start", help="Start date (YYYYMMDD)")
    p_hist.add_argument("end", help="End date (YYYYMMDD)")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if not args.appkey or not args.secretkey:
        print("Error: App key and secret key required.", file=sys.stderr)
        print("Set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables,", file=sys.stderr)
        print("or use --appkey and --secretkey flags.", file=sys.stderr)
        return 1

    from .client import PyKiwoom
    from .constants import MOCK, REAL

    host = MOCK if args.mock else REAL

    try:
        client = PyKiwoom(appkey=args.appkey, secretkey=args.secretkey, host=host)
    except Exception as e:
        print(f"Error: Failed to connect — {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "price":
            _cmd_price(client, args)
        elif args.command == "balance":
            _cmd_balance(client, args)
        elif args.command == "portfolio":
            _cmd_portfolio(client, args)
        elif args.command == "buy":
            _cmd_buy(client, args)
        elif args.command == "sell":
            _cmd_sell(client, args)
        elif args.command == "history":
            _cmd_history(client, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        client.close()

    return 0


def _cmd_price(client: Any, args: argparse.Namespace) -> None:
    price = client.domestic.price(args.stock_code)
    if args.as_json:
        print(json.dumps(price.raw, ensure_ascii=False, indent=2))
    else:
        sign = "+" if price.change >= 0 else ""
        print(f"{args.stock_code} {price.stock_name}")
        print(f"  Price:  {price.current_price:,.0f}")
        print(f"  Change: {sign}{price.change:,.0f} ({sign}{price.change_rate:.2f}%)")
        print(f"  Volume: {price.volume:,}")
        print(f"  High:   {price.high_price:,.0f}  Low: {price.low_price:,.0f}  Open: {price.open_price:,.0f}")


def _cmd_balance(client: Any, args: argparse.Namespace) -> None:
    bal = client.domestic.balance()
    if args.as_json:
        print(json.dumps(bal.raw, ensure_ascii=False, indent=2))
        return
    print("Balance")
    print(f"  Deposit:   {bal.deposit:>15,.0f} KRW")
    print(f"  Cash:      {bal.available_cash:>15,.0f} KRW")
    print(f"  Eval:      {bal.eval_total:>15,.0f} KRW")
    print(f"  P&L:       {bal.pnl_total:>15,.0f} KRW ({bal.pnl_rate:+.2f}%)")
    if bal.positions:
        print("  Positions:")
        for p in bal.positions:
            print(
                f"    {p.stock_code:8s} {p.stock_name:16s} {p.quantity:>5d}"
                f"  {p.eval_amount:>12,.0f}  P&L: {p.pnl_amount:>10,.0f}"
            )


def _cmd_portfolio(client: Any, args: argparse.Namespace) -> None:
    summary = client.portfolio_summary()
    if args.as_json:
        print(json.dumps(summary.model_dump(), ensure_ascii=False, indent=2, default=str))
        return
    print("Portfolio Summary")
    print(f"  Total NAV: {summary.total_nav:>15,.0f}")
    print(f"  Cash:      {summary.cash:>15,.0f}")
    print(f"  Profit:    {summary.profit:>15,.0f} ({summary.ror:+.2f}%)")
    if summary.positions:
        print(f"  Positions ({len(summary.positions)}):")
        for p in summary.positions:
            print(f"    {p.stock_code:8s} {p.stock_name:16s} {p.quantity:>5d}  P&L: {p.pnl_amount:>10,.0f}")


def _cmd_buy(client: Any, args: argparse.Namespace) -> None:
    result = client.domestic.buy(args.stock_code, args.quantity, args.price)
    if args.as_json:
        print(json.dumps(result.raw, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result.success else "FAILED"
        print(f"BUY {args.stock_code} x{args.quantity} @ {args.price:,} — {status}")
        if result.order_no:
            print(f"  Order#: {result.order_no}")
        if result.message:
            print(f"  Message: {result.message}")


def _cmd_sell(client: Any, args: argparse.Namespace) -> None:
    result = client.domestic.sell(args.stock_code, args.quantity, args.price)
    if args.as_json:
        print(json.dumps(result.raw, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result.success else "FAILED"
        print(f"SELL {args.stock_code} x{args.quantity} @ {args.price:,} — {status}")
        if result.order_no:
            print(f"  Order#: {result.order_no}")
        if result.message:
            print(f"  Message: {result.message}")


def _cmd_history(client: Any, args: argparse.Namespace) -> None:
    records = client.domestic.execution_history(args.start, args.end)
    if args.as_json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        print(f"Execution History ({args.start} ~ {args.end}): {len(records)} records")
        for r in records[:20]:
            print(f"  {json.dumps(r, ensure_ascii=False)}")
        if len(records) > 20:
            print(f"  ... and {len(records) - 20} more")


if __name__ == "__main__":
    sys.exit(main())
