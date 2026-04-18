import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'solar_financing',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}

def get_engine():
    password = os.getenv('DB_PASSWORD')
    return create_engine(f'postgresql://postgres:{password}@localhost:5433/solar_financing')

def run_query(sql):
    engine = get_engine()
    df = pd.read_sql(sql, engine)
    return df

def revenue_trends():
    return run_query("""
        SELECT 
            ticker,
            period_date,
            revenue,
            ROUND(
                (revenue - LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date)) 
                / NULLIF(LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date), 0) * 100, 2
            ) AS yoy_growth_pct
        FROM income_statements
        WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """)


def profitability():
    return run_query("""
        SELECT
            ticker,
            period_date,
            net_income,
            ROUND(net_income / NULLIF(revenue, 0) * 100, 2) AS net_margin_pct
        FROM income_statements
        WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """)


def stock_performance():
    return run_query("""
        SELECT
            ticker,
            DATE_TRUNC('year', date) AS year,
            ROUND(AVG(close)::NUMERIC, 2) AS avg_annual_price,
            ROUND(MIN(close)::NUMERIC, 2) AS min_price,
            ROUND(MAX(close)::NUMERIC, 2) AS max_price
        FROM stock_prices
        GROUP BY ticker, DATE_TRUNC('year', date)
        ORDER BY ticker, year
    """)


def debt_levels():
    return run_query("""
        SELECT
            ticker,
            period_date,
            total_debt,
            total_equity,
            ROUND(total_debt / NULLIF(total_equity, 0), 2) AS debt_to_equity
        FROM balance_sheets
        WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """)


def free_cash_flow():
    return run_query("""
        SELECT
            ticker,
            period_date,
            operating_cash_flow,
            capital_expenditure,
            free_cash_flow
        FROM cash_flows
        WHERE period_type = 'annual'
        ORDER BY ticker, period_date
    """)


if __name__ == "__main__":
    print("=== Revenue Trends ===")
    print(revenue_trends().to_string())
    print("\n=== Profitability ===")
    print(profitability().to_string())
    print("\n=== Stock Performance ===")
    print(stock_performance().to_string())
    print("\n=== Debt Levels ===")
    print(debt_levels().to_string())
    print("\n=== Free Cash Flow ===")
    print(free_cash_flow().to_string())



