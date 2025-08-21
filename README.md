# Free-Only Personal Finance ETL Starter

This repo is a minimal working pipeline to track your finances for **free** (no Plaid). It uses only **CSV/QFX exports** from your institutions and loads data into **ClickHouse**, with dashboards via **Metabase**.

## What it Does
- Parse **bank CSV** exports (Bank of America, US Bank, Citi — configurable).
- Parse **Fidelity QFX/OFX** (or any QFX with standard sections).
- Parse **Coinbase CSV** exports (trades, balances).
- Normalize into 3 tables: `transactions_bank`, `transactions_investment`, `positions_snapshot`.
- Load into **ClickHouse** (Docker Compose provided).
- Basic **Metabase** setup notes for dashboards.

## Quick Start (Local)
1. Install Docker & Docker Compose.
2. Start DB & Metabase:
   ```bash
   docker compose up -d
   ```
   - ClickHouse at `localhost:8123` (HTTP) and `localhost:9000` (native).
   - Metabase at `http://localhost:3000`

3. Create ClickHouse tables:
   ```bash
   docker compose exec clickhouse clickhouse-client --queries-file /schemas/schemas.sql
   ```

4. Put your files here:
   - Bank CSVs → `etl/downloads/banks/`
   - Fidelity QFX/OFX → `etl/downloads/fidelity/`
   - Coinbase CSVs → `etl/downloads/coinbase/`

5. Create & activate a virtualenv, install deps:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

6. Run ETL:
   ```bash
   python etl/run_etl.py
   ```

7. Open **Metabase** → add ClickHouse as a database (host `clickhouse`, port `8123` if inside Docker network, or `localhost:8123` from host). Build cards:
   - Monthly Cash Flow
   - Category Spend
   - Holdings by Symbol
   - Net Worth over Time

## File Layout
```
finance-etl-starter/
├─ docker-compose.yml
├─ requirements.txt
├─ README.md
├─ etl/
│  ├─ downloads/
│  │  ├─ banks/        # CSV from BoA/USBank/Citi
│  │  ├─ fidelity/     # QFX/OFX from Fidelity
│  │  └─ coinbase/     # CSV from Coinbase
│  ├─ mappings.yaml    # column mappings for banks; category rules
│  ├─ parse_bank_csv.py
│  ├─ parse_ofx.py
│  ├─ parse_coinbase_csv.py
│  ├─ load_clickhouse.py
│  └─ run_etl.py
└─ schemas/
   └─ schemas.sql
```

## Notes
- This starter assumes **manual exports**. You can automate downloads later with Playwright.
- `mappings.yaml` lets you define header mappings per bank and category rules.
- The pipeline is **idempotent** (uses unique keys `fitid` / hashes). Re-running won't duplicate rows.


## Python-only Download Automation (optional)
You can automate CSV/QFX downloads using **Playwright (Python)** — no Node required.

1. Create a virtualenv and install deps:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   make install-browsers   # installs Chromium for Playwright
   cp .env.example .env    # fill credentials (use read-only if possible)
   ```
2. Run a downloader (example Fidelity):
   ```bash
   make download-fidelity
   ```
   or run all:
   ```bash
   make download-all
   ```

**Note:** The selectors in the `etl/download_*.py` scripts are placeholders. On your first run,
open the site in a regular browser, inspect the login & export elements, then update the selectors accordingly.
