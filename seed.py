"""Φτιάχνει το shop.db. Τρέξε: python3 seed.py"""

import sqlite3
from pathlib import Path

import bcrypt

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

def hashed(secret: str) -> str:
    return bcrypt.hashpw(secret.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


USERS = [
    (1, "maria@example.gr", hashed("kalimera123"), 0),
    (2, "giorgos@example.gr", hashed("mystiko456"), 0),
]
ORDERS = [
    (1, 1, "PAR-1001", 4520),
    (2, 1, "PAR-1002", 1180),
    (3, 2, "PAR-1003", 9940),
]

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.executescript(
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        reference TEXT NOT NULL,
        total_cents INTEGER NOT NULL
    );
    """
)
connection.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", USERS)
connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ORDERS)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {len(USERS)} χρήστες και {len(ORDERS)} παραγγελίες")
