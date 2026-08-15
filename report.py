"""Η αναφορά του Ιουλίου. Τρέξε: python3 report.py

Απαντάει σωστά. Απλώς κάθε φορά που τη ζητάει κάποιος, διαβάζει όλον τον
πίνακα από την αρχή.
"""

import sqlite3
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"


def july_total(connection: sqlite3.Connection) -> int:
    """Το σύνολο των παραγγελιών του Ιουλίου 2026 πάνω από 50 ευρώ, σε λεπτά."""
    row = connection.execute(
        """
        SELECT SUM(total_cents)
        FROM orders
        WHERE substr(created, 1, 7) = '2026-07' AND total_cents > 5000
        """
    ).fetchone()
    return row[0] or 0


if __name__ == "__main__":
    connection = sqlite3.connect(DB)
    started = time.perf_counter()
    total = july_total(connection)
    elapsed = time.perf_counter() - started
    connection.close()
    print(f"Σύνολο Ιουλίου: {total / 100:.2f} ευρώ")
    print(f"Χρόνος: {elapsed * 1000:.1f} ms")
