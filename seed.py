"""Φτιάχνει το shop.db. Τρέξε: python3 seed.py"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.execute(
    """
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        total_cents INTEGER NOT NULL
    )
    """
)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name}, άδειο και έτοιμο για παραγγελίες")
