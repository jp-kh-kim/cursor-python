"""
RSI(Relative Strength Index) 계산 모듈

이 모듈은 주식 데이터에 대한 RSI 지표를 계산합니다.

설계 방향 및 원칙:
- 핵심 책임: 주식 데이터에 대한 RSI 계산
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 RSI 계산 기능만 담당
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


class RSI:
    """
    RSI 계산 클래스

    이 클래스는 주식 데이터에 대한 RSI(Relative Strength Index) 지표를 계산합니다.
    """

    def __init__(self, period: int = 14):
        """
        RSI 클래스 초기화

        Args:
            period (int, optional): RSI 계산 기간. 기본값은 14.
        """
        self.period = period
        logger.info(f"RSI 초기화 (period={period})")

    def calculate(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        주어진 데이터에 대한 RSI를 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): RSI를 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: RSI가 추가된 데이터프레임

        Raises:
            ValueError: 데이터가 충분하지 않은 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 충분한 데이터가 있는지 확인
        if len(data) < self.period + 1:
            logger.warning(
                f"데이터가 충분하지 않습니다. 최소 {self.period + 1}개의 데이터 포인트가 필요합니다."
            )
            raise ValueError(
                f"데이터가 충분하지 않습니다. 최소 {self.period + 1}개의 데이터 포인트가 필요합니다."
            )

        # 가격 변화 계산
        delta = result[column].diff()

        # 상승과 하락 분리
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 첫 번째 평균 계산
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()

        # 이후 평균 계산 (Wilder의 스무딩 방법)
        # avg_gain = (이전 avg_gain * (period - 1) + 현재 gain) / period
        # avg_loss = (이전 avg_loss * (period - 1) + 현재 loss) / period
        for i in range(self.period + 1, len(result)):
            avg_gain.iloc[i] = (
                avg_gain.iloc[i - 1] * (self.period - 1) + gain.iloc[i]
            ) / self.period
            avg_loss.iloc[i] = (
                avg_loss.iloc[i - 1] * (self.period - 1) + loss.iloc[i]
            ) / self.period

        # 상대적 강도(RS) 계산
        rs = avg_gain / avg_loss

        # RSI 계산: 100 - (100 / (1 + RS))
        result["RSI"] = 100 - (100 / (1 + rs))

        logger.info("RSI 계산 완료")
        return result

    def calculate_simple(
        self, data: pd.DataFrame, column: str = "Close"
    ) -> pd.DataFrame:
        """
        간단한 방법으로 RSI를 계산합니다 (pandas의 rolling 함수만 사용).

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): RSI를 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: RSI가 추가된 데이터프레임
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 가격 변화 계산
        delta = result[column].diff()

        # 상승과 하락 분리
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 평균 계산 (단순 이동평균)
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()

        # 상대적 강도(RS) 계산
        rs = avg_gain / avg_loss

        # RSI 계산: 100 - (100 / (1 + RS))
        result["RSI_Simple"] = 100 - (100 / (1 + rs))

        logger.info("간단한 RSI 계산 완료")
        return result

    def get_signals(
        self, data: pd.DataFrame, overbought: float = 70, oversold: float = 30
    ) -> pd.DataFrame:
        """
        RSI 기반 매매 신호를 계산합니다.

        Args:
            data (pd.DataFrame): RSI가 포함된 주식 데이터
            overbought (float, optional): 과매수 기준값. 기본값은 70.
            oversold (float, optional): 과매도 기준값. 기본값은 30.

        Returns:
            pd.DataFrame: 매매 신호가 추가된 데이터프레임

        Raises:
            ValueError: 필요한 열이 없는 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        if "RSI" not in result.columns:
            logger.error("필요한 열이 없습니다: RSI")
            raise ValueError("필요한 열이 없습니다: RSI")

        # 이전 날짜의 RSI
        result["prev_rsi"] = result["RSI"].shift(1)

        # 매수 신호: 이전에는 RSI < 과매도, 현재는 RSI > 과매도
        result["RSI_Buy_Signal"] = (result["prev_rsi"] < oversold) & (
            result["RSI"] > oversold
        )

        # 매도 신호: 이전에는 RSI > 과매수, 현재는 RSI < 과매수
        result["RSI_Sell_Signal"] = (result["prev_rsi"] > overbought) & (
            result["RSI"] < overbought
        )

        # 임시 열 제거
        result = result.drop(["prev_rsi"], axis=1)

        logger.info("RSI 신호 계산 완료")
        return result

    def get_divergence(
        self, data: pd.DataFrame, price_column: str = "Close", window: int = 10
    ) -> pd.DataFrame:
        """
        RSI 다이버전스를 계산합니다.

        Args:
            data (pd.DataFrame): RSI가 포함된 주식 데이터
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
        required_columns = ["RSI", price_column]
        for col in required_columns:
            if col not in result.columns:
                logger.error(f"필요한 열이 없습니다: {col}")
                raise ValueError(f"필요한 열이 없습니다: {col}")

        # 다이버전스 계산을 위한 준비
        result["price_diff"] = result[price_column].diff(window)
        result["rsi_diff"] = result["RSI"].diff(window)

        # 불리시 다이버전스: 가격은 하락하지만 RSI는 상승
        result["RSI_Bullish_Divergence"] = (result["price_diff"] < 0) & (
            result["rsi_diff"] > 0
        )

        # 베어리시 다이버전스: 가격은 상승하지만 RSI는 하락
        result["RSI_Bearish_Divergence"] = (result["price_diff"] > 0) & (
            result["rsi_diff"] < 0
        )

        # 임시 열 제거
        result = result.drop(["price_diff", "rsi_diff"], axis=1)

        logger.info("RSI 다이버전스 계산 완료")
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

    # RSI 계산
    rsi = RSI()
    result = rsi.calculate(data)

    # 매매 신호 계산
    result = rsi.get_signals(result)

    # 결과 출력
    print(result[["Close", "RSI", "RSI_Buy_Signal", "RSI_Sell_Signal"]].tail())
