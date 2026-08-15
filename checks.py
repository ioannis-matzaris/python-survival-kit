"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Στέλνει στο /signup ό,τι θα του έστελνε ένας κακογραμμένος client και ένας
κακόβουλος, και κοιτάει τι δέχτηκες. Σταμάτα τον δικό σου uvicorn πριν το
τρέξεις: η θύρα 8000 δεν χωράει δύο.
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

GOOD = {"name": "Μαρία Παπαδοπούλου", "afm": "094019245", "email": "maria@example.gr"}

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


def post(payload: Any) -> tuple[int, Any]:
    request = urllib.request.Request(
        f"{BASE}/signup",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        raw = failure.read().decode("utf-8")
        try:
            return failure.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return failure.code, raw
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, None


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 20.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if post(GOOD)[0] != 0:
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

    status, accepted = post(GOOD)
    report(
        "Μια σωστή εγγραφή γίνεται δεκτή",
        status == 200 and isinstance(accepted, dict) and accepted.get("afm") == "094019245",
    )

    status, _ = post({"name": "Μαρία", "email": "maria@example.gr"})
    report("Εγγραφή χωρίς ΑΦΜ παίρνει 422", status == 422)

    status, _ = post({**GOOD, "afm": "123456789"})
    report("ΑΦΜ που δεν περνάει τον έλεγχο ψηφίου παίρνει 422", status == 422)

    status, _ = post({**GOOD, "afm": 94019245})
    report("ΑΦΜ που ήρθε ως αριθμός δεν γίνεται δεκτό", status == 422)

    status, _ = post({**GOOD, "email": "maria-at-example"})
    report("Email χωρίς σχήμα διεύθυνσης παίρνει 422", status == 422)

    status, _ = post({**GOOD, "is_admin": True})
    report("Πεδίο που δεν ζήτησες παίρνει 422", status == 422)

    status, sneaky = post({**GOOD, "name": "  Μαρία Παπαδοπούλου  "})
    report(
        "Τα κενά γύρω από το όνομα κόβονται πριν αποθηκευτεί",
        status == 200
        and isinstance(sneaky, dict)
        and sneaky.get("name") == "Μαρία Παπαδοπούλου",
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
