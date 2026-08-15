"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Καλεί τη july_total, κρατάει το SQL που έστειλε στη βάση, το περνάει από
EXPLAIN QUERY PLAN και μετράει χρόνο. Δεν κοιτάει πώς το έγραψες, κοιτάει τι
έκανε η βάση.
"""

import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"
JULY_TOTAL = 1245524500
BUDGET_MS = 20.0

results: list[tuple[bool, str]] = []
statements: list[str] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


if not DB.exists():
    print("Δεν βρήκα το shop.db. Τρέξε πρώτα: python3 seed.py")
    sys.exit(1)

try:
    import report as student
except Exception as error:
    print(f"Το report.py δεν φορτώνει: {error}")
    sys.exit(1)

connection = sqlite3.connect(DB)
connection.set_trace_callback(statements.append)

connection.execute("SELECT 1").fetchone()
started = time.perf_counter()
answer = student.july_total(connection)
elapsed_ms = (time.perf_counter() - started) * 1000

connection.set_trace_callback(None)

report(f"Το σύνολο του Ιουλίου βγαίνει {JULY_TOTAL} λεπτά", answer == JULY_TOTAL)

indexes = connection.execute(
    "SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = 'orders' AND sql IS NOT NULL"
).fetchall()
index_sql = " ".join(row[0] for row in indexes).lower()
report("Υπάρχει δείκτης πάνω στη στήλη created", "created" in index_sql)

selects = [one for one in statements if one.strip().lower().startswith("select")]
query = selects[-1] if selects else ""

plan = ""
if query:
    try:
        rows = connection.execute("EXPLAIN QUERY PLAN " + query).fetchall()
        plan = " ".join(str(row[-1]) for row in rows)
    except sqlite3.Error as error:
        plan = f"σφάλμα: {error}"

report("Το ερώτημα ψάχνει, δεν σαρώνει τον πίνακα", "SEARCH" in plan)

report(
    "Καμία συνάρτηση δεν μπαίνει πάνω στη στήλη created",
    bool(query) and "substr" not in query.lower() and "strftime" not in query.lower(),
)

report(
    "Ο δείκτης απαντάει χωρίς να ανοίξει τον πίνακα",
    "COVERING INDEX" in plan,
)

report(f"Η αναφορά τελειώνει κάτω από {BUDGET_MS:.0f} ms ({elapsed_ms:.1f})", elapsed_ms < BUDGET_MS)

connection.close()

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(64) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
