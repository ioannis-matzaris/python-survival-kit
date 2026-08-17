"""Φτιάχνει το shop.db με τον τιμοκατάλογο. Τρέξε: python3 seed.py"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

PRODUCTS = [
    ("KAF-500", "Καφές φίλτρου 500γρ", 640),
    ("ZAX-1", "Ζάχαρη 1κ", 115),
    ("GAL-1", "Γάλα φρέσκο 1λ", 160),
]

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.execute(
    """
    CREATE TABLE products (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        price_cents INTEGER NOT NULL
    )
    """
)
connection.executemany("INSERT INTO products VALUES (?, ?, ?)", PRODUCTS)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {len(PRODUCTS)} προϊόντα")
