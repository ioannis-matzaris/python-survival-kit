"""Ο πάροχος αποστολών, όπως είναι στην πραγματικότητα. Μην τον πειράξεις.

Τρέχει μόνος του στο 8001 και τον σηκώνει ο βαθμολογητής. Μπορεί να πέσει, να
σηκωθεί, και να αρχίσει να αργεί, γιατί έτσι κάνουν και οι αληθινοί.
"""

import time

from fastapi import FastAPI, HTTPException

app = FastAPI()

state = {"up": True, "delay_seconds": 0.0}


@app.post("/state")
def set_state(up: bool = True, delay_seconds: float = 0.0) -> dict[str, object]:
    state["up"] = up
    state["delay_seconds"] = delay_seconds
    return dict(state)


@app.get("/ping")
def ping() -> dict[str, str]:
    time.sleep(float(state["delay_seconds"]))
    if not state["up"]:
        raise HTTPException(status_code=503, detail="Ο πάροχος είναι εκτός")
    return {"status": "ok"}


@app.get("/shipping/{order_id}")
def shipping(order_id: int) -> dict[str, int | str]:
    time.sleep(float(state["delay_seconds"]))
    if not state["up"]:
        raise HTTPException(status_code=503, detail="Ο πάροχος είναι εκτός")
    return {"order_id": order_id, "carrier": "ELTA", "tracking": f"EL{order_id:06d}GR"}
