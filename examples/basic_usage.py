"""Basic usage of pykiwoom — sync client."""

from pykiwoom import PyKiwoom, REAL

client = PyKiwoom(
    appkey="YOUR_APPKEY",
    secretkey="YOUR_SECRETKEY",
    host=REAL,
)

# Stock price
price = client.domestic.price("005930")
print(f"{price.stock_name}: {price.current_price:,.0f}원 ({price.change_rate}%)")

# Order book
ob = client.domestic.order_book("005930")
print(f"Best ask: {ob.asks[0].price:,.0f}  Best bid: {ob.bids[0].price:,.0f}")

# Balance
balance = client.domestic.balance()
print(f"Available cash: {balance.available_cash:,.0f}원")
for pos in balance.positions:
    print(f"  {pos.stock_name}: {pos.quantity}주, P&L {pos.pnl_rate}%")

client.close()
