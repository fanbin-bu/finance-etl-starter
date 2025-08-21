.PHONY: up down init-db ingest ingest-banks ingest-fidelity ingest-coinbase mb-seed clean

up:
	docker compose up -d

down:
	docker compose down -v

init-db:
	docker compose exec clickhouse clickhouse-client --queries-file /schemas/schemas.sql

ingest: ingest-banks ingest-fidelity ingest-coinbase
	@echo "Ingest complete."

ingest-banks:
	. ./.venv/bin/activate && python etl/parse_bank_csv.py >/dev/null || true
	. ./.venv/bin/activate && python etl/run_etl.py

ingest-fidelity:
	. ./.venv/bin/activate && python etl/run_etl.py

ingest-coinbase:
	. ./.venv/bin/activate && python etl/run_etl.py

mb-seed:
	@echo "Importing example Metabase dashboard via API..."
	@echo "Open http://localhost:3000 and set up ClickHouse first, then use the JSON in metabase/sample_dashboard.json"

clean:
	rm -rf etl/downloads/banks/* etl/downloads/fidelity/* etl/downloads/coinbase/* 2>/dev/null || true
	find . -name "__pycache__" -type d -exec rm -rf {} +


install-browsers:
	. ./.venv/bin/activate && python -m playwright install chromium

download-fidelity:
	. ./.venv/bin/activate && python etl/download_fidelity.py

download-boa:
	. ./.venv/bin/activate && python etl/download_boa.py

download-usbank:
	. ./.venv/bin/activate && python etl/download_usbank.py

download-citi:
	. ./.venv/bin/activate && python etl/download_citi.py

download-all: download-fidelity download-boa download-usbank download-citi
	@echo "All downloads attempted."
