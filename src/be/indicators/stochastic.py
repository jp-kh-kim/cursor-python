"""
스토캐스틱 슬로우 계산 모듈

이 모듈은 주식 데이터에 대한 스토캐스틱 슬로우 지표를 계산합니다.

설계 방향 및 원칙:
- 핵심 책임: 주식 데이터에 대한 스토캐스틱 슬로우 계산
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 스토캐스틱 슬로우 계산 기능만 담당
- 기술적 고려사항: 효율적인 계산을 위한 pandas 활용
- 사용 시 고려사항: 충분한 데이터 포인트 확보 필요 (최소 14개 이상의 데이터 포인트 필요)
"""

import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StochasticSlow:
    """
    스토캐스틱 슬로우 계산 클래스

    이 클래스는 주식 데이터에 대한 스토캐스틱 슬로우 지표를 계산합니다.
    """

    def __init__(self, k_period: int = 14, d_period: int = 3, slowing: int = 3):
        """
        StochasticSlow 클래스 초기화

        Args:
            k_period (int, optional): %K 계산 기간. 기본값은 14.
            d_period (int, optional): %D 계산 기간. 기본값은 3.
            slowing (int, optional): 슬로잉 기간. 기본값은 3.
        """
        self.k_period = k_period
        self.d_period = d_period
        self.slowing = slowing
        logger.info(
            f"StochasticSlow 초기화 (k_period={k_period}, d_period={d_period}, slowing={slowing})"
        )

    def calculate(
        self,
        data: pd.DataFrame,
        high_column: str = "High",
        low_column: str = "Low",
        close_column: str = "Close",
    ) -> pd.DataFrame:
        """
        주어진 데이터에 대한 스토캐스틱 슬로우를 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            high_column (str, optional): 고가 열 이름. 기본값은 'High'.
            low_column (str, optional): 저가 열 이름. 기본값은 'Low'.
            close_column (str, optional): 종가 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: 스토캐스틱 슬로우가 추가된 데이터프레임

        Raises:
            ValueError: 데이터가 충분하지 않은 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 충분한 데이터가 있는지 확인
        min_periods = self.k_period + self.slowing + self.d_period - 2
        if len(data) < min_periods:
            logger.warning(
                f"데이터가 충분하지 않습니다. 최소 {min_periods}개의 데이터 포인트가 필요합니다."
            )
            raise ValueError(
                f"데이터가 충분하지 않습니다. 최소 {min_periods}개의 데이터 포인트가 필요합니다."
            )

        # 필요한 열이 있는지 확인
        required_columns = [high_column, low_column, close_column]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 최근 k_period 기간 동안의 최고가
        high_max = result[high_column].rolling(window=self.k_period).max()

        # 최근 k_period 기간 동안의 최저가
        low_min = result[low_column].rolling(window=self.k_period).min()

        # %K 계산 (Fast Stochastic): ((종가 - 최저가) / (최고가 - 최저가)) * 100
        result["%K_Fast"] = (
            (result[close_column] - low_min) / (high_max - low_min)
        ) * 100

        # %K 슬로잉 (Slow Stochastic): %K_Fast의 slowing 기간 이동평균
        result["%K"] = result["%K_Fast"].rolling(window=self.slowing).mean()

        # %D 계산: %K의 d_period 이동평균
        result["%D"] = result["%K"].rolling(window=self.d_period).mean()

        logger.info("스토캐스틱 슬로우 계산 완료")
        return result

    def get_signals(
        self, data: pd.DataFrame, overbought: float = 80, oversold: float = 20
    ) -> pd.DataFrame:
        """
        스토캐스틱 슬로우 기반 매매 신호를 계산합니다.

        Args:
            data (pd.DataFrame): 스토캐스틱 슬로우가 포함된 주식 데이터
            overbought (float, optional): 과매수 기준값. 기본값은 80.
            oversold (float, optional): 과매도 기준값. 기본값은 20.

        Returns:
            pd.DataFrame: 매매 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        required_columns = ["%K", "%D"]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 이전 날짜의 %K와 %D
        result["prev_k"] = result["%K"].shift(1)
        result["prev_d"] = result["%D"].shift(1)

        # 매수 신호 1: %K가 %D를 상향 돌파
        result["Stoch_Buy_Signal_1"] = (result["prev_k"] < result["prev_d"]) & (
            result["%K"] > result["%D"]
        )

        # 매수 신호 2: %K와 %D가 모두 과매도 영역에서 상승
        result["Stoch_Buy_Signal_2"] = (
            (result["prev_k"] < oversold)
            & (result["%K"] > result["prev_k"])
            & (result["prev_d"] < oversold)
            & (result["%D"] > result["prev_d"])
        )

        # 매도 신호 1: %K가 %D를 하향 돌파
        result["Stoch_Sell_Signal_1"] = (result["prev_k"] > result["prev_d"]) & (
            result["%K"] < result["%D"]
        )

        # 매도 신호 2: %K와 %D가 모두 과매수 영역에서 하락
        result["Stoch_Sell_Signal_2"] = (
            (result["prev_k"] > overbought)
            & (result["%K"] < result["prev_k"])
            & (result["prev_d"] > overbought)
            & (result["%D"] < result["prev_d"])
        )

        # 임시 열 제거
        result = result.drop(["prev_k", "prev_d"], axis=1)

        logger.info("스토캐스틱 슬로우 신호 계산 완료")
        return result

    def get_divergence(
        self, data: pd.DataFrame, price_column: str = "Close", window: int = 10
    ) -> pd.DataFrame:
        """
        스토캐스틱 슬로우 다이버전스를 계산합니다.

        Args:
            data (pd.DataFrame): 스토캐스틱 슬로우가 포함된 주식 데이터
            price_column (str, optional): 가격 열 이름. 기본값은 'Close'.
            window (int, optional): 다이버전스를 확인할 기간. 기본값은 10.

        Returns:
            pd.DataFrame: 다이버전스 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        required_columns = ["%K", price_column]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 다이버전스 계산을 위한 준비
        result["price_diff"] = result[price_column].diff(window)
        result["stoch_diff"] = result["%K"].diff(window)

        # 불리시 다이버전스: 가격은 하락하지만 스토캐스틱은 상승
        result["Stoch_Bullish_Divergence"] = (result["price_diff"] < 0) & (
            result["stoch_diff"] > 0
        )

        # 베어리시 다이버전스: 가격은 상승하지만 스토캐스틱은 하락
        result["Stoch_Bearish_Divergence"] = (result["price_diff"] > 0) & (
            result["stoch_diff"] < 0
        )

        # 임시 열 제거
        result = result.drop(["price_diff", "stoch_diff"], axis=1)

        logger.info("스토캐스틱 슬로우 다이버전스 계산 완료")
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

    # 스토캐스틱 슬로우 계산
    stoch = StochasticSlow()
    result = stoch.calculate(data)

    # 매매 신호 계산
    result = stoch.get_signals(result)

    # 결과 출력
    print(
        result[
            ["Close", "%K", "%D", "Stoch_Buy_Signal_1", "Stoch_Sell_Signal_1"]
        ].tail()
    )
