"""
이동평균선 계산 모듈

이 모듈은 주식 데이터에 대한 다양한 이동평균선을 계산합니다.

설계 방향 및 원칙:
- 핵심 책임: 주식 데이터에 대한 이동평균선 계산
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 이동평균선 계산 기능만 담당
- 기술적 고려사항: 효율적인 계산을 위한 pandas 활용
- 사용 시 고려사항: 충분한 데이터 포인트 확보 필요 (예: MA60 계산 시 최소 60개 데이터 포인트 필요)
"""

import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MovingAverages:
    """
    이동평균선 계산 클래스

    이 클래스는 주식 데이터에 대한 다양한 이동평균선을 계산합니다.
    """

    def __init__(self):
        """
        MovingAverages 클래스 초기화
        """
        logger.info("MovingAverages 초기화")

    def calculate_ma(
        self, data: pd.DataFrame, column: str = "Close", periods: list = [5, 10, 30, 60]
    ) -> pd.DataFrame:
        """
        주어진 데이터에 대한 이동평균선을 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.
            periods (list, optional): 이동평균 기간 목록. 기본값은 [5, 10, 30, 60].

        Returns:
            pd.DataFrame: 이동평균선이 추가된 데이터프레임

        Raises:
            ValueError: 데이터가 충분하지 않은 경우
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 충분한 데이터가 있는지 확인
        max_period = max(periods)
        if len(data) < max_period:
            logger.warning(
                f"데이터가 충분하지 않습니다. 최소 {max_period}개의 데이터 포인트가 필요합니다."
            )
            raise ValueError(
                f"데이터가 충분하지 않습니다. 최소 {max_period}개의 데이터 포인트가 필요합니다."
            )

        # 각 기간에 대한 이동평균 계산
        for period in periods:
            column_name = f"MA{period}"
            logger.info(f"{column_name} 계산 중...")
            result[column_name] = result[column].rolling(window=period).mean()

        logger.info("이동평균선 계산 완료")
        return result

    def calculate_multiple(
        self, data: pd.DataFrame, periods: list, column: str = "Close"
    ) -> pd.DataFrame:
        """
        여러 기간의 이동평균선을 한 번에 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            periods (list): 이동평균 기간 목록 (예: [5, 10, 30, 60])
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: 이동평균선이 추가된 데이터프레임
        """
        logger.info(f"여러 이동평균선 계산 시작: {periods}")
        return self.calculate_ma(data, column, periods)

    def calculate_ma5(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        5일 이동평균선을 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: MA5가 추가된 데이터프레임
        """
        return self.calculate_ma(data, column, [5])

    def calculate_ma10(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        10일 이동평균선을 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: MA10이 추가된 데이터프레임
        """
        return self.calculate_ma(data, column, [10])

    def calculate_ma30(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        30일 이동평균선을 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: MA30이 추가된 데이터프레임
        """
        return self.calculate_ma(data, column, [30])

    def calculate_ma60(self, data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
        """
        60일 이동평균선을 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.

        Returns:
            pd.DataFrame: MA60이 추가된 데이터프레임
        """
        return self.calculate_ma(data, column, [60])

    def calculate_ema(
        self, data: pd.DataFrame, column: str = "Close", periods: list = [12, 26]
    ) -> pd.DataFrame:
        """
        지수 이동평균선(EMA)을 계산합니다.

        Args:
            data (pd.DataFrame): 주식 데이터
            column (str, optional): 이동평균을 계산할 열 이름. 기본값은 'Close'.
            periods (list, optional): 이동평균 기간 목록. 기본값은 [12, 26].

        Returns:
            pd.DataFrame: EMA가 추가된 데이터프레임
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 각 기간에 대한 지수 이동평균 계산
        for period in periods:
            column_name = f"EMA{period}"
            logger.info(f"{column_name} 계산 중...")
            result[column_name] = result[column].ewm(span=period, adjust=False).mean()

        logger.info("지수 이동평균선 계산 완료")
        return result

    def calculate_crossovers(
        self, data: pd.DataFrame, short_ma: str = "MA5", long_ma: str = "MA30"
    ) -> pd.DataFrame:
        """
        골든 크로스와 데드 크로스를 계산합니다.

        Args:
            data (pd.DataFrame): 이동평균선이 포함된 주식 데이터
            short_ma (str, optional): 단기 이동평균선 열 이름. 기본값은 'MA5'.
            long_ma (str, optional): 장기 이동평균선 열 이름. 기본값은 'MA30'.

        Returns:
            pd.DataFrame: 크로스오버 신호가 추가된 데이터프레임
        """
        # 데이터 복사본 생성
        result = data.copy()

        # 필요한 열이 있는지 확인
        if short_ma not in result.columns or long_ma not in result.columns:
            logger.error(f"필요한 열이 없습니다: {short_ma} 또는 {long_ma}")
            raise ValueError(f"필요한 열이 없습니다: {short_ma} 또는 {long_ma}")

        # 이전 날짜의 단기/장기 이동평균선 차이
        result["prev_diff"] = result[short_ma].shift(1) - result[long_ma].shift(1)

        # 현재 날짜의 단기/장기 이동평균선 차이
        result["curr_diff"] = result[short_ma] - result[long_ma]

        # 골든 크로스: 이전에는 단기 < 장기, 현재는 단기 > 장기
        result["golden_cross"] = (result["prev_diff"] < 0) & (result["curr_diff"] > 0)

        # 데드 크로스: 이전에는 단기 > 장기, 현재는 단기 < 장기
        result["dead_cross"] = (result["prev_diff"] > 0) & (result["curr_diff"] < 0)

        # 임시 열 제거
        result = result.drop(["prev_diff", "curr_diff"], axis=1)

        logger.info("크로스오버 계산 완료")
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

    # 이동평균선 계산
    ma = MovingAverages()
    result = ma.calculate_ma(data)

    # 결과 출력
    print(result.tail())
