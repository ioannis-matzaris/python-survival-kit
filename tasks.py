"""Οι δουλειές που τρέχουν έξω από το request.

Η αποστολή της απόδειξης δουλεύει. Απλώς δεν έχει σκεφτεί τι γίνεται αν την
καλέσει κάποιος δεύτερη φορά.
"""

import sqlite3
import time
from pathlib import Path

import redis

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

counter = redis.Redis(decode_responses=True)


def send_receipt(order_id: int, email: str) -> None:
    time.sleep(1)
    counter.incr(f"sent:{order_id}")

    connection = sqlite3.connect(DB)
    connection.execute("INSERT INTO receipts (order_id) VALUES (?)", (order_id,))
    connection.commit()
    connection.close()
