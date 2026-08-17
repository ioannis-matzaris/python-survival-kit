"""Φτιάχνει το shop.db. Τρέξε: python3 seed.py"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

PRODUCTS = [("KAF-500", 640), ("ZAX-1", 115), ("GAL-1", 160)]

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.executescript(
    """
    CREATE TABLE products (code TEXT PRIMARY KEY, price_cents INTEGER NOT NULL);
    CREATE TABLE orders (id INTEGER PRIMARY KEY, email TEXT NOT NULL, total_cents INTEGER NOT NULL);
    CREATE TABLE receipts (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL);
    """
)
connection.executemany("INSERT INTO products VALUES (?, ?)", PRODUCTS)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {len(PRODUCTS)} προϊόντα και καμία παραγγελία")
