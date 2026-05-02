import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "database": "solar_financing",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
}

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")

ALTER_SQL = """
ALTER TABLE income_statements
    ALTER COLUMN revenue TYPE NUMERIC,
    ALTER COLUMN gross_profit TYPE NUMERIC,
    ALTER COLUMN operating_income TYPE NUMERIC,
    ALTER COLUMN net_income TYPE NUMERIC,
    ALTER COLUMN ebitda TYPE NUMERIC;

ALTER TABLE balance_sheets
    ALTER COLUMN total_assets TYPE NUMERIC,
    ALTER COLUMN total_debt TYPE NUMERIC,
    ALTER COLUMN cash TYPE NUMERIC,
    ALTER COLUMN total_equity TYPE NUMERIC;

ALTER TABLE cash_flows
    ALTER COLUMN operating_cash_flow TYPE NUMERIC,
    ALTER COLUMN capital_expenditure TYPE NUMERIC,
    ALTER COLUMN free_cash_flow TYPE NUMERIC;

ALTER TABLE solar_metrics
    ALTER COLUMN recurring_revenue TYPE NUMERIC;
"""


def init_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            cur.execute(ALTER_SQL)

    print("Database schema initialized.")


if __name__ == "__main__":
    init_schema()
