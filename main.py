"""Το API του θεάτρου. Τρέξε: uvicorn main:app --reload

Τρία endpoints, και τα τρία σωστά με έναν χρήστη. Με πενήντα ταυτόχρονους, το
ένα παγώνει το service, το άλλο το καίει, και το τρίτο πουλάει θέσεις που δεν
υπάρχουν.
"""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from outside import crunch, fetch_occupancy_blocking

HERE = Path(__file__).resolve().parent
DB = HERE / "hall.db"

app = FastAPI()


class Booking(BaseModel):
    code: str
    customer: str


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB, timeout=15)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/report/{hall}")
async def report(hall: str) -> dict[str, int | str]:
    return {"hall": hall, "occupancy": fetch_occupancy_blocking(hall)}


@app.get("/crunch/{seed}")
async def heavy(seed: int) -> dict[str, int]:
    return {"seed": seed, "total": crunch(seed)}


@app.get("/shows/{code}")
def read_show(code: str) -> dict[str, int | str]:
    connection = connect()
    found = connection.execute(
        "SELECT code, title, seats_left FROM shows WHERE code = ?", (code,)
    ).fetchall()
    connection.close()
    if not found:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοια παράσταση")
    return {"code": found[0][0], "title": found[0][1], "seats_left": found[0][2]}


@app.post("/bookings", status_code=201)
def book(body: Booking) -> dict[str, int | str]:
    connection = connect()

    found = connection.execute("SELECT seats_left FROM shows WHERE code = ?", (body.code,)).fetchall()
    if not found:
        connection.close()
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοια παράσταση")

    seats_left = found[0][0]
    if seats_left < 1:
        connection.close()
        raise HTTPException(status_code=409, detail="Δεν έμειναν θέσεις")

    connection.execute("UPDATE shows SET seats_left = ? WHERE code = ?", (seats_left - 1, body.code))
    cursor = connection.execute(
        "INSERT INTO bookings (code, customer) VALUES (?, ?)", (body.code, body.customer)
    )
    connection.commit()
    booking_id = cursor.lastrowid
    connection.close()
    return {"id": booking_id or 0, "code": body.code}
