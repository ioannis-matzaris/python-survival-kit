"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Δεν βαθμολογεί την υλοποίησή σου, βαθμολογεί το suite σου. Αντιγράφει το
test_shipping.py δίπλα σε κάθε υλοποίηση και κοιτάει αν περνάει ή κοκκινίζει.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITE = HERE / "test_shipping.py"
MIN_TESTS = 8

MUTANTS = [
    ("m1", "κουπόνι κάτω από το μηδέν", "m1_coupon_below_zero.py"),
    ("m2", "κλάσμα κιλού στα μεταφορικά", "m2_truncated_weight.py"),
    ("m3", "όριο των 40 ευρώ", "m3_free_shipping_boundary.py"),
    ("m4", "άγνωστο κουπόνι", "m4_silent_unknown_coupon.py"),
    ("m5", "quantity στο subtotal", "m5_ignores_quantity.py"),
]

results: list[tuple[bool, str]] = []


def run_suite_against(implementation: Path) -> tuple[int, str]:
    """Τρέχει το suite του μαθητή δίπλα σε μια υλοποίηση, σε δικό της φάκελο."""
    with tempfile.TemporaryDirectory() as room:
        sandbox = Path(room)
        shutil.copy(implementation, sandbox / "shipping.py")
        shutil.copy(SUITE, sandbox / "test_shipping.py")
        finished = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "test_shipping.py"],
            cwd=sandbox,
            capture_output=True,
            text=True,
        )
        return finished.returncode, finished.stdout


def collected_tests() -> int:
    finished = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", str(SUITE)],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    return sum(1 for line in finished.stdout.splitlines() if "::" in line)


if not SUITE.exists():
    print("[1/8] Το test_shipping.py υπάρχει και δίνει 8+ tests       ❌")
    print("[2/8] Το suite περνάει στο δικό σου shipping.py            ❌")
    print("[3/8] Το suite περνάει στη σωστή υλοποίηση                 ❌")
    for index, (tag, label, _) in enumerate(MUTANTS, start=4):
        print(f"[{index}/8] Το suite πιάνει το {tag} ({label})".ljust(58) + " ❌")
    print()
    print("Σκορ: 0/8")
    print()
    print("Δεν βρήκα test_shipping.py στη ρίζα. Ξεκίνα από την Αποστολή 1.")
    raise SystemExit(1)

found = collected_tests()
results.append((found >= MIN_TESTS, f"Το test_shipping.py υπάρχει και δίνει 8+ tests ({found})"))

own_code, own_output = run_suite_against(HERE / "shipping.py")
results.append((own_code == 0, "Το suite περνάει στο δικό σου shipping.py"))

ref_code, ref_output = run_suite_against(HERE / "reference" / "shipping.py")
results.append((ref_code == 0, "Το suite περνάει στη σωστή υλοποίηση"))

for tag, label, filename in MUTANTS:
    code, _ = run_suite_against(HERE / "mutants" / filename)
    results.append((code != 0, f"Το suite πιάνει το {tag} ({label})"))

passed = 0
for number, (ok, title) in enumerate(results, start=1):
    mark = "✅" if ok else "❌"
    if ok:
        passed += 1
    print(f"[{number}/{len(results)}] {title}".ljust(58) + f" {mark}")

print()
print(f"Σκορ: {passed}/{len(results)}")

if not results[2][0]:
    print()
    print("Το suite σου κοκκινίζει στη σωστή υλοποίηση. Κάποιο test περιμένει")
    print("κάτι που η προδιαγραφή δεν λέει. Ξαναδιάβασε τους κανόνες.")
