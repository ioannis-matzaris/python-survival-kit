"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Ξεκινάει ο ίδιος το server.py σου σε δικό του process, του μιλάει με σκέτο
socket όπως θα του μιλούσε ένας οποιοσδήποτε client, και κοιτάει τι γύρισε
πίσω στο καλώδιο. Σταμάτα τον δικό σου server πριν το τρέξεις, αλλιώς η
θύρα 8000 είναι πιασμένη.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE / "server.py"
HOST = "127.0.0.1"
PORT = 8000
BODY = "εντάξει"

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


def ask(request: str, timeout: float = 3.0) -> str:
    """Στέλνει ένα request με σκέτο socket. Κενό string σημαίνει καμία απάντηση."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect((HOST, PORT))
        client.sendall(request.encode("utf-8"))
        chunks: list[bytes] = []
        while True:
            piece = client.recv(4096)
            if not piece:
                break
            chunks.append(piece)
        return b"".join(chunks).decode("utf-8", errors="replace")
    except OSError:
        return ""
    finally:
        client.close()


def get(path: str) -> str:
    return ask(f"GET {path} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n")


def header(raw: str, name: str) -> str:
    for line in raw.replace("\r\n", "\n").split("\n"):
        if line.lower().startswith(f"{name.lower()}:"):
            return line.split(":", 1)[1].strip()
    return ""


def body_of(raw: str) -> str:
    normalised = raw.replace("\r\n", "\n")
    if "\n\n" not in normalised:
        return ""
    return normalised.split("\n\n", 1)[1]


def first_response(process: subprocess.Popen[bytes], seconds: float = 5.0) -> str:
    """Το πρώτο GET /health που παίρνει απάντηση.

    Δοκιμάζει ξανά όσο η σύνδεση δεν περνάει, γιατί ο server θέλει λίγο για να
    σηκωθεί. Δεν ανοίγει σύνδεση που δεν στέλνει request: ένας server που
    απαντάει μία φορά και σταματάει πρέπει να τη δώσει αυτή τη μία εδώ.
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            return ""
        answer = get("/health")
        if answer:
            return answer
        time.sleep(0.1)
    return ""


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


if not SERVER.exists():
    print("Δεν βρήκα το server.py στη ρίζα του repo.")
    sys.exit(1)

if not port_is_free():
    print(f"Η θύρα {PORT} είναι πιασμένη. Σταμάτα τον server σου και ξανατρέξε.")
    sys.exit(1)

server_process = subprocess.Popen(
    [sys.executable, str(SERVER)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    first = first_response(server_process)
    report("Το server.py ξεκινάει και απαντάει στο 8000", bool(first))

    report(
        "Το GET /health απαντάει 200 με σώμα «εντάξει»",
        first.startswith("HTTP/1.1 200") and body_of(first) == BODY,
    )
    report(
        "Το Content-Length μετράει bytes, όχι χαρακτήρες",
        header(first, "Content-Length") == str(len(BODY.encode("utf-8"))),
    )
    report(
        "Το Content-Type δηλώνει charset=utf-8",
        "charset=utf-8" in header(first, "Content-Type").lower(),
    )
    report(
        "Οι γραμμές της απάντησης χωρίζονται με \\r\\n",
        bool(first) and "\r\n" in first and "\n" not in first.replace("\r\n", ""),
    )

    unknown = get("/den-yparxei")
    report("Μια άγνωστη διαδρομή παίρνει 404", unknown.startswith("HTTP/1.1 404"))

    second = get("/health")
    third = get("/health")
    report(
        "Ο server απαντάει και στο δεύτερο και στο τρίτο request",
        second.startswith("HTTP/1.1 200") and third.startswith("HTTP/1.1 200"),
    )

    ask("ΣΚΟΥΠΙΔΙΑ\r\n\r\n")
    after = get("/health")
    report(
        "Ένα χαλασμένο request δεν ρίχνει τον server",
        server_process.poll() is None and after.startswith("HTTP/1.1 200"),
    )
finally:
    server_process.terminate()
    try:
        server_process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        server_process.kill()

total = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total}] {label}".ljust(62) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total}")
