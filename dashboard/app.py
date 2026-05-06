import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Solar Financing Landscape",
    page_icon="☀️",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'DM Mono', monospace; }
    
    .metric-card {
        background: #0f1117;
        border: 1px solid #2d2d2d;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .stMetric { background: #0f1117; border: 1px solid #2d2d2d; border-radius: 8px; padding: 15px; }
</style>
""", unsafe_allow_html=True)


# DB connection
@st.cache_resource
def get_engine():
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', 5433)
    password = os.getenv('DB_PASSWORD')
    return create_engine(f'postgresql://postgres:{password}@{host}:{port}/solar_financing')


@st.cache_data
def load_data():
    engine = get_engine()
    
    revenue = pd.read_sql("""
        SELECT ticker, period_date, revenue, gross_profit, net_income,
            ROUND(gross_profit / NULLIF(revenue, 0) * 100, 2) AS gross_margin_pct,
            ROUND(net_income / NULLIF(revenue, 0) * 100, 2) AS net_margin_pct,
            ROUND(
                (revenue - LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date))
                / NULLIF(LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date), 0) * 100, 1
            ) AS yoy_growth_pct
        FROM income_statements WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """, engine)

    stock = pd.read_sql("""
        SELECT ticker, date, close FROM stock_prices ORDER BY ticker, date
    """, engine)

    debt = pd.read_sql("""
        SELECT ticker, period_date, total_debt, total_equity,
            ROUND(total_debt / NULLIF(total_equity, 0), 2) AS debt_to_equity
        FROM balance_sheets WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """, engine)

    fcf = pd.read_sql("""
        SELECT ticker, period_date, operating_cash_flow, free_cash_flow
        FROM cash_flows WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """, engine)

    return revenue, stock, debt, fcf


# Load data
revenue_df, stock_df, debt_df, fcf_df = load_data()

# Colors
COLORS = {'RUN': '#f59e0b', 'ENPH': '#10b981', 'SPWR': '#6366f1'}

# Header
st.title("☀️ Solar Financing Landscape")
st.markdown("**Financial analysis of US residential solar companies**")
st.markdown("🟡 **RUN** — Sunrun Inc. &nbsp;&nbsp; 🟢 **ENPH** — Enphase Energy &nbsp;&nbsp; 🟣 **SPWR** — SunPower Corporation")
st.divider()

# KPI cards
col1, col2, col3 = st.columns(3)
for col, ticker in zip([col1, col2, col3], ['RUN', 'ENPH', 'SPWR']):
    latest = revenue_df[revenue_df['ticker'] == ticker].dropna(subset=['revenue']).iloc[-1]
    with col:
        st.metric(
            label=f"**{ticker}** Latest Revenue",
            value=f"${latest['revenue']/1e9:.2f}B",
            delta=f"{latest['net_margin_pct']:.1f}% net margin"
        )

st.divider()

# Charts
tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue", "💰 Profitability", "📊 Stock Price", "⚖️ Debt & Cash Flow"])

with tab1:
    df = revenue_df.dropna(subset=['revenue'])
    fig = px.line(df, x='period_date', y='revenue', color='ticker',
                  color_discrete_map=COLORS, markers=True,
                  title='Annual Revenue Comparison')
    fig.update_layout(template='plotly_dark', yaxis_tickformat='$,.0f')
    st.plotly_chart(fig, use_container_width=True)

    fig_yoy = px.bar(revenue_df.dropna(subset=['yoy_growth_pct']), x='period_date', y='yoy_growth_pct',
                     color='ticker', color_discrete_map=COLORS, barmode='group',
                     title='Year-over-Year Revenue Growth (%)')
    fig_yoy.update_layout(
        template='plotly_dark',
        yaxis=dict(ticksuffix='%'),
        xaxis_title='Year',
        yaxis_title='YoY Growth'
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

with tab2:
    df = revenue_df.dropna(subset=['net_income'])
    fig = px.bar(df, x='period_date', y='net_income', color='ticker',
                 color_discrete_map=COLORS, barmode='group',
                 title='Net Income by Year')
    fig.update_layout(template='plotly_dark', yaxis_tickformat='$,.0f')
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(df.dropna(subset=['net_margin_pct']), x='period_date', y='net_margin_pct',
                   color='ticker', color_discrete_map=COLORS, markers=True,
                   title='Net Profit Margin (%)')
    fig2.update_layout(
        template='plotly_dark',
        yaxis=dict(
            ticksuffix='%',
            dtick=25,
            range=[-150, 50]
        ),
        xaxis_title='Year',
        yaxis_title='Net Margin'
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(revenue_df.dropna(subset=['gross_margin_pct']), x='period_date', y='gross_margin_pct',
                   color='ticker', color_discrete_map=COLORS, markers=True,
                   title='Gross Margin (%)')
    fig3.update_layout(
        template='plotly_dark',
        yaxis=dict(ticksuffix='%'),
        xaxis_title='Year',
        yaxis_title='Gross Margin'
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    fig = px.line(stock_df, x='date', y='close', color='ticker',
                  color_discrete_map=COLORS, title='Stock Price History (2019–2026)')
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        df = debt_df.dropna(subset=['debt_to_equity'])
        fig = px.line(df, x='period_date', y='debt_to_equity', color='ticker',
                      color_discrete_map=COLORS, markers=True,
                      title='Debt-to-Equity Ratio')
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        df = fcf_df.dropna(subset=['free_cash_flow'])
        fig = px.bar(df, x='period_date', y='free_cash_flow', color='ticker',
                     color_discrete_map=COLORS, barmode='group',
                     title='Free Cash Flow')
        fig.update_layout(template='plotly_dark', yaxis_tickformat='$,.0f')
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data sourced from Yahoo Finance via yfinance · Built with Streamlit + PostgreSQL")
