import subprocess
import sys

ACCEPTED = ["ΕΠΣ-101: δεκτή", "ΕΠΣ-102: δεκτή"]
REJECTED = [
    "ΕΠΣ-103: απορρίπτεται - ανοιγμένη συσκευασία",
    "ΕΠΣ-104: απορρίπτεται - πέρασαν 21 ημέρες",
    "ΕΠΣ-105: απορρίπτεται - η κατηγορία δεν επιστρέφεται",
    "ΕΠΣ-106: απορρίπτεται - χωρίς απόδειξη",
]
MAX_INDENT = 8

proc = subprocess.run([sys.executable, "returns.py"], capture_output=True, text=True)
stderr = proc.stderr.strip().splitlines()
failure = "" if proc.returncode == 0 else (stderr[-1] if stderr else f"exit {proc.returncode}")
lines = proc.stdout.strip().splitlines()

source_lines = open("returns.py", encoding="utf-8").read().splitlines()
deep = [line for line in source_lines if line.strip() and len(line) - len(line.lstrip(" ")) > MAX_INDENT]
elses = [line.strip() for line in source_lines if line.strip().startswith("else")]

results: list[tuple[bool, str, str]] = []

got = [line for line in lines if "δεκτή" in line]
results.append((
    not failure and got == ACCEPTED,
    "Δεκτά βγαίνουν ακριβώς τα ΕΠΣ-101 και ΕΠΣ-102",
    failure or f"πήρα {got}",
))

got = [line for line in lines if "απορρίπτεται" in line]
results.append((
    not failure and got == REJECTED,
    "Οι τέσσερις απορρίψεις βγαίνουν με τον σωστό λόγο",
    failure or f"πήρα {got}",
))

results.append((
    not deep,
    f"Καμία γραμμή του returns.py δεν ξεκινάει με περισσότερα από {MAX_INDENT} κενά",
    f"{len(deep)} γραμμές πιο μέσα, π.χ. {deep[0].strip()!r}" if deep else "",
))

results.append((
    not elses,
    "Δεν έμεινε κανένα else στο returns.py",
    f"βρήκα {len(elses)}",
))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
