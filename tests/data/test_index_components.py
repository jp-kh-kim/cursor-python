"""
주요 지수 구성 종목 수집기 테스트 모듈

이 모듈은 IndexComponents 클래스의 기능을 테스트합니다.

설계 방향 및 원칙:
- 핵심 책임: IndexComponents 클래스의 기능 검증
- 설계 원칙: 단위 테스트 원칙에 따라 독립적인 테스트 케이스 작성
- 기술적 고려사항: pytest 프레임워크 활용
- 사용 시 고려사항: 캐시 관련 기능 테스트
"""

import pytest
import pandas as pd
import os
import json
import shutil
from datetime import datetime, timedelta
from src.be.data.index_components import IndexComponents
from unittest.mock import patch, MagicMock


class TestIndexComponents:
    """
    IndexComponents 클래스 테스트
    """

    def setup_method(self):
        """
        각 테스트 메서드 실행 전 설정
        """
        # 테스트용 캐시 디렉토리 생성
        self.test_cache_dir = os.path.join(os.path.dirname(__file__), "test_cache")
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
        os.makedirs(self.test_cache_dir)

        # IndexComponents 인스턴스 생성
        self.index_components = IndexComponents(cache_dir=self.test_cache_dir)

    def teardown_method(self):
        """
        각 테스트 메서드 실행 후 정리
        """
        # 테스트용 캐시 디렉토리 삭제
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_init(self):
        """
        IndexComponents 초기화 테스트
        """
        assert isinstance(self.index_components, IndexComponents)
        assert os.path.exists(self.test_cache_dir)

        # 사용자 정의 파라미터로 초기화
        custom_components = IndexComponents(
            cache_dir=self.test_cache_dir, cache_expiry_days=14
        )
        assert custom_components.cache_expiry_days == 14

    def test_get_sp500_components(self):
        """
        S&P 500 구성 종목 목록 조회 테스트
        """
        # S&P 500 구성 종목 목록 조회
        components = self.index_components.get_sp500_components()

        # 결과 데이터 타입 확인
        assert isinstance(components, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = ["Symbol", "Name"]
        for col in required_columns:
            assert col in components.columns

        # 데이터가 비어있지 않은지 확인
        assert not components.empty

        # 캐시 파일이 생성되었는지 확인
        cache_file = os.path.join(self.test_cache_dir, "sp500_components.json")
        assert os.path.exists(cache_file)

    def test_get_nasdaq100_components(self):
        """
        NASDAQ 100 구성 종목 목록 조회 테스트
        """
        # NASDAQ 100 구성 종목 목록 조회
        components = self.index_components.get_nasdaq100_components()

        # 결과 데이터 타입 확인
        assert isinstance(components, pd.DataFrame)

        # 필요한 열이 있는지 확인
        required_columns = ["Symbol", "Name"]
        for col in required_columns:
            assert col in components.columns

        # 데이터가 비어있지 않은지 확인
        assert not components.empty

        # 캐시 파일이 생성되었는지 확인
        cache_file = os.path.join(self.test_cache_dir, "nasdaq100_components.json")
        assert os.path.exists(cache_file)

    def test_cache_loading(self):
        """
        캐시 로딩 테스트
        """
        # 첫 번째 호출 - 캐시 생성
        components1 = self.index_components.get_sp500_components()

        # _fetch_components 메서드를 모킹하여 두 번째 호출에서는 호출되지 않도록 함
        with patch.object(self.index_components, "_fetch_components") as mock_fetch:
            # 두 번째 호출 - 캐시에서 로드
            components2 = self.index_components.get_sp500_components()

            # _fetch_components가 호출되지 않았는지 확인
            mock_fetch.assert_not_called()

        # 두 결과가 동일한지 확인
        pd.testing.assert_frame_equal(components1, components2)

    def test_cache_expiry(self):
        """
        캐시 만료 테스트
        """
        # 첫 번째 호출 - 캐시 생성
        components1 = self.index_components.get_sp500_components()

        # 캐시 파일 경로
        cache_file = os.path.join(self.test_cache_dir, "sp500_components.json")

        # 캐시 파일의 수정 시간을 8일 전으로 변경 (기본 만료 기간은 7일)
        old_time = datetime.now() - timedelta(days=8)
        os.utime(cache_file, (old_time.timestamp(), old_time.timestamp()))

        # _fetch_components 메서드를 모킹
        with patch.object(self.index_components, "_fetch_components") as mock_fetch:
            # 모의 반환값 설정
            mock_data = pd.DataFrame(
                {
                    "Symbol": ["TEST1", "TEST2"],
                    "Name": ["Test Company 1", "Test Company 2"],
                }
            )
            mock_fetch.return_value = mock_data

            # 두 번째 호출 - 캐시가 만료되어 새로 가져와야 함
            components2 = self.index_components.get_sp500_components()

            # _fetch_components가 호출되었는지 확인
            mock_fetch.assert_called_once_with("sp500")

        # 두 결과가 다른지 확인
        assert not components1.equals(components2)
        assert list(components2["Symbol"]) == ["TEST1", "TEST2"]

    def test_invalid_cache_handling(self):
        """
        유효하지 않은 캐시 처리 테스트
        """
        # 캐시 파일 경로
        cache_file = os.path.join(self.test_cache_dir, "sp500_components.json")

        # 유효하지 않은 JSON 데이터로 캐시 파일 생성
        with open(cache_file, "w") as f:
            f.write('{"invalid_json":')

        # 캐시 로드 시 오류가 발생하고 _fetch_components가 호출되어야 함
        with patch.object(self.index_components, "_fetch_components") as mock_fetch:
            # 모의 반환값 설정
            mock_data = pd.DataFrame(
                {
                    "Symbol": ["TEST1", "TEST2"],
                    "Name": ["Test Company 1", "Test Company 2"],
                }
            )
            mock_fetch.return_value = mock_data

            # 캐시가 유효하지 않아 새로 가져와야 함
            components = self.index_components.get_sp500_components()

            # _fetch_components가 호출되었는지 확인
            mock_fetch.assert_called_once_with("sp500")

        # 결과 확인
        assert list(components["Symbol"]) == ["TEST1", "TEST2"]

        # 캐시 파일이 다시 생성되었는지 확인
        assert os.path.exists(cache_file)


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main(["-xvs", __file__])
