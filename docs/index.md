# pykiwoom

**Python wrapper for Kiwoom Securities (키움증권) OPEN API (REST)**

키움증권 REST API의 복잡한 인증, 페이지네이션, 속도 제한을 추상화하여, 투자 전략 로직에 집중할 수 있도록 설계된 Python 라이브러리입니다.

## Key Features

- **Sync + Async** — `PyKiwoom` / `AsyncPyKiwoom` 클라이언트
- **자동 토큰 관리** — OAuth2 인증, 만료 시 자동 갱신
- **속도 제한** — Token bucket (실서버 5req/s, 모의서버 1req/s)
- **자동 페이지네이션** — `cont-yn`/`next-key` 기반 자동 병합
- **Pydantic 모델** — 타입 안전한 응답 (`StockPrice`, `Balance`, `OrderResult`)
- **MCP 서버** — AI 어시스턴트 연동
- **CLI** — 터미널에서 시세 조회, 주문 실행

## Quick Example

```python
from pykiwoom import PyKiwoom, REAL

with PyKiwoom(appkey="YOUR_KEY", secretkey="YOUR_SECRET", host=REAL) as client:
    price = client.domestic.price("005930")
    print(f"삼성전자: {price.current_price:,.0f}원")
```

## Installation

```bash
pip install pykiwoom
```

## Requirements

- Python 3.10+
- 키움증권 OPEN API 앱 키 ([openapi.kiwoom.com](https://openapi.kiwoom.com))
