from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis
import os
import asyncpg
import asyncio

app = FastAPI(title="Production-Grade FastAPI", version="1.0.0")

#redis Connection pool
redis_client = redis.asyncio.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
pg_pool = None

async def get_pg_pool():
    global pg_pool
    if pg_pool is None:
        pg_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    return pg_pool

class Transaction(BaseModel):
    user_id: str
    amount: float
    currency: str = "USD"
    merchant: str
    country: str
    device_type: Literal["mobile", "desktop", "tablet"]
    is_international: bool = False

@app.post("/transactions")
async def receive_transaction(tx: Transaction):
    tx_id = str(uuid.uuid4())
    score = None

    # Mark as potentialy fraudulent for demo
    is_fraud = random.random() < 0.03
    if tx.amount > 5000 or (tx.is_international and tx.amount > 800):
        is_fraud = True

    await redis_client.setex(f"tx:{tx_id}", 3600, tx.json())

    pg = await get_pg_pool()
    await pg.execute("""INSERT INTO transactions(tx_id, user_id, amount, merchant, country, is_international, is_fraud, detected_at)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""", tx_id, tx.user_id, tx.amount, tx.merchant, tx.country, tx.is_international, is_fraud, datetime.utcnow())
    
    risk_level = "HIGH" if is_fraud else "LOW"

    return {
        "tx_id": tx_id,
        "risk_level": risk_level,
        "message": "FLAGGED FOR FRAUD REVIEW" if is_fraud else "Approved",
        "ai_score": score or "Pending"
    }

@app.get("/health")
async def health(): return {"status": "healthy", "service": "payguard-ai"}