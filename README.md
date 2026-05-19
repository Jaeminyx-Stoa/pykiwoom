# pykiwoom

Python wrapper for Kiwoom Securities (키움증권) OPEN API (REST).

키움증권 REST API의 복잡한 인증, 페이지네이션, 속도 제한을 추상화하여, 투자 전략 로직에 집중할 수 있도록 설계된 Python 라이브러리입니다.

## Features

- **Sync + Async** — `PyKiwoom` (동기) / `AsyncPyKiwoom` (비동기) 클라이언트
- **자동 토큰 관리** — OAuth2 인증, 만료 시 자동 갱신
- **속도 제한** — Token bucket rate limiter (실서버 5req/s, 모의서버 1req/s)
- **자동 페이지네이션** — `cont-yn`/`next-key` 헤더 기반 자동 병합
- **Pydantic 모델** — 타입 안전한 응답 모델 (`StockPrice`, `Balance`, `OrderResult` 등)
- **MCP 서버** — Claude Desktop 등 AI 어시스턴트에서 바로 사용
- **CLI** — 터미널에서 시세 조회, 주문 실행

## Installation

```bash
pip install pykiwoom

# MCP 서버 사용 시
pip install pykiwoom[mcp]
```

## Quick Start

```python
from pykiwoom import PyKiwoom, REAL

client = PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL)

# 현재가 조회
price = client.domestic.price("005930")
print(f"삼성전자: {price.current_price:,.0f}원")

# 잔고 조회
balance = client.domestic.balance()
for pos in balance.positions:
    print(f"{pos.stock_name}: {pos.quantity}주, P&L: {pos.pnl_amount:,.0f}원")

# 매수 주문
result = client.domestic.buy("005930", quantity=10, price=70000)
print(f"주문번호: {result.order_no}")

client.close()
```

## Async Usage

```python
import asyncio
from pykiwoom import AsyncPyKiwoom, REAL

async def main():
    async with AsyncPyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
        price = await client.domestic.price("005930")
        balance = await client.domestic.balance()
        print(f"삼성전자: {price.current_price:,.0f}원")

asyncio.run(main())
```

## CLI

```bash
export KIWOOM_APPKEY="your_app_key"
export KIWOOM_SECRETKEY="your_secret_key"

pykiwoom price 005930           # 현재가 조회
pykiwoom balance                # 잔고 조회
pykiwoom portfolio              # 포트폴리오 요약
pykiwoom buy 005930 10 70000    # 매수 주문
pykiwoom sell 005930 5 72000    # 매도 주문
pykiwoom history 20250901 20250930  # 체결내역

# 모의투자 서버 사용
pykiwoom --mock price 005930

# JSON 출력
pykiwoom --json price 005930
```

## MCP Server (Claude Desktop)

`claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "kiwoom": {
            "command": "pykiwoom-mcp",
            "env": {
                "KIWOOM_APPKEY": "your_app_key",
                "KIWOOM_SECRETKEY": "your_secret_key"
            }
        }
    }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_stock_price` | 주식 현재가 조회 |
| `get_balance` | 잔고 조회 |
| `get_portfolio_summary` | 포트폴리오 요약 |
| `place_order` | 매수/매도 주문 |
| `get_order_book` | 호가 조회 |
| `get_chart` | 차트 데이터 조회 |
| `get_execution_history` | 체결내역 조회 |

### Anthropic SDK Integration

```python
import anthropic
from pykiwoom.mcp.helpers import get_anthropic_tools, execute_tool

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=get_anthropic_tools(),
    messages=[{"role": "user", "content": "삼성전자 현재가 알려줘"}],
)

# Tool execution in agentic loop
for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
```

## Context Manager

리소스 자동 정리를 위해 `with` 문 사용을 권장합니다:

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
    print(f"{price.stock_name}: {price.current_price:,.0f}원")
```

## Chart Data

ATS 통합코드 형식(`종목코드_AL`)으로 차트를 조회합니다:

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    # 일봉
    day_chart = client.domestic.chart("005930_AL", period="day", start="20250401", end="20250430")
    for candle in day_chart.candles[:5]:
        print(f"{candle.date}: O={candle.open} H={candle.high} L={candle.low} C={candle.close}")

    # 분봉
    min_chart = client.domestic.chart("005930_AL", period="min", start="20250501", end="20250501")

    # 틱
    tick_chart = client.domestic.chart("005930_AL", period="tick", start="20250501", end="20250501")
```

## Order Book

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    ob = client.domestic.order_book("005930")
    for ask in ob.asks[:5]:
        print(f"매도 {ask.price:,.0f}원 × {ask.volume:,}")
    for bid in ob.bids[:5]:
        print(f"매수 {bid.price:,.0f}원 × {bid.volume:,}")
```

## Order Management

```python
from pykiwoom import PyKiwoom, MOCK

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=MOCK) as client:
    # 매수
    buy = client.domestic.buy("005930", quantity=10, price=70000)
    print(f"주문번호: {buy.order_no}, 성공: {buy.success}")

    # 매도
    sell = client.domestic.sell("005930", quantity=5, price=72000)

    # 정정
    modify = client.domestic.modify(buy.order_no, "005930", quantity=10, price=71000)

    # 취소
    cancel = client.domestic.cancel(buy.order_no, "005930", quantity=10)

    # 체결내역
    records = client.domestic.execution_history("20250501", "20250519")
    print(f"체결 건수: {len(records)}")
```

## Portfolio Summary

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    summary = client.portfolio_summary()
    print(f"총 평가: {summary.eval_total:,.0f}원")
    print(f"총 손익: {summary.pnl_total:,.0f}원 ({summary.pnl_rate}%)")
```

## Raw API Response

모든 응답 모델은 `.raw` 필드로 원본 API 응답에 접근할 수 있습니다:

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
    print(price.raw)  # {"stk_cd": "005930", "now_pric": "70000", ...}
```

## API Reference

### DomesticAPI

```python
from pykiwoom import PyKiwoom, REAL

client = PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL)

# 시세
client.domestic.price("005930")           # 현재가
client.domestic.order_book("005930")      # 호가
client.domestic.stock_info("005930")      # 종목정보
client.domestic.tickers()                 # 종목리스트

# 계좌
client.domestic.balance()                 # 잔고
client.domestic.execution_history("20250901", "20250930")  # 체결내역
client.domestic.orderable_quantity("005930", price=70000)   # 주문가능수량

# 주문
client.domestic.buy("005930", 10, 70000)  # 매수
client.domestic.sell("005930", 5, 72000)  # 매도
client.domestic.modify("12345", "005930", 10, 71000)  # 정정
client.domestic.cancel("12345", "005930", 10)  # 취소

# 차트
client.domestic.chart("005930_AL", period="day", start="20250901", end="20250930")
client.domestic.chart("005930_AL", period="min", start="20250901", end="20250901")
client.domestic.chart("005930_AL", period="tick", start="20250901", end="20250901")

client.close()
```

## Environment

| Variable | Description |
|----------|-------------|
| `KIWOOM_APPKEY` | 키움 OPEN API 앱 키 |
| `KIWOOM_SECRETKEY` | 키움 OPEN API 시크릿 키 |
| `KIWOOM_MOCK` | `1`/`true` 설정 시 모의투자 서버 사용 |

## License

MIT
