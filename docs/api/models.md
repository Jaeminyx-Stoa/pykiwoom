# Models

모든 응답 모델은 Pydantic `BaseModel`을 상속하며, `.raw` 필드로 원본 API 응답에 접근할 수 있습니다.

## StockPrice

현재가 조회 응답.

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
    print(price.stock_code)    # "005930"
    print(price.stock_name)    # "삼성전자"
    print(price.current_price) # 70000.0
    print(price.change)        # 500.0
    print(price.change_rate)   # 0.72
    print(price.volume)        # 12345678
    print(price.high_price)    # 70500.0
    print(price.low_price)     # 69500.0
    print(price.open_price)    # 69800.0
```

| Field | Type | Description |
|-------|------|-------------|
| `stock_code` | `str` | 종목코드 |
| `stock_name` | `str` | 종목명 |
| `current_price` | `float` | 현재가 |
| `change` | `float` | 전일 대비 |
| `change_rate` | `float` | 등락률 (%) |
| `volume` | `int` | 거래량 |
| `high_price` | `float` | 고가 |
| `low_price` | `float` | 저가 |
| `open_price` | `float` | 시가 |
| `raw` | `dict` | 원본 응답 |

## OrderBook

호가 조회 응답.

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    ob = client.domestic.order_book("005930")
    for ask in ob.asks[:3]:
        print(f"매도 {ask.price:,.0f}원 × {ask.volume:,}")
    for bid in ob.bids[:3]:
        print(f"매수 {bid.price:,.0f}원 × {bid.volume:,}")
    print(ob.raw)  # original API response dict
```

| Field | Type | Description |
|-------|------|-------------|
| `asks` | `list[Quote]` | 매도 호가 (가격순) |
| `bids` | `list[Quote]` | 매수 호가 (가격순) |
| `raw` | `dict` | 원본 응답 |

### Quote

| Field | Type | Description |
|-------|------|-------------|
| `price` | `float` | 호가 가격 |
| `volume` | `int` | 호가 잔량 |

## ChartData

차트 조회 응답.

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    # 일봉 차트
    data = client.domestic.chart("005930_AL", period="day", start="20250401", end="20250430")
    print(f"Total candles: {len(data.candles)}")
    for candle in data.candles[:5]:
        print(f"{candle.date}: O={candle.open} H={candle.high} L={candle.low} C={candle.close} V={candle.volume}")

    # 분봉 차트
    min_data = client.domestic.chart("005930_AL", period="min", start="20250501", end="20250501")
    for candle in min_data.candles[:3]:
        print(f"{candle.date}: {candle.close}")
```

| Field | Type | Description |
|-------|------|-------------|
| `candles` | `list[ChartCandle]` | 캔들 데이터 |
| `raw` | `dict` | 원본 응답 |

### ChartCandle

| Field | Type | Description |
|-------|------|-------------|
| `date` | `str` | 일시 |
| `open` | `float` | 시가 |
| `high` | `float` | 고가 |
| `low` | `float` | 저가 |
| `close` | `float` | 종가 |
| `volume` | `int` | 거래량 |

## Balance

잔고 조회 응답.

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    balance = client.domestic.balance()
    print(f"예수금: {balance.deposit:,.0f}원")
    print(f"주문가능: {balance.available_cash:,.0f}원")
    print(f"총평가: {balance.eval_total:,.0f}원")
    print(f"총손익: {balance.pnl_total:,.0f}원 ({balance.pnl_rate}%)")

    for pos in balance.positions:
        print(f"  {pos.stock_name} ({pos.stock_code})")
        print(f"    보유: {pos.quantity}주, 평단: {pos.avg_price:,.0f}원")
        print(f"    현재가: {pos.current_price:,.0f}원")
        print(f"    평가: {pos.eval_amount:,.0f}원, 손익: {pos.pnl_amount:,.0f}원 ({pos.pnl_rate}%)")
```

| Field | Type | Description |
|-------|------|-------------|
| `deposit` | `float` | 예수금 |
| `available_cash` | `float` | 주문 가능 금액 |
| `eval_total` | `float` | 총 평가금액 |
| `pnl_total` | `float` | 총 손익 |
| `pnl_rate` | `float` | 총 수익률 (%) |
| `positions` | `list[Position]` | 보유 종목 |
| `raw` | `dict` | 원본 응답 |

### Position

| Field | Type | Description |
|-------|------|-------------|
| `stock_code` | `str` | 종목코드 |
| `stock_name` | `str` | 종목명 |
| `quantity` | `int` | 보유 수량 |
| `avg_price` | `float` | 평균 매입가 |
| `current_price` | `float` | 현재가 |
| `eval_amount` | `float` | 평가금액 |
| `pnl_amount` | `float` | 손익금액 |
| `pnl_rate` | `float` | 수익률 (%) |

## OrderResult

주문 응답.

```python
from pykiwoom import PyKiwoom, MOCK

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=MOCK) as client:
    # 매수 주문
    buy = client.domestic.buy("005930", quantity=10, price=70000)
    print(f"성공: {buy.success}")
    print(f"주문번호: {buy.order_no}")
    print(f"메시지: {buy.message}")

    # 매도 주문
    sell = client.domestic.sell("005930", quantity=5, price=72000)
    if sell.success:
        print(f"매도 주문번호: {sell.order_no}")

    # 주문 정정
    modify = client.domestic.modify(buy.order_no, "005930", quantity=10, price=71000)
    print(f"정정: {modify.success}")

    # 주문 취소
    cancel = client.domestic.cancel(buy.order_no, "005930", quantity=10)
    print(f"취소: {cancel.success}")
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | 성공 여부 |
| `order_no` | `str \| None` | 주문번호 |
| `message` | `str` | 응답 메시지 |
| `raw` | `dict` | 원본 응답 |

## Accessing Raw Data

모든 모델은 `.raw` 필드로 원본 API 응답 딕셔너리에 접근할 수 있습니다:

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
    # Pydantic model fields
    print(price.stock_name, price.current_price)

    # Original API response
    print(price.raw)
    # {"stk_cd": "005930", "stk_nm": "삼성전자", "now_pric": "70000", ...}

    # Access any field from the raw response
    print(price.raw.get("stk_cd"))
```
