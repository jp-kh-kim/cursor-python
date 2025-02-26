# 주식 데이터 분석 애플리케이션 Dockerfile
#
# 설계 방향 및 원칙:
# - 핵심 책임: Python 3.12 기반으로 주식 데이터 분석 애플리케이션을 컨테이너화
# - 설계 원칙: 경량화된 이미지, 재현 가능한 빌드, 보안 고려
# - 기술적 고려사항: Poetry를 통한 의존성 관리, 멀티 스테이지 빌드 적용
# - 사용 시 고려사항: 컨테이너 실행 시 포트 매핑 필요 (8501)

# 베이스 이미지로 Python 3.12 사용
FROM python:3.12-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Poetry 설정: 가상환경 생성하지 않음
RUN poetry config virtualenvs.create false

# 의존성 파일 복사
COPY pyproject.toml poetry.lock* ./

# 의존성 설치 (개발 의존성 제외)
# --no-dev 옵션이 더 이상 지원되지 않으므로 --only main 옵션으로 변경
RUN poetry install --only main --no-interaction --no-ansi

# 실행 이미지 구성
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치 (헬스체크를 위한 curl 추가)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 비루트 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

# builder 스테이지에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY src/ /app/src/
COPY streamlit/ /app/streamlit/
COPY tests/ /app/tests/
COPY docs/ /app/docs/

# 비루트 사용자로 전환
RUN chown -R appuser:appuser /app
USER appuser

# 환경 변수 설정
ENV PYTHONPATH=/app

# 포트 노출
EXPOSE 8501

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/healthz || exit 1

# 애플리케이션 실행
CMD ["streamlit", "run", "streamlit/app.py", "--server.address=0.0.0.0"] 