"""Οι παραγγελίες του πελάτη. Τρέξε: uvicorn main:app --reload

Το token ελέγχεται σωστά. Ποιος ζητάει τι, δεν το ελέγχει κανείς.
"""

import sqlite3
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"
SECRET = "to-mystiko-tou-service-pou-den-fevgei-pote"
ALGORITHM = "HS256"

app = FastAPI()


def current_user(authorization: str = Header(default="")) -> int:
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Λείπει το token")
    try:
        payload = jwt.decode(
            token, SECRET, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Το token δεν ισχύει")
    return int(payload["sub"])


def rows(query: str, parameters: tuple) -> list[tuple]:
    connection = sqlite3.connect(DB)
    found = connection.execute(query, parameters).fetchall()
    connection.close()
    return found


@app.get("/orders")
def list_orders(user_id: int | None = None, user: int = Depends(current_user)) -> list[dict]:
    owner = user_id if user_id is not None else user
    found = rows(
        "SELECT id, reference, total_cents, status FROM orders WHERE user_id = ?",
        (owner,),
    )
    return [
        {"id": one[0], "reference": one[1], "total_cents": one[2], "status": one[3]}
        for one in found
    ]


@app.get("/orders/{order_id}")
def read_order(order_id: int, user: int = Depends(current_user)) -> dict:
    found = rows(
        "SELECT id, reference, total_cents, status FROM orders WHERE id = ?", (order_id,)
    )
    if not found:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοια παραγγελία")
    one = found[0]
    return {"id": one[0], "reference": one[1], "total_cents": one[2], "status": one[3]}


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, user: int = Depends(current_user)) -> dict:
    connection = sqlite3.connect(DB)
    changed = connection.execute(
        "UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,)
    ).rowcount
    connection.commit()
    connection.close()
    if changed == 0:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοια παραγγελία")
    return {"id": order_id, "status": "cancelled"}
