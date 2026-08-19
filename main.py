"""Το service των τιμών. Τρέξε: uvicorn main:app --reload

Ρωτάει τον πάροχο και επιστρέφει την ισοτιμία. Όταν ο πάροχος αργεί, περιμένει
όσο χρειαστεί. Όταν αποτυγχάνει, ξαναρωτάει αμέσως, όσες φορές χρειαστεί.
"""

import requests
from fastapi import FastAPI

UPSTREAM = "http://127.0.0.1:8001"

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/quote")
def quote() -> dict[str, int]:
    answer = requests.get(f"{UPSTREAM}/slow")
    return {"rate_cents": answer.json()["rate_cents"]}


@app.get("/rates")
def rates() -> dict[str, int]:
    while True:
        try:
            answer = requests.get(f"{UPSTREAM}/flaky")
            answer.raise_for_status()
            return {"rate_cents": answer.json()["rate_cents"]}
        except requests.RequestException:
            continue


@app.get("/rates/backup")
def backup_rates() -> dict[str, int]:
    while True:
        try:
            answer = requests.get(f"{UPSTREAM}/broken")
            answer.raise_for_status()
            return {"rate_cents": answer.json()["rate_cents"]}
        except requests.RequestException:
            continue
