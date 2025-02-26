"""
RSI 계산 모듈 테스트

이 모듈은 RSI 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: RSI 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 충분한 테스트 데이터 생성
"""

import pytest
import pandas as pd
import numpy as np
from src.be.indicators.rsi import RSI


class TestRSI:
    """
    RSI 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        self.rsi = RSI()

        # 테스트용 데이터 생성
        dates = pd.date_range(start="2023-01-01", periods=100)
        self.data = pd.DataFrame(
            {
                "Open": np.random.normal(100, 5, size=100),
                "High": np.random.normal(105, 5, size=100),
                "Low": np.random.normal(95, 5, size=100),
                "Close": np.random.normal(100, 5, size=100),
                "Volume": np.random.normal(1000000, 200000, size=100),
            },
            index=dates,
        )

        # 충분하지 않은 데이터
        self.insufficient_data = self.data.iloc[:10].copy()

    def test_init(self):
        """
        RSI 초기화 테스트
        """
        assert isinstance(self.rsi, RSI)

        # 사용자 정의 파라미터로 초기화
        custom_rsi = RSI(period=7)
        assert custom_rsi.period == 7

    def test_calculate(self):
        """
        RSI 계산 테스트
        """
        # RSI 계산
        result = self.rsi.calculate(self.data)

        # 결과 데이터 타입 확인
        assert isinstance(result, pd.DataFrame)

        # 필요한 열이 있는지 확인
        assert "RSI" in result.columns

        # 계산 결과 검증
        # RSI는 period 이후부터 값이 있어야 함
        assert not pd.isna(result["RSI"].iloc[self.rsi.period])

        # RSI 값은 0에서 100 사이여야 함
        for i in range(self.rsi.period, len(result)):
            assert 0 <= result["RSI"].iloc[i] <= 100

    def test_calculate_with_insufficient_data(self):
        """
        충분하지 않은 데이터로 RSI 계산 테스트
        """
        # 충분하지 않은 데이터로 RSI 계산 시 ValueError 발생 예상
        with pytest.raises(ValueError):
            self.rsi.calculate(self.insufficient_data)

    def test_calculate_simple(self):
        """
        간단한 방법으로 RSI 계산 테스트
        """
        # 간단한 방법으로 RSI 계산
        result = self.rsi.calculate_simple(self.data)

        # 필요한 열이 있는지 확인
        assert "RSI_Simple" in result.columns

        # RSI_Simple 값은 0에서 100 사이여야 함
        for i in range(self.rsi.period, len(result)):
            if not pd.isna(result["RSI_Simple"].iloc[i]):
                assert 0 <= result["RSI_Simple"].iloc[i] <= 100

    def test_get_signals(self):
        """
        RSI 기반 매매 신호 계산 테스트
        """
        # RSI 계산
        data_with_rsi = self.rsi.calculate(self.data)

        # 매매 신호 계산
        result = self.rsi.get_signals(data_with_rsi)

        # 필요한 열이 있는지 확인
        required_columns = ["RSI_Buy_Signal", "RSI_Sell_Signal"]
        for col in required_columns:
            assert col in result.columns

        # 신호는 불리언 값이어야 함
        assert result["RSI_Buy_Signal"].dtype == bool
        assert result["RSI_Sell_Signal"].dtype == bool


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
