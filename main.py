"""Οι κρατήσεις σεμιναρίων. Τρέξε: uvicorn main:app --reload

Κάθε endpoint πιάνει μόνο του ό,τι μπορεί να πάει στραβά, και ό,τι πιάσει το
επιστρέφει ως κείμενο με status 200.
"""

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, EmailStr

import bookings

app = FastAPI()


class NewBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    email: EmailStr


@app.get("/workshops/{code}")
def read_workshop(code: str) -> dict:
    try:
        return bookings.workshop(code)
    except bookings.UnknownWorkshop as error:
        return {"error": str(error)}


@app.post("/bookings")
def create_booking(booking: NewBooking) -> dict:
    try:
        return bookings.book(booking.code, booking.email)
    except bookings.DuplicateBooking as error:
        return {"error": str(error)}
    except bookings.SoldOut as error:
        return {"error": str(error)}
    except bookings.UnknownWorkshop as error:
        return {"error": str(error)}


@app.get("/workshops/{code}/attendance")
def read_attendance(code: str) -> dict:
    try:
        return {"rate": bookings.attendance_rate(code)}
    except Exception as error:
        return {"error": str(error)}
