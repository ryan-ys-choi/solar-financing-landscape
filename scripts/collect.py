import yfinance as yf
import pandas as pd
import os
from datetime import datetime

TICKERS = ['RUN', 'ENPH', 'SPWR']
START_DATE = '2019-01-01'
END_DATE = datetime.today().strftime('%Y-%m-%d')

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

def collect_stock_prices():
    print("Collecting stock prices...")
    for ticker in TICKERS:
        print(f" Fetching {ticker}...")
        stock = yf.Ticker(ticker)
        df = stock.history(start=START_DATE, end=END_DATE)
        if df.empty:
            print(f" WARNING: No data for {ticker}")
            continue
        df = df.reset_index()
        df['ticker'] = ticker
        df = df[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date']).dt.date
        df.to_csv(os.path.join(RAW_DIR, f'{ticker}_stock_prices.csv'), index=False)
        print(f" Saved {len(df)} rows")
    
def collect_income_statements():
    print("Collecting income statements...")
    for ticker in TICKERS:
        print(f" Fetching {ticker}...")
        stock = yf.Ticker(ticker)
        for period_type, income in [('annual', stock.income_stmt), ('quarterly', stock.quarterly_income_stmt)]:
            if income is None or income.empty:
                print(f" WARNING: No {period_type} income data for {ticker}")
                continue
            df = income.T.reset_index()
            df['ticker'] = ticker
            df['period_type'] = period_type
            df = df.rename(columns={'index': 'period_date'})
            df['period_date'] = pd.to_datetime(df['period_date']).dt.date
            df.to_csv(os.path.join(RAW_DIR, f'{ticker}_income_{period_type}.csv'), index=False)
            print(f"  Saved {period_type} income for {ticker}")

def collect_balance_sheets():
    print("Collecting balance sheets...")
    for ticker in TICKERS:
        print(f"  Fetching {ticker}...")
        stock = yf.Ticker(ticker)
        for period_type, balance in [('annual', stock.balance_sheet), ('quarterly', stock.quarterly_balance_sheet)]:
            if balance is None or balance.empty:
                print(f"  WARNING: No {period_type} balance for {ticker}")
                continue
            df = balance.T.reset_index()
            df.columns = [str(c).strip() for c in df.columns]
            df['ticker'] = ticker
            df['period_type'] = period_type
            df = df.rename(columns={'index': 'period_date'})
            df['period_date'] = pd.to_datetime(df['period_date']).dt.date
            df.to_csv(os.path.join(RAW_DIR, f'{ticker}_balance_{period_type}.csv'), index=False)
            print(f"  Saved {period_type} balance for {ticker}")

def collect_cash_flows():
    print("Collecting cash flows...")
    for ticker in TICKERS:
        print(f"  Fetching {ticker}...")
        stock = yf.Ticker(ticker)
        for period_type, cashflow in [('annual', stock.cashflow), ('quarterly', stock.quarterly_cashflow)]:
            if cashflow is None or cashflow.empty:
                print(f"  WARNING: No {period_type} cash flow for {ticker}")
                continue
            df = cashflow.T.reset_index()
            df.columns = [str(c).strip() for c in df.columns]
            df['ticker'] = ticker
            df['period_type'] = period_type
            df = df.rename(columns={'index': 'period_date'})
            df['period_date'] = pd.to_datetime(df['period_date']).dt.date
            df.to_csv(os.path.join(RAW_DIR, f'{ticker}_cashflow_{period_type}.csv'), index=False)
            print(f"  Saved {period_type} cash flow for {ticker}")

def collect_all():
    print(f"Starting data collection at {datetime.now()}")
    print(f"Tickers: {TICKERS}")
    print("-" * 50)
    collect_stock_prices()
    collect_income_statements()
    collect_balance_sheets()
    collect_cash_flows()
    print("-" * 50)
    print("Data collection complete!")

if __name__ == "__main__":
    collect_all()