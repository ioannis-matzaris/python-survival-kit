"""Το service των αποστολών. Τρέξε: uvicorn main:app --reload

Δουλεύει. Λέει τι κάνει με print, κρατάει τις ρυθμίσεις του μέσα στον κώδικα,
περιμένει τον πάροχο όσο χρειαστεί, και λέει πάντα ότι είναι μια χαρά.
"""

import requests
from fastapi import FastAPI, HTTPException

PROVIDER_URL = "http://127.0.0.1:8001"
PROVIDER_API_KEY = "kleidi-tou-parochou-1234567890"

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    answer = requests.get(f"{PROVIDER_URL}/ping")
    return {"status": "ok", "provider": str(answer.status_code)}


@app.get("/orders/{order_id}/shipping")
def shipping(order_id: int) -> dict[str, int | str]:
    print(f"Ζητήθηκε η αποστολή της παραγγελίας {order_id}")
    answer = requests.get(f"{PROVIDER_URL}/shipping/{order_id}")
    if answer.status_code != 200:
        print(f"Ο πάροχος απάντησε {answer.status_code}")
        raise HTTPException(status_code=502, detail="Ο πάροχος δεν απάντησε σωστά")
    body = answer.json()
    print(f"Βρέθηκε: {body['tracking']}")
    return body
