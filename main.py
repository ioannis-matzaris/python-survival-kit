"""Το service των παραγγελιών. Τρέξε: uvicorn main:app --reload

Λέει τι κάνει. Το λέει με print, σε ελεύθερο κείμενο, χωρίς να λέει ποιανού
request ήταν η κάθε γραμμή.
"""

from fastapi import FastAPI, HTTPException

import provider

app = FastAPI()

ORDERS = {
    1001: {"reference": "PAR-1001", "total_cents": 4520},
    1002: {"reference": "PAR-1002", "total_cents": 1990},
    1003: {"reference": "PAR-1003", "total_cents": 7350},
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def read_order(order_id: int) -> dict[str, int | str]:
    print(f"Ζητήθηκε η παραγγελία {order_id}")
    if order_id not in ORDERS:
        print(f"Δεν βρέθηκε η παραγγελία {order_id}")
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοια παραγγελία")
    one = ORDERS[order_id]
    return {"id": order_id, "reference": one["reference"], "total_cents": one["total_cents"]}


@app.post("/orders/{order_id}/refund")
def refund_order(order_id: int) -> dict[str, int | str]:
    print(f"Ξεκινάει επιστροφή για την παραγγελία {order_id}")
    try:
        cents = provider.refund(order_id)
    except Exception as failure:
        print(f"Η επιστροφή απέτυχε: {failure}")
        raise HTTPException(status_code=502, detail="Ο πάροχος δεν απάντησε σωστά")
    print(f"Η επιστροφή ολοκληρώθηκε: {cents} λεπτά")
    return {"id": order_id, "refunded_cents": cents}
