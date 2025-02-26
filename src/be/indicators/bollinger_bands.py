"""
볼린저 밴드 계산 모듈

이 모듈은 주식 데이터에 대한 볼린저 밴드를 계산합니다.

설계 방향 및 원칙:
- 핵심 책임: 주식 데이터에 대한 볼린저 밴드 계산
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 볼린저 밴드 계산 기능만 담당
- 기술적 고려사항: 효율적인 계산을 위한 pandas 활용
- 사용 시 고려사항: 충분한 데이터 포인트 확보 필요 (최소 20개 이상의 데이터 포인트 필요)
"""

import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BollingerBands:
    """
    볼린저 밴드 계산 클래스

    이 클래스는 주식 데이터에 대한 볼린저 밴드를 계산합니다.
    """

    def __init__(self, window: int = 20, num_std: float = 2.0):
        """
        BollingerBands 클래스 초기화

        Args:
            window (int, optional): 이동평균 기간. 기본값은 20.
            num_std (float, optional): 표준편차 배수. 기본값은 2.0.
        """
        self.window = window
        self.num_std = num_std
        logger.info(f"BollingerBands 초기화 (window={window}, num_std={num_std})")

    def calculate(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        주어진 데이터에 대한 볼린저 밴드를 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 볼린저 밴드를 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: 볼린저 밴드가 추가된 데이터프레임

        Raises:
            ValueError: 데이터가 충분하지 않은 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 충분한 데이터가 있는지 확인
        if len(data) < self.window:
            logger.warning(
                f"데이터가 충분하지 않습니다. 최소 {self.window}개의 데이터 포인트가 필요합니다."
            )
            raise ValueError(
                f"데이터가 충분하지 않습니다. 최소 {self.window}개의 데이터 포인트가 필요합니다."
            )

        # 중간 밴드 계산 (이동평균)
        result["BB_Middle"] = result[column].rolling(window=self.window).mean()

        # 표준편차 계산
        std = result[column].rolling(window=self.window).std()

        # 상단 밴드 계산 (중간 밴드 + num_std * 표준편차)
        result["BB_Upper"] = result["BB_Middle"] + (std * self.num_std)

        # 하단 밴드 계산 (중간 밴드 - num_std * 표준편차)
        result["BB_Lower"] = result["BB_Middle"] - (std * self.num_std)

        # 밴드폭 계산 ((상단 밴드 - 하단 밴드) / 중간 밴드)
        result["BB_Width"] = (result["BB_Upper"] - result["BB_Lower"]) / result[
            "BB_Middle"
        ]

        # %B 계산 ((종가 - 하단 밴드) / (상단 밴드 - 하단 밴드))
        result["BB_PercentB"] = (result[column] - result["BB_Lower"]) / (
            result["BB_Upper"] - result["BB_Lower"]
        )

        logger.info("볼린저 밴드 계산 완료")
        return result

    def get_signals(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        볼린저 밴드 기반 매매 신호를 계산합니다.

        Args:
            data (pd.DataFrame): 볼린저 밴드가 포함된 주식 데이터
            column (str, optional): 가격 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: 매매 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        required_columns = ["BB_Upper", "BB_Middle", "BB_Lower", column]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 이전 날짜의 가격
        result["prev_close"] = result[column].shift(1)

        # 매수 신호: 이전에는 가격이 하단 밴드 아래, 현재는 하단 밴드 위
        result["BB_Buy_Signal"] = (
            result["prev_close"] < result["BB_Lower"].shift(1)
        ) & (result[column] > result["BB_Lower"])

        # 매도 신호: 이전에는 가격이 상단 밴드 위, 현재는 상단 밴드 아래
        result["BB_Sell_Signal"] = (
            result["prev_close"] > result["BB_Upper"].shift(1)
        ) & (result[column] < result["BB_Upper"])

        # 스퀴즈 신호: 밴드폭이 좁아지는 경우 (변동성 감소)
        result["BB_Squeeze"] = (
            result["BB_Width"] < result["BB_Width"].rolling(window=20).mean()
        )

        # 임시 열 제거
        result = result.drop(["prev_close"], axis=1)

        logger.info("볼린저 밴드 신호 계산 완료")
        return result

    def get_breakout_signals(
        self, data: pd.DataFrame, column: str = "Close", threshold: float = 0.05
    ) -> pd.DataFrame:
        """
        볼린저 밴드 돌파 신호를 계산합니다.

        Args:
            data (pd.DataFrame): 볼린저 밴드가 포함된 주식 데이터
            column (str, optional): 가격 열 이름. 기본값은 'Close'.
            threshold (float, optional): 돌파 임계값. 기본값은 0.05 (5%).

        Returns:
            pd.DataFrame: 돌파 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        required_columns = ["BB_Upper", "BB_Lower", column]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 상단 밴드 돌파 비율 계산
        result["upper_breakout_ratio"] = (result[column] - result["BB_Upper"]) / result[
            "BB_Upper"
        ]

        # 하단 밴드 돌파 비율 계산
        result["lower_breakout_ratio"] = (result["BB_Lower"] - result[column]) / result[
            "BB_Lower"
        ]

        # 상단 밴드 돌파 신호
        result["BB_Upper_Breakout"] = result["upper_breakout_ratio"] > threshold

        # 하단 밴드 돌파 신호
        result["BB_Lower_Breakout"] = result["lower_breakout_ratio"] > threshold

        # 임시 열 제거
        result = result.drop(["upper_breakout_ratio", "lower_breakout_ratio"], axis=1)

        logger.info("볼린저 밴드 돌파 신호 계산 완료")
        return result


# 모듈 사용 예시
if __name__ == "__main__":
    # 샘플 데이터 생성
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = pd.DataFrame(
        {
            "Open": np.random.normal(100, 5, size=100),
            "High": np.random.normal(105, 5, size=100),
            "Low": np.random.normal(95, 5, size=100),
            "Close": np.random.normal(100, 5, size=100),
            "Volume": np.random.normal(1000000, 200000, size=100),
        },
        index=dates,
    )

    # 볼린저 밴드 계산
    bb = BollingerBands()
    result = bb.calculate(data)

    # 매매 신호 계산
    result = bb.get_signals(result)

    # 결과 출력
    print(
        result[
            [
                "Close",
                "BB_Upper",
                "BB_Middle",
                "BB_Lower",
                "BB_Width",
                "BB_PercentB",
                "BB_Buy_Signal",
                "BB_Sell_Signal",
            ]
        ].tail()
    )
