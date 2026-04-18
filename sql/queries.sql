-- 1. Annual revenue trends
SELECT
    ticker,
    period_date,
    revenue,
    LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date) AS prev_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date)) 
        / NULLIF(LAG(revenue) OVER (PARTITION BY ticker ORDER BY period_date), 0) * 100, 2
    ) AS yoy_growth_pct
FROM income_statements
WHERE period_type = 'annual'
ORDER BY ticker, period_date;

-- 2. Net income (profitability)
SELECT
    ticker,
    period_date,
    net_income,
    ROUND(net_income / NULLIF(revenue, 0) * 100, 2) AS net_margin_pct
FROM income_statements
WHERE period_type = 'annual'
ORDER BY ticker, period_date;

-- 3. Stock price performance (year-end close)
SELECT
    ticker,
    DATE_TRUNC('year', date) AS year,
    ROUND(AVG(close)::NUMERIC, 2) AS avg_annual_price,
    ROUND(MIN(close)::NUMERIC, 2) AS min_price,
    ROUND(MAX(close)::NUMERIC, 2) AS max_price
FROM stock_prices
GROUP BY ticker, DATE_TRUNC('year', date)
ORDER BY ticker, year;

-- 4. Debt levels
SELECT
    ticker,
    period_date,
    total_debt,
    total_equity,
    ROUND(total_debt / NULLIF(total_equity, 0), 2) AS debt_to_equity
FROM balance_sheets
WHERE period_type = 'annual'
ORDER BY ticker, period_date;


-- 5. Free cash flow
SELECT
    ticker,
    period_date,
    operating_cash_flow,
    capital_expenditure,
    free_cash_flow
FROM cash_flows
WHERE period_type = 'annual'
ORDER BY ticker, period_date;