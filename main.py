"""Το API των παραγγελιών. Τρέξε: uvicorn main:app --reload

Κοιτάει αν υπάρχει απόθεμα και μετά το μειώνει. Με έναν πελάτη τη φορά είναι
σωστό. Με είκοσι μαζί, πουλάει κομμάτια που δεν έχει.
"""

import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

app = FastAPI()


class Order(BaseModel):
    sku: str
    quantity: int
    customer: str


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB, timeout=15)


@app.get("/products/{sku}")
def read_product(sku: str) -> dict[str, int | str]:
    connection = connect()
    found = connection.execute("SELECT sku, name, stock FROM products WHERE sku = ?", (sku,)).fetchall()
    connection.close()
    if not found:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοιο προϊόν")
    return {"sku": found[0][0], "name": found[0][1], "stock": found[0][2]}


@app.post("/orders", status_code=201)
def place_order(body: Order) -> dict[str, int | str]:
    connection = connect()

    found = connection.execute("SELECT stock FROM products WHERE sku = ?", (body.sku,)).fetchall()
    if not found:
        connection.close()
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοιο προϊόν")

    stock = found[0][0]
    time.sleep(0.02)

    if stock < body.quantity:
        connection.close()
        raise HTTPException(status_code=409, detail="Δεν έχει τόσα κομμάτια")

    connection.execute("UPDATE products SET stock = ? WHERE sku = ?", (stock - body.quantity, body.sku))
    cursor = connection.execute(
        "INSERT INTO orders (sku, quantity, customer) VALUES (?, ?, ?)",
        (body.sku, body.quantity, body.customer),
    )
    connection.commit()
    order_id = cursor.lastrowid
    connection.close()
    return {"id": order_id or 0, "sku": body.sku, "quantity": body.quantity}
