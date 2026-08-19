"""Φτιάχνει τη βάση από την αρχή. Τρέξε: python3 seed.py

Μία παράσταση, είκοσι θέσεις, καμία κράτηση.
"""

import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "hall.db"

DB.unlink(missing_ok=True)

connection = sqlite3.connect(DB)
connection.executescript(
    """
    CREATE TABLE shows (
        code       TEXT PRIMARY KEY,
        title      TEXT NOT NULL,
        seats_left INTEGER NOT NULL
    );

    CREATE TABLE bookings (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        code     TEXT NOT NULL,
        customer TEXT NOT NULL
    );

    INSERT INTO shows (code, title, seats_left) VALUES ('PAR-1', 'Η βραδιά των δέκα', 20);
    """
)
connection.commit()
connection.close()

print("Έτοιμη η βάση: PAR-1, είκοσι θέσεις.")
