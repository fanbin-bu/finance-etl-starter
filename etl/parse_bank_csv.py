import pandas as pd
import glob, os, hashlib, yaml
from datetime import datetime

def load_mappings(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def hash_fitid(account: str, date: str, desc: str, amount: float):
    key = f"{account}|{date}|{desc}|{amount}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]

def detect_bank_config(df, configs):
    headers = list(df.columns)
    for bank, cfg in configs["banks"].items():
        match = all(h in headers for h in cfg.get("match_headers", []))
        if match:
            return bank, cfg
    return None, None

def apply_category(description: str, rules):
    d = (description or "").upper()
    for rule in rules or []:
        if rule.get("contains") and rule["contains"] in d:
            return rule.get("category", "Uncategorized")
    return "Uncategorized"

def parse_csv_folder(folder, mappings_path):
    configs = load_mappings(mappings_path)
    out = []
    for path in glob.glob(os.path.join(folder, "*.csv")):
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")
        bank, cfg = detect_bank_config(df, configs)
        if not cfg:
            print(f"[WARN] Unknown header format for {path}, skipping.")
            continue

        # Build normalized rows
        if "debit_field" in cfg and "credit_field" in cfg:
            # Citi style (separate debit/credit columns)
            for _, row in df.iterrows():
                date_str = str(row[cfg["date"]])
                desc = str(row[cfg["description"]])
                debit = row.get(cfg["debit_field"], 0) or 0
                credit = row.get(cfg["credit_field"], 0) or 0
                amount = float(credit) - float(debit)
                dt = pd.to_datetime(date_str).date().isoformat()
                fitid = hash_fitid("BANK", dt, desc, amount)
                category = apply_category(desc, configs.get("category_rules"))
                out.append({
                    "fitid": fitid,
                    "account": "BANK",
                    "txn_date": dt,
                    "description": desc,
                    "amount": amount,
                    "category": category,
                    "source": os.path.basename(path),
                })
        else:
            # One amount column; ensure sign convention
            for _, row in df.iterrows():
                date_str = str(row[cfg["date"]])
                desc = str(row[cfg["description"]])
                amount = float(row[cfg["amount"]])
                if cfg.get("debit_negative", True):
                    # Many banks export debits as negative already; if not, add logic here
                    pass
                dt = pd.to_datetime(date_str).date().isoformat()
                fitid = hash_fitid("BANK", dt, desc, amount)
                category = apply_category(desc, configs.get("category_rules"))
                out.append({
                    "fitid": fitid,
                    "account": "BANK",
                    "txn_date": dt,
                    "description": desc,
                    "amount": amount,
                    "category": category,
                    "source": os.path.basename(path),
                })
    return out

if __name__ == "__main__":
    rows = parse_csv_folder("etl/downloads/banks", "etl/mappings.yaml")
    print(f"Parsed {len(rows)} bank rows.")
