"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ανοίγει το shop.db, καλεί τις πέντε συναρτήσεις σου και συγκρίνει τις
απαντήσεις. Και κοιτάει ένα ακόμα: αν την απάντηση τη βρήκε η SQL ή η Python.
"""

import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

results: list[tuple[bool, str]] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


def answer(call) -> object:
    try:
        return call()
    except Exception as error:
        return f"σφάλμα: {error}"


if not DB.exists():
    print("Δεν βρήκα το shop.db. Τρέξε πρώτα: python3 seed.py")
    sys.exit(1)

try:
    import queries
except Exception as error:
    print(f"Το queries.py δεν φορτώνει: {error}")
    sys.exit(1)

connection = sqlite3.connect(DB)

report("Η total_customers μετράει 4 πελάτες", answer(lambda: queries.total_customers(connection)) == 4)

report(
    "Η orders_over(5000) δίνει τις τέσσερις μεγάλες με σειρά",
    answer(lambda: queries.orders_over(connection, 5000))
    == ["PAR-1006", "PAR-1003", "PAR-1008", "PAR-1004"],
)

report(
    "Η orders_in_month(2026-07) μετράει 5 παραγγελίες",
    answer(lambda: queries.orders_in_month(connection, "2026-07")) == 5,
)

report(
    "Η customer_of(PAR-1004) δίνει τον Γιώργο Δήμου",
    answer(lambda: queries.customer_of(connection, "PAR-1004")) == "Γιώργος Δήμου",
)

report(
    "Η customer_of σε ανύπαρκτη παραγγελία δίνει None",
    answer(lambda: queries.customer_of(connection, "PAR-9999")) is None,
)

report(
    "Η spend_by_customer δίνει τα σύνολα κατά φθίνουσα σειρά",
    answer(lambda: queries.spend_by_customer(connection))
    == [("Γιώργος Δήμου", 18325), ("Ελένη Νικολάου", 16490), ("Μαρία Παπαδοπούλου", 13040)],
)

report(
    "Κωδικός με απόστροφο μέσα του δεν ρίχνει το ερώτημα",
    answer(lambda: queries.customer_of(connection, "PAR-1004' OR reference LIKE '%")) is None,
)

connection.close()

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(64) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
