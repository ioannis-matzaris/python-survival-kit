"""Η αναζήτηση τιμών του e-shop. Τρέξε: uvicorn main:app --reload

Το endpoint απαντάει σε όλους το ίδιο πράγμα: ολόκληρο τον κατάλογο. Ό,τι κι
αν του ζητήσεις.
"""

from decimal import Decimal

from fastapi import FastAPI

app = FastAPI()

PRODUCTS = [
    {"code": "KAF-500", "name": "Καφές φίλτρου 500γρ", "price": Decimal("6.40")},
    {"code": "KAF-250", "name": "Καφές espresso 250γρ", "price": Decimal("3.60")},
    {"code": "ZAX-1", "name": "Ζάχαρη 1κ", "price": Decimal("1.15")},
    {"code": "GAL-1", "name": "Γάλα φρέσκο 1λ", "price": Decimal("1.60")},
]


def as_json(product: dict) -> dict[str, str]:
    return {
        "code": product["code"],
        "name": product["name"],
        "price": str(product["price"]),
    }


@app.get("/search")
def search() -> list[dict[str, str]]:
    return [as_json(product) for product in PRODUCTS]
