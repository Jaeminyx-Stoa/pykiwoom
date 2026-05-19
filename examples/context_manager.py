"""Using context manager for automatic resource cleanup."""

from pykiwoom import PyKiwoom, REAL

with PyKiwoom(
    appkey="YOUR_APPKEY",
    secretkey="YOUR_SECRETKEY",
    host=REAL,
) as client:
    # Client is automatically cleaned up when exiting the block
    price = client.domestic.price("005930")
    print(f"{price.stock_name}: {price.current_price:,.0f}원")

    summary = client.portfolio_summary()
    print(f"Total eval: {summary.eval_total:,.0f}원, P&L: {summary.pnl_rate}%")
