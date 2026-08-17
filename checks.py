"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ξεκινάει το service σου, ζητάει την ίδια αναφορά δύο φορές και κρατάει χρόνο.
Μετά ανοίγει το Redis και κοιτάει τι άφησες μέσα. Σταμάτα τον δικό σου uvicorn
πριν το τρέξεις: η θύρα 8000 δεν χωράει δύο.
"""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import redis

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
JULY = {"orders": 51645, "total_cents": 1047231143}
JUNE = {"orders": 49812, "total_cents": 1010130048}
BUDGET_MS = 20.0

results: list[tuple[bool, str]] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


def port_is_free() -> bool:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        probe.close()


def call(path: str) -> tuple[int, Any, float]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as answer:
            raw = answer.read().decode("utf-8")
            elapsed = (time.perf_counter() - started) * 1000
            return answer.status, json.loads(raw) if raw else None, elapsed
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return 0, None, (time.perf_counter() - started) * 1000


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 40.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/report?month=2025-01")[0] != 0:
            return True
        time.sleep(0.3)
    return False


if not (HERE / "shop.db").exists():
    print("Δεν βρήκα το shop.db. Τρέξε πρώτα: python3 seed.py")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα το service σου και ξανατρέξε.")
    sys.exit(1)

try:
    cache = redis.Redis(decode_responses=True)
    cache.ping()
except redis.RedisError:
    print("Δεν βρήκα Redis στο 6379. Ξεκίνα το με: sudo service redis-server start")
    sys.exit(1)

cache.flushdb()

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, july, cold_ms = call("/report?month=2025-07")
    report("Η αναφορά του Ιουλίου βγάζει σωστά νούμερα", status == 200 and july == JULY)

    status, again, warm_ms = call("/report?month=2025-07")
    report(
        f"Η δεύτερη κλήση για τον ίδιο μήνα κάτω από {BUDGET_MS:.0f} ms ({warm_ms:.1f})",
        status == 200 and again == JULY and warm_ms < BUDGET_MS,
    )

    status, june, _ = call("/report?month=2025-06")
    report(
        "Άλλος μήνας δίνει τα δικά του νούμερα, όχι του Ιουλίου",
        status == 200 and june == JUNE,
    )

    keys = sorted(cache.keys("*"))
    report("Το cache ζει στο Redis, όχι μέσα στο process", len(keys) >= 2)

    ttls = [cache.ttl(key) for key in keys]
    report(
        "Κάθε κλειδί έχει προθεσμία λήξης, δεν μένει για πάντα",
        bool(ttls) and all(isinstance(one, int) and one > 0 for one in ttls),
    )

    report(
        "Ο μήνας είναι μέσα στο κλειδί, ώστε να μην μπερδεύονται δύο αναφορές",
        any("2025-07" in key for key in keys) and any("2025-06" in key for key in keys),
    )
finally:
    service.terminate()
    try:
        service.wait(timeout=5)
    except subprocess.TimeoutExpired:
        service.kill()

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(68) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
