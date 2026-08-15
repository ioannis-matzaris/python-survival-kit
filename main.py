"""Το service του φούρνου. Τρέξε: uvicorn main:app --reload

Τρεις συναρτήσεις είναι γραμμένες και δουλεύουν. Μόνο η μία απαντάει σε
διεύθυνση.
"""

from decimal import Decimal

from fastapi import FastAPI

app = FastAPI()

PRICE_PER_KWH = Decimal("0.15")

MENU = [
    {"name": "Τυρόπιτα", "price": Decimal("2.20")},
    {"name": "Κουλούρι", "price": Decimal("0.90")},
    {"name": "Μπουγάτσα", "price": Decimal("3.50")},
]


@app.get("/")
def welcome() -> dict[str, str]:
    return {"service": "Ο φούρνος της γειτονιάς"}


def hours() -> dict[str, str]:
    return {"open": "07:00", "close": "15:00"}


def menu() -> list[dict[str, str]]:
    return [{"name": item["name"], "price": str(item["price"])} for item in MENU]


def bill(kwh: int) -> dict[str, str]:
    return {"total": str(kwh * PRICE_PER_KWH)}
