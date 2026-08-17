"""Το API του e-shop, ορθάνοιχτο. Τρέξε: uvicorn main:app --reload

Δουλεύει. Η εγγραφή, η σύνδεση, οι παραγγελίες. Και δεν προστατεύει τίποτα.
"""

import sqlite3
from pathlib import Path

import bcrypt
import jwt
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"
SECRET = "to-mystiko-tou-service-pou-den-fevgei-pote"
ALGORITHM = "HS256"

app = FastAPI()


class Signup(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False


class Login(BaseModel):
    email: EmailStr
    password: str


def query(sql: str, parameters: tuple = ()) -> list[tuple]:
    connection = sqlite3.connect(DB)
    found = connection.execute(sql, parameters).fetchall()
    connection.close()
    return found


@app.post("/signup", status_code=201)
def signup(body: Signup) -> dict[str, str]:
    connection = sqlite3.connect(DB)
    cursor = connection.execute(
        "INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)",
        (body.email, body.password, int(body.is_admin)),
    )
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return {"id": str(user_id), "email": body.email}


@app.post("/login")
def login(body: Login) -> dict[str, str]:
    found = query("SELECT id, password FROM users WHERE email = ?", (body.email,))
    if not found or not bcrypt.checkpw(body.password.encode("utf-8"), found[0][1].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Λάθος στοιχεία")
    token = jwt.encode({"sub": str(found[0][0])}, SECRET, algorithm=ALGORITHM)
    return {"token": token}


def current_user(authorization: str = Header(default="")) -> int:
    token = authorization.removeprefix("Bearer ").strip()
    payload = jwt.decode(token, options={"verify_signature": False})
    return int(payload["sub"])


@app.get("/orders/{order_id}")
def read_order(order_id: int, authorization: str = Header(default="")) -> dict:
    current_user(authorization)
    found = query(
        "SELECT id, user_id, reference, total_cents FROM orders WHERE id = ?", (order_id,)
    )
    if not found:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοια παραγγελία")
    one = found[0]
    return {"id": one[0], "reference": one[2], "total_cents": one[3]}
