"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Κάνει δύο πράγματα. Ξεκινάει το service σου και το ρωτάει από έξω, και μετά
καλεί τις συναρτήσεις του pricing.py κατευθείαν, χωρίς κανένα HTTP. Το δεύτερο
είναι όλο το νόημα του lab. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
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
        if call("/quote?kwh=1")[0] != 0:
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

    status, day = call("/quote?kwh=320")
    report(
        "Το GET /quote?kwh=320 απαντάει 50.88",
        status == 200 and isinstance(day, dict) and day.get("total") == "50.88",
    )

    status, night = call("/quote?kwh=320&tariff=night&vat=false")
    report(
        "Το νυχτερινό τιμολόγιο χωρίς ΦΠΑ απαντάει 25.60",
        status == 200 and isinstance(night, dict) and night.get("total") == "25.60",
    )
finally:
    service.terminate()
    try:
        service.wait(timeout=5)
    except subprocess.TimeoutExpired:
        service.kill()

report("Υπάρχει αρχείο pricing.py στη ρίζα", (HERE / "pricing.py").exists())

WITHOUT_HTTP = """
import sys
from decimal import Decimal

import pricing

assert "fastapi" not in sys.modules, "το pricing.py έφερε μαζί του το FastAPI"
assert pricing.energy_charge(320, "day") == Decimal("48.00")
assert pricing.energy_charge(320, "night") == Decimal("25.60")
assert pricing.with_vat(Decimal("48.00")) == Decimal("50.88")
assert pricing.quote(320, "day", True) == Decimal("50.88")
assert pricing.quote(320, "night", False) == Decimal("25.60")
print("ok")
"""

direct = subprocess.run(
    [sys.executable, "-c", WITHOUT_HTTP],
    cwd=HERE,
    capture_output=True,
    text=True,
)
report(
    "Οι συναρτήσεις του pricing.py δίνουν σωστά ποσά μόνες τους",
    direct.returncode == 0,
)
NO_FASTAPI = """
import sys

import pricing

assert "fastapi" not in sys.modules, "το pricing.py έφερε μαζί του το FastAPI"
"""

alone = subprocess.run(
    [sys.executable, "-c", NO_FASTAPI],
    cwd=HERE,
    capture_output=True,
    text=True,
)
report(
    "Το pricing.py φορτώνει μόνο του, χωρίς το FastAPI",
    alone.returncode == 0,
)

main_source = (HERE / "main.py").read_text(encoding="utf-8")
report(
    "Τα ποσοστά του τιμολογίου δεν έμειναν μέσα στο main.py",
    "0.15" not in main_source
    and "0.08" not in main_source
    and "1.06" not in main_source,
)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(62) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
