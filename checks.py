"""Οι έλεγχοι του lab. Τρέξε: python3 checks.py

Δεν κατεβάζει τίποτα. Κοιτάζει τα αρχεία σου και το περιβάλλον που έφτιαξες.
"""

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"
VENV_PYTHON = VENV / "bin" / "python"
PACKAGE = "tabulate"
VERSION = "0.9.0"

EXPECTED_REPORT = """Προϊόν           Κατάστημα      Τιμή
---------------  -----------  ------
Καλώδιο HDMI     Public         6.90
Ποντίκι          Kotsovolos    12.50
Ακουστικά        Kotsovolos    29.90
Πληκτρολόγιο     Public        45.00
Οθόνη 24 ιντσών  Plaisio      159.90
ΣΥΝΟΛΟ: 254.20 ευρώ"""

results: list[tuple[bool, str, str]] = []


def check(ok: bool, title: str, detail: str = "") -> None:
    results.append((ok, title, detail))


venv_ok = (VENV / "pyvenv.cfg").exists() and VENV_PYTHON.exists()
check(
    venv_ok,
    "Υπάρχει virtualenv στον φάκελο .venv",
    "" if venv_ok else "δεν βρήκα .venv/pyvenv.cfg και .venv/bin/python, τρέξε python3 -m venv .venv",
)

installed = ""
if venv_ok:
    frozen = subprocess.run(
        [str(VENV_PYTHON), "-m", "pip", "freeze"], capture_output=True, text=True
    )
    for line in frozen.stdout.splitlines():
        if line.lower().startswith(f"{PACKAGE}=="):
            installed = line.split("==", 1)[1].strip()
            break
check(
    installed == VERSION,
    f"Το {PACKAGE} {VERSION} είναι εγκατεστημένο μέσα σε αυτό",
    "δεν είναι εγκατεστημένο μέσα στο .venv" if not installed else f"βρήκα την έκδοση {installed}",
)

requirements = HERE / "requirements.txt"
lines = []
if requirements.exists():
    lines = [line.strip() for line in requirements.read_text(encoding="utf-8").splitlines() if line.strip()]
loose = [line for line in lines if not re.match(r"^[A-Za-z0-9._-]+==", line)]
check(
    bool(lines) and not loose,
    "Το requirements.txt καρφώνει κάθε γραμμή με ==",
    "δεν βρήκα requirements.txt με περιεχόμενο" if not lines
    else (f'η γραμμή "{loose[0]}" δεν καρφώνει έκδοση' if loose else ""),
)

pinned = next((line for line in lines if line.lower().startswith(f"{PACKAGE}==")), "")
check(
    pinned == f"{PACKAGE}=={VERSION}" and installed == VERSION,
    "Το requirements.txt συμφωνεί με ό,τι είναι εγκατεστημένο",
    f'το αρχείο λέει "{pinned or "τίποτα"}" και εγκατεστημένο είναι "{installed or "τίποτα"}"',
)

report = HERE / "report.py"
if not report.exists():
    check(False, "Το report.py τυπώνει ακριβώς την αναμενόμενη αναφορά", "δεν βρήκα report.py")
elif not venv_ok:
    check(False, "Το report.py τυπώνει ακριβώς την αναμενόμενη αναφορά", "χρειάζεται πρώτα το .venv")
else:
    run = subprocess.run(
        [str(VENV_PYTHON), "report.py"], cwd=HERE, capture_output=True, text=True
    )
    if run.returncode != 0:
        check(False, "Το report.py τυπώνει ακριβώς την αναμενόμενη αναφορά",
              (run.stderr.strip().splitlines() or ["-"])[-1])
    else:
        produced = run.stdout.rstrip("\n")
        if produced == EXPECTED_REPORT:
            check(True, "Το report.py τυπώνει ακριβώς την αναμενόμενη αναφορά")
        else:
            mine = produced.splitlines()
            theirs = EXPECTED_REPORT.splitlines()
            spot = next(
                (i for i in range(max(len(mine), len(theirs)))
                 if (mine[i] if i < len(mine) else None) != (theirs[i] if i < len(theirs) else None)),
                0,
            )
            got = mine[spot] if spot < len(mine) else "<λείπει>"
            want = theirs[spot] if spot < len(theirs) else "<περισσεύει>"
            check(False, "Το report.py τυπώνει ακριβώς την αναμενόμενη αναφορά",
                  f'γραμμή {spot + 1}: "{got}", περίμενα "{want}"')

ignore = HERE / ".gitignore"
ignored = False
if ignore.exists():
    entries = [line.strip().rstrip("/") for line in ignore.read_text(encoding="utf-8").splitlines()]
    ignored = ".venv" in entries
tracked = subprocess.run(
    ["git", "ls-files", "--error-unmatch", ".venv"], cwd=HERE, capture_output=True, text=True
).returncode == 0
check(
    ignored and not tracked,
    "Το .gitignore κρατάει το .venv έξω από το git",
    "το .venv είναι ήδη στο git" if tracked else "δεν βρήκα γραμμή .venv/ στο .gitignore",
)

passed = 0
for number, (ok, title, detail) in enumerate(results, start=1):
    if ok:
        passed += 1
        print(f"✅ {number}. {title}")
    else:
        print(f"❌ {number}. {title}")
        if detail:
            print(f"     {detail}")

print()
print(f"{passed}/{len(results)}")
