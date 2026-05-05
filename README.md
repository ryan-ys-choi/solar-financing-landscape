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

Five analysis views:

- **Revenue** — annual revenue comparison across tickers
- **Profitability** — net income and net margin trends
- **Stock Price** — daily close price history (2019–present)
- **Debt & Cash Flow** — debt-to-equity ratio and free cash flow

## Pipeline

The Airflow DAG (`solar_pipeline`) runs weekly and executes three tasks in sequence:

```
collect_data → init_schema → load_data
```
