"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ξεκινάει ο ίδιος το service σου με uvicorn και το ρωτάει από έξω. Σταμάτα τον
δικό σου uvicorn πριν το τρέξεις: η θύρα 8000 δεν χωράει δύο.
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
        if call("/search")[0] != 0:
            return True
        time.sleep(0.2)
    return False


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


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

    status, everything = call("/search")
    report(
        "Το GET /search χωρίς παράμετρο δίνει όλα τα προϊόντα",
        status == 200 and isinstance(everything, list) and len(everything) == 4,
    )

    status, coffee = call("/search?q=%CE%BA%CE%B1%CF%86")
    report(
        "Το GET /search?q=καφ κρατάει μόνο τους δύο καφέδες",
        status == 200
        and isinstance(coffee, list)
        and sorted(item.get("code") for item in coffee) == ["KAF-250", "KAF-500"],
    )

    status, cheap = call("/search?max_price=1.50")
    report(
        "Το GET /search?max_price=1.50 κρατάει μόνο τη ζάχαρη",
        status == 200
        and isinstance(cheap, list)
        and [item.get("code") for item in cheap] == ["ZAX-1"],
    )

    status, both = call("/search?q=%CE%BA%CE%B1%CF%86&max_price=4.00")
    report(
        "Οι δύο παράμετροι μαζί αφήνουν μόνο τον espresso",
        status == 200
        and isinstance(both, list)
        and [item.get("code") for item in both] == ["KAF-250"],
    )

    status, price = call("/products/ZAX-1/price")
    report(
        "Το GET /products/ZAX-1/price δίνει την τιμή ως κείμενο",
        status == 200 and isinstance(price, dict) and price.get("price") == "1.15",
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
    print(f"[{index}/{total_checks}] {label}".ljust(60) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
