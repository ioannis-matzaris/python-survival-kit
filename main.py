"""Η αναφορά του μήνα. Τρέξε: uvicorn main:app --reload

Κάθε κλήση ξαναδιαβάζει ένα εκατομμύριο γραμμές. Ακόμα κι αν ο ίδιος μήνας
ζητήθηκε πριν από δύο δευτερόλεπτα.
"""

import sqlite3
from pathlib import Path

from fastapi import FastAPI

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

app = FastAPI()


def month_report(month: str) -> dict[str, int]:
    connection = sqlite3.connect(DB)
    row = connection.execute(
        """
        SELECT COUNT(*), SUM(total_cents)
        FROM orders
        WHERE substr(created, 1, 7) = ?
        """,
        (month,),
    ).fetchone()
    connection.close()
    return {"orders": row[0], "total_cents": row[1] or 0}


@app.get("/report")
def report(month: str) -> dict[str, int]:
    return month_report(month)
