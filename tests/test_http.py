"""Tests for HTTP client."""

from pykiwoom.http import _merge_page


class TestMergePage:
    def test_first_page(self):
        result = _merge_page({"key": "val", "items": [1, 2]}, None)
        assert result == {"key": "val", "items": [1, 2]}

    def test_merge_lists(self):
        acc = {"key": "val", "items": [1, 2]}
        new = {"key": "val2", "items": [3, 4]}
        result = _merge_page(new, acc)
        assert result["items"] == [1, 2, 3, 4]
        assert result["key"] == "val2"

    def test_merge_scalars_overwritten(self):
        acc = {"code": 0, "msg": "ok"}
        new = {"code": 0, "msg": "page2"}
        result = _merge_page(new, acc)
        assert result["msg"] == "page2"
