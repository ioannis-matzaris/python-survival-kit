"""Φτιάχνει το shop.db με παραγγελίες δύο πελατών. Τρέξε: python3 seed.py"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

ORDERS = [
    (1, 1, "PAR-1001", 4520, "sent"),
    (2, 1, "PAR-1002", 1180, "packing"),
    (3, 2, "PAR-1003", 9940, "sent"),
    (4, 2, "PAR-1004", 6075, "packing"),
    (5, 2, "PAR-1005", 2310, "packing"),
]

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.execute(
    """
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        reference TEXT NOT NULL,
        total_cents INTEGER NOT NULL,
        status TEXT NOT NULL
    )
    """
)
connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", ORDERS)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {len(ORDERS)} παραγγελίες, δύο πελατών")
