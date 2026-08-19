"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ρίχνει είκοσι ταυτόχρονες παραγγελίες πάνω σε δέκα κομμάτια και μετράει τι
έμεινε. Ξαναφτιάχνει τη βάση κάθε φορά. Σταμάτα τον δικό σου uvicorn πριν το
τρέξεις.
"""

import json
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
SKU = "SKU-777"
BUYERS = 20

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


def call(path: str, method: str = "GET", payload: Any = None, timeout: float = 30.0) -> tuple[int, Any]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        return failure.code, None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None


def query_db(sql: str, parameters: tuple = ()) -> list[tuple]:
    connection = sqlite3.connect(HERE / "shop.db")
    found = connection.execute(sql, parameters).fetchall()
    connection.close()
    return found


def reseed() -> None:
    subprocess.run(
        [sys.executable, str(HERE / "seed.py")], cwd=HERE, stdout=subprocess.DEVNULL, check=True
    )


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call(f"/products/{SKU}", timeout=2.0)[0] == 200:
            return True
        time.sleep(0.3)
    return False


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα το service σου και ξανατρέξε.")
    sys.exit(1)

reseed()

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, _ = call("/orders", "POST", {"sku": SKU, "quantity": 3, "customer": "maria"})
    left = query_db("SELECT stock FROM products WHERE sku = ?", (SKU,))
    report(
        "Μία παραγγελία περνάει και κατεβάζει το απόθεμα",
        status == 201 and bool(left) and left[0][0] == 7,
    )

    status, _ = call("/orders", "POST", {"sku": SKU, "quantity": 99, "customer": "maria"})
    report("Παραγγελία πάνω από το απόθεμα επιστρέφει 409", status == 409)

    status, _ = call("/orders", "POST", {"sku": "SKU-000", "quantity": 1, "customer": "maria"})
    report("Ανύπαρκτο προϊόν επιστρέφει 404", status == 404)

    reseed()

    def buy(number: int) -> int:
        return call("/orders", "POST", {"sku": SKU, "quantity": 1, "customer": f"pelatis-{number}"})[0]

    started = time.time()
    with ThreadPoolExecutor(max_workers=BUYERS) as crowd:
        codes = list(crowd.map(buy, range(BUYERS)))
    rush_seconds = time.time() - started

    accepted = sum(1 for code in codes if code == 201)
    refused = sum(1 for code in codes if code == 409)
    stock_left = query_db("SELECT stock FROM products WHERE sku = ?", (SKU,))[0][0]
    orders_written = query_db("SELECT COUNT(*) FROM orders")[0][0]

    report(f"Από τους είκοσι ταυτόχρονους περνάνε ακριβώς δέκα ({accepted})", accepted == 10)
    report(f"Οι υπόλοιποι δέκα παίρνουν 409 ({refused})", refused == 10)
    report(f"Το απόθεμα καταλήγει στο μηδέν, ποτέ αρνητικό ({stock_left})", stock_left == 0)
    report(
        f"Οι γραμμές στο orders είναι όσες και οι επιτυχίες ({orders_written})",
        orders_written == accepted,
    )
    report(
        f"Οι είκοσι ταυτόχρονοι τελειώνουν κάτω από 5 δευτερόλεπτα ({rush_seconds:.2f}s)",
        rush_seconds < 5.0,
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
    print(f"[{index}/{total_checks}] {label}".ljust(66) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
