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
        if call("/")[0] != 0:
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

    status, welcome = call("/")
    report(
        "Το GET / απαντάει με το όνομα του service",
        status == 200 and isinstance(welcome, dict) and "service" in welcome,
    )

    status, hours = call("/hours")
    report(
        "Το GET /hours δίνει ώρα ανοίγματος και κλεισίματος",
        status == 200
        and isinstance(hours, dict)
        and hours.get("open") == "07:00"
        and hours.get("close") == "15:00",
    )

    status, menu = call("/menu")
    report(
        "Το GET /menu δίνει τα τρία είδη του φούρνου",
        status == 200 and isinstance(menu, list) and len(menu) == 3,
    )

    report(
        "Οι τιμές του menu ταξιδεύουν ως κείμενο",
        isinstance(menu, list)
        and len(menu) == 3
        and all(isinstance(item.get("price"), str) for item in menu),
    )

    status, total = call("/bill?kwh=320")
    report(
        "Το GET /bill?kwh=320 απαντάει 48.00",
        status == 200 and isinstance(total, dict) and total.get("total") == "48.00",
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
