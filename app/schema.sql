CREATE TABLE IF NOT EXIST transactions (
    id SERIAL PRIMARY KEY,
    tx_id TEXT UNIQUE,
    user_id TEXT,
    amount DECIMAL,
    merchant TEXT,
    country TEXT,
    is_international BOOLEAN,
    is_fraud BOOLEAN,
    detected_at TIMESTAMP
    ai_score FLOAT
);