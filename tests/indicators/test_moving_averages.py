"""
이동평균선 계산 모듈 테스트

이 모듈은 MovingAverages 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: MovingAverages 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 충분한 테스트 데이터 생성
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.be.indicators.moving_averages import MovingAverages


class TestMovingAverages:
    """
    MovingAverages 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        self.ma = MovingAverages()

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
        self.insufficient_data = self.data.iloc[:5].copy()

    def test_init(self):
        """
        MovingAverages 초기화 테스트
        """
        assert isinstance(self.ma, MovingAverages)

    def test_calculate_ma(self):
        """
        이동평균선 계산 테스트
        """
        # 이동평균선 계산
        result = self.ma.calculate_ma(self.data)

        # 결과 데이터 타입 확인
        assert isinstance(result, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = ["MA5", "MA10", "MA30", "MA60"]
        for col in required_columns:
            assert col in result.columns

        # 계산 결과 검증
        # MA5는 5일째부터 값이 있어야 함
        assert pd.isna(result["MA5"].iloc[3])
        assert not pd.isna(result["MA5"].iloc[4])

        # MA10은 10일째부터 값이 있어야 함
        assert pd.isna(result["MA10"].iloc[8])
        assert not pd.isna(result["MA10"].iloc[9])

        # MA30은 30일째부터 값이 있어야 함
        assert pd.isna(result["MA30"].iloc[28])
        assert not pd.isna(result["MA30"].iloc[29])

        # MA60은 60일째부터 값이 있어야 함
        assert pd.isna(result["MA60"].iloc[58])
        assert not pd.isna(result["MA60"].iloc[59])

        # 수동 계산 결과와 비교
        ma5_manual = self.data["Close"].iloc[:5].mean()
        assert np.isclose(result["MA5"].iloc[4], ma5_manual)

    def test_calculate_ma_with_custom_periods(self):
        """
        사용자 정의 기간으로 이동평균선 계산 테스트
        """
        # 사용자 정의 기간으로 이동평균선 계산
        custom_periods = [3, 15]
        result = self.ma.calculate_ma(self.data, periods=custom_periods)

        # 필요한 열이 있는지 확인
        required_columns = ["MA3", "MA15"]
        for col in required_columns:
            assert col in result.columns

        # 기본 열이 없는지 확인
        default_columns = ["MA5", "MA10", "MA30", "MA60"]
        for col in default_columns:
            if col not in [f"MA{p}" for p in custom_periods]:
                assert col not in result.columns

        # 계산 결과 검증
        # MA3은 3일째부터 값이 있어야 함
        assert pd.isna(result["MA3"].iloc[1])
        assert not pd.isna(result["MA3"].iloc[2])

        # MA15는 15일째부터 값이 있어야 함
        assert pd.isna(result["MA15"].iloc[13])
        assert not pd.isna(result["MA15"].iloc[14])

    def test_calculate_ma_with_insufficient_data(self):
        """
        충분하지 않은 데이터로 이동평균선 계산 테스트
        """
        # 충분하지 않은 데이터로 이동평균선 계산 시 ValueError 발생 예상
        with pytest.raises(ValueError):
            self.ma.calculate_ma(self.insufficient_data)

    def test_calculate_ma5(self):
        """
        MA5 계산 테스트
        """
        # MA5 계산
        result = self.ma.calculate_ma5(self.data)

        # 필요한 열이 있는지 확인
        assert "MA5" in result.columns

        # 계산 결과 검증
        # MA5는 5일째부터 값이 있어야 함
        assert pd.isna(result["MA5"].iloc[3])
        assert not pd.isna(result["MA5"].iloc[4])

        # 수동 계산 결과와 비교
        ma5_manual = self.data["Close"].iloc[:5].mean()
        assert np.isclose(result["MA5"].iloc[4], ma5_manual)

    def test_calculate_ema(self):
        """
        지수 이동평균선 계산 테스트
        """
        # 지수 이동평균선 계산
        result = self.ma.calculate_ema(self.data)

        # 필요한 열이 있는지 확인
        required_columns = ["EMA12", "EMA26"]
        for col in required_columns:
            assert col in result.columns

        # 계산 결과 검증
        # EMA는 첫 번째 값부터 계산됨
        assert not pd.isna(result["EMA12"].iloc[0])
        assert not pd.isna(result["EMA26"].iloc[0])

    def test_calculate_crossovers(self):
        """
        크로스오버 계산 테스트
        """
        # 이동평균선 계산
        data_with_ma = self.ma.calculate_ma(self.data, periods=[5, 30])

        # 크로스오버 계산
        result = self.ma.calculate_crossovers(data_with_ma)

        # 필요한 열이 있는지 확인
        required_columns = ["golden_cross", "dead_cross"]
        for col in required_columns:
            assert col in result.columns

        # 크로스오버 결과는 불리언 값이어야 함
        assert result["golden_cross"].dtype == bool
        assert result["dead_cross"].dtype == bool


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
