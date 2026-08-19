"""Φτιάχνει τη βάση από την αρχή. Τρέξε: python3 seed.py

Ένα προϊόν, δέκα κομμάτια στο ράφι, καμία παραγγελία.
"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

DB.unlink(missing_ok=True)

connection = sqlite3.connect(DB)
connection.executescript(
    """
    CREATE TABLE products (
        sku   TEXT PRIMARY KEY,
        name  TEXT NOT NULL,
        stock INTEGER NOT NULL
    );

    CREATE TABLE orders (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        sku      TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        customer TEXT NOT NULL
    );

    INSERT INTO products (sku, name, stock) VALUES ('SKU-777', 'Ασύρματο πληκτρολόγιο', 10);
    """
)
connection.commit()
connection.close()

print("Έτοιμη η βάση: SKU-777, δέκα κομμάτια.")
