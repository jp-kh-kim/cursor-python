"""
주식 데이터 분석 및 시각화 애플리케이션

이 애플리케이션은 yfinance를 통해 주식 데이터를 수집하고, 다양한 기술적 지표를 계산하여
Streamlit을 통해 시각화하는 데모 프로젝트입니다.

설계 방향 및 원칙:
- 핵심 책임: 사용자가 선택한 주식 데이터를 수집하고 기술적 지표와 함께 시각화
- 설계 원칙: 단일 페이지 애플리케이션, 사용자 친화적 UI
- 기술적 고려사항: Streamlit의 위젯을 활용한 인터랙티브 요소 구현
- 사용 시 고려사항: 네트워크 연결 필요, yfinance API 제한 고려
"""

import streamlit as st
import pandas as pd
import sys
import os
import json
from datetime import datetime, timedelta
from streamlit_searchbox import st_searchbox

# Plotly 라이브러리 임포트
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 백엔드 모듈 임포트
from src.be.data.stock_collector import StockCollector
from src.be.data.index_components import IndexComponents
from src.be.indicators.moving_averages import MovingAverages
from src.be.indicators.macd import MACD
from src.be.indicators.bollinger_bands import BollingerBands
from src.be.indicators.rsi import RSI
from src.be.indicators.stochastic import StochasticSlow


