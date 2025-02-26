"""
볼린저 밴드 계산 모듈 테스트

이 모듈은 BollingerBands 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: BollingerBands 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 충분한 테스트 데이터 생성
"""

import pytest
import pandas as pd
import numpy as np
from src.be.indicators.bollinger_bands import BollingerBands


class TestBollingerBands:
    """
    BollingerBands 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        self.bb = BollingerBands()

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
        self.insufficient_data = self.data.iloc[:15].copy()

    def test_init(self):
        """
        BollingerBands 초기화 테스트
        """
        assert isinstance(self.bb, BollingerBands)

        # 사용자 정의 파라미터로 초기화
        custom_bb = BollingerBands(window=10, num_std=1.5)
        assert custom_bb.window == 10
        assert custom_bb.num_std == 1.5

    def test_calculate(self):
        """
        볼린저 밴드 계산 테스트
        """
        # 볼린저 밴드 계산
        result = self.bb.calculate(self.data)

        # 결과 데이터 타입 확인
        assert isinstance(result, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = [
            "BB_Upper",
            "BB_Middle",
            "BB_Lower",
            "BB_Width",
            "BB_PercentB",
        ]
        for col in required_columns:
            assert col in result.columns

        # 계산 결과 검증
        # BB_Middle는 window 이후부터 값이 있어야 함
        assert pd.isna(result["BB_Middle"].iloc[self.bb.window - 2])
        assert not pd.isna(result["BB_Middle"].iloc[self.bb.window - 1])

        # BB_Upper > BB_Middle > BB_Lower
        for i in range(self.bb.window - 1, len(result)):
            assert result["BB_Upper"].iloc[i] > result["BB_Middle"].iloc[i]
            assert result["BB_Middle"].iloc[i] > result["BB_Lower"].iloc[i]

        # BB_Width = (BB_Upper - BB_Lower) / BB_Middle
        for i in range(self.bb.window - 1, len(result)):
            assert np.isclose(
                result["BB_Width"].iloc[i],
                (result["BB_Upper"].iloc[i] - result["BB_Lower"].iloc[i])
                / result["BB_Middle"].iloc[i],
            )

    def test_calculate_with_insufficient_data(self):
        """
        충분하지 않은 데이터로 볼린저 밴드 계산 테스트
        """
        # 충분하지 않은 데이터로 볼린저 밴드 계산 시 ValueError 발생 예상
        with pytest.raises(ValueError):
            self.bb.calculate(self.insufficient_data)

    def test_get_signals(self):
        """
        볼린저 밴드 기반 매매 신호 계산 테스트
        """
        # 볼린저 밴드 계산
        data_with_bb = self.bb.calculate(self.data)

        # 매매 신호 계산
        result = self.bb.get_signals(data_with_bb)

        # 필요한 열이 있는지 확인
        required_columns = ["BB_Buy_Signal", "BB_Sell_Signal", "BB_Squeeze"]
        for col in required_columns:
            assert col in result.columns

        # 신호는 불리언 값이어야 함
        assert result["BB_Buy_Signal"].dtype == bool
        assert result["BB_Sell_Signal"].dtype == bool
        assert result["BB_Squeeze"].dtype == bool


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
