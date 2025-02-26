"""
MACD 계산 모듈 테스트

이 모듈은 MACD 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: MACD 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 충분한 테스트 데이터 생성
"""

import pytest
import pandas as pd
import numpy as np
from src.be.indicators.macd import MACD


class TestMACD:
    """
    MACD 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        self.macd = MACD()

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
        self.insufficient_data = self.data.iloc[:20].copy()

    def test_init(self):
        """
        MACD 초기화 테스트
        """
        assert isinstance(self.macd, MACD)

        # 사용자 정의 파라미터로 초기화
        custom_macd = MACD(fast_period=8, slow_period=17, signal_period=5)
        assert custom_macd.fast_period == 8
        assert custom_macd.slow_period == 17
        assert custom_macd.signal_period == 5

    def test_calculate(self):
        """
        MACD 계산 테스트
        """
        # MACD 계산
        result = self.macd.calculate(self.data)

        # 결과 데이터 타입 확인
        assert isinstance(result, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = ["MACD", "MACD_Signal", "MACD_Histogram"]
        for col in required_columns:
            assert col in result.columns

        # 계산 결과 검증
        # MACD는 첫 번째 값부터 계산됨
        assert not pd.isna(result["MACD"].iloc[0])

        # MACD_Signal은 signal_period 이후부터 값이 있어야 함
        assert not pd.isna(result["MACD_Signal"].iloc[self.macd.signal_period])

        # MACD_Histogram = MACD - MACD_Signal
        for i in range(self.macd.signal_period, len(result)):
            assert np.isclose(
                result["MACD_Histogram"].iloc[i],
                result["MACD"].iloc[i] - result["MACD_Signal"].iloc[i],
            )

    def test_calculate_with_insufficient_data(self):
        """
        충분하지 않은 데이터로 MACD 계산 테스트
        """
        # 충분하지 않은 데이터로 MACD 계산 시 ValueError 발생 예상
        with pytest.raises(ValueError):
            self.macd.calculate(self.insufficient_data)

    def test_get_crossover_signals(self):
        """
        MACD 크로스오버 신호 계산 테스트
        """
        # MACD 계산
        data_with_macd = self.macd.calculate(self.data)

        # 크로스오버 신호 계산
        result = self.macd.get_crossover_signals(data_with_macd)

        # 필요한 열이 있는지 확인
        required_columns = ["MACD_Buy_Signal", "MACD_Sell_Signal"]
        for col in required_columns:
            assert col in result.columns

        # 신호는 불리언 값이어야 함
        assert result["MACD_Buy_Signal"].dtype == bool
        assert result["MACD_Sell_Signal"].dtype == bool

    def test_get_zero_crossover_signals(self):
        """
        MACD 0선 크로스오버 신호 계산 테스트
        """
        # MACD 계산
        data_with_macd = self.macd.calculate(self.data)

        # 0선 크로스오버 신호 계산
        result = self.macd.get_zero_crossover_signals(data_with_macd)

        # 필요한 열이 있는지 확인
        required_columns = ["MACD_Zero_Cross_Up", "MACD_Zero_Cross_Down"]
        for col in required_columns:
            assert col in result.columns

        # 신호는 불리언 값이어야 함
        assert result["MACD_Zero_Cross_Up"].dtype == bool
        assert result["MACD_Zero_Cross_Down"].dtype == bool


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
