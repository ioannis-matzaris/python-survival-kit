"""Η εγγραφή και η σύνδεση. Εδώ δουλεύεις.

Δουλεύουν και οι δύο. Ο κωδικός του καθενός είναι διαβάσιμος από όποιον
ανοίξει τη βάση.
"""

import sqlite3


def register(connection: sqlite3.Connection, email: str, password: str) -> int:
    """Καταχωρεί χρήστη και επιστρέφει το id του."""
    cursor = connection.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)", (email, password)
    )
    connection.commit()
    return cursor.lastrowid


def login(connection: sqlite3.Connection, email: str, password: str) -> bool:
    """Λέει αν το ζεύγος email και κωδικού είναι σωστό."""
    row = connection.execute(
        "SELECT password FROM users WHERE email = ?", (email,)
    ).fetchone()
    if row is None:
        return False
    return row[0] == password
