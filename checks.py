"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ξεκινάει ο ίδιος το service σου με uvicorn και το χτυπάει από έξω, όπως κάθε
άλλος client. Δεν διαβάζει τον κώδικά σου, διαβάζει τις απαντήσεις του.
Σταμάτα τον δικό σου uvicorn πριν το τρέξεις: η θύρα 8000 δεν χωράει δύο.
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

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"

results: list[tuple[bool, str]] = []


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


def call(path: str) -> tuple[int, Any]:
    """Επιστρέφει (status, σώμα). Status 0 σημαίνει ότι δεν απάντησε κανείς."""
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=5) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        raw = failure.read().decode("utf-8")
        try:
            return failure.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return failure.code, raw
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return 0, None


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 20.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/products")[0] != 0:
            return True
        time.sleep(0.2)
    return False


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


def price_of(product: Any) -> Any:
    return product.get("price") if isinstance(product, dict) else None


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα το service σου και ξανατρέξε.")
    sys.exit(1)

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, catalogue = call("/products")
    report(
        "Το GET /products επιστρέφει τα τρία προϊόντα",
        status == 200 and isinstance(catalogue, list) and len(catalogue) == 3,
    )

    status, one = call("/products/ZAX-1")
    report(
        "Το GET /products/ZAX-1 επιστρέφει τη ζάχαρη",
        status == 200 and isinstance(one, dict) and one.get("code") == "ZAX-1",
    )

    report(
        "Η τιμή ταξιδεύει ως κείμενο με δύο δεκαδικά",
        price_of(one) == "1.15",
    )

    if isinstance(catalogue, list):
        prices = [price_of(item) for item in catalogue]
    else:
        prices = []
    report(
        "Καμία τιμή του καταλόγου δεν έγινε αριθμός",
        len(prices) == 3 and all(isinstance(price, str) for price in prices),
    )

    status, missing = call("/products/DEN-YPARXEI")
    report("Ένας άγνωστος κωδικός παίρνει 404", status == 404)

    status, cheap = call("/products?max_price=1.50")
    report(
        "Το GET /products?max_price=1.50 αφήνει μόνο τη ζάχαρη",
        status == 200
        and isinstance(cheap, list)
        and [item.get("code") for item in cheap] == ["ZAX-1"],
    )

    status, health = call("/health")
    report(
        "Το GET /health απαντάει 200 με status ok",
        status == 200 and isinstance(health, dict) and health.get("status") == "ok",
    )
finally:
    service.terminate()
    try:
        service.wait(timeout=5)
    except subprocess.TimeoutExpired:
        service.kill()

total = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total}] {label}".ljust(60) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total}")
