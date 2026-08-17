"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Μπαίνει ως δύο διαφορετικοί πελάτες με έγκυρα tokens, και ζητάει ο ένας τα
πράγματα του άλλου. Ξαναφτιάχνει τη βάση κάθε φορά. Σταμάτα τον δικό σου
uvicorn πριν το τρέξεις.
"""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import sqlite3

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
SECRET = "to-mystiko-tou-service-pou-den-fevgei-pote"
OTHER_SECRET = "to-mystiko-enos-allou-service-entelos-diaforetiko"

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


def call(path: str, token: str | None, method: str = "GET") -> tuple[int, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token is not None else {}
    request = urllib.request.Request(f"{BASE}{path}", headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        return failure.code, None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None


def mint(claims: dict[str, Any], secret: str = SECRET, algorithm: str = "HS256") -> str:
    return jwt.encode(claims, secret, algorithm=algorithm)


def now() -> datetime:
    return datetime.now(timezone.utc)


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/orders", MARIA)[0] != 0:
            return True
        time.sleep(0.3)
    return False


MARIA = mint({"sub": "1", "exp": now() + timedelta(minutes=30)})
GIORGOS = mint({"sub": "2", "exp": now() + timedelta(minutes=30)})

subprocess.run([sys.executable, str(HERE / "seed.py")], cwd=HERE, stdout=subprocess.DEVNULL, check=True)

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

    status, mine = call("/orders/1", MARIA)
    report(
        "Η Μαρία βλέπει τη δική της παραγγελία",
        status == 200 and isinstance(mine, dict) and mine.get("reference") == "PAR-1001",
    )

    status, stolen = call("/orders/3", MARIA)
    report("Η Μαρία δεν βλέπει την παραγγελία του Γιώργου", status == 404)

    status, listing = call("/orders", MARIA)
    report(
        "Η λίστα της Μαρίας έχει μόνο τις δικές της δύο",
        status == 200 and isinstance(listing, list) and len(listing) == 2,
    )

    status, wider = call("/orders?user_id=2", MARIA)
    report(
        "Το user_id στο URL δεν της δίνει τις παραγγελίες του Γιώργου",
        status in (200, 400, 404, 422)
        and (not isinstance(wider, list) or len(wider) == 2),
    )

    status, _ = call("/orders/3/cancel", MARIA, "POST")
    connection = sqlite3.connect(HERE / "shop.db")
    still = connection.execute("SELECT status FROM orders WHERE id = 3").fetchone()[0]
    connection.close()
    report(
        "Η Μαρία δεν μπορεί να ακυρώσει ξένη παραγγελία",
        status == 404 and still == "sent",
    )

    status, _ = call("/orders/2/cancel", MARIA, "POST")
    connection = sqlite3.connect(HERE / "shop.db")
    own = connection.execute("SELECT status FROM orders WHERE id = 2").fetchone()[0]
    connection.close()
    report(
        "Η Μαρία ακυρώνει κανονικά τη δική της",
        status == 200 and own == "cancelled",
    )

    status, his = call("/orders", GIORGOS)
    report(
        "Ο Γιώργος βλέπει τις τρεις δικές του, άθικτες",
        status == 200 and isinstance(his, list) and len(his) == 3,
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
