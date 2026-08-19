"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Μετράει δύο πράγματα: πόσο κάνουν δέκα κλήσεις, και αν το service απαντάει σε
κάτι άλλο όσο τις κάνει. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
"""

import json
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from upstream import price_of

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
SKUS = [f"SKU-{number:03d}" for number in range(1, 11)]

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


def call(path: str, timeout: float = 30.0) -> tuple[int, Any]:
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=timeout) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        return failure.code, None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None


def prices_path(skus: list[str]) -> str:
    return "/prices?" + urllib.parse.urlencode([("sku", one) for one in skus])


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/health", timeout=2.0)[0] == 200:
            return True
        time.sleep(0.3)
    return False


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

    started = time.time()
    status, many = call(prices_path(SKUS))
    ten_seconds = time.time() - started
    rows = many.get("prices") if isinstance(many, dict) else None

    report(
        "Τα δέκα SKU επιστρέφονται όλα, στη σειρά που ζητήθηκαν",
        status == 200
        and isinstance(rows, list)
        and [row.get("sku") for row in rows] == SKUS,
    )
    report(
        "Οι τιμές είναι οι σωστές",
        isinstance(rows, list)
        and all(row.get("price_cents") == price_of(row.get("sku", "")) for row in rows),
    )

    status, one = call(prices_path(["SKU-001"]))
    single = one.get("prices") if isinstance(one, dict) else None
    report(
        "Ένα SKU δουλεύει κι αυτό",
        status == 200
        and isinstance(single, list)
        and len(single) == 1
        and single[0].get("price_cents") == price_of("SKU-001"),
    )

    report(f"Οι δέκα κλήσεις τελειώνουν κάτω από 1 δευτερόλεπτο ({ten_seconds:.2f}s)", ten_seconds < 1.0)

    health_delays: list[float] = []

    def measure_health() -> None:
        time.sleep(0.15)
        for _ in range(3):
            mark = time.time()
            call("/health", timeout=10.0)
            health_delays.append(time.time() - mark)

    watcher = threading.Thread(target=measure_health)
    watcher.start()
    call(prices_path(SKUS))
    watcher.join()
    slowest = max(health_delays) if health_delays else 99.0
    report(
        f"Το /health απαντάει κι όσο τρέχουν οι κλήσεις ({slowest * 1000:.0f}ms)",
        slowest < 0.2,
    )

    source = (HERE / "main.py").read_text(encoding="utf-8")
    report(
        "Ο handler δεν καλεί τον blocking client",
        "fetch_price_blocking" not in source and "time.sleep" not in source,
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
    print(f"[{index}/{total_checks}] {label}".ljust(64) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
