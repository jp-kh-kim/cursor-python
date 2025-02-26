"""
주요 지수 구성 종목 수집 모듈

이 모듈은 S&P500, NASDAQ 100 지수의 구성 종목 목록을 수집합니다.

설계 방향 및 원칙:
- 핵심 책임: 주요 지수 구성 종목 목록 수집 및 캐싱
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 지수 구성 종목 수집 기능만 담당
- 기술적 고려사항: 데이터 캐싱을 통한 API 호출 최소화
- 사용 시 고려사항: 네트워크 오류 처리, 데이터 형식 오류 처리
"""

import pandas as pd
import yfinance as yf
import logging
import os
import json
import requests
import bs4 as bs
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IndexComponents:
    """
    주요 지수 구성 종목 수집기 클래스

    이 클래스는 S&P500, NASDAQ 100 지수의 구성 종목 목록을 수집하고 캐싱합니다.
    """

    def __init__(self, cache_dir: str = None, cache_expiry_days: int = 7):
        """
        IndexComponents 클래스 초기화

        Args:
            cache_dir (str, optional): 캐시 파일을 저장할 디렉토리. 기본값은 None으로, 현재 디렉토리에 저장.
            cache_expiry_days (int, optional): 캐시 만료 기간(일). 기본값은 7일.
        """
        logger.info("IndexComponents 초기화")
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "cache")
        self.cache_expiry_days = cache_expiry_days

        # 캐시 디렉토리가 없으면 생성
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # 지수 심볼 매핑
        self.index_symbols = {
            "sp500": "^GSPC",  # S&P 500
            "nasdaq100": "^NDX",  # NASDAQ 100
        }

    def get_sp500_components(self) -> pd.DataFrame:
        """
        S&P 500 지수 구성 종목 목록을 반환합니다.

        Returns:
            pd.DataFrame: 티커와 기업명이 포함된 DataFrame

        Raises:
            ConnectionError: 네트워크 오류가 발생한 경우
            ValueError: 데이터 형식 오류가 발생한 경우
        """
        logger.info("S&P 500 구성 종목 목록 조회")
        return self._get_components("sp500")

    def get_nasdaq100_components(self) -> pd.DataFrame:
        """
        NASDAQ 100 지수 구성 종목 목록을 반환합니다.

        Returns:
            pd.DataFrame: 티커와 기업명이 포함된 DataFrame

        Raises:
            ConnectionError: 네트워크 오류가 발생한 경우
            ValueError: 데이터 형식 오류가 발생한 경우
        """
        logger.info("NASDAQ 100 구성 종목 목록 조회")
        return self._get_components("nasdaq100")

    def _get_components(self, index_name: str) -> pd.DataFrame:
        """
        지정된 지수의 구성 종목 목록을 반환합니다.

        Args:
            index_name (str): 지수 이름 ('sp500' 또는 'nasdaq100')

        Returns:
            pd.DataFrame: 티커와 기업명이 포함된 DataFrame
        """
        # 캐시 파일 경로
        cache_file = os.path.join(self.cache_dir, f"{index_name}_components.json")

        # 캐시 파일이 있고 만료되지 않았으면 캐시에서 로드
        if os.path.exists(cache_file) and self._is_cache_valid(cache_file):
            logger.info(f"{index_name} 구성 종목 목록을 캐시에서 로드")
            try:
                return self._load_from_cache(cache_file)
            except Exception as e:
                logger.error(f"캐시 로드 실패, 새로 데이터를 가져옵니다: {str(e)}")
                # 캐시 로드 실패 시 새로 가져옴

        # 캐시가 없거나 만료되었거나 로드 실패 시 새로 가져옴
        logger.info(f"{index_name} 구성 종목 목록을 새로 가져옴")
        components = self._fetch_components(index_name)

        # 캐시에 저장
        self._save_to_cache(components, cache_file)

        return components

    def _fetch_components(self, index_name: str) -> pd.DataFrame:
        """
        지정된 지수의 구성 종목 목록을 가져옵니다.

        Args:
            index_name (str): 지수 이름 ('sp500' 또는 'nasdaq100')

        Returns:
            pd.DataFrame: 티커와 기업명이 포함된 DataFrame
        """
        try:
            if index_name == "sp500":
                # S&P 500 구성 종목 목록을 위키피디아에서 가져옴
                resp = requests.get(
                    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
                )
                soup = bs.BeautifulSoup(resp.text, "lxml")
                table = soup.find("table", {"class": "wikitable sortable"})

                tickers = []
                names = []

                for row in table.findAll("tr")[1:]:
                    cells = row.findAll("td")
                    ticker = cells[0].text.strip()
                    name = cells[1].text.strip()
                    tickers.append(ticker)
                    names.append(name)

                data = {"Symbol": tickers, "Name": names}

                logger.info(f"S&P 500 구성 종목 {len(tickers)}개 가져오기 성공")

            elif index_name == "nasdaq100":
                # NASDAQ 100 구성 종목 목록을 위키피디아에서 가져옴
                resp = requests.get("https://en.wikipedia.org/wiki/Nasdaq-100")
                soup = bs.BeautifulSoup(resp.text, "lxml")
                table = soup.find("table", {"class": "wikitable sortable"})

                tickers = []
                names = []

                for row in table.findAll("tr")[1:]:
                    cells = row.findAll("td")
                    if len(cells) >= 2:  # 최소 2개의 셀이 있는지 확인
                        ticker = cells[1].text.strip()
                        name = cells[0].text.strip()
                        tickers.append(ticker)
                        names.append(name)

                data = {"Symbol": tickers, "Name": names}

                logger.info(f"NASDAQ 100 구성 종목 {len(tickers)}개 가져오기 성공")

            else:
                raise ValueError(f"지원되지 않는 지수: {index_name}")

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"{index_name} 구성 종목 목록 가져오기 실패: {str(e)}")

            # 오류 발생 시 기본 데이터 반환 (예시 데이터)
            if index_name == "sp500":
                data = {
                    "Symbol": [
                        "AAPL",
                        "MSFT",
                        "AMZN",
                        "GOOGL",
                        "META",
                        "TSLA",
                        "NVDA",
                        "BRK-B",
                        "JPM",
                        "JNJ",
                    ],
                    "Name": [
                        "Apple Inc.",
                        "Microsoft Corporation",
                        "Amazon.com Inc.",
                        "Alphabet Inc.",
                        "Meta Platforms Inc.",
                        "Tesla Inc.",
                        "NVIDIA Corporation",
                        "Berkshire Hathaway Inc.",
                        "JPMorgan Chase & Co.",
                        "Johnson & Johnson",
                    ],
                }
                logger.warning("S&P 500 구성 종목 가져오기 실패, 예시 데이터 사용")
            elif index_name == "nasdaq100":
                data = {
                    "Symbol": [
                        "AAPL",
                        "MSFT",
                        "AMZN",
                        "GOOGL",
                        "META",
                        "TSLA",
                        "NVDA",
                        "ADBE",
                        "PYPL",
                        "INTC",
                    ],
                    "Name": [
                        "Apple Inc.",
                        "Microsoft Corporation",
                        "Amazon.com Inc.",
                        "Alphabet Inc.",
                        "Meta Platforms Inc.",
                        "Tesla Inc.",
                        "NVIDIA Corporation",
                        "Adobe Inc.",
                        "PayPal Holdings Inc.",
                        "Intel Corporation",
                    ],
                }
                logger.warning("NASDAQ 100 구성 종목 가져오기 실패, 예시 데이터 사용")

            return pd.DataFrame(data)

    def _is_cache_valid(self, cache_file: str) -> bool:
        """
        캐시 파일이 유효한지 확인합니다.

        Args:
            cache_file (str): 캐시 파일 경로

        Returns:
            bool: 캐시가 유효하면 True, 그렇지 않으면 False
        """
        # 파일 수정 시간 확인
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        expiry_time = datetime.now() - timedelta(days=self.cache_expiry_days)

        return mod_time > expiry_time

    def _load_from_cache(self, cache_file: str) -> pd.DataFrame:
        """
        캐시 파일에서 데이터를 로드합니다.

        Args:
            cache_file (str): 캐시 파일 경로

        Returns:
            pd.DataFrame: 캐시에서 로드한 DataFrame
        """
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"캐시 로드 실패: {str(e)}")
            # 캐시 로드 실패 시 캐시 파일 삭제
            if os.path.exists(cache_file):
                os.remove(cache_file)
            raise

    def _save_to_cache(self, df: pd.DataFrame, cache_file: str) -> None:
        """
        데이터를 캐시 파일에 저장합니다.

        Args:
            df (pd.DataFrame): 저장할 DataFrame
            cache_file (str): 캐시 파일 경로
        """
        try:
            with open(cache_file, "w") as f:
                json.dump(df.to_dict(orient="records"), f)

            logger.info(f"캐시 저장 완료: {cache_file}")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {str(e)}")
