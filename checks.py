"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Φτιάχνει ο ίδιος έξι tokens, ένα σωστό και πέντε χαλασμένα, και κοιτάει ποιο
δέχεται το service σου. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
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


def call(token: str | None) -> tuple[int, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token is not None else {}
    request = urllib.request.Request(f"{BASE}/me", headers=headers)
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
        if call(GOOD)[0] != 0:
            return True
        time.sleep(0.3)
    return False


GOOD = mint({"sub": "1", "exp": now() + timedelta(minutes=30), "iat": now()})
EXPIRED = mint({"sub": "1", "exp": now() - timedelta(minutes=5), "iat": now() - timedelta(hours=1)})
NO_EXPIRY = mint({"sub": "1"})
OTHER_KEY = mint({"sub": "1", "exp": now() + timedelta(minutes=30)}, OTHER_SECRET)

head, payload, signature = GOOD.split(".")
forged_payload = (
    jwt.utils.base64url_encode(json.dumps({"sub": "2"}).encode("utf-8")).decode("utf-8")
)
FORGED = f"{head}.{forged_payload}.{signature}"

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

    status, body = call(GOOD)
    report(
        "Έγκυρο token δίνει 200 και το σωστό όνομα",
        status == 200 and isinstance(body, dict) and body.get("name") == "Μαρία Παπαδοπούλου",
    )

    status, _ = call(FORGED)
    report("Token με πειραγμένο περιεχόμενο παίρνει 401", status == 401)

    status, _ = call(EXPIRED)
    report("Ληγμένο token παίρνει 401", status == 401)

    status, _ = call(NO_EXPIRY)
    report("Token χωρίς ημερομηνία λήξης παίρνει 401", status == 401)

    status, _ = call(OTHER_KEY)
    report("Token υπογεγραμμένο με άλλο μυστικό παίρνει 401", status == 401)

    status, _ = call(None)
    report("Καθόλου token παίρνει 401", status == 401)

    status, _ = call("skoupidia.skoupidia.skoupidia")
    report("Σκουπίδια στη θέση του token παίρνουν 401, όχι 500", status == 401)
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
