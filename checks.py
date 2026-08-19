"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Σηκώνει και τον πάροχο και το service σου, και μετά τους βάζει σε δύσκολη
θέση: μια πόρτα που κρέμεται, μια που αποτυγχάνει δύο φορές, και μια που δεν
συνέρχεται ποτέ. Σταμάτα τον δικό σου uvicorn πριν το τρέξεις.
"""

import json
import re
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
UPSTREAM_PORT = 8001
BASE = f"http://{HOST}:{PORT}"
UPSTREAM = f"http://{HOST}:{UPSTREAM_PORT}"

results: list[tuple[bool, str]] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


def port_is_free(port: int) -> bool:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind((HOST, port))
        return True
    except OSError:
        return False
    finally:
        probe.close()


def fetch(url: str, method: str = "GET", timeout: float = 30.0) -> tuple[int, Any, float]:
    started = time.time()
    request = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None, time.time() - started
    except urllib.error.HTTPError as failure:
        return failure.code, None, time.time() - started
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None, time.time() - started


def calls_to(name: str) -> int:
    status, body, _ = fetch(f"{UPSTREAM}/calls/{name}", timeout=10.0)
    return body.get("calls", -1) if status == 200 and isinstance(body, dict) else -1


def start(module: str, port: int) -> "subprocess.Popen[bytes]":
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{module}:app", "--host", HOST, "--port", str(port)],
        cwd=HERE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_until_up(process: "subprocess.Popen[bytes]", url: str, seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if fetch(url, timeout=2.0)[0] == 200:
            return True
        time.sleep(0.3)
    return False


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
    sys.exit(1)

for one in (PORT, UPSTREAM_PORT):
    if not port_is_free(one):
        print(f"Η θύρα {one} είναι πιασμένη. Σταμάτα τα services σου και ξανατρέξε.")
        sys.exit(1)

provider = start("upstream", UPSTREAM_PORT)
service = start("main", PORT)

try:
    up = wait_until_up(provider, f"{UPSTREAM}/calls/slow") and wait_until_up(
        service, f"{BASE}/health"
    )
    report("Ο πάροχος και το service ξεκινάνε", up)
    fetch(f"{UPSTREAM}/reset", "POST", timeout=10.0)

    status, _, slow_seconds = fetch(f"{BASE}/quote", timeout=15.0)
    report(
        f"Το /quote δεν κρέμεται στον αργό πάροχο ({slow_seconds:.1f}s)",
        status != 0 and slow_seconds < 10.0,
    )
    report(f"Και απαντάει 504 στον πελάτη ({status})", status == 504)

    status, rate, flaky_seconds = fetch(f"{BASE}/rates", timeout=30.0)
    report(
        "Το /rates πετυχαίνει παρά τις δύο αποτυχίες του παρόχου",
        status == 200 and isinstance(rate, dict) and rate.get("rate_cents") == 10850,
    )
    report(
        f"Οι επαναλήψεις περιμένουν ανάμεσά τους ({flaky_seconds:.2f}s)",
        status == 200 and flaky_seconds >= 0.8,
    )
    report(f"Και δεν ξαναρώτησαν παραπάνω από τρεις φορές ({calls_to('flaky')})", calls_to("flaky") == 3)

    status, _, broken_seconds = fetch(f"{BASE}/rates/backup", timeout=30.0)
    tried = calls_to("broken")
    report(
        f"Στον μόνιμα χαλασμένο πάροχο το service παραιτείται και απαντάει ({status})",
        status == 502,
    )
    report(f"Και δεν του έριξε πάνω από τέσσερις κλήσεις ({tried})", 0 < tried <= 4)
finally:
    for one in (service, provider):
        one.terminate()
        try:
            one.wait(timeout=5)
        except subprocess.TimeoutExpired:
            one.kill()

source = (HERE / "main.py").read_text(encoding="utf-8")
naked = [
    line.strip()
    for line in source.splitlines()
    if re.search(r"requests\.(get|post|put|delete|request)\(", line) and "timeout" not in line
]
report(
    f"Καμία κλήση προς τα έξω χωρίς timeout ({len(naked)})",
    not naked and "requests" in source,
)
report("Δεν έμεινε ατέρμονο while True στον κώδικα", "while True" not in source)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(70) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
