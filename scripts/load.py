import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'solar_financing',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def load_stock_prices():
    print("Loading stock prices...")
    conn = get_connection()
    cur = conn.cursor()

    for file in os.listdir(RAW_DIR):
        if not file.endswith('_stock_prices.csv'):
            continue
        df = pd.read_csv(os.path.join(RAW_DIR, file))
        df = df[['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']]
        rows = [tuple(r) for r in df.itertuples(index=False)]
        execute_values(cur, """
            INSERT INTO stock_prices (ticker, date, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (ticker, date) DO NOTHING
        """, rows)
        print(f"  Loaded {len(rows)} rows from {file}")

    conn.commit()
    cur.close()
    conn.close()

def load_income_statements():
    print("Loading income statements...")
    conn = get_connection()
    cur = conn.cursor()

    for file in os.listdir(RAW_DIR):
        if not file.endswith('_income_annual.csv') and not file.endswith('_income_quarterly.csv'):
            continue
        df = pd.read_csv(os.path.join(RAW_DIR, file))
        df = df.rename(columns={
            'Total Revenue': 'revenue',
            'Gross Profit': 'gross_profit',
            'Operating Income': 'operating_income',
            'Net Income': 'net_income',
            'EBITDA': 'ebitda'
        })
        for col in ['revenue', 'gross_profit', 'operating_income', 'net_income', 'ebitda']:
            if col not in df.columns:
                df[col] = None
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        rows = [tuple(r) for r in df[['ticker', 'period_date', 'period_type', 'revenue', 'gross_profit', 'operating_income', 'net_income', 'ebitda']].itertuples(index=False)]
        execute_values(cur, """
            INSERT INTO income_statements (ticker, period_date, period_type, revenue, gross_profit, operating_income, net_income, ebitda)
            VALUES %s
            ON CONFLICT (ticker, period_date, period_type) DO NOTHING
        """, rows)
        print(f"  Loaded {len(rows)} rows from {file}")

    conn.commit()
    cur.close()
    conn.close()

def load_balance_sheets():
    print("Loading balance sheets...")
    conn = get_connection()
    cur = conn.cursor()

    for file in os.listdir(RAW_DIR):
        if 'balance' not in file:
            continue
        df = pd.read_csv(os.path.join(RAW_DIR, file))
        df = df.rename(columns={
            'Total Assets': 'total_assets',
            'Total Debt': 'total_debt',
            'Cash And Cash Equivalents': 'cash',
            'Stockholders Equity': 'total_equity'
        })
        for col in ['total_assets', 'total_debt', 'cash', 'total_equity']:
            if col not in df.columns:
                df[col] = None
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        rows = [tuple(r) for r in df[['ticker', 'period_date', 'period_type', 'total_assets', 'total_debt', 'cash', 'total_equity']].itertuples(index=False)]
        execute_values(cur, """
            INSERT INTO balance_sheets (ticker, period_date, period_type, total_assets, total_debt, cash, total_equity)
            VALUES %s
            ON CONFLICT (ticker, period_date, period_type) DO NOTHING
        """, rows)
        print(f"  Loaded {len(rows)} rows from {file}")

    conn.commit()
    cur.close()
    conn.close()


def load_cash_flows():
    print("Loading cash flows...")
    conn = get_connection()
    cur = conn.cursor()

    for file in os.listdir(RAW_DIR):
        if 'cashflow' not in file:
            continue
        df = pd.read_csv(os.path.join(RAW_DIR, file))
        df = df.rename(columns={
            'Operating Cash Flow': 'operating_cash_flow',
            'Capital Expenditure': 'capital_expenditure',
            'Free Cash Flow': 'free_cash_flow'
        })
        for col in ['operating_cash_flow', 'capital_expenditure', 'free_cash_flow']:
            if col not in df.columns:
                df[col] = None
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        rows = [tuple(r) for r in df[['ticker', 'period_date', 'period_type', 'operating_cash_flow', 'capital_expenditure', 'free_cash_flow']].itertuples(index=False)]
        execute_values(cur, """
            INSERT INTO cash_flows (ticker, period_date, period_type, operating_cash_flow, capital_expenditure, free_cash_flow)
            VALUES %s
            ON CONFLICT (ticker, period_date, period_type) DO NOTHING
        """, rows)
        print(f"  Loaded {len(rows)} rows from {file}")

    conn.commit()
    cur.close()
    conn.close()


def load_all():
    print("Starting data load...")
    print("-" * 50)
    load_stock_prices()
    load_income_statements()
    load_balance_sheets()
    load_cash_flows()
    print("-" * 50)
    print("Data load complete!")


if __name__ == "__main__":
    load_all()