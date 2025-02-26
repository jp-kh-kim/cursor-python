"""
주식 데이터 수집기 테스트 모듈

이 모듈은 StockCollector 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: StockCollector 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 네트워크 연결 필요, yfinance API 제한 고려
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.be.data.stock_collector import StockCollector
from unittest.mock import patch, MagicMock


class TestStockCollector:
    """
    StockCollector 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        self.collector = StockCollector()
        self.valid_ticker = "AAPL"  # 유효한 티커
        self.invalid_ticker = "INVALID_TICKER_123"  # 유효하지 않은 티커

    def test_init(self):
        """
        StockCollector 초기화 테스트
        """
        assert isinstance(self.collector, StockCollector)

    def test_get_stock_data_valid_ticker(self):
        """
        유효한 티커에 대한 주식 데이터 수집 테스트
        """
        # 최근 7일 데이터 요청
        data = self.collector.get_stock_data(self.valid_ticker, days=7)

        # 데이터 타입 확인
        assert isinstance(data, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_columns:
            assert col in data.columns

        # 데이터가 비어있지 않은지 확인
        assert not data.empty

        # 데이터 길이가 적절한지 확인 (주말, 공휴일 등으로 인해 정확히 7일이 아닐 수 있음)
        # 최소 1일 이상의 데이터가 있어야 함
        assert len(data) >= 1

    def test_get_stock_data_invalid_ticker(self):
        """
        유효하지 않은 티커에 대한 주식 데이터 수집 테스트
        """
        # 유효하지 않은 티커로 요청 시 ValueError 발생 예상
        with pytest.raises(Exception):
            self.collector.get_stock_data(self.invalid_ticker, days=7)

    def test_get_stock_data_date_range(self):
        """
        날짜 범위에 따른 주식 데이터 수집 테스트
        """
        # 최근 30일 데이터 요청
        data_30 = self.collector.get_stock_data(self.valid_ticker, days=30)

        # 최근 7일 데이터 요청
        data_7 = self.collector.get_stock_data(self.valid_ticker, days=7)

        # 30일 데이터가 7일 데이터보다 많거나 같아야 함 (주말, 공휴일 등 고려)
        assert len(data_30) >= len(data_7)

    @patch("yfinance.Ticker")
    def test_get_stock_info_valid_ticker(self, mock_ticker):
        """
        유효한 티커에 대한 주식 정보 수집 테스트
        """
        # Mock 설정
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.info = {
            "shortName": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "United States",
            "website": "https://www.apple.com",
            "marketCap": 2500000000000,
            "currency": "USD",
        }

        # 주식 정보 요청
        info = self.collector.get_stock_info(self.valid_ticker)

        # 데이터 타입 확인
        assert isinstance(info, dict)

        # 필요한 키가 있는지 확인
        required_keys = ["name", "sector", "industry", "country"]
        for key in required_keys:
            assert key in info

        # 이름이 비어있지 않은지 확인
        assert info["name"] != "N/A"

    def test_get_stock_info_invalid_ticker(self):
        """
        유효하지 않은 티커에 대한 주식 정보 수집 테스트
        """
        # 유효하지 않은 티커로 요청 시 Exception 발생 예상
        with pytest.raises(Exception):
            self.collector.get_stock_info(self.invalid_ticker)


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
