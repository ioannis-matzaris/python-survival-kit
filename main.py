"""Οι παραγγελίες του e-shop. Τρέξε: uvicorn main:app --reload

Η παραγγελία γράφεται σε δέκα χιλιοστά. Ο πελάτης περιμένει τρία δευτερόλεπτα,
γιατί μέσα στο ίδιο request στέλνεται και η απόδειξη.
"""

import sqlite3
import time
from pathlib import Path

import redis
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, EmailStr

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

app = FastAPI()
cache = redis.Redis(decode_responses=True)


class NewOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    total_cents: int


def send_receipt(order_id: int, email: str) -> None:
    """Μιλάει με τον πάροχο email. Αργεί, και δεν επιταχύνεται."""
    time.sleep(3)
    cache.set(f"receipt:{order_id}", email)


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

    send_receipt(order_id, order.email)

    return {"order_id": str(order_id), "status": "η απόδειξη στάλθηκε"}
