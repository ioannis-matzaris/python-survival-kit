"""Ο τιμοκατάλογος. Τρέξε: uvicorn main:app --reload

Η τιμή διαβάζεται μία φορά και μένει στο Redis. Και μένει εκεί ακόμα κι όταν
το λογιστήριο την αλλάξει.
"""

import sqlite3
from pathlib import Path

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

app = FastAPI()
cache = redis.Redis(decode_responses=True)


class NewPrice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price_cents: int


def read_price(code: str) -> int | None:
    connection = sqlite3.connect(DB)
    row = connection.execute(
        "SELECT price_cents FROM products WHERE code = ?", (code,)
    ).fetchone()
    connection.close()
    return row[0] if row else None


@app.get("/products/{code}/price")
def price(code: str) -> dict[str, str]:
    key = f"price:{code}"
    cached = cache.get(key)
    if cached is not None:
        return {"code": code, "price": cached}

    cents = read_price(code)
    if cents is None:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοιο προϊόν")

    value = f"{cents / 100:.2f}"
    cache.set(key, value)
    return {"code": code, "price": value}


@app.put("/products/{code}/price")
def set_price(code: str, body: NewPrice) -> dict[str, str]:
    connection = sqlite3.connect(DB)
    changed = connection.execute(
        "UPDATE products SET price_cents = ? WHERE code = ?", (body.price_cents, code)
    ).rowcount
    connection.commit()
    connection.close()

    if changed == 0:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοιο προϊόν")
    return {"code": code, "price": f"{body.price_cents / 100:.2f}"}
