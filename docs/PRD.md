# Stock Analysis (DEMO)

본 프로젝트는 데모 프로젝트로서, 파이썬 개발을 소개하기 위한 목적으로 구상되었습니다.
따라서, API 통신과 같이 실무 레벨에서 중점적으로 고려되어야 하는 사항들은 구현하지 않습니다.

기본적인 기능은 `src/be` 이하의 폴더에 구현하고자 하며, 최종적으로 기능 구현이 완료되었다면 streamlit으로 서빙하는 것을 목적으로 합니다.

# Functionalities

- Ticker가 주어졌을 때, 주식 데이터를 수집하는 기능 구현
- 인자로 현재로부터 <DAYS> 이전의 값들을 전부 가져올 수 있도록 함
    - 수집하는 데이터는 Open, High, Low, Close, Volume
- 수집한 데이터로 핵심 주식 지표를 연산하는 기능 구현
    - MA5, MA10, MA30, MA60
    - MACD
    - Bollinger Band
    - RSI
    - Stochastic Slow

# `src/be`

Streamlit에서 사용될 함수들을 전반적으로 구현한 코드베이스

# `streamlit`
Streamlit 구현이 작성 될 페이지.
페이지는 다음과 같은 구성을 지님

## 구성
    - Single Page로 구성
    - 주식 조회 기능 :: Params -> Ticker(Default='AAPL'), Days(Default=365)
    - 각 보조지표에 대한 주식 거래 측면에서의 설명 (웹에서 수집 할 것)
    - 차트 렌더링
        - 보조지표들을 포함해서 한번에 렌더 할 수 있어야 함
        - 보조지표들은 체크박스로 선택 할 수 있어야 함