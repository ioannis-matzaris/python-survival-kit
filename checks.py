"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Δουλεύει πάνω σε αντίγραφο της βάσης, καλεί τις δικές σου register και login,
και μετά ανοίγει τη βάση και κοιτάει τι έγραψες μέσα.
"""

import shutil
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "users.db"
COPY = HERE / "checks.db"
LONG_GREEK = "Το σπίτι μου στη Θεσσαλονίκη έχει μπλε παράθυρα και κόκκινη πόρτα"

results: list[tuple[bool, str]] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


def attempt(call, fallback=None):
    try:
        return call()
    except Exception as error:
        return f"σφάλμα: {error}" if fallback is None else fallback


if not SOURCE.exists():
    print("Δεν βρήκα το users.db. Τρέξε πρώτα: python3 seed.py")
    sys.exit(1)

try:
    import users
except Exception as error:
    print(f"Το users.py δεν φορτώνει: {error}")
    sys.exit(1)

shutil.copy(SOURCE, COPY)
connection = sqlite3.connect(COPY)

migrated = attempt(lambda: users.migrate_plaintext(connection), "λείπει")

first = attempt(lambda: users.register(connection, "nikos@example.gr", "kalimera123"))
second = attempt(lambda: users.register(connection, "sofia@example.gr", "kalimera123"))

stored = {
    row[0]: row[1]
    for row in connection.execute("SELECT email, password FROM users").fetchall()
}

report(
    "Υπάρχει migrate_plaintext και τρέχει χωρίς σφάλμα",
    migrated != "λείπει" and not str(migrated).startswith("σφάλμα:"),
)

report(
    "Κανένας κωδικός δεν είναι αποθηκευμένος σε καθαρό κείμενο",
    "kalimera123" not in stored.values() and "Th3sSal0niki!" not in stored.values(),
)

new_secrets = [stored.get("nikos@example.gr", ""), stored.get("sofia@example.gr", "")]
report(
    "Ό,τι αποθηκεύεις μοιάζει με bcrypt hash",
    all(isinstance(one, str) and one.startswith("$2") and len(one) >= 59 for one in new_secrets),
)

report(
    "Δύο χρήστες με τον ίδιο κωδικό δεν έχουν το ίδιο αποθηκευμένο",
    new_secrets[0] != new_secrets[1] and all(new_secrets),
)

report(
    "Σωστός κωδικός περνάει το login",
    attempt(lambda: users.login(connection, "nikos@example.gr", "kalimera123"), False) is True,
)

report(
    "Λάθος κωδικός δεν περνάει",
    attempt(lambda: users.login(connection, "nikos@example.gr", "kalimera124"), True) is False,
)

report(
    "Ο κωδικός του ενός δεν ανοίγει τον λογαριασμό του άλλου",
    attempt(lambda: users.login(connection, "eleni@example.gr", "kalimera123"), True) is False,
)

report(
    "Ανύπαρκτο email δεν περνάει και δεν ρίχνει το πρόγραμμα",
    attempt(lambda: users.login(connection, "kanenas@example.gr", "kalimera123"), True) is False,
)


def refuses_long_password() -> bool:
    """Θέλουμε δικό σου ValueError με ελληνικό μήνυμα, όχι το σφάλμα της bcrypt."""
    try:
        users.register(connection, "long@example.gr", LONG_GREEK)
    except ValueError as error:
        message = str(error)
        return any("Α" <= letter <= "ω" for letter in message) and "72" not in message
    except Exception:
        return False
    return False


report(
    f"Passphrase {len(LONG_GREEK.encode('utf-8'))} bytes απορρίπτεται με δικό σου μήνυμα",
    refuses_long_password(),
)

connection.close()
COPY.unlink(missing_ok=True)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(72) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
