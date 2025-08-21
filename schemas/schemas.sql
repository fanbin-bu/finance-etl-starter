CREATE DATABASE IF NOT EXISTS finance;

CREATE TABLE IF NOT EXISTS finance.transactions_bank
(
    fitid String,
    account String,
    txn_date Date,
    description String,
    amount Float64,
    category String,
    source String,
    _ingested_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree()
ORDER BY (fitid);

CREATE TABLE IF NOT EXISTS finance.transactions_investment
(
    fitid String,
    account String,
    trade_date Date,
    settle_date Date,
    action String,
    symbol String,
    units Float64,
    unit_price Float64,
    amount Float64,
    memo String,
    source String,
    _ingested_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree()
ORDER BY (fitid);

CREATE TABLE IF NOT EXISTS finance.positions_snapshot
(
    account String,
    symbol String,
    units Float64,
    mkt_price Float64,
    mkt_value Float64,
    asof Date,
    source String,
    _ingested_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree()
ORDER BY (account, symbol, asof);

-- Optional materialized views or rollups can be added later.
