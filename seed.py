"""Φτιάχνει το shop.db με μισό εκατομμύριο παραγγελίες.

Τρέξε: python3 seed.py

Θέλει λίγα δευτερόλεπτα και γύρω στα 40 MB στον δίσκο.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"
ORDERS = 2_000_000
START = date(2024, 1, 1)

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.executescript(
    """
    CREATE TABLE orders (
        reference TEXT PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        created TEXT NOT NULL,
        total_cents INTEGER NOT NULL
    );
    """
)

generator = random.Random(20260815)


def rows():
    for number in range(ORDERS):
        day = START + timedelta(days=generator.randrange(1000))
        yield (
            f"PAR-{number:07d}",
            generator.randrange(1, 5000),
            day.isoformat(),
            generator.randrange(500, 40000),
        )


connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", rows())
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {ORDERS} παραγγελίες")
