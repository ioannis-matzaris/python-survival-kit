"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Σηκώνει το service, μαζεύει ό,τι γράφει στην έξοδό του, και μετά διαβάζει τις
γραμμές σαν μηχανή: τις φορτώνει με json και ψάχνει τα πεδία. Σταμάτα τον δικό
σου uvicorn πριν το τρέξεις.
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
LOGFILE = HERE / "checks-output.log"
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
MY_ID = "aitima-tou-vathmologiti-42"

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
    path: str, method: str = "GET", request_id: str | None = None
) -> tuple[int, dict[str, str]]:
    headers = {"X-Request-ID": request_id} if request_id else {}
    request = urllib.request.Request(f"{BASE}{path}", headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as answer:
            answer.read()
            return answer.status, dict(answer.headers)
    except urllib.error.HTTPError as failure:
        return failure.code, dict(failure.headers)
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, {}


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/health")[0] == 200:
            return True
        time.sleep(0.3)
    return False


def json_lines(raw: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            one = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(one, dict):
            found.append(one)
    return found


def text_lines(raw: str) -> list[str]:
    noise = ("INFO:", "WARNING:", "ERROR:", "Started", "Waiting", "Application", "Uvicorn", "Shutting", "Finished")
    keep = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("{") or line.startswith(noise):
            continue
        keep.append(line)
    return keep


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα το service σου και ξανατρέξε.")
    sys.exit(1)

LOGFILE.unlink(missing_ok=True)
sink = LOGFILE.open("wb")

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=sink,
    stderr=subprocess.STDOUT,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, headers = call("/orders/1001", request_id=MY_ID)
    mine_ok = status == 200
    echoed = headers.get("X-Request-ID") or headers.get("x-request-id")

    call("/orders/9999", request_id="anyparkti-paraggelia")
    call("/orders/4242/refund", "POST", request_id="apotyximeni-epistrofi")
    call("/orders/1001/refund", "POST")

    time.sleep(1.0)
finally:
    service.terminate()
    try:
        service.wait(timeout=5)
    except subprocess.TimeoutExpired:
        service.kill()
    sink.close()

raw = LOGFILE.read_text(encoding="utf-8", errors="replace")
lines = json_lines(raw)
leftovers = text_lines(raw)
mine = [one for one in lines if one.get("request_id") == MY_ID]
failed = [one for one in lines if one.get("request_id") == "apotyximeni-epistrofi"]

report("Η ανάγνωση παραγγελίας απαντάει κανονικά", mine_ok)

report(f"Το service γράφει γραμμές JSON ({len(lines)})", len(lines) >= 4)

report(
    "Καμία γραμμή δεν έμεινε σε ελεύθερο κείμενο",
    bool(lines) and not leftovers,
)

report(
    "Κάθε γραμμή έχει level και μήνυμα",
    bool(lines)
    and all(one.get("level") and (one.get("message") or one.get("msg")) for one in lines),
)

report(
    f"Οι γραμμές κουβαλάνε το X-Request-ID που έστειλα ({len(mine)})",
    len(mine) >= 1,
)

report("Η απάντηση γυρίζει πίσω το X-Request-ID", echoed == MY_ID)

own = [
    one.get("request_id")
    for one in lines
    if one.get("request_id") not in (None, "", MY_ID, "anyparkti-paraggelia", "apotyximeni-epistrofi")
]
report(f"Χωρίς header, το service φτιάχνει δικό του id ({len(set(own))})", len(set(own)) >= 1)

report(
    "Η αποτυχία του παρόχου γράφει ολόκληρο το traceback",
    any("ProviderError" in json.dumps(one, ensure_ascii=False) for one in failed),
)

report(
    "Τα ελληνικά μένουν ελληνικά, όχι \\u escapes",
    "\\u03" not in raw and any("α" <= letter <= "ω" for letter in raw),
)

report("Δεν έμεινε print στο main.py", "print(" not in (HERE / "main.py").read_text(encoding="utf-8"))

LOGFILE.unlink(missing_ok=True)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(66) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
