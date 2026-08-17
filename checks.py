"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Κοιτάει τρία πράγματα μαζί: τι κρατάει το cache, τι φεύγει από το request, και
τι γίνεται όταν το ίδιο job τρέξει δεύτερη φορά. Ξαναφτιάχνει τη βάση κάθε
φορά. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
"""

import json
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import redis
from rq import Queue

import tasks as tasks_module

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
BUDGET_MS = 300.0
CUSTOMER = "maria@example.gr"

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


def call(path: str, payload: Any = None, method: str = "GET") -> tuple[int, Any, float]:
    started = time.perf_counter()
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as answer:
            raw = answer.read().decode("utf-8")
            elapsed = (time.perf_counter() - started) * 1000
            try:
                body = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = raw
            return answer.status, body, elapsed
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return 0, None, (time.perf_counter() - started) * 1000


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 40.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/docs")[0] != 0:
            return True
        time.sleep(0.3)
    return False


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
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
subprocess.run([sys.executable, str(HERE / "seed.py")], cwd=HERE, stdout=subprocess.DEVNULL, check=True)

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, first, _ = call("/products/KAF-500/price")
    status, second, warm_ms = call("/products/KAF-500/price")
    report(
        f"Η δεύτερη κλήση της τιμής απαντάει κάτω από 20 ms ({warm_ms:.1f})",
        status == 200 and second == first and warm_ms < 20.0,
    )

    price_keys = [key for key in cache.keys("*") if "KAF-500" in key]
    report(
        "Το κλειδί της τιμής ζει στο Redis και έχει προθεσμία λήξης",
        bool(price_keys) and all(cache.ttl(key) > 0 for key in price_keys),
    )

    call("/products/KAF-500/price", {"price_cents": 710}, "PUT")
    status, after, _ = call("/products/KAF-500/price")
    report(
        "Μετά την αλλαγή τιμής σερβίρεται η καινούρια, όχι η παλιά",
        status == 200 and isinstance(after, dict) and after.get("price") == "7.10",
    )

    status, created, elapsed_ms = call(
        "/orders", {"email": CUSTOMER, "total_cents": 4520}, "POST"
    )
    report(
        f"Η παραγγελία απαντάει χωρίς να περιμένει το email ({elapsed_ms:.0f} ms)",
        status == 201 and elapsed_ms < BUDGET_MS,
    )

    connection = sqlite3.connect(DB)
    rows = connection.execute("SELECT id FROM orders").fetchall()
    connection.close()
    order_id = rows[0][0] if rows else 0

    queue = Queue(connection=redis.Redis())
    report("Ένα job περιμένει στο queue", queue.count == 1)

    subprocess.run(
        [sys.executable, "-m", "rq.cli", "worker", "--burst"],
        cwd=HERE, capture_output=True, text=True, timeout=60,
    )
    connection = sqlite3.connect(DB)
    receipts_once = connection.execute(
        "SELECT COUNT(*) FROM receipts WHERE order_id = ?", (order_id,)
    ).fetchone()[0]
    connection.close()
    report("Ο worker στέλνει την απόδειξη μία φορά", receipts_once == 1)

    queue.enqueue(tasks_module.send_receipt, order_id, CUSTOMER)
    subprocess.run(
        [sys.executable, "-m", "rq.cli", "worker", "--burst"],
        cwd=HERE, capture_output=True, text=True, timeout=60,
    )
    connection = sqlite3.connect(DB)
    receipts_twice = connection.execute(
        "SELECT COUNT(*) FROM receipts WHERE order_id = ?", (order_id,)
    ).fetchone()[0]
    connection.close()
    report(
        f"Το ίδιο job δεύτερη φορά δεν στέλνει δεύτερη απόδειξη ({receipts_twice})",
        receipts_twice == 1,
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
