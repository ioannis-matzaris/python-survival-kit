"""Οι παραγγελίες του e-shop. Τρέξε: uvicorn main:app --reload

Απαντάει σε όλα. Και σε όλα απαντάει «όλα καλά».
"""

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class NewOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference: str = Field(min_length=3)
    customer: str = Field(min_length=2)


ORDERS: list[dict] = [
    {"reference": "PAR-1001", "customer": "maria", "status": "sent"},
    {"reference": "PAR-1002", "customer": "maria", "status": "packing"},
    {"reference": "PAR-1003", "customer": "giorgos", "status": "sent"},
]


def find(reference: str) -> dict | None:
    for order in ORDERS:
        if order["reference"] == reference:
            return order
    return None


@app.get("/orders")
def list_orders(customer: str) -> list[dict] | dict:
    chosen = [order for order in ORDERS if order["customer"] == customer]
    if not chosen:
        return {"error": "δεν βρέθηκαν παραγγελίες"}
    return chosen


@app.get("/orders/{reference}")
def read_order(reference: str) -> dict | None:
    return find(reference)


@app.post("/orders")
def create_order(order: NewOrder) -> dict:
    ORDERS.append({**order.model_dump(), "status": "new"})
    return {"reference": order.reference, "status": "new"}
