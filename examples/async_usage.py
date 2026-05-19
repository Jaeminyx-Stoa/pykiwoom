"""Async usage of pykiwoom — concurrent API calls."""

import asyncio

from pykiwoom import AsyncPyKiwoom, REAL


async def main() -> None:
    async with AsyncPyKiwoom(
        appkey="YOUR_APPKEY",
        secretkey="YOUR_SECRETKEY",
        host=REAL,
    ) as client:
        # Concurrent price lookups
        codes = ["005930", "000660", "035420"]
        prices = await asyncio.gather(*(client.domestic.price(c) for c in codes))

        for p in prices:
            print(f"{p.stock_name}: {p.current_price:,.0f}원")

        # Chart data
        chart = await client.domestic.chart(
            "005930_AL", period="day", start="20250401", end="20250430"
        )
        print(f"\nChart: {len(chart.candles)} candles")
        for c in chart.candles[:3]:
            print(f"  {c.date}: O={c.open} H={c.high} L={c.low} C={c.close}")


asyncio.run(main())
