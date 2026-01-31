-- Table for storing stock tick data
CREATE TABLE IF NOT EXISTS stock_ticks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(16),
    stock VARCHAR(64),
    price NUMERIC,
    chg_percentage NUMERIC,
    volume BIGINT,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_symbol_time ON stock_ticks(symbol, timestamp);
