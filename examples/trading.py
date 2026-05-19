"""Trading example — buy, sell, check execution history."""

from pykiwoom import PyKiwoom, MOCK

# Use MOCK server for testing
client = PyKiwoom(
    appkey="YOUR_APPKEY",
    secretkey="YOUR_SECRETKEY",
    host=MOCK,
)

# Buy order
buy = client.domestic.buy("005930", quantity=10, price=70000)
print(f"Buy order: {'Success' if buy.success else 'Failed'} — {buy.message}")
if buy.order_no:
    print(f"  Order no: {buy.order_no}")

# Sell order
sell = client.domestic.sell("005930", quantity=5, price=72000)
print(f"Sell order: {'Success' if sell.success else 'Failed'} — {sell.message}")

# Execution history
records = client.domestic.execution_history("20250501", "20250519")
print(f"\nExecution history: {len(records)} records")

client.close()
