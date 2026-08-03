import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

VARIANTS = [
    "ΚΩΔ-4471;Καφετιέρα; 5,35 € ;5 τεμ;10%",
    "ΚΩΔ-4471;Καφετιέρα;5.35;5;10",
    "ΚΩΔ-4471;Καφετιέρα;  5,35€ ;  5 τεμ  ; 10 %",
]


def run(script: str, stdin_text: str) -> tuple[int, list[str]]:
    path = HERE / script
    if not path.exists():
        return 1, [f"δεν βρέθηκε αρχείο {script}"]
    finished = subprocess.run(
        [sys.executable, str(path)],
        input=stdin_text + "\n",
        capture_output=True,
        text=True,
    )
    return finished.returncode, finished.stdout.splitlines()


def line(output: list[str], index: int) -> str:
    return output[index] if index < len(output) else "<λείπει>"


results: list[tuple[bool, str, str]] = []


def check(ok: bool, title: str, detail: str = "") -> None:
    results.append((ok, title, detail))


runs = [run("receipt.py", variant) for variant in VARIANTS]

failed = [i for i, (code, _) in enumerate(runs) if code != 0]
check(
    not failed,
    "Το receipt.py τρέχει χωρίς σφάλμα και με τα τρία input",
    "" if not failed else f"σκάει στο input: {VARIANTS[failed[0]]}",
)

first = runs[0][1]
check(
    line(first, 2) == "Καθαρή αξία: 26.75",
    "Τυπώνει Καθαρή αξία: 26.75",
    f"βρήκα: {line(first, 2)}",
)
check(
    line(first, 3) == "Έκπτωση: 2.68" and line(first, 4) == "Πληρωτέο: 24.07",
    "Τυπώνει Έκπτωση: 2.68 και Πληρωτέο: 24.07",
    f"βρήκα: {line(first, 3)} / {line(first, 4)}",
)
check(
    line(first, 1) == "Έγκυρος κωδικός: True",
    "Τυπώνει Έγκυρος κωδικός: True",
    f"βρήκα: {line(first, 1)}",
)

source_ok = all(
    line(output, 5) == f"Πηγή: {variant}"
    for variant, (_, output) in zip(VARIANTS, runs)
)
check(
    source_ok,
    "Η γραμμή Πηγή επιστρέφει ακριβώς τη γραμμή που δόθηκε",
    f"βρήκα: {line(first, 5)}",
)

heads = {tuple(output[:5]) for _, output in runs}
check(
    len(heads) == 1,
    "Και τα τρία input δίνουν τις ίδιες πέντε πρώτες γραμμές",
    f"βρήκα {len(heads)} διαφορετικά αποτελέσματα",
)

vat_code, vat_out = run("vat.py", "74,40 €")
check(
    vat_code == 0 and vat_out[:2] == ["60.00", "14.40"],
    "Το vat.py τυπώνει 60.00 και 14.40",
    f"βρήκα: {vat_out[:2]}",
)

passed = 0
for ok, title, detail in results:
    if ok:
        passed += 1
        print(f"✅ {title}")
    else:
        print(f"❌ {title} - {detail}")

print()
print(f"{passed}/{len(results)}")
