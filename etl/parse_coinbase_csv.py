import pandas as pd
import glob, os, hashlib

# Coinbase provides multiple CSV types (e.g., 'fills', 'transactions').
# This parser handles a generic 'transactions' export with columns:
# Timestamp, Transaction Type, Asset, Quantity Transacted, USD Amount (inclusive of fees), ...
# Adjust mapping if your CSV headers differ.

def hash_fitid(ts: str, typ: str, asset: str, qty: float, usd: float):
    key = f"{ts}|{typ}|{asset}|{qty}|{usd}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]

def parse_coinbase_folder(folder):
    out_bank_like = []
    out_inv = []
    for path in glob.glob(os.path.join(folder, "*.csv")):
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")

        cols = {c.lower(): c for c in df.columns}
        # Basic detection
        tcol = cols.get("timestamp")
        typecol = cols.get("transaction type")
        assetcol = cols.get("asset")
        qtycol = cols.get("quantity transacted")
        usdcol = cols.get("usd amount (inclusive of fees)") or cols.get("usd amount")

        if not all([tcol, typecol, assetcol, qtycol, usdcol]):
            print(f"[WARN] Unrecognized Coinbase CSV format for {path}, skipping.")
            continue

        for _, row in df.iterrows():
            ts = str(row[tcol])
            typ = str(row[typecol])
            asset = str(row[assetcol])
            qty = float(row[qtycol] or 0)
            usd = float(row[usdcol] or 0)
            fitid = hash_fitid(ts, typ, asset, qty, usd)
            # Treat crypto trades/dividends as investment txns
            out_inv.append({
                "fitid": fitid,
                "account": "COINBASE",
                "trade_date": pd.to_datetime(ts).date().isoformat(),
                "settle_date": pd.to_datetime(ts).date().isoformat(),
                "action": typ.upper(),  # BUY/SELL/REWARD/CONVERT/etc.
                "symbol": asset.upper(),
                "units": qty,
                "unit_price": (usd/qty) if qty else 0.0,
                "amount": usd,
                "memo": os.path.basename(path),
                "source": os.path.basename(path),
            })
    return out_bank_like, out_inv, []

if __name__ == "__main__":
    b, i, p = parse_coinbase_folder("etl/downloads/coinbase")
    print(f"Coinbase parsed inv={len(i)}")
