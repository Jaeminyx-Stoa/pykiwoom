"""Tests for Pydantic models."""

from pykiwoom.models.balance import Balance, Position
from pykiwoom.models.order import OrderResult
from pykiwoom.models.quote import ChartData, OrderBook, StockPrice


class TestStockPrice:
    def test_from_api(self):
        data = {
            "stk_cd": "005930",
            "stk_nm": "삼성전자",
            "now_pric": "70000",
            "change": "1000",
            "change_rate": "1.45",
            "volume": "12345678",
            "open_pric": "69000",
            "high_pric": "70500",
            "low_pric": "68500",
        }
        price = StockPrice.from_api(data)
        assert price.stock_code == "005930"
        assert price.stock_name == "삼성전자"
        assert price.current_price == 70000.0
        assert price.change == 1000.0
        assert price.volume == 12345678

    def test_from_api_missing_fields(self):
        price = StockPrice.from_api({})
        assert price.current_price == 0
        assert price.volume == 0


class TestOrderBook:
    def test_from_api(self):
        data = {
            "ask_pric1": "70100",
            "ask_qty1": "500",
            "bid_pric1": "70000",
            "bid_qty1": "300",
            "tot_ask_qty": "5000",
            "tot_bid_qty": "3000",
        }
        ob = OrderBook.from_api(data)
        assert len(ob.asks) == 1
        assert ob.asks[0].price == 70100.0
        assert len(ob.bids) == 1
        assert ob.bids[0].price == 70000.0
        assert ob.total_ask_volume == 5000


class TestChartData:
    def test_from_api(self):
        data = {
            "stk_min_pole_chart_qry": [
                {
                    "cntr_tm": "20250901090100",
                    "open_pric": "61200",
                    "high_pric": "61500",
                    "low_pric": "61000",
                    "close_pric": "61300",
                    "volume": "1000",
                },
            ]
        }
        chart = ChartData.from_api(data)
        assert len(chart.candles) == 1
        assert chart.candles[0].datetime == "20250901090100"
        assert chart.candles[0].open == 61200.0
        assert chart.candles[0].close == 61300.0

    def test_from_api_with_list_key(self):
        data = {
            "my_key": [
                {"cntr_tm": "20250901", "open_pric": "100", "high_pric": "110",
                 "low_pric": "90", "close_pric": "105", "volume": "500"}
            ]
        }
        chart = ChartData.from_api(data, list_key="my_key")
        assert len(chart.candles) == 1

    def test_from_api_empty(self):
        chart = ChartData.from_api({})
        assert len(chart.candles) == 0


class TestPosition:
    def test_from_api(self):
        data = {
            "stk_cd": "005930",
            "stk_nm": "삼성전자",
            "hold_qty": "100",
            "now_pric": "70000",
            "avg_pric": "65000",
            "eval_amt": "7000000",
            "pnl_amt": "500000",
            "pnl_rate": "7.69",
        }
        pos = Position.from_api(data)
        assert pos.stock_code == "005930"
        assert pos.quantity == 100
        assert pos.eval_amount == 7000000.0


class TestBalance:
    def test_from_api(self):
        data = {
            "deposit": "10000000",
            "ord_able_amt": "5000000",
            "eval_tot": "8000000",
            "pnl_tot": "500000",
            "pnl_rate": "6.67",
            "balance": [
                {"stk_cd": "005930", "stk_nm": "삼성전자", "hold_qty": "10"},
            ],
        }
        bal = Balance.from_api(data)
        assert bal.deposit == 10000000.0
        assert bal.available_cash == 5000000.0
        assert len(bal.positions) == 1

    def test_from_api_empty(self):
        bal = Balance.from_api({})
        assert bal.deposit == 0
        assert len(bal.positions) == 0


class TestOrderResult:
    def test_success(self):
        data = {"return_code": 0, "ord_no": "12345", "return_msg": "정상처리"}
        result = OrderResult.from_api(data)
        assert result.success is True
        assert result.order_no == "12345"
        assert result.message == "정상처리"

    def test_failure(self):
        data = {"return_code": -1, "return_msg": "주문 실패"}
        result = OrderResult.from_api(data)
        assert result.success is False
