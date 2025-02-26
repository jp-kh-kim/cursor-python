"""
주식 데이터 수집 모듈

이 모듈은 yfinance를 사용하여 주어진 Ticker에 대한 주식 데이터를 수집합니다.

설계 방향 및 원칙:
- 핵심 책임: 주식 데이터 수집 및 전처리
- 설계 원칙: 단일 책임 원칙(SRP)에 따라 데이터 수집 기능만 담당
- 기술적 고려사항: yfinance API 호출 제한 고려
- 사용 시 고려사항: 유효하지 않은 Ticker 처리, 네트워크 오류 처리
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockCollector:
    """
    주식 데이터 수집기 클래스
    
    이 클래스는 yfinance를 사용하여 주어진 Ticker에 대한 주식 데이터를 수집합니다.
    """
    
    def __init__(self):
        """
        StockCollector 클래스 초기화
        """
        logger.info("StockCollector 초기화")
    
    def get_stock_data(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """
        주어진 Ticker에 대한 주식 데이터를 수집합니다.
        
        Args:
            ticker (str): 주식 심볼 (예: 'AAPL')
            days (int, optional): 현재로부터 가져올 과거 데이터의 일수. 기본값은 365일.
            
        Returns:
            pd.DataFrame: 주식 데이터 (Open, High, Low, Close, Volume 포함)
            
        Raises:
            ValueError: 유효하지 않은 Ticker가 제공된 경우
            ConnectionError: 네트워크 오류가 발생한 경우
        """
        logger.info(f"{ticker} 데이터 수집 시작 (기간: {days}일)")
        
        try:
            # 시작 날짜와 종료 날짜 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # yfinance를 사용하여 데이터 다운로드
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            # 데이터가 비어있는지 확인
            if data.empty:
                raise ValueError(f"'{ticker}'에 대한 데이터를 찾을 수 없습니다.")
            
            # 필요한 열만 선택 (Open, High, Low, Close, Volume)
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            logger.info(f"{ticker} 데이터 수집 완료: {len(data)}개 행")
            return data
            
        except ValueError as e:
            logger.error(f"유효하지 않은 Ticker: {e}")
            raise
        except Exception as e:
            logger.error(f"데이터 수집 중 오류 발생: {e}")
            raise ConnectionError(f"데이터 수집 중 오류 발생: {e}")
    
    def get_stock_info(self, ticker: str) -> dict:
        """
        주어진 Ticker에 대한 기본 정보를 수집합니다.
        
        Args:
            ticker (str): 주식 심볼 (예: 'AAPL')
            
        Returns:
            dict: 주식 기본 정보 (회사명, 섹터, 산업 등)
            
        Raises:
            ValueError: 유효하지 않은 Ticker가 제공된 경우
            ConnectionError: 네트워크 오류가 발생한 경우
        """
        logger.info(f"{ticker} 기본 정보 수집 시작")
        
        try:
            # yfinance를 사용하여 정보 가져오기
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 필요한 정보만 선택
            selected_info = {
                'name': info.get('shortName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'website': info.get('website', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'currency': info.get('currency', 'USD')
            }
            
            logger.info(f"{ticker} 기본 정보 수집 완료")
            return selected_info
            
        except Exception as e:
            logger.error(f"정보 수집 중 오류 발생: {e}")
            raise ConnectionError(f"정보 수집 중 오류 발생: {e}")


# 모듈 사용 예시
if __name__ == "__main__":
    collector = StockCollector()
    
    try:
        # 애플 주식 데이터 가져오기 (최근 30일)
        apple_data = collector.get_stock_data("AAPL", days=30)
        print(apple_data.head())
        
        # 애플 기본 정보 가져오기
        apple_info = collector.get_stock_info("AAPL")
        print(apple_info)
        
    except Exception as e:
        print(f"오류 발생: {e}") 