"""Ο πάροχος συναλλάγματος, όπως είναι στην πραγματικότητα. Μην τον πειράξεις.

Τρέχει μόνος του στο 8001 και τον σηκώνει ο βαθμολογητής. Έχει τρεις πόρτες:
μία που κρέμεται, μία που αποτυγχάνει δύο φορές και μετά συνέρχεται, και μία
που δεν συνέρχεται ποτέ.
"""

import time

from fastapi import FastAPI, HTTPException

app = FastAPI()

calls: dict[str, int] = {"slow": 0, "flaky": 0, "broken": 0}


@app.get("/calls/{name}")
def how_many(name: str) -> dict[str, int]:
    return {"calls": calls.get(name, 0)}


@app.post("/reset")
def reset() -> dict[str, str]:
    for name in calls:
        calls[name] = 0
    return {"status": "ok"}


@app.get("/slow")
def slow() -> dict[str, int]:
    calls["slow"] += 1
    time.sleep(30)
    return {"rate_cents": 10850}


@app.get("/flaky")
def flaky() -> dict[str, int]:
    calls["flaky"] += 1
    if calls["flaky"] <= 2:
        raise HTTPException(status_code=503, detail="Ο πάροχος είναι απασχολημένος")
    return {"rate_cents": 10850}


@app.get("/broken")
def broken() -> dict[str, int]:
    calls["broken"] += 1
    raise HTTPException(status_code=503, detail="Ο πάροχος είναι εκτός")
