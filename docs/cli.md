# CLI

pykiwoom은 터미널에서 바로 사용할 수 있는 CLI 도구를 제공합니다.

## 환경변수 설정

```bash
export KIWOOM_APPKEY="your_app_key"
export KIWOOM_SECRETKEY="your_secret_key"
```

## 명령어

### price — 현재가 조회

```bash
pykiwoom price 005930
```

```
삼성전자 (005930)
현재가: 70,000원 (+500, +0.72%)
거래량: 12,345,678
고가: 70,500  저가: 69,500  시가: 69,800
```

### balance — 잔고 조회

```bash
pykiwoom balance
```

### portfolio — 포트폴리오 요약

```bash
pykiwoom portfolio
```

### buy — 매수 주문

```bash
pykiwoom buy 005930 10 70000
# 종목코드, 수량, 가격
```

### sell — 매도 주문

```bash
pykiwoom sell 005930 5 72000
```

### history — 체결내역

```bash
pykiwoom history 20250501 20250519
# 시작일, 종료일 (YYYYMMDD)
```

## 옵션

| Flag | Description |
|------|-------------|
| `--appkey` | 앱 키 (환경변수 대신 사용) |
| `--secretkey` | 시크릿 키 (환경변수 대신 사용) |
| `--mock` | 모의투자 서버 사용 |
| `--json` | JSON 형식으로 출력 |

### 예시

```bash
# 모의투자 서버에서 JSON 출력
pykiwoom --mock --json price 005930

# 인라인 키 지정
pykiwoom --appkey YOUR_KEY --secretkey YOUR_SECRET price 005930
```
