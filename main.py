"""Ο κατάλογος του e-shop. Τρέξε: uvicorn main:app --reload

Απαντάει, αλλά όχι όπως το περιμένει ο client που θα το καλέσει.
"""

from decimal import Decimal

from fastapi import FastAPI

app = FastAPI()

PRODUCTS = [
    {"code": "KAF-500", "name": "Καφές φίλτρου 500γρ", "price": Decimal("6.40")},
    {"code": "ZAX-1", "name": "Ζάχαρη 1κ", "price": Decimal("1.15")},
    {"code": "GAL-1", "name": "Γάλα φρέσκο 1λ", "price": Decimal("1.60")},
]


@app.get("/products")
def list_products():
    print(PRODUCTS)


@app.get("/products/{code}")
def read_product(code: str):
    for product in PRODUCTS:
        if product["code"] == code:
            return product
    return None
