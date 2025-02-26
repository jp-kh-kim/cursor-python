"""
스토캐스틱 슬로우 계산 모듈 테스트

이 모듈은 StochasticSlow 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: StochasticSlow 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 충분한 테스트 데이터 생성
"""

import pytest
import pandas as pd
import numpy as np
from src.be.indicators.stochastic import StochasticSlow


class TestStochasticSlow:
    """
    StochasticSlow 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        self.stoch = StochasticSlow()

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
        StochasticSlow 초기화 테스트
        """
        assert isinstance(self.stoch, StochasticSlow)

        # 사용자 정의 파라미터로 초기화
        custom_stoch = StochasticSlow(k_period=10, d_period=5, slowing=2)
        assert custom_stoch.k_period == 10
        assert custom_stoch.d_period == 5
        assert custom_stoch.slowing == 2

    def test_calculate(self):
        """
        스토캐스틱 슬로우 계산 테스트
        """
        # 스토캐스틱 슬로우 계산
        result = self.stoch.calculate(self.data)

        # 결과 데이터 타입 확인
        assert isinstance(result, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = ["%K_Fast", "%K", "%D"]
        for col in required_columns:
            assert col in result.columns

        # 계산 결과 검증
        # %K_Fast는 k_period 이후부터 값이 있어야 함
        assert pd.isna(result["%K_Fast"].iloc[self.stoch.k_period - 2])
        assert not pd.isna(result["%K_Fast"].iloc[self.stoch.k_period - 1])

        # %K와 %D 값은 0에서 100 사이여야 함
        for i in range(self.stoch.k_period, len(result)):
            if not pd.isna(result["%K"].iloc[i]):
                assert 0 <= result["%K"].iloc[i] <= 100
            if not pd.isna(result["%D"].iloc[i]):
                assert 0 <= result["%D"].iloc[i] <= 100

    def test_calculate_with_insufficient_data(self):
        """
        충분하지 않은 데이터로 스토캐스틱 슬로우 계산 테스트
        """
        # 충분하지 않은 데이터로 스토캐스틱 슬로우 계산 시 ValueError 발생 예상
        with pytest.raises(ValueError):
            self.stoch.calculate(self.insufficient_data)

    def test_get_signals(self):
        """
        스토캐스틱 슬로우 기반 매매 신호 계산 테스트
        """
        # 스토캐스틱 슬로우 계산
        data_with_stoch = self.stoch.calculate(self.data)

        # 매매 신호 계산
        result = self.stoch.get_signals(data_with_stoch)

        # 필요한 열이 있는지 확인
        required_columns = [
            "Stoch_Buy_Signal_1",
            "Stoch_Buy_Signal_2",
            "Stoch_Sell_Signal_1",
            "Stoch_Sell_Signal_2",
        ]
        for col in required_columns:
            assert col in result.columns

        # 신호는 불리언 값이어야 함
        for col in required_columns:
            assert result[col].dtype == bool


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
