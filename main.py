"""Ο υπολογισμός λογαριασμού ρεύματος. Τρέξε: uvicorn main:app --reload

Ο υπολογισμός είναι σωστός. Ζει ολόκληρος μέσα στο endpoint, οπότε ο μόνος
τρόπος να τον δοκιμάσεις είναι να σηκώσεις HTTP.
"""

from decimal import ROUND_HALF_UP, Decimal

from fastapi import FastAPI

app = FastAPI()


@app.get("/quote")
def quote(kwh: int, tariff: str = "day", vat: bool = True) -> dict[str, str]:
    if tariff == "night":
        rate = Decimal("0.08")
    else:
        rate = Decimal("0.15")

    total = kwh * rate

    if vat:
        total = total * Decimal("1.06")

    total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"total": str(total)}
