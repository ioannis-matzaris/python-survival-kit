"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ρωτάει το service σου με σωστά και με λάθος αιτήματα, και κοιτάει τρία
πράγματα: τον αριθμό, το σχήμα του σώματος, και τι αποκαλύπτει όταν σκάσει.
Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
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


def send(path: str, payload: Any = None) -> tuple[int, Any, dict[str, str]]:
    """Επιστρέφει (status, σώμα, επικεφαλίδες). Status 0 σημαίνει καμία απάντηση."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as answer:
            raw = answer.read().decode("utf-8")
            headers = {key.lower(): value for key, value in answer.headers.items()}
            return answer.status, json.loads(raw) if raw else None, headers
    except urllib.error.HTTPError as failure:
        raw = failure.read().decode("utf-8")
        headers = {key.lower(): value for key, value in failure.headers.items()}
        try:
            return failure.code, json.loads(raw) if raw else None, headers
        except json.JSONDecodeError:
            return failure.code, raw, headers
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, None, {}


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 20.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if send("/workshops/PY-101")[0] != 0:
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

    status, workshop, _ = send("/workshops/PY-101")
    report(
        "Υπαρκτό σεμινάριο δίνει 200",
        status == 200 and isinstance(workshop, dict) and workshop.get("seats") == 2,
    )

    status, missing, _ = send("/workshops/DEN-YPARXEI")
    report("Ανύπαρκτο σεμινάριο δίνει 404", status == 404)
    report(
        "Το σώμα του λάθους έχει code και message στο πρώτο επίπεδο",
        isinstance(missing, dict)
        and missing.get("code") == "unknown_workshop"
        and isinstance(missing.get("message"), str)
        and missing.get("message") != "",
    )

    status, _, _ = send("/bookings", {"code": "PY-101", "email": "maria@example.gr"})
    report("Νέα κράτηση δίνει 201", status == 201)

    status, again, _ = send("/bookings", {"code": "PY-101", "email": "maria@example.gr"})
    report(
        "Δεύτερη κράτηση του ίδιου δίνει 409 με code duplicate_booking",
        status == 409 and isinstance(again, dict) and again.get("code") == "duplicate_booking",
    )

    status, full, _ = send("/bookings", {"code": "API-201", "email": "giorgos@example.gr"})
    report(
        "Κράτηση σε πλήρες σεμινάριο δίνει 409 με code sold_out",
        status == 409 and isinstance(full, dict) and full.get("code") == "sold_out",
    )

    status, boom, _ = send("/workshops/API-201/attendance")
    leaked = json.dumps(boom, ensure_ascii=False) if boom is not None else ""
    report(
        "Ένα δικό σου bug δίνει 500 χωρίς να αποκαλύπτει το σφάλμα",
        status == 500 and "division" not in leaked and "zero" not in leaked.lower(),
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
    print(f"[{index}/{total_checks}] {label}".ljust(62) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
