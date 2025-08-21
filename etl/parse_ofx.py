from ofxparse import OfxParser
import glob, os

def parse_qfx_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        ofx = OfxParser.parse(f)

    bank_txns, inv_txns, positions = [], [], []
    for acct in ofx.accounts:
        # Banking transactions
        stmt = getattr(acct, 'statement', None)
        if stmt and getattr(stmt, 'transactions', None):
            for t in stmt.transactions:
                bank_txns.append({
                    "fitid": getattr(t, 'id', None) or f"{acct.account_id}-{t.date}-{t.memo}-{t.amount}",
                    "account": acct.account_id or "FIDELITY_BANK",
                    "txn_date": t.date.date().isoformat() if t.date else None,
                    "description": t.memo or t.payee or "",
                    "amount": float(t.amount or 0),
                    "category": "Uncategorized",
                    "source": os.path.basename(path),
                })

        # Investment
        inv = getattr(acct, 'investment', None)
        if inv:
            # transactions: buys/sells/dividends/etc.
            for t in getattr(inv, 'transactions', []):
                fitid = getattr(t, 'uniqueid', None) or getattr(t, 'memo', None) or f"{acct.account_id}-{t.tradeDate}-{t.units}-{getattr(getattr(t,'security',None),'ticker',None)}"
                inv_txns.append({
                    "fitid": str(fitid),
                    "account": acct.account_id or "FIDELITY_INV",
                    "trade_date": getattr(t, 'tradeDate', None).date().isoformat() if getattr(t,'tradeDate', None) else None,
                    "settle_date": getattr(t, 'settleDate', None).date().isoformat() if getattr(t,'settleDate', None) else None,
                    "action": getattr(t, 'type', None),
                    "symbol": getattr(getattr(t, 'security', None), 'ticker', None),
                    "units": float(getattr(t, 'units', 0) or 0),
                    "unit_price": float(getattr(t, 'unitprice', 0) or 0),
                    "amount": float(getattr(t, 'total', 0) or 0),
                    "memo": getattr(t, 'memo', None),
                    "source": os.path.basename(path),
                })
            # positions
            for p in getattr(inv, 'positions', []):
                units = float(getattr(p, 'units', 0) or 0)
                price = float(getattr(p, 'unitprice', 0) or 0)
                positions.append({
                    "account": acct.account_id or "FIDELITY_INV",
                    "symbol": getattr(p.security, 'ticker', None) if getattr(p, 'security', None) else None,
                    "units": units,
                    "mkt_price": price,
                    "mkt_value": units * price,
                    "asof": inv.asof.date().isoformat() if getattr(inv, 'asof', None) else None,
                    "source": os.path.basename(path),
                })
    return bank_txns, inv_txns, positions

def parse_folder(folder_glob):
    b, i, p = [], [], []
    for path in glob.glob(os.path.join(folder_glob, "*.qfx")) + glob.glob(os.path.join(folder_glob, "*.ofx")):
        bank_txns, inv_txns, positions = parse_qfx_file(path)
        b.extend(bank_txns); i.extend(inv_txns); p.extend(positions)
    return b, i, p

if __name__ == "__main__":
    b, i, p = parse_folder("etl/downloads/fidelity")
    print(f"Parsed bank={len(b)} inv={len(i)} positions={len(p)}")
