import subprocess
import sys

TIMEOUT_SECONDS = 5

lines: list[str] = []
failure = ""

try:
    proc = subprocess.run(
        [sys.executable, "stock.py"],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )
except subprocess.TimeoutExpired:
    failure = f"το stock.py δεν τερμάτισε μέσα σε {TIMEOUT_SECONDS} δευτερόλεπτα"
else:
    if proc.returncode != 0:
        stderr = proc.stderr.strip().splitlines()
        failure = stderr[-1] if stderr else f"exit {proc.returncode}"
    lines = proc.stdout.strip().splitlines()

source = open("stock.py", encoding="utf-8").read()
while_count = sum(1 for line in source.splitlines() if line.strip().startswith("while "))

BELOW = {"ΚΩΔ-2245": "Καλώδιο USB-C", "ΚΩΔ-4418": "Ακουστικά", "ΚΩΔ-5502": "Φορτιστής αυτοκινήτου"}
ABOVE = {"ΚΩΔ-1180": "Θήκη κινητού", "ΚΩΔ-3390": "Powerbank"}
BOXES_LINE = "Κιβώτια για ΚΩΔ-5502: 3 (απόθεμα 38)"

listed = [line for line in lines if line.startswith("Κάτω από το όριο:")]

results: list[tuple[bool, str, str]] = []

results.append((not failure, f"Το stock.py τερματίζει μόνο του μέσα σε {TIMEOUT_SECONDS} δευτερόλεπτα", failure))

missing = [code for code in BELOW if not any(code in line for line in listed)]
results.append((
    not failure and not missing,
    "Και τα τρία προϊόντα κάτω από το όριο εμφανίζονται",
    failure or "λείπουν: " + ", ".join(missing),
))

extra = [code for code in ABOVE if any(code in line for line in listed)]
results.append((
    not failure and not extra,
    "Κανένα προϊόν πάνω από το όριο δεν μπαίνει στη λίστα",
    failure or "περισσεύουν: " + ", ".join(extra),
))

boxes = next((line for line in lines if line.startswith("Κιβώτια")), "")
results.append((
    not failure and boxes == BOXES_LINE,
    "Τα κιβώτια βγαίνουν 3 και το απόθεμα 38",
    failure or f"πήρα {boxes!r} αντί για {BOXES_LINE!r}",
))

results.append((
    while_count == 1,
    "Το stock.py έχει ένα μόνο while",
    f"βρήκα {while_count}",
))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
