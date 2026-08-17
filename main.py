"""Το service του e-shop. Τρέξε: uvicorn main:app --reload

Οι τιμές ξαναδιαβάζονται σε κάθε κλήση και η απόδειξη φεύγει μέσα από το
request. Και τα δύο δουλεύουν, και τα δύο κοστίζουν.
"""

import sqlite3
from pathlib import Path

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr

import tasks

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

app = FastAPI()
cache = redis.Redis(decode_responses=True)


class NewOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    total_cents: int


class NewPrice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price_cents: int


@app.get("/products/{code}/price")
def price(code: str) -> dict[str, str]:
    connection = sqlite3.connect(DB)
    row = connection.execute(
        "SELECT price_cents FROM products WHERE code = ?", (code,)
    ).fetchone()
    connection.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοιο προϊόν")
    return {"code": code, "price": f"{row[0] / 100:.2f}"}


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


@app.post("/orders", status_code=201)
def create_order(order: NewOrder) -> dict[str, str]:
    connection = sqlite3.connect(DB)
    cursor = connection.execute(
        "INSERT INTO orders (email, total_cents) VALUES (?, ?)",
        (order.email, order.total_cents),
    )
    connection.commit()
    order_id = cursor.lastrowid
    connection.close()

    tasks.send_receipt(order_id, order.email)

    return {"order_id": str(order_id), "status": "η απόδειξη στάλθηκε"}
