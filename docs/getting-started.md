# Getting Started

## 1. API 키 발급

[키움증권 OPEN API](https://openapi.kiwoom.com)에서 앱을 등록하고 **앱 키**와 **시크릿 키**를 발급받습니다.

## 2. 설치

```bash
pip install pykiwoom
```

## 3. 기본 사용법

### Sync Client

```python
from pykiwoom import PyKiwoom, REAL

client = PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL)

# 현재가 조회
price = client.domestic.price("005930")
print(f"{price.stock_name}: {price.current_price:,.0f}원")

# 잔고 조회
balance = client.domestic.balance()
for pos in balance.positions:
    print(f"{pos.stock_name}: {pos.quantity}주")

client.close()
```

### Async Client

```python
import asyncio
from pykiwoom import AsyncPyKiwoom, REAL

async def main():
    async with AsyncPyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
        price = await client.domestic.price("005930")
        print(f"{price.stock_name}: {price.current_price:,.0f}원")

asyncio.run(main())
```

### Context Manager

리소스 자동 정리를 위해 `with` 문 사용을 권장합니다:

```python
with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
```

## 4. 환경변수

키를 코드에 하드코딩하지 않고 환경변수로 관리할 수 있습니다:

```bash
export KIWOOM_APPKEY="your_app_key"
export KIWOOM_SECRETKEY="your_secret_key"
```

```python
import os
from pykiwoom import PyKiwoom, REAL

client = PyKiwoom(
    appkey=os.environ["KIWOOM_APPKEY"],
    secretkey=os.environ["KIWOOM_SECRETKEY"],
    host=REAL,
)
```

## 5. 모의투자 서버

테스트 시 모의투자 서버를 사용할 수 있습니다:

```python
from pykiwoom import PyKiwoom, MOCK

client = PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=MOCK)
```

!!! note
    모의투자 서버는 속도 제한이 1 req/s로 실서버(5 req/s)보다 낮습니다.

## 6. 키를 파일로 관리

앱 키와 시크릿 키를 파일 경로로 지정할 수도 있습니다:

```python
client = PyKiwoom(appkey="/path/to/appkey.txt", secretkey="/path/to/secretkey.txt", host=REAL)
```
