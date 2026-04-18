-- Solar Financing Landscape Database Schema

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    ticker          VARCHAR(10) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    headquarters    VARCHAR(100),
    founded         INTEGER,
    business_model  VARCHAR(50), -- 'TPO', 'Loan', 'Mixed'
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert our target companies
INSERT INTO companies (ticker, name, headquarters, founded, business_model) VALUES
    ('RUN',  'Sunrun Inc.',          'San Francisco, CA', 2007, 'TPO'),
    ('ENPH', 'Enphase Energy',       'Fremont, CA',       2006, 'Mixed'),
    ('SPWR', 'SunPower Corporation', 'San Jose, CA',      1985, 'Mixed')
ON CONFLICT (ticker) DO NOTHING;

-- Stock prices table
CREATE TABLE IF NOT EXISTS stock_prices (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR(10) REFERENCES companies(ticker),
    date        DATE NOT NULL,
    open        NUMERIC(10,2),
    high        NUMERIC(10,2),
    low         NUMERIC(10,2),
    close       NUMERIC(10,2),
    volume      BIGINT,
    UNIQUE(ticker, date)
);

-- Income statements table
CREATE TABLE IF NOT EXISTS income_statements (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR(10) REFERENCES companies(ticker),
    period_date         DATE NOT NULL,
    period_type         VARCHAR(10), -- 'annual' or 'quarterly'
    revenue             BIGINT,
    gross_profit        BIGINT,
    operating_income    BIGINT,
    net_income          BIGINT,
    ebitda              BIGINT,
    UNIQUE(ticker, period_date, period_type)
);

-- Balance sheets table
CREATE TABLE IF NOT EXISTS balance_sheets (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR(10) REFERENCES companies(ticker),
    period_date         DATE NOT NULL,
    period_type         VARCHAR(10),
    total_assets        BIGINT,
    total_debt          BIGINT,
    cash                BIGINT,
    total_equity        BIGINT,
    UNIQUE(ticker, period_date, period_type)
);

-- Cash flow statements table
CREATE TABLE IF NOT EXISTS cash_flows (
    id                      SERIAL PRIMARY KEY,
    ticker                  VARCHAR(10) REFERENCES companies(ticker),
    period_date             DATE NOT NULL,
    period_type             VARCHAR(10),
    operating_cash_flow     BIGINT,
    capital_expenditure     BIGINT,
    free_cash_flow          BIGINT,
    UNIQUE(ticker, period_date, period_type)
);

-- Solar specific metrics table
CREATE TABLE IF NOT EXISTS solar_metrics (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR(10) REFERENCES companies(ticker),
    period_date         DATE NOT NULL,
    period_type         VARCHAR(10),
    installed_mw        NUMERIC(10,2),
    customers           INTEGER,
    recurring_revenue   BIGINT,
    UNIQUE(ticker, period_date, period_type)
);