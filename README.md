# 주식 데이터 분석 애플리케이션

이 프로젝트는 yfinance를 통해 주식 데이터를 수집하고, 다양한 기술적 지표를 계산하여 Streamlit을 통해 시각화하는 데모 애플리케이션입니다.

## 기능

- 주식 데이터 수집 (yfinance 활용)
- 기술적 지표 계산 (이동평균선, MACD, 볼린저 밴드, RSI, 스토캐스틱 슬로우)
- 주요 지수 구성 종목 목록 제공 (S&P500, NASDAQ 100)
- 인터랙티브 차트 시각화 (Plotly 활용)

## 기술 스택

- **언어**: Python 3.12
- **패키지 관리자**: Poetry
- **프론트엔드 프레임워크**: Streamlit
- **데이터 처리**: Pandas
- **데이터 수집**: yfinance
- **시각화**: Plotly

## 설치 및 실행 방법

### 로컬 환경에서 실행

1. 저장소 클론
   ```bash
   git clone <repository-url>
   cd cursor-python-implementation
   ```

2. Poetry를 사용하여 의존성 설치
   ```bash
   poetry install
   ```

3. 애플리케이션 실행
   ```bash
   poetry run streamlit run streamlit/app.py
   ```

### Docker를 사용하여 실행

#### Docker Compose 사용 (권장)

1. Docker Compose를 사용하여 애플리케이션 실행
   ```bash
   docker-compose up -d
   ```

2. 애플리케이션 접속
   - 웹 브라우저에서 `http://localhost:8501` 접속

#### Dockerfile 직접 사용

1. Docker 이미지 빌드
   ```bash
   docker build -t stock-analysis-app .
   ```

2. Docker 컨테이너 실행
   ```bash
   docker run -d -p 8501:8501 --name stock-analysis-app stock-analysis-app
   ```

3. 애플리케이션 접속
   - 웹 브라우저에서 `http://localhost:8501` 접속

## 사용 방법

1. 사이드바에서 주식 심볼 선택 또는 직접 입력
   - S&P 500 또는 NASDAQ 100 지수에서 기업 선택 가능
   - 직접 주식 심볼 입력 가능 (예: AAPL, MSFT, GOOGL)

2. 조회 기간 설정
   - 슬라이더를 사용하여 30일부터 730일(2년)까지 설정 가능

3. 기술적 지표 선택
   - 이동평균선 (MA5, MA10, MA30, MA60)
   - MACD
   - 볼린저 밴드
   - RSI
   - 스토캐스틱 슬로우

4. "데이터 로드" 버튼 클릭
   - 선택한 주식의 데이터와 기술적 지표가 차트로 표시됨

## 프로젝트 구조

```
.
├── docs/               # 문서 (PRD, Spec 등)
├── src/                # 소스 코드
│   └── be/             # 백엔드 로직
│       ├── data/       # 데이터 수집 및 처리 관련 모듈
│       └── indicators/ # 기술적 지표 계산 모듈
├── streamlit/          # Streamlit 애플리케이션
├── tests/              # 테스트 코드
├── Dockerfile          # Docker 이미지 빌드 파일
├── docker-compose.yml  # Docker Compose 설정 파일
└── pyproject.toml      # 프로젝트 의존성 및 설정
```

## 개발 환경 설정

### 개발 의존성 설치

```bash
# 최신 Poetry 버전에서는 --with 옵션을 사용합니다
poetry install --with dev
```

### 테스트 실행

```bash
poetry run pytest
```

## 문제 해결

### Docker 빌드 오류

Poetry 2.0 이상에서는 `--no-dev` 옵션이 더 이상 지원되지 않습니다. 대신 `--only main` 옵션을 사용해야 합니다.

```bash
# 오류가 발생하는 명령어
poetry install --no-dev

# 올바른 명령어
poetry install --only main
```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.