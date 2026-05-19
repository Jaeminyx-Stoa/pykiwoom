# Client

## PyKiwoom

동기 클라이언트. HTTP 요청을 동기적으로 처리합니다.

```python
from pykiwoom import PyKiwoom, REAL

client = PyKiwoom(
    appkey="YOUR_KEY",
    secretkey="YOUR_SECRET",
    host=REAL,           # REAL or MOCK
    timeout=30.0,        # HTTP timeout (seconds)
    rate_limit=True,     # enable rate limiting
    log_level="WARNING", # logging level
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `appkey` | `str` | required | 앱 키 (문자열 또는 파일 경로) |
| `secretkey` | `str` | required | 시크릿 키 (문자열 또는 파일 경로) |
| `host` | `str` | `REAL` | API 서버 (`REAL` or `MOCK`) |
| `timeout` | `float` | `30.0` | HTTP 타임아웃 (초) |
| `rate_limit` | `bool` | `True` | 속도 제한 활성화 |
| `log_level` | `str` | `"WARNING"` | 로그 레벨 |
| `token` | `str \| None` | `None` | 기존 토큰 재사용 |
| `expires_at` | `float \| None` | `None` | 토큰 만료 시각 (epoch) |

### Properties

- `client.domestic` — `DomesticAPI` 인스턴스
- `client.portfolio_summary()` — 포트폴리오 요약 조회

### Context Manager

```python
with PyKiwoom(appkey="KEY", secretkey="SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
# client.close() is called automatically
```

### Cleanup

```python
client.close()  # manually close HTTP connections
```

## AsyncPyKiwoom

비동기 클라이언트. `PyKiwoom`과 동일한 인터페이스를 `async/await`로 제공합니다.

```python
import asyncio
from pykiwoom import AsyncPyKiwoom, REAL

async def main():
    async with AsyncPyKiwoom(appkey="KEY", secretkey="SECRET", host=REAL) as client:
        price = await client.domestic.price("005930")
        balance = await client.domestic.balance()

asyncio.run(main())
```

Parameters와 properties는 `PyKiwoom`과 동일합니다.
