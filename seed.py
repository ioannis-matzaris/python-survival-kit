"""Φτιάχνει το users.db από το μηδέν. Τρέξε: python3 seed.py"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "users.db"

PEOPLE = [
    ("maria@example.gr", "kalimera123"),
    ("giorgos@example.gr", "kalimera123"),
    ("eleni@example.gr", "Th3sSal0niki!"),
]

if DB.exists():
    DB.unlink()

connection = sqlite3.connect(DB)
connection.execute(
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """
)
connection.executemany("INSERT INTO users (email, password) VALUES (?, ?)", PEOPLE)
connection.commit()
connection.close()

print(f"Έτοιμο: {DB.name} με {len(PEOPLE)} χρήστες")