def main():
    """
    메인 애플리케이션 함수
    """
    # 페이지 설정
    st.set_page_config(page_title="주식 데이터 분석", page_icon="📈", layout="wide")

    # 제목 및 설명
    st.title("📈 주식 데이터 분석 애플리케이션")
    st.markdown("""
    이 애플리케이션은 선택한 주식의 과거 데이터를 분석하고 다양한 기술적 지표를 시각화합니다.
    원하는 주식 심볼과 기간을 선택하고, 보고 싶은 기술적 지표를 체크하세요.
    """)

    # 사이드바 - 입력 파라미터
    with st.sidebar:
        st.header("설정")

        # 지수 선택
        index_options = ["직접 입력", "S&P 500", "NASDAQ 100"]
        selected_index = st.selectbox("지수 선택", index_options)

        # 지수 구성 종목 로드
        if selected_index != "직접 입력":
            with st.spinner(f"{selected_index} 구성 종목 로드 중..."):
                try:
                    index_components = IndexComponents()
                    if selected_index == "S&P 500":
                        components_df = index_components.get_sp500_components()
                    else:  # NASDAQ 100
                        components_df = index_components.get_nasdaq100_components()

                    # 전체 종목 수 표시
                    total_components = len(components_df)
                    st.write(f"전체 {total_components}개 종목")

                    # 검색 함수 정의
                    def search_companies(search_term):
                        if not search_term:
                            return []

                        # 검색어가 있으면 필터링
                        filtered_df = components_df[
                            components_df["Symbol"].str.contains(
                                search_term, case=False
                            )
                            | components_df["Name"].str.contains(
                                search_term, case=False
                            )
                        ]

                        # 검색 결과 반환
                        return [
                            f"{row['Symbol']} - {row['Name']}"
                            for _, row in filtered_df.iterrows()
                        ]

                    # 검색 가능한 드롭다운 구현
                    selected_option = st_searchbox(
                        search_function=search_companies,
                        placeholder="종목 검색 (심볼 또는 기업명)...",
                        label="기업 선택",
                        key="company_searchbox",
                    )

                    # 선택된 옵션이 있으면 처리
                    if selected_option:
                        # 선택된 옵션에서 티커만 추출
                        ticker = selected_option.split(" - ")[0]

                        # 선택된 종목 정보 표시
                        try:
                            selected_info = components_df[
                                components_df["Symbol"] == ticker
                            ].iloc[0]
                            st.info(
                                f"선택된 종목: {selected_info['Symbol']} - {selected_info['Name']}"
                            )
                        except:
                            st.info(f"선택된 종목: {ticker}")
                    else:
                        # 기본값 설정
                        default_ticker = components_df.iloc[0]["Symbol"]
                        ticker = default_ticker
                        st.info(
                            f"기본 종목: {default_ticker} - {components_df.iloc[0]['Name']}"
                        )

                except Exception as e:
                    st.error(f"지수 구성 종목 로드 실패: {str(e)}")
                    ticker = st.text_input("주식 심볼 입력", "AAPL")

        else:
            ticker = st.text_input("주식 심볼 입력", "AAPL")

        # 기간 선택
        days = st.slider(
            "조회 기간 (일)", min_value=30, max_value=365 * 2, value=365, step=30
        )

        # 기술적 지표 선택
        st.subheader("기술적 지표 선택")
        show_ma = st.checkbox("이동평균선 (MA)", value=True)

        if show_ma:
            col1, col2 = st.columns(2)
            with col1:
                show_ma5 = st.checkbox("MA5", value=True)
                show_ma10 = st.checkbox("MA10", value=True)
            with col2:
                show_ma30 = st.checkbox("MA30", value=True)
                show_ma60 = st.checkbox("MA60", value=False)
        else:
            show_ma5 = show_ma10 = show_ma30 = show_ma60 = False

        show_macd = st.checkbox("MACD", value=False)
        show_bollinger = st.checkbox("볼린저 밴드", value=False)
        show_rsi = st.checkbox("RSI", value=False)
        show_stochastic = st.checkbox("스토캐스틱 슬로우", value=False)

        # 데이터 로드 버튼
        load_data = st.button("데이터 로드")

    # 메인 컨텐츠
    if "load_data" in locals() and load_data:
        # 데이터 로드 중 표시
        with st.spinner(f"{ticker} 데이터를 로드 중입니다..."):
            try:
                # 주식 데이터 수집
                collector = StockCollector()
                stock_data = collector.get_stock_data(ticker, days)

                # 주식 정보 가져오기
                try:
                    stock_info = collector.get_stock_info(ticker)
                    st.subheader(
                        f"{stock_info.get('name', ticker)} ({ticker}) - {stock_info.get('sector', 'N/A')}"
                    )
                except:
                    st.subheader(f"{ticker} 주식 데이터")

                # 기술적 지표 계산
                data = stock_data.copy()

                # 이동평균선 계산
                if show_ma:
                    ma = MovingAverages()
                    periods = []
                    if show_ma5:
                        periods.append(5)
                    if show_ma10:
                        periods.append(10)
                    if show_ma30:
                        periods.append(30)
                    if show_ma60:
                        periods.append(60)

                    if periods:
                        data = ma.calculate_multiple(data, periods)

                # MACD 계산
                if show_macd:
                    macd = MACD()
                    data = macd.calculate(data)

                # 볼린저 밴드 계산
                if show_bollinger:
                    bb = BollingerBands()
                    data = bb.calculate(data)

                # RSI 계산
                if show_rsi:
                    rsi = RSI()
                    data = rsi.calculate(data)

                # 스토캐스틱 슬로우 계산
                if show_stochastic:
                    stoch = StochasticSlow()
                    data = stoch.calculate(data)

                # 차트 생성
                st.subheader("주가 차트")

                # Plotly 차트 생성
                create_stock_chart(
                    data,
                    show_ma5,
                    show_ma10,
                    show_ma30,
                    show_ma60,
                    show_bollinger,
                    show_macd,
                    show_rsi,
                    show_stochastic,
                )

                # 데이터 테이블 표시
                with st.expander("데이터 테이블"):
                    st.dataframe(data)

                # 기술적 지표 설명
                with st.expander("기술적 지표 설명"):
                    display_indicator_descriptions()

            except Exception as e:
                st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")


