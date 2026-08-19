"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Σηκώνει τον πάροχο και το service σου και τα βάζει στη δύσκολη θέση: πάροχος
που πέφτει, πάροχος που αργεί, και περιβάλλον που λείπει. Σταμάτα τα δικά σου
πριν το τρέξεις.
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
LOGFILE = HERE / "checks-output.log"
HOST = "127.0.0.1"
PORT = 8000
PROVIDER_PORT = 8001
BASE = f"http://{HOST}:{PORT}"
PROVIDER = f"http://{HOST}:{PROVIDER_PORT}"
MY_ID = "aitima-tou-vathmologiti-7"

GOOD = {
    "PROVIDER_URL": PROVIDER,
    "PROVIDER_API_KEY": "kleidi-apo-to-perivallon",
    "PROVIDER_TIMEOUT_SECONDS": "2",
}

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


def fetch(
    url: str, method: str = "GET", timeout: float = 30.0, request_id: str | None = None
) -> tuple[int, Any, float, dict[str, str]]:
    started = time.time()
    headers = {"X-Request-ID": request_id} if request_id else {}
    request = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as answer:
            raw = answer.read().decode("utf-8")
            body = json.loads(raw) if raw else None
            return answer.status, body, time.time() - started, dict(answer.headers)
    except urllib.error.HTTPError as failure:
        return failure.code, None, time.time() - started, dict(failure.headers)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None, time.time() - started, {}


def provider_state(up: bool = True, delay_seconds: float = 0.0) -> None:
    fetch(
        f"{PROVIDER}/state?up={'true' if up else 'false'}&delay_seconds={delay_seconds}",
        "POST",
        timeout=10.0,
    )


def environment(**changes: str | None) -> dict[str, str]:
    import os

    clean = {key: value for key, value in os.environ.items() if key not in GOOD}
    clean.update(GOOD)
    for key, value in changes.items():
        if value is None:
            clean.pop(key, None)
        else:
            clean[key] = value
    return clean


def refuses(**changes: str | None) -> bool:
    finished = subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=HERE,
        env=environment(**changes),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return finished.returncode != 0


def start(module: str, port: int, sink: Any = subprocess.DEVNULL) -> "subprocess.Popen[bytes]":
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{module}:app", "--host", HOST, "--port", str(port)],
        cwd=HERE,
        env=environment(),
        stdout=sink,
        stderr=subprocess.STDOUT,
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


def json_lines(raw: str) -> list[dict[str, Any]]:
    found = []
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


if not (HERE / "main.py").exists():
    print("Δεν βρήκα το main.py στη ρίζα του repo.")
    sys.exit(1)

for one in (PORT, PROVIDER_PORT):
    if not port_is_free(one):
        print(f"Η θύρα {one} είναι πιασμένη. Σταμάτα τα services σου και ξανατρέξε.")
        sys.exit(1)

LOGFILE.unlink(missing_ok=True)
sink = LOGFILE.open("wb")

carrier = start("provider", PROVIDER_PORT)
service = start("main", PORT, sink)

try:
    up = wait_until_up(carrier, f"{PROVIDER}/ping") and wait_until_up(service, f"{BASE}/health")
    report("Ο πάροχος και το service ξεκινάνε", up)
    provider_state(up=True)

    status, body, health_seconds, _ = fetch(f"{BASE}/health", timeout=10.0)
    report("Το /health απαντάει", status == 200)

    status, _, _, _ = fetch(f"{BASE}/ready", timeout=10.0)
    report("Με τον πάροχο όρθιο, το /ready λέει ναι", status == 200)

    status, tracking, _, headers = fetch(
        f"{BASE}/orders/1001/shipping", timeout=10.0, request_id=MY_ID
    )
    report(
        "Η αποστολή επιστρέφεται σωστά",
        status == 200 and isinstance(tracking, dict) and tracking.get("tracking") == "EL001001GR",
    )
    echoed = headers.get("X-Request-ID") or headers.get("x-request-id")
    report("Η απάντηση φέρνει πίσω το X-Request-ID", echoed == MY_ID)

    provider_state(up=False)
    status, _, _, _ = fetch(f"{BASE}/ready", timeout=10.0)
    report(f"Με τον πάροχο πεσμένο, το /ready λέει όχι ({status})", status == 503)

    status, _, still_seconds, _ = fetch(f"{BASE}/health", timeout=10.0)
    report(
        "Το /health μένει πράσινο κι όταν ο πάροχος είναι πεσμένος",
        status == 200 and still_seconds < 0.1,
    )

    provider_state(up=True, delay_seconds=30.0)

    status, _, hung_seconds, _ = fetch(f"{BASE}/health", timeout=15.0)
    report(
        f"Το /health απαντάει κι όταν ο πάροχος έχει κολλήσει ({hung_seconds:.1f}s)",
        status == 200 and hung_seconds < 1.0,
    )

    status, _, slow_seconds, _ = fetch(f"{BASE}/orders/1002/shipping", timeout=15.0)
    report(
        f"Ο αργός πάροχος δεν κρεμάει το request ({slow_seconds:.1f}s)",
        status != 0 and slow_seconds < 10.0,
    )
    report(f"Και ο πελάτης παίρνει 504 ({status})", status == 504)
    provider_state(up=True, delay_seconds=0.0)

    time.sleep(0.8)
finally:
    for one in (service, carrier):
        one.terminate()
        try:
            one.wait(timeout=5)
        except subprocess.TimeoutExpired:
            one.kill()
    sink.close()

raw = LOGFILE.read_text(encoding="utf-8", errors="replace")
lines = json_lines(raw)
report(f"Το service γράφει γραμμές JSON ({len(lines)})", len(lines) >= 2)
report(
    "Και οι γραμμές κουβαλάνε το request id",
    any(one.get("request_id") == MY_ID for one in lines),
)
LOGFILE.unlink(missing_ok=True)

report("Χωρίς PROVIDER_API_KEY το service αρνείται να ξεκινήσει", refuses(PROVIDER_API_KEY=None))
report(
    "Με PROVIDER_TIMEOUT_SECONDS που δεν είναι αριθμός αρνείται",
    refuses(PROVIDER_TIMEOUT_SECONDS="ochi-arithmos"),
)

sources = {path.name: path.read_text(encoding="utf-8") for path in HERE.glob("*.py")}
mine = {name: text for name, text in sources.items() if name not in ("checks.py", "provider.py")}
CALL = re.compile(r"requests\.(?:get|post|put|delete|request)\((?:[^()]|\([^()]*\))*\)")
naked = [
    call
    for text in mine.values()
    for call in CALL.findall(text)
    if "timeout" not in call
]
report(f"Καμία κλήση προς τον πάροχο χωρίς timeout ({len(naked)})", not naked)
report("Δεν έμεινε print στον κώδικά σου", all("print(" not in text for text in mine.values()))
report(
    "Κανένα κλειδί δεν είναι γραμμένο μέσα στον κώδικα",
    all("kleidi-tou-parochou" not in text for text in mine.values()),
)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(72) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
