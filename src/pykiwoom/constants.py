"""Kiwoom Securities OPEN API (REST) constants."""

from __future__ import annotations

# ── Server hosts ──
REAL = "https://openapi.kiwoom.com"
MOCK = "https://mockapi.kiwoom.com"

BASE_URL = REAL

# ── OAuth endpoints ──
OAUTH_TOKEN_URL = "/oauth2/token"

# ── Domestic (국내) Stock endpoints ──
# Quote / Info
DOMESTIC_STOCK_INFO = "/api/dostk/stkinfo"         # 주식종목정보
DOMESTIC_PRICE = "/api/dostk/price"                 # 주식현재가
DOMESTIC_ORDERBOOK = "/api/dostk/hoga"              # 주식호가
DOMESTIC_TICKER_LIST = "/api/dostk/stklist"         # 종목리스트
DOMESTIC_BROKER_RANKING = "/api/dostk/rkinfo"       # 증권사별매매상위

# Chart
DOMESTIC_CHART_TICK = "/api/dostk/chart"            # 틱/분/일 차트
DOMESTIC_CHART_SECTOR_TICK = "/api/dostk/sectchart"  # 업종 틱/분/일 차트

# Account / Trading
DOMESTIC_ACCOUNT = "/api/dostk/acnt"                # 계좌내역 (체결, 잔고 등)
DOMESTIC_ORDER = "/api/dostk/order"                 # 주식주문
DOMESTIC_MODIFY_ORDER = "/api/dostk/mdcl"           # 주식정정/취소

# ── API IDs (tr_id / api_id) ──
# Quote
API_STOCK_INFO = "ka10099"          # 주식종목정보요청
API_CURRENT_PRICE = "ka10001"       # 주식현재가요청
API_ORDERBOOK = "ka10002"           # 주식호가요청
API_TICKER_LIST = "ka10100"         # 종목리스트요청
API_BROKER_RANKING = "ka10039"      # 증권사별매매상위요청

# Chart
API_CHART_TICK = "ka10079"          # 주식틱차트
API_CHART_MINUTE = "ka10080"        # 주식분차트
API_CHART_DAY = "ka10081"           # 주식일차트
API_SECTOR_CHART_TICK = "ka20004"   # 업종틱차트
API_SECTOR_CHART_MINUTE = "ka20005"  # 업종분차트
API_SECTOR_CHART_DAY = "ka20006"    # 업종일차트

# Account / Trading
API_EXECUTION_HISTORY = "kt00009"   # 체결내역요청
API_BALANCE = "kt00010"             # 잔고요청
API_ORDER_BUY = "kt00001"           # 매수주문
API_ORDER_SELL = "kt00002"          # 매도주문
API_ORDER_MODIFY = "kt00003"        # 정정주문
API_ORDER_CANCEL = "kt00004"        # 취소주문
API_ORDERABLE_QTY = "kt00011"       # 주문가능수량

# ── Rate limits (requests per second) ──
# REAL server: 5 req/s, MOCK server: 1 req/s
RATE_LIMIT_REAL = 5
RATE_LIMIT_MOCK = 1

# ── Return codes ──
RETURN_CODE_SUCCESS = 0
RETURN_CODE_TOKEN_EXPIRED = 3
