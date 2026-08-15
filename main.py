"""Η εγγραφή πελάτη του e-shop. Τρέξε: uvicorn main:app --reload

Δέχεται ό,τι του στείλεις. Και ό,τι δεχτεί, το πιστεύει.
"""

from decimal import Decimal

from fastapi import FastAPI

app = FastAPI()

CUSTOMERS: list[dict] = []


@app.post("/signup")
def signup(customer: dict) -> dict:
    CUSTOMERS.append(customer)
    return {
        "name": customer["name"],
        "afm": customer["afm"],
        "credit": str(Decimal(str(customer.get("credit", "0")))),
    }
