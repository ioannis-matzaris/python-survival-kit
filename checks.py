"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ζητάει τιμές, αλλάζει τιμές, και ξαναζητάει. Ανάμεσα κοιτάει τι κρατάει το
Redis. Ξαναφτιάχνει τη βάση κάθε φορά, ώστε να ξεκινάει πάντα από τις ίδιες
τιμές. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
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

import redis

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"
BUDGET_MS = 20.0

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


def call(path: str, payload: Any = None, method: str = "GET") -> tuple[int, Any, float]:
    started = time.perf_counter()
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as answer:
            raw = answer.read().decode("utf-8")
            elapsed = (time.perf_counter() - started) * 1000
            return answer.status, json.loads(raw) if raw else None, elapsed
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return 0, None, (time.perf_counter() - started) * 1000


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 40.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/products/ZAX-1/price")[0] != 0:
            return True
        time.sleep(0.3)
    return False


if not (HERE / "shop.db").exists():
    print("Δεν βρήκα το shop.db. Τρέξε πρώτα: python3 seed.py")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα το service σου και ξανατρέξε.")
    sys.exit(1)

try:
    cache = redis.Redis(decode_responses=True)
    cache.ping()
except redis.RedisError:
    print("Δεν βρήκα Redis στο 6379. Ξεκίνα το με: sudo service redis-server start")
    sys.exit(1)

cache.flushdb()
subprocess.run([sys.executable, str(HERE / "seed.py")], cwd=HERE, stdout=subprocess.DEVNULL, check=True)

service = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Το service ξεκινάει και απαντάει στο 8000", wait_until_up(service))

    status, first, _ = call("/products/KAF-500/price")
    report(
        "Η τιμή του καφέ βγαίνει σωστά την πρώτη φορά",
        status == 200 and isinstance(first, dict) and first.get("price") == "6.40",
    )

    status, second, warm_ms = call("/products/KAF-500/price")
    report(
        f"Η δεύτερη κλήση έρχεται από το cache, κάτω από {BUDGET_MS:.0f} ms ({warm_ms:.1f})",
        status == 200 and second == first and warm_ms < BUDGET_MS,
    )

    call("/products/ZAX-1/price")
    sugar_cached = cache.exists("price:ZAX-1") == 1

    status, _, _ = call("/products/KAF-500/price", {"price_cents": 710}, "PUT")
    report("Η αλλαγή τιμής περνάει", status == 200)

    status, after, _ = call("/products/KAF-500/price")
    report(
        "Αμέσως μετά την αλλαγή, η τιμή που σερβίρεται είναι η καινούρια",
        status == 200 and isinstance(after, dict) and after.get("price") == "7.10",
    )

    report(
        "Η αλλαγή στον καφέ δεν πέταξε το cache της ζάχαρης",
        sugar_cached and cache.exists("price:ZAX-1") == 1,
    )

    ttls = [cache.ttl(key) for key in cache.keys("*")]
    report(
        "Κάθε κλειδί έχει προθεσμία λήξης, δεν μένει για πάντα",
        bool(ttls) and all(isinstance(one, int) and one > 0 for one in ttls),
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
    print(f"[{index}/{total_checks}] {label}".ljust(68) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
