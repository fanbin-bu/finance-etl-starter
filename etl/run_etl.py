import os
from parse_bank_csv import parse_csv_folder
from parse_ofx import parse_folder as parse_ofx_folder
from parse_coinbase_csv import parse_coinbase_folder
from load_clickhouse import get_client, upsert_transactions_bank, upsert_transactions_investment, upsert_positions_snapshot

BANK_DIR = "etl/downloads/banks"
FID_DIR = "etl/downloads/fidelity"
CB_DIR = "etl/downloads/coinbase"

def main():
    # Parse sources
    bank_rows = parse_csv_folder(BANK_DIR, "etl/mappings.yaml")
    b2, inv_from_fid, pos_from_fid = parse_ofx_folder(FID_DIR)
    cb_bank_like, cb_inv, cb_pos = parse_coinbase_folder(CB_DIR)

    # Combine
    all_bank = bank_rows + b2 + cb_bank_like
    all_inv = inv_from_fid + cb_inv
    all_pos = pos_from_fid + cb_pos

    # Load
    ch_host = os.getenv("CH_HOST", "localhost")
    ch_port = int(os.getenv("CH_PORT", "8123"))
    client = get_client(host=ch_host, port=ch_port)

    n_bank = upsert_transactions_bank(client, all_bank)
    n_inv = upsert_transactions_investment(client, all_inv)
    n_pos = upsert_positions_snapshot(client, all_pos)

    print(f"Ingested rows -> bank: {n_bank}, investment: {n_inv}, positions: {n_pos}")

if __name__ == "__main__":
    main()