def create_stock_chart(
    data,
    show_ma5,
    show_ma10,
    show_ma30,
    show_ma60,
    show_bollinger,
    show_macd,
    show_rsi,
    show_stochastic,
):
    """
    Plotly를 사용하여 주식 차트를 생성합니다.

    Args:
        data (pd.DataFrame): 주식 데이터 및 기술적 지표
        show_ma5 (bool): MA5 표시 여부
        show_ma10 (bool): MA10 표시 여부
        show_ma30 (bool): MA30 표시 여부
        show_ma60 (bool): MA60 표시 여부
        show_bollinger (bool): 볼린저 밴드 표시 여부
        show_macd (bool): MACD 표시 여부
        show_rsi (bool): RSI 표시 여부
        show_stochastic (bool): 스토캐스틱 슬로우 표시 여부
    """
    # 서브플롯 생성
    rows = 2  # 기본 행 수 (주가 차트 + 거래량)

    # 추가 지표에 따라 행 수 증가
    if show_macd:
        rows += 1
    if show_rsi:
        rows += 1
    if show_stochastic:
        rows += 1

    # 행 높이 설정
    row_heights = [0.6, 0.2]  # 주가 차트 60%, 거래량 20%

    # 추가 지표에 따라 행 높이 추가
    if show_macd:
        row_heights.append(0.2)
    if show_rsi:
        row_heights.append(0.2)
    if show_stochastic:
        row_heights.append(0.2)

    # 서브플롯 제목 설정
    subplot_titles = ["주가", "거래량"]
    if show_macd:
        subplot_titles.append("MACD")
    if show_rsi:
        subplot_titles.append("RSI")
    if show_stochastic:
        subplot_titles.append("스토캐스틱")

    # 서브플롯 생성
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    # 캔들스틱 차트 추가
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="주가",
            increasing_line_color="red",
            decreasing_line_color="blue",
        ),
        row=1,
        col=1,
    )

    # 이동평균선 추가
    if show_ma5 and "MA5" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MA5"],
                name="MA5",
                line=dict(color="#FF5733", width=1),
            ),
            row=1,
            col=1,
        )

    if show_ma10 and "MA10" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MA10"],
                name="MA10",
                line=dict(color="#33FF57", width=1),
            ),
            row=1,
            col=1,
        )

    if show_ma30 and "MA30" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MA30"],
                name="MA30",
                line=dict(color="#3357FF", width=1),
            ),
            row=1,
            col=1,
        )

    if show_ma60 and "MA60" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MA60"],
                name="MA60",
                line=dict(color="#FF33A8", width=1),
            ),
            row=1,
            col=1,
        )

    # 볼린저 밴드 추가
    if show_bollinger and "Upper_Band" in data.columns and "Lower_Band" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Upper_Band"],
                name="상단 밴드",
                line=dict(color="rgba(76, 175, 80, 0.5)", width=1),
                fill=None,
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Middle_Band"],
                name="중간 밴드",
                line=dict(color="rgba(76, 175, 80, 1)", width=1),
                fill=None,
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Lower_Band"],
                name="하단 밴드",
                line=dict(color="rgba(76, 175, 80, 0.5)", width=1),
                fill="tonexty",
            ),
            row=1,
            col=1,
        )

    # 거래량 차트 추가
    colors = [
        "red" if row["Close"] >= row["Open"] else "blue" for _, row in data.iterrows()
    ]

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="거래량",
            marker=dict(color=colors, opacity=0.5),
        ),
        row=2,
        col=1,
    )

    # MACD 차트 추가
    if show_macd and "MACD" in data.columns and "Signal" in data.columns:
        current_row = 3

        # MACD 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MACD"],
                name="MACD",
                line=dict(color="#2196F3", width=1),
            ),
            row=current_row,
            col=1,
        )

        # Signal 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Signal"],
                name="Signal",
                line=dict(color="#FF5722", width=1),
            ),
            row=current_row,
            col=1,
        )

        # Histogram
        colors = ["red" if val >= 0 else "blue" for val in data["Histogram"]]

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Histogram"],
                name="Histogram",
                marker=dict(color=colors, opacity=0.5),
            ),
            row=current_row,
            col=1,
        )

    # RSI 차트 추가
    if show_rsi and "RSI" in data.columns:
        current_row = 3 + (1 if show_macd else 0)

        # RSI 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["RSI"],
                name="RSI",
                line=dict(color="#9C27B0", width=1),
            ),
            row=current_row,
            col=1,
        )

        # 과매수/과매도 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[70] * len(data),
                name="과매수",
                line=dict(color="rgba(244, 67, 54, 0.5)", width=1, dash="dash"),
            ),
            row=current_row,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[30] * len(data),
                name="과매도",
                line=dict(color="rgba(76, 175, 80, 0.5)", width=1, dash="dash"),
            ),
            row=current_row,
            col=1,
        )

    # 스토캐스틱 슬로우 차트 추가
    if show_stochastic and "%K" in data.columns and "%D" in data.columns:
        current_row = 3 + (1 if show_macd else 0) + (1 if show_rsi else 0)

        # %K 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["%K"],
                name="%K",
                line=dict(color="#2196F3", width=1),
            ),
            row=current_row,
            col=1,
        )

        # %D 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["%D"],
                name="%D",
                line=dict(color="#FF5722", width=1),
            ),
            row=current_row,
            col=1,
        )

        # 과매수/과매도 라인
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[80] * len(data),
                name="과매수",
                line=dict(color="rgba(244, 67, 54, 0.5)", width=1, dash="dash"),
            ),
            row=current_row,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[20] * len(data),
                name="과매도",
                line=dict(color="rgba(76, 175, 80, 0.5)", width=1, dash="dash"),
            ),
            row=current_row,
            col=1,
        )

    # 레이아웃 설정
    fig.update_layout(
        title="주식 차트",
        xaxis_title="날짜",
        yaxis_title="가격",
        height=800,
        width=1200,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # X축 범위 설정
    fig.update_xaxes(
        rangeslider_visible=False,
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # 주말 제외
        ],
    )

    # 차트 표시
    st.plotly_chart(fig, use_container_width=True)


