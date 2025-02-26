"""
MACD(Moving Average Convergence Divergence) 계산 모듈

이 모듈은 주식 데이터에 대한 MACD 지표를 계산합니다.

설계 방향 및 원칙:
- 핵심 책임: 주식 데이터에 대한 MACD 계산
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 MACD 계산 기능만 담당
- 기술적 고려사항: 효율적인 계산을 위한 pandas 활용
- 사용 시 고려사항: 충분한 데이터 포인트 확보 필요 (최소 26개 이상의 데이터 포인트 필요)
"""

import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MACD:
    """
    MACD 계산 클래스

    이 클래스는 주식 데이터에 대한 MACD(Moving Average Convergence Divergence) 지표를 계산합니다.
    """

    def __init__(
        self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
    ):
        """
        MACD 클래스 초기화

        Args:
            fast_period (int, optional): 단기 EMA 기간. 기본값은 12.
            slow_period (int, optional): 장기 EMA 기간. 기본값은 26.
            signal_period (int, optional): 시그널 라인 기간. 기본값은 9.
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        logger.info(
            f"MACD 초기화 (fast_period={fast_period}, slow_period={slow_period}, signal_period={signal_period})"
        )

    def calculate(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        주어진 데이터에 대한 MACD를 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): MACD를 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: MACD, Signal, Histogram이 추가된 데이터프레임

        Raises:
            ValueError: 데이터가 충분하지 않은 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 충분한 데이터가 있는지 확인
        min_periods = max(self.fast_period, self.slow_period) + self.signal_period
        if len(data) < min_periods:
            logger.warning(
                f"데이터가 충분하지 않습니다. 최소 {min_periods}개의 데이터 포인트가 필요합니다."
            )
            raise ValueError(
                f"데이터가 충분하지 않습니다. 최소 {min_periods}개의 데이터 포인트가 필요합니다."
            )

        # 단기 EMA 계산
        fast_ema = result[column].ewm(span=self.fast_period, adjust=False).mean()

        # 장기 EMA 계산
        slow_ema = result[column].ewm(span=self.slow_period, adjust=False).mean()

        # MACD 라인 계산 (단기 EMA - 장기 EMA)
        result["MACD"] = fast_ema - slow_ema

        # 시그널 라인 계산 (MACD의 EMA)
        result["MACD_Signal"] = (
            result["MACD"].ewm(span=self.signal_period, adjust=False).mean()
        )

        # 히스토그램 계산 (MACD - 시그널 라인)
        result["MACD_Histogram"] = result["MACD"] - result["MACD_Signal"]

        logger.info("MACD 계산 완료")
        return result

    def get_crossover_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 크로스오버 신호를 계산합니다.

        Args:
            data (pd.DataFrame): MACD가 포함된 주식 데이터

        Returns:
            pd.DataFrame: 매수/매도 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        required_columns = ["MACD", "MACD_Signal"]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 이전 날짜의 MACD와 시그널 라인 차이
        result["prev_diff"] = result["MACD"].shift(1) - result["MACD_Signal"].shift(1)

        # 현재 날짜의 MACD와 시그널 라인 차이
        result["curr_diff"] = result["MACD"] - result["MACD_Signal"]

        # 매수 신호: 이전에는 MACD < 시그널, 현재는 MACD > 시그널
        result["MACD_Buy_Signal"] = (result["prev_diff"] < 0) & (
            result["curr_diff"] > 0
        )

        # 매도 신호: 이전에는 MACD > 시그널, 현재는 MACD < 시그널
        result["MACD_Sell_Signal"] = (result["prev_diff"] > 0) & (
            result["curr_diff"] < 0
        )

        # 임시 열 제거
        result = result.drop(["prev_diff", "curr_diff"], axis=1)

        logger.info("MACD 크로스오버 신호 계산 완료")
        return result

    def get_zero_crossover_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD의 0선 크로스오버 신호를 계산합니다.

        Args:
            data (pd.DataFrame): MACD가 포함된 주식 데이터

        Returns:
            pd.DataFrame: 0선 크로스오버 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        if "MACD" not in result.columns:
            logger.error("필요한 열이 없습니다: MACD")
            raise ValueError("필요한 열이 없습니다: MACD")

        # 이전 날짜의 MACD
        result["prev_macd"] = result["MACD"].shift(1)

        # 0선 상향 돌파: 이전에는 MACD < 0, 현재는 MACD > 0
        result["MACD_Zero_Cross_Up"] = (result["prev_macd"] < 0) & (result["MACD"] > 0)

        # 0선 하향 돌파: 이전에는 MACD > 0, 현재는 MACD < 0
        result["MACD_Zero_Cross_Down"] = (result["prev_macd"] > 0) & (
            result["MACD"] < 0
        )

        # 임시 열 제거
        result = result.drop(["prev_macd"], axis=1)

        logger.info("MACD 0선 크로스오버 신호 계산 완료")
        return result

    def get_divergence(
        self, data: pd.DataFrame, price_column: str = "Close", window: int = 10
    ) -> pd.DataFrame:
        """
        MACD 다이버전스를 계산합니다.

        Args:
            data (pd.DataFrame): MACD가 포함된 주식 데이터
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
        required_columns = ["MACD", price_column]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 다이버전스 계산을 위한 준비
        result["price_diff"] = result[price_column].diff(window)
        result["macd_diff"] = result["MACD"].diff(window)

        # 불리시 다이버전스: 가격은 하락하지만 MACD는 상승
        result["MACD_Bullish_Divergence"] = (result["price_diff"] < 0) & (
            result["macd_diff"] > 0
        )

        # 베어리시 다이버전스: 가격은 상승하지만 MACD는 하락
        result["MACD_Bearish_Divergence"] = (result["price_diff"] > 0) & (
            result["macd_diff"] < 0
        )

        # 임시 열 제거
        result = result.drop(["price_diff", "macd_diff"], axis=1)

        logger.info("MACD 다이버전스 계산 완료")
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

    # MACD 계산
    macd = MACD()
    result = macd.calculate(data)

    # 크로스오버 신호 계산
    result = macd.get_crossover_signals(result)

    # 결과 출력
    print(
        result[
            [
                "Close",
                "MACD",
                "MACD_Signal",
                "MACD_Histogram",
                "MACD_Buy_Signal",
                "MACD_Sell_Signal",
            ]
        ].tail()
    )
