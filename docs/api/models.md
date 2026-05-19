# Models

모든 응답 모델은 Pydantic `BaseModel`을 상속하며, `.raw` 필드로 원본 API 응답에 접근할 수 있습니다.

## StockPrice

현재가 조회 응답.

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

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | 성공 여부 |
| `order_no` | `str \| None` | 주문번호 |
| `message` | `str` | 응답 메시지 |
| `raw` | `dict` | 원본 응답 |

## Accessing Raw Data

모든 모델은 `.raw` 필드로 원본 API 응답 딕셔너리에 접근할 수 있습니다:

```python
price = client.domestic.price("005930")
print(price.raw)  # {"stk_cd": "005930", "now_pric": "70000", ...}
```
