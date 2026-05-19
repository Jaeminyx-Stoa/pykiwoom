# Domestic API

`client.domestic`으로 접근하는 국내 주식 API입니다.

## 시세 조회

### price

현재가를 조회합니다.

```python
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

### order_book

호가창을 조회합니다.

```python
ob = client.domestic.order_book("005930")
for ask in ob.asks:
    print(f"매도: {ask.price:,.0f}원 × {ask.volume}")
for bid in ob.bids:
    print(f"매수: {bid.price:,.0f}원 × {bid.volume}")
```

### stock_info

종목 정보를 조회합니다.

```python
info = client.domestic.stock_info("005930")
```

### tickers

종목 리스트를 조회합니다.

```python
tickers = client.domestic.tickers()
```

## 차트

### chart

차트 데이터를 조회합니다. `stock_code`는 ATS 통합코드 형식을 사용합니다.

```python
# 일봉
data = client.domestic.chart("005930_AL", period="day", start="20250401", end="20250430")

# 분봉
data = client.domestic.chart("005930_AL", period="min", start="20250501", end="20250501")

# 틱
data = client.domestic.chart("005930_AL", period="tick", start="20250501", end="20250501")

for candle in data.candles:
    print(f"{candle.date}: O={candle.open} H={candle.high} L={candle.low} C={candle.close} V={candle.volume}")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `stock_code` | `str` | ATS 통합코드 (예: `"005930_AL"`) |
| `period` | `str` | `"tick"`, `"min"`, `"day"` |
| `start` | `str` | 시작일 (`YYYYMMDD`) |
| `end` | `str` | 종료일 (`YYYYMMDD`) |

## 주문

### buy

매수 주문을 실행합니다.

```python
result = client.domestic.buy("005930", quantity=10, price=70000)
print(result.success)   # True
print(result.order_no)  # "0001234567"
print(result.message)   # "정상 처리"
```

### sell

매도 주문을 실행합니다.

```python
result = client.domestic.sell("005930", quantity=5, price=72000)
```

### modify

주문을 정정합니다.

```python
result = client.domestic.modify("0001234567", "005930", quantity=10, price=71000)
```

### cancel

주문을 취소합니다.

```python
result = client.domestic.cancel("0001234567", "005930", quantity=10)
```

## 계좌

### balance

잔고를 조회합니다.

```python
balance = client.domestic.balance()
print(balance.deposit)        # 총 예수금
print(balance.available_cash) # 주문 가능 금액
print(balance.eval_total)     # 총 평가금액
print(balance.pnl_total)      # 총 손익
print(balance.pnl_rate)       # 총 수익률

for pos in balance.positions:
    print(f"{pos.stock_name}: {pos.quantity}주, 평가 {pos.eval_amount:,.0f}원")
```

### execution_history

체결내역을 조회합니다.

```python
records = client.domestic.execution_history("20250501", "20250519")
```

### orderable_quantity

주문 가능 수량을 조회합니다.

```python
qty = client.domestic.orderable_quantity("005930", price=70000)
```
