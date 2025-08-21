import clickhouse_connect
from typing import List, Dict

def get_client(host="localhost", port=8123, username="", password=""):
    return clickhouse_connect.get_client(host=host, port=port, username=username, password=password)

def upsert_transactions_bank(client, rows: List[Dict]):
    if not rows:
        return 0
    data = [(r["fitid"], r["account"], r["txn_date"], r["description"], r["amount"], r.get("category","Uncategorized"), r.get("source","")) for r in rows]
    client.insert("finance.transactions_bank",
        data,
        column_names=["fitid","account","txn_date","description","amount","category","source"]
    )
    return len(rows)

def upsert_transactions_investment(client, rows: List[Dict]):
    if not rows:
        return 0
    data = [(r["fitid"], r["account"], r["trade_date"], r.get("settle_date"), r.get("action"), r.get("symbol"),
             float(r.get("units",0)), float(r.get("unit_price",0)), float(r.get("amount",0)), r.get("memo",""), r.get("source","")) for r in rows]
    client.insert("finance.transactions_investment",
        data,
        column_names=["fitid","account","trade_date","settle_date","action","symbol","units","unit_price","amount","memo","source"]
    )
    return len(rows)

def upsert_positions_snapshot(client, rows: List[Dict]):
    if not rows:
        return 0
    data = [(r["account"], r["symbol"], float(r.get("units",0)), float(r.get("mkt_price",0)), float(r.get("mkt_value",0)), r["asof"], r.get("source","")) for r in rows]
    client.insert("finance.positions_snapshot",
        data,
        column_names=["account","symbol","units","mkt_price","mkt_value","asof","source"]
    )
    return len(rows)
