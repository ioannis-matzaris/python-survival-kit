"""Το API των τιμών. Τρέξε: uvicorn main:app --reload

Δίνεις SKU, σου γυρίζει τιμές. Δουλεύει σωστά και αργεί απελπιστικά, και όσο
αργεί δεν απαντάει σε τίποτα άλλο.
"""

from fastapi import FastAPI, Query

from upstream import fetch_price_blocking

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/prices")
async def prices(sku: list[str] = Query(default=[])) -> dict[str, list[dict[str, int | str]]]:
    found: list[dict[str, int | str]] = []
    for one in sku:
        found.append({"sku": one, "price_cents": fetch_price_blocking(one)})
    return {"prices": found}
