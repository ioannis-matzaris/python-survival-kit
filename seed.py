"""Φτιάχνει το shop.db από το μηδέν. Τρέξε: python3 seed.py

Το τρέχεις όποτε θες να γυρίσεις τη βάση στην αρχική της κατάσταση.
"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

CUSTOMERS = [
    (1, "Μαρία Παπαδοπούλου", "maria@example.gr"),
    (2, "Γιώργος Δήμου", "giorgos@example.gr"),
    (3, "Ελένη Νικολάου", "eleni@example.gr"),
    (4, "Νίκος Αντωνίου", "nikos@example.gr"),
]

ORDERS = [
    ("PAR-1001", 1, "2026-07-03", 4520),
    ("PAR-1002", 1, "2026-07-19", 1180),
    ("PAR-1003", 2, "2026-06-28", 9940),
    ("PAR-1004", 2, "2026-07-21", 6075),
    ("PAR-1005", 2, "2026-08-02", 2310),
    ("PAR-1006", 3, "2026-07-11", 15600),
    ("PAR-1007", 3, "2026-07-30", 890),
    ("PAR-1008", 1, "2026-08-14", 7340),
]

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.executescript(
    """
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );

    CREATE TABLE orders (
        reference TEXT PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        created TEXT NOT NULL,
        total_cents INTEGER NOT NULL
    );
    """
)
connection.executemany("INSERT INTO customers VALUES (?, ?, ?)", CUSTOMERS)
connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ORDERS)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {len(CUSTOMERS)} πελάτες και {len(ORDERS)} παραγγελίες")
