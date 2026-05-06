# Solar Financing Landscape

Financial analysis pipeline for US residential solar companies — tracking revenue, profitability, stock performance, debt, and cash flow across **RUN** (Sunrun), **ENPH** (Enphase Energy), and **SPWR** (SunPower).

## Stack

| Layer | Tool |
|---|---|
| Data collection | Python + yfinance |
| Orchestration | Apache Airflow 3.x |
| Storage | PostgreSQL 15 |
| Dashboard | Streamlit + Plotly |
| Infrastructure | Docker Compose |

## Project Structure

```
.
├── dags/               # Airflow DAG (weekly pipeline)
├── scripts/
│   ├── collect.py      # Fetch data from Yahoo Finance
│   ├── init_schema.py  # Create DB tables
│   ├── load.py         # Load CSVs into PostgreSQL
│   └── analyze.py      # Analysis utilities
├── dashboard/
│   └── app.py          # Streamlit dashboard
├── sql/
│   ├── schema.sql      # Table definitions
│   └── queries.sql     # Analysis queries
├── data/raw/           # Raw CSVs (gitignored)
└── docker-compose.yml
```

## Setup

### Prerequisites

- Docker + Docker Compose
- A `.env` file in the project root:

```env
DB_PASSWORD=your_password_here
```

### Run

```bash
docker-compose up -d
```

This starts three services:

| Service | URL |
|---|---|
| Airflow | http://localhost:8080 (admin / admin) |
| Streamlit dashboard | http://localhost:8501 |
| PostgreSQL | localhost:5433 |

### Manual pipeline run

```bash
# Collect raw data
python scripts/collect.py

# Initialize schema
python scripts/init_schema.py

# Load into PostgreSQL
python scripts/load.py
```

## Dashboard

Four tabs, seven charts:

- **Revenue** — annual revenue comparison + year-over-year growth % (SQL window function)
- **Profitability** — net income, net margin %, and gross margin % by ticker
- **Stock Price** — daily close price history (2019–present)
- **Debt & Cash Flow** — debt-to-equity ratio and free cash flow

## Pipeline

The Airflow DAG (`solar_pipeline`) runs weekly and executes three tasks in sequence:

```
collect_data → init_schema → load_data
```

## Key Findings

**1. Gross margin reveals the hardware vs. financing divide.**
ENPH (microinverter hardware) sustained ~42–47% gross margins across 2022–2025. RUN (solar leasing/financing) averaged 7–16% over the same period before recovering to 30% in 2025. Same industry, fundamentally different unit economics — hardware commands pricing power that a financing model cannot.

**2. ENPH's 42% revenue decline in 2024 was a demand correction, not a competitive loss.**
Revenue dropped from $2.29B (2023) to $1.33B (2024) due to European demand slowdown and installer inventory destocking. Gross margins held at ~47% throughout. A revenue decline with stable margins signals a volume problem, not a pricing or cost problem — the business model remained intact.

**3. RUN's -$2.85B net loss in 2024 was accounting-driven, not operational.**
$3.1B of that loss came from non-cash asset impairment charges. Stripping those out, gross profit in 2025 rebounded to $897M on $2.96B revenue — the strongest margin profile in the dataset for RUN. Distinguishing between accounting write-downs and operating deterioration is critical when reading solar company financials, which carry large long-term asset portfolios.
