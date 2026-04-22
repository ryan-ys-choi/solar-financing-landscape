"""
Solar Financing Landscape — Streamlit dashboard.

Pulls from the Postgres container spun up by docker-compose and surfaces
the five analyses already defined in scripts/analyze.py:

    1. Revenue trends (with YoY growth)
    2. Profitability (net margin)
    3. Stock performance
    4. Debt levels (debt-to-equity)
    5. Free cash flow

Run locally (against Dockerized Postgres on :5433):
    streamlit run dashboard/app.py

Run inside Docker (compose service "dashboard"):
    docker compose up dashboard
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# DB_HOST defaults to "localhost" for local dev; docker-compose overrides it
# to "postgres" (the service name) so the container talks to the DB container.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "solar_financing")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

TICKER_LABELS = {
    "RUN": "Sunrun (RUN)",
    "ENPH": "Enphase Energy (ENPH)",
    "SPWR": "SunPower (SPWR)",
}
TICKER_COLORS = {"RUN": "#F7941D", "ENPH": "#00A651", "SPWR": "#0072CE"}


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------
@st.cache_resource
def get_engine():
    url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=300)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(sql, engine, params=params or {})


def tickers_in_clause(tickers: list[str]) -> tuple[str, dict]:
    """Build a safe parameterized IN (...) clause for SQLAlchemy."""
    if not tickers:
        return "('')", {}
    keys = [f"t{i}" for i in range(len(tickers))]
    placeholders = ", ".join(f":{k}" for k in keys)
    return f"({placeholders})", dict(zip(keys, tickers))


# ---------------------------------------------------------------------------
# Queries (mirror scripts/analyze.py)
# ---------------------------------------------------------------------------
def q_revenue_trends(tickers):
    in_clause, params = tickers_in_clause(tickers)
    return run_query(
        f"""
        SELECT
            ticker,
            period_date,
            revenue,
            ROUND(
                (revenue - LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date))
                / NULLIF(LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date), 0) * 100, 2
            ) AS yoy_growth_pct
        FROM income_statements
        WHERE period_type = 'annual' AND ticker IN {in_clause}
        ORDER BY ticker, period_date
        """,
        params,
    )


def q_profitability(tickers):
    in_clause, params = tickers_in_clause(tickers)
    return run_query(
        f"""
        SELECT
            ticker,
            period_date,
            revenue,
            net_income,
            ROUND(net_income::numeric / NULLIF(revenue, 0) * 100, 2) AS net_margin_pct
        FROM income_statements
        WHERE period_type = 'annual' AND ticker IN {in_clause}
        ORDER BY ticker, period_date
        """,
        params,
    )


def q_stock_performance(tickers):
    in_clause, params = tickers_in_clause(tickers)
    return run_query(
        f"""
        SELECT
            ticker,
            date,
            close,
            volume
        FROM stock_prices
        WHERE ticker IN {in_clause}
        ORDER BY ticker, date
        """,
        params,
    )


def q_debt_levels(tickers):
    in_clause, params = tickers_in_clause(tickers)
    return run_query(
        f"""
        SELECT
            ticker,
            period_date,
            total_debt,
            total_equity,
            ROUND(total_debt::numeric / NULLIF(total_equity, 0), 2) AS debt_to_equity
        FROM balance_sheets
        WHERE period_type = 'annual' AND ticker IN {in_clause}
        ORDER BY ticker, period_date
        """,
        params,
    )


def q_free_cash_flow(tickers):
    in_clause, params = tickers_in_clause(tickers)
    return run_query(
        f"""
        SELECT
            ticker,
            period_date,
            operating_cash_flow,
            capital_expenditure,
            free_cash_flow
        FROM cash_flows
        WHERE period_type = 'annual' AND ticker IN {in_clause}
        ORDER BY ticker, period_date
        """,
        params,
    )


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def _empty_state(msg: str = "No data for the selected tickers."):
    st.info(msg)


def _color_map(df):
    return {t: TICKER_COLORS.get(t, None) for t in df["ticker"].unique()}


def render_revenue_tab(tickers):
    st.subheader("Annual revenue & YoY growth")
    df = q_revenue_trends(tickers)
    if df.empty:
        return _empty_state()
    df["period_date"] = pd.to_datetime(df["period_date"])
    df["revenue_b"] = df["revenue"] / 1e9

    fig = px.bar(
        df,
        x="period_date",
        y="revenue_b",
        color="ticker",
        barmode="group",
        labels={"revenue_b": "Revenue (USD billions)", "period_date": "Fiscal year"},
        color_discrete_map=_color_map(df),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("YoY revenue growth (%)")
    fig2 = px.line(
        df.dropna(subset=["yoy_growth_pct"]),
        x="period_date",
        y="yoy_growth_pct",
        color="ticker",
        markers=True,
        labels={"yoy_growth_pct": "YoY growth (%)", "period_date": "Fiscal year"},
        color_discrete_map=_color_map(df),
    )
    fig2.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Raw data"):
        st.dataframe(df.drop(columns=["revenue_b"]), use_container_width=True)


def render_profitability_tab(tickers):
    st.subheader("Net income")
    df = q_profitability(tickers)
    if df.empty:
        return _empty_state()
    df["period_date"] = pd.to_datetime(df["period_date"])
    df["net_income_m"] = df["net_income"] / 1e6

    fig = px.bar(
        df,
        x="period_date",
        y="net_income_m",
        color="ticker",
        barmode="group",
        labels={"net_income_m": "Net income (USD millions)", "period_date": "Fiscal year"},
        color_discrete_map=_color_map(df),
    )
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Net margin (%)")
    fig2 = px.line(
        df.dropna(subset=["net_margin_pct"]),
        x="period_date",
        y="net_margin_pct",
        color="ticker",
        markers=True,
        labels={"net_margin_pct": "Net margin (%)", "period_date": "Fiscal year"},
        color_discrete_map=_color_map(df),
    )
    fig2.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Raw data"):
        st.dataframe(df.drop(columns=["net_income_m"]), use_container_width=True)


def render_stock_tab(tickers):
    st.subheader("Daily closing price")
    df = q_stock_performance(tickers)
    if df.empty:
        return _empty_state()
    df["date"] = pd.to_datetime(df["date"])

    # Optional date range filter
    min_d, max_d = df["date"].min().date(), df["date"].max().date()
    start, end = st.slider(
        "Date range",
        min_value=min_d,
        max_value=max_d,
        value=(min_d, max_d),
        format="YYYY-MM-DD",
    )
    mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
    view = df.loc[mask]

    fig = px.line(
        view,
        x="date",
        y="close",
        color="ticker",
        labels={"close": "Close (USD)", "date": "Date"},
        color_discrete_map=_color_map(view),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rebased to 100 at start of window")

    def _rebase(g: pd.DataFrame) -> pd.DataFrame:
        if g.empty:
            return g.assign(rebased=pd.Series(dtype="float64"))
        base = g["close"].iloc[0]
        return g.assign(rebased=g["close"] / base * 100 if base else float("nan"))

    rebased = (
        view.sort_values("date")
        .groupby("ticker", group_keys=False)
        .apply(_rebase)
    )
    fig2 = px.line(
        rebased,
        x="date",
        y="rebased",
        color="ticker",
        labels={"rebased": "Index (start = 100)", "date": "Date"},
        color_discrete_map=_color_map(rebased),
    )
    st.plotly_chart(fig2, use_container_width=True)


def render_debt_tab(tickers):
    st.subheader("Debt-to-equity")
    df = q_debt_levels(tickers)
    if df.empty:
        return _empty_state()
    df["period_date"] = pd.to_datetime(df["period_date"])

    fig = px.line(
        df.dropna(subset=["debt_to_equity"]),
        x="period_date",
        y="debt_to_equity",
        color="ticker",
        markers=True,
        labels={"debt_to_equity": "Debt / Equity", "period_date": "Fiscal year"},
        color_discrete_map=_color_map(df),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Total debt vs total equity")
    stacked = df.melt(
        id_vars=["ticker", "period_date"],
        value_vars=["total_debt", "total_equity"],
        var_name="metric",
        value_name="value",
    )
    stacked["value_b"] = stacked["value"] / 1e9
    fig2 = px.bar(
        stacked,
        x="period_date",
        y="value_b",
        color="metric",
        facet_col="ticker",
        barmode="group",
        labels={"value_b": "USD billions", "period_date": "Fiscal year"},
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Raw data"):
        st.dataframe(df, use_container_width=True)


def render_fcf_tab(tickers):
    st.subheader("Operating cash flow, capex, and free cash flow")
    df = q_free_cash_flow(tickers)
    if df.empty:
        return _empty_state()
    df["period_date"] = pd.to_datetime(df["period_date"])
    melted = df.melt(
        id_vars=["ticker", "period_date"],
        value_vars=["operating_cash_flow", "capital_expenditure", "free_cash_flow"],
        var_name="metric",
        value_name="value",
    )
    melted["value_m"] = melted["value"] / 1e6

    fig = px.bar(
        melted,
        x="period_date",
        y="value_m",
        color="metric",
        facet_col="ticker",
        barmode="group",
        labels={"value_m": "USD millions", "period_date": "Fiscal year"},
    )
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw data"):
        st.dataframe(df, use_container_width=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Solar Financing Landscape",
        layout="wide",
    )
    st.title("Solar Financing Landscape")
    st.caption(
        "Residential solar public markets tracker. RUN, ENPH, and SPWR, "
        "pulled from yfinance and loaded into Postgres."
    )

    # Connection health check
    try:
        get_engine().connect().close()
    except SQLAlchemyError as e:
        st.error(
            "Could not connect to Postgres. Is the `solar_db` container running "
            "and is `DB_PASSWORD` set in your .env?\n\n"
            f"```\n{e}\n```"
        )
        st.stop()

    with st.sidebar:
        st.header("Filters")
        selected = st.multiselect(
            "Tickers",
            options=list(TICKER_LABELS.keys()),
            default=list(TICKER_LABELS.keys()),
            format_func=lambda t: TICKER_LABELS[t],
        )
        st.divider()
        st.caption(f"DB host: `{DB_HOST}:{DB_PORT}`")
        if st.button("Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if not selected:
        st.warning("Select at least one ticker from the sidebar.")
        st.stop()

    tabs = st.tabs(
        [
            "Revenue trends",
            "Profitability",
            "Stock performance",
            "Debt levels",
            "Free cash flow",
        ]
    )
    with tabs[0]:
        render_revenue_tab(selected)
    with tabs[1]:
        render_profitability_tab(selected)
    with tabs[2]:
        render_stock_tab(selected)
    with tabs[3]:
        render_debt_tab(selected)
    with tabs[4]:
        render_fcf_tab(selected)


if __name__ == "__main__":
    main()
