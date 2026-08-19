"""Το service των παραγγελιών. Τρέξε: uvicorn main:app --reload

Διαβάζει τις ρυθμίσεις του από το περιβάλλον, με προεπιλογές παντού, και
ξεκινάει ό,τι κι αν του δώσεις. Ακόμα κι αν δεν του δώσεις τίποτα.
"""

import os

from fastapi import FastAPI

DEBUG = bool(os.environ.get("DEBUG", "false"))
PORT = os.environ.get("PORT", "8000")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
TIMEOUT_SECONDS = os.environ.get("TIMEOUT_SECONDS", "5")
PROVIDER_API_KEY = "kleidi-tou-parochou-1234567890"

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config")
def config() -> dict[str, object]:
    return {
        "debug": DEBUG,
        "port": PORT,
        "database_url": DATABASE_URL,
        "timeout_seconds": TIMEOUT_SECONDS,
    }