def display_indicator_descriptions():
    """
    기술적 지표에 대한 설명을 표시합니다.
    """
    st.markdown("""
    ### 이동평균선 (Moving Average)
    이동평균선은 일정 기간 동안의 주가 평균을 나타내는 지표로, 주가의 추세를 파악하는 데 사용됩니다.
    - **MA5**: 5일 이동평균선으로, 단기 추세를 나타냅니다.
    - **MA10**: 10일 이동평균선으로, 단기 추세를 나타냅니다.
    - **MA30**: 30일 이동평균선으로, 중기 추세를 나타냅니다.
    - **MA60**: 60일 이동평균선으로, 중장기 추세를 나타냅니다.
    
    **해석**: 단기 이동평균선이 장기 이동평균선을 상향 돌파하면 매수 신호, 하향 돌파하면 매도 신호로 해석할 수 있습니다.
    
    ### MACD (Moving Average Convergence Divergence)
    MACD는 단기 이동평균선과 장기 이동평균선의 차이를 나타내는 지표로, 추세의 방향과 강도를 파악하는 데 사용됩니다.
    - **MACD 라인**: 12일 EMA - 26일 EMA
    - **Signal 라인**: MACD의 9일 EMA
    - **Histogram**: MACD 라인 - Signal 라인
    
    **해석**: MACD 라인이 Signal 라인을 상향 돌파하면 매수 신호, 하향 돌파하면 매도 신호로 해석할 수 있습니다.
    
    ### 볼린저 밴드 (Bollinger Bands)
    볼린저 밴드는 주가의 변동성을 기반으로 한 지표로, 주가의 상대적인 고가와 저가를 파악하는 데 사용됩니다.
    - **상단 밴드**: 20일 이동평균선 + (20일 표준편차 × 2)
    - **중간 밴드**: 20일 이동평균선
    - **하단 밴드**: 20일 이동평균선 - (20일 표준편차 × 2)
    
    **해석**: 주가가 상단 밴드에 접근하면 과매수, 하단 밴드에 접근하면 과매도로 해석할 수 있습니다.
    
    ### RSI (Relative Strength Index)
    RSI는 주가의 상승 압력과 하락 압력의 상대적인 강도를 나타내는 지표로, 과매수/과매도 상태를 파악하는 데 사용됩니다.
    - **계산 방법**: RSI = 100 - (100 / (1 + RS)), RS = 평균 상승폭 / 평균 하락폭
    - **기간**: 일반적으로 14일 사용
    
    **해석**: RSI가 70 이상이면 과매수, 30 이하면 과매도로 해석할 수 있습니다.
    
    ### 스토캐스틱 슬로우 (Stochastic Slow)
    스토캐스틱 슬로우는 주가의 현재 위치가 일정 기간 동안의 가격 범위 내에서 어디에 위치하는지를 나타내는 지표입니다.
    - **%K**: (현재 종가 - n일 중 최저가) / (n일 중 최고가 - n일 중 최저가) × 100의 m일 이동평균
    - **%D**: %K의 d일 이동평균
    - **일반적인 설정**: n=14, m=3, d=3
    
    **해석**: %K가 %D를 상향 돌파하면 매수 신호, 하향 돌파하면 매도 신호로 해석할 수 있습니다. 또한, 80 이상이면 과매수, 20 이하면 과매도로 해석할 수 있습니다.
    """)


if __name__ == "__main__":
    main()
