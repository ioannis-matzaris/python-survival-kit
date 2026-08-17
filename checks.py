"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Περνάει από όλα όσα έμαθε το κεφάλαιο: πώς αποθηκεύεις κωδικούς, τι δέχεσαι
ως token, και ποιος βλέπει τι. Ξαναφτιάχνει τη βάση κάθε φορά. Σταμάτα τον
δικό σου uvicorn πριν το τρέξεις.
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


def call(
    path: str, token: str | None = None, method: str = "GET", payload: Any = None
) -> tuple[int, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token is not None else {}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
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
        if call("/orders/1", MARIA)[0] != 0:
            return True
        time.sleep(0.3)
    return False


MARIA = mint({"sub": "1", "exp": now() + timedelta(minutes=30)})
NO_EXPIRY = mint({"sub": "1"})
head, payload, signature = MARIA.split(".")
FORGED = (
    f"{head}."
    f"{jwt.utils.base64url_encode(json.dumps({'sub': '2', 'exp': 9999999999}).encode()).decode()}."
    f"{signature}"
)


def query_db(sql: str, parameters: tuple = ()) -> list[tuple]:
    connection = sqlite3.connect(HERE / "shop.db")
    found = connection.execute(sql, parameters).fetchall()
    connection.close()
    return found

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

    status, session = call("/login", None, "POST", {"email": "maria@example.gr", "password": "kalimera123"})
    maria_token = session.get("token") if isinstance(session, dict) else None
    report("Η σύνδεση με σωστά στοιχεία δίνει token", status == 200 and bool(maria_token))

    status, _ = call("/signup", None, "POST", {"email": "nikos@example.gr", "password": "kalimera123"})
    stored = query_db("SELECT password FROM users WHERE email = ?", ("nikos@example.gr",))
    report(
        "Ο κωδικός της εγγραφής δεν αποθηκεύεται σε καθαρό κείμενο",
        status == 201 and bool(stored) and stored[0][0].startswith("$2"),
    )

    call("/signup", None, "POST", {"email": "kakos@example.gr", "password": "kalimera123", "is_admin": True})
    sneaky = query_db("SELECT is_admin FROM users WHERE email = ?", ("kakos@example.gr",))
    report(
        "Κανείς δεν γίνεται admin γράφοντάς το στο σώμα του request",
        not sneaky or sneaky[0][0] == 0,
    )

    status, _ = call("/orders/1", FORGED)
    report("Πλαστό token δεν ανοίγει τίποτα", status == 401)

    status, _ = call("/orders/1", NO_EXPIRY)
    report("Token χωρίς λήξη δεν γίνεται δεκτό", status == 401)

    status, mine = call("/orders/1", maria_token)
    report(
        "Η Μαρία βλέπει τη δική της παραγγελία",
        status == 200 and isinstance(mine, dict) and mine.get("reference") == "PAR-1001",
    )

    status, _ = call("/orders/3", maria_token)
    report("Η Μαρία δεν βλέπει την παραγγελία του Γιώργου", status == 404)
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
