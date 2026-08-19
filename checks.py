"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ρίχνει φορτίο και μετράει: πόσο κάνουν τα πολλά μαζί, αν το /health απαντάει
όσο τρέχουν, και πόσες θέσεις πούλησε το service που είχε είκοσι.
Ξαναφτιάχνει τη βάση κάθε φορά. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
"""

import json
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from outside import crunch, occupancy_of

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
SHOW = "PAR-1"
SEATS = 20
CROWD = 50

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


def call(path: str, method: str = "GET", payload: Any = None, timeout: float = 60.0) -> tuple[int, Any]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        return failure.code, None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None


def query_db(sql: str, parameters: tuple = ()) -> list[tuple]:
    connection = sqlite3.connect(HERE / "hall.db")
    found = connection.execute(sql, parameters).fetchall()
    connection.close()
    return found


def reseed() -> None:
    subprocess.run(
        [sys.executable, str(HERE / "seed.py")], cwd=HERE, stdout=subprocess.DEVNULL, check=True
    )


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/health", timeout=2.0)[0] == 200:
            return True
        time.sleep(0.3)
    return False


def health_while(work: "threading.Thread") -> float:
    delays: list[float] = []
    work.start()
    time.sleep(0.15)
    while work.is_alive():
        mark = time.time()
        call("/health", timeout=20.0)
        delays.append(time.time() - mark)
        time.sleep(0.05)
    work.join()
    return max(delays) if delays else 99.0


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα το service σου και ξανατρέξε.")
    sys.exit(1)

reseed()

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, one = call("/report/A")
    report(
        "Το /report δίνει τη σωστή πληρότητα",
        status == 200 and isinstance(one, dict) and one.get("occupancy") == occupancy_of("A"),
    )

    halls = [f"HALL-{number:02d}" for number in range(CROWD)]
    started = time.time()
    with ThreadPoolExecutor(max_workers=CROWD) as visitors:
        codes = list(visitors.map(lambda hall: call(f"/report/{hall}")[0], halls))
    report_seconds = time.time() - started
    report(
        f"Πενήντα ταυτόχρονα /report τελειώνουν κάτω από 2 δευτερόλεπτα ({report_seconds:.2f}s)",
        all(code == 200 for code in codes) and report_seconds < 2.0,
    )

    def report_rush() -> None:
        with ThreadPoolExecutor(max_workers=20) as visitors:
            list(visitors.map(lambda number: call(f"/report/HALL-{number:02d}"), range(20)))

    load = threading.Thread(target=report_rush)
    report(
        "Το /health απαντάει κι όσο τρέχουν τα /report",
        health_while(load) < 0.3,
    )

    status, heavy = call("/crunch/3")
    report(
        "Το /crunch δίνει το σωστό σύνολο",
        status == 200 and isinstance(heavy, dict) and heavy.get("total") == crunch(3),
    )

    burn = threading.Thread(target=lambda: call("/crunch/5"))
    report(
        "Το /health απαντάει κι όσο τρέχει το /crunch",
        health_while(burn) < 0.3,
    )

    reseed()

    def grab(number: int) -> int:
        return call("/bookings", "POST", {"code": SHOW, "customer": f"theatis-{number}"})[0]

    with ThreadPoolExecutor(max_workers=CROWD) as crowd:
        booking_codes = list(crowd.map(grab, range(CROWD)))

    accepted = sum(1 for code in booking_codes if code == 201)
    seats_left = query_db("SELECT seats_left FROM shows WHERE code = ?", (SHOW,))[0][0]
    written = query_db("SELECT COUNT(*) FROM bookings")[0][0]

    report(f"Από τους πενήντα κλείνουν ακριβώς είκοσι ({accepted})", accepted == SEATS)
    report(f"Οι θέσεις καταλήγουν στο μηδέν, ποτέ αρνητικές ({seats_left})", seats_left == 0)
    report(f"Οι κρατήσεις στη βάση είναι όσες και οι επιτυχίες ({written})", written == accepted)
finally:
    service.terminate()
    try:
        service.wait(timeout=5)
    except subprocess.TimeoutExpired:
        service.kill()

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(68) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
