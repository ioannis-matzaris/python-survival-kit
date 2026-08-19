"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Δοκιμάζει το service με σωστό περιβάλλον, και μετά με πέντε λάθος. Το σωστό
πρέπει να ξεκινάει, τα λάθος πρέπει να αρνούνται. Σταμάτα τον δικό σου uvicorn
πριν το τρέξεις.
"""

import json
import os
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

GOOD = {
    "DEBUG": "false",
    "PORT": "8000",
    "DATABASE_URL": "sqlite:///shop.db",
    "TIMEOUT_SECONDS": "5",
    "PROVIDER_API_KEY": "kleidi-apo-to-perivallon",
}

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


def call(path: str) -> tuple[int, Any]:
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as answer:
            raw = answer.read().decode("utf-8")
            return answer.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as failure:
        return failure.code, None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return 0, None


def environment(**changes: str | None) -> dict[str, str]:
    clean = {key: value for key, value in os.environ.items() if key not in GOOD}
    clean.update(GOOD)
    for key, value in changes.items():
        if value is None:
            clean.pop(key, None)
        else:
            clean[key] = value
    return clean


def refuses(**changes: str | None) -> tuple[bool, str]:
    """Το service πρέπει να πεθάνει με μη μηδενικό κωδικό, όχι να ξεκινήσει."""
    finished = subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=HERE,
        env=environment(**changes),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return finished.returncode != 0, finished.stdout + finished.stderr


def wait_until_up(process: "subprocess.Popen[bytes]", seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if call("/health")[0] == 200:
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
    env=environment(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    report("Με σωστό περιβάλλον το service ξεκινάει", wait_until_up(service))

    status, settings = call("/config")
    settings = settings if isinstance(settings, dict) else {}

    report("Το /config απαντάει", status == 200 and bool(settings))
    report(
        "Το DEBUG=false διαβάζεται ως ψευδές, όχι ως αληθές",
        settings.get("debug") is False,
    )
    report(
        f"Το PORT είναι ακέραιος, όχι κείμενο ({settings.get('port')!r})",
        isinstance(settings.get("port"), int),
    )
    report(
        f"Το TIMEOUT_SECONDS είναι αριθμός ({settings.get('timeout_seconds')!r})",
        isinstance(settings.get("timeout_seconds"), (int, float))
        and not isinstance(settings.get("timeout_seconds"), bool),
    )
finally:
    service.terminate()
    try:
        service.wait(timeout=5)
    except subprocess.TimeoutExpired:
        service.kill()

missing_ok, missing_output = refuses(DATABASE_URL=None)
report("Χωρίς DATABASE_URL το service αρνείται να ξεκινήσει", missing_ok)
report(
    "Και το μήνυμα ονομάζει τη μεταβλητή που λείπει",
    missing_ok and "DATABASE_URL" in missing_output.upper(),
)

report("Με PORT που δεν είναι αριθμός αρνείται", refuses(PORT="ochi-arithmos")[0])
report("Με TIMEOUT_SECONDS εκτός ορίων αρνείται", refuses(TIMEOUT_SECONDS="0")[0])
report("Χωρίς PROVIDER_API_KEY αρνείται", refuses(PROVIDER_API_KEY=None)[0])

sources = {path.name: path.read_text(encoding="utf-8") for path in HERE.glob("*.py")}
outside_settings = [
    name
    for name, text in sources.items()
    if name not in ("settings.py", "checks.py") and ("os.environ" in text or "os.getenv" in text)
]
report(
    f"Το περιβάλλον διαβάζεται από ένα σημείο ({', '.join(outside_settings) or 'κανένα άλλο'})",
    not outside_settings,
)
report(
    "Κανένα κλειδί δεν είναι γραμμένο μέσα στον κώδικα",
    all("kleidi-tou-parochou" not in text for name, text in sources.items() if name != "checks.py"),
)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(68) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
