"""Οι έλεγχοι του lab. Τρέξε: python3 checks.py"""

import ast
import contextlib
import importlib
import io
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

EXPECTED_REPORT = """ΠΑΡΑΓΓΕΛΙΕΣ ΑΝΑ ΠΕΛΑΤΗ

Γιώργος Αντωνίου       223.94
Μαρία Δημητρίου        115.94
Ελένη Παπαδάκη         100.33
Νίκος Σαββίδης          40.58

ΣΥΝΟΛΟ                 480.79"""

EXPECTED_TOTALS = {
    "Γιώργος Αντωνίου": 223.94,
    "Μαρία Δημητρίου": 115.94,
    "Ελένη Παπαδάκη": 100.33,
    "Νίκος Σαββίδης": 40.58,
}

SAMPLE_CSV = """order_id,customer,category,product,quantity,unit_price
2001,Δοκιμαστικός Πελάτης,regular,Δοκιμή,2,10.00
"""

results: list[tuple[bool, str, str]] = []


def check(ok: bool, title: str, detail: str = "") -> None:
    results.append((ok, title, detail))


def load(name: str) -> tuple[ModuleType | None, str, str]:
    if not (HERE / f"{name}.py").exists():
        return None, f"δεν βρήκα το {name}.py", ""
    sys.modules.pop(name, None)
    try:
        with contextlib.redirect_stdout(io.StringIO()) as sink:
            module = importlib.import_module(name)
    except Exception as error:
        return None, f"το {name}.py δεν κάνει import: {type(error).__name__}: {error}", ""
    return module, "", sink.getvalue()


def grab(module: ModuleType | None, name: str):
    return getattr(module, name, None) if module else None


finished = subprocess.run(
    [sys.executable, "main.py"], cwd=HERE, capture_output=True, text=True
)
if finished.returncode != 0:
    check(False, "Η έξοδος του main.py είναι ακριβώς η ίδια",
          (finished.stderr.strip().splitlines() or ["-"])[-1])
else:
    produced = finished.stdout.rstrip("\n")
    if produced == EXPECTED_REPORT:
        check(True, "Η έξοδος του main.py είναι ακριβώς η ίδια")
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
        check(False, "Η έξοδος του main.py είναι ακριβώς η ίδια",
              f'γραμμή {spot + 1}: "{got}", περίμενα "{want}"')

orders_mod, orders_err, orders_noise = load("orders")
pricing_mod, pricing_err, pricing_noise = load("pricing")
report_mod, report_err, report_noise = load("report")

missing = [e for e in (orders_err, pricing_err, report_err) if e]
noisy = [n for n in (orders_noise, pricing_noise, report_noise) if n.strip()]
check(
    not missing and not noisy,
    "Υπάρχουν τα orders.py, pricing.py, report.py και κάνουν import",
    missing[0] if missing else ("ένα από αυτά τυπώνει κατά το import" if noisy else ""),
)

read_orders = grab(orders_mod, "read_orders")
if read_orders is None:
    check(False, "Η read_orders διαβάζει το path που της δίνεις", "δεν βρήκα συνάρτηση read_orders")
else:
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".csv", encoding="utf-8", delete=False) as handle:
            handle.write(SAMPLE_CSV)
            temp_path = handle.name
        rows = read_orders(temp_path)
        ok = isinstance(rows, list) and len(rows) == 1 and rows[0].get("customer") == "Δοκιμαστικός Πελάτης"
        check(ok, "Η read_orders διαβάζει το path που της δίνεις",
              "" if ok else f"με δικό μου αρχείο επέστρεψε {rows!r}"[:150])
    except Exception as error:
        check(False, "Η read_orders διαβάζει το path που της δίνεις", f"{type(error).__name__}: {error}")

discount_for = grab(pricing_mod, "discount_for")
if discount_for is None:
    check(False, "Η discount_for δίνει 0.0 / 0.10 / 0.15", "δεν βρήκα συνάρτηση discount_for")
else:
    wrong = ""
    for category, want in (("regular", 0.0), ("student", 0.10), ("senior", 0.15), ("άγνωστη", 0.0)):
        try:
            got = discount_for(category)
        except Exception as error:
            wrong = f"για {category!r}: {type(error).__name__}: {error}"
            break
        if round(float(got), 4) != want:
            wrong = f"για {category!r} περίμενα {want}, βρήκα {got!r}"
            break
    check(not wrong, "Η discount_for δίνει 0.0 / 0.10 / 0.15", wrong)

shipping_for = grab(pricing_mod, "shipping_for")
if shipping_for is None:
    check(False, "Η shipping_for δίνει 3.50 κάτω από 50 και 0.0 από 50 και πάνω", "δεν βρήκα συνάρτηση shipping_for")
else:
    wrong = ""
    for subtotal, want in ((49.99, 3.50), (50.0, 0.0), (120.0, 0.0), (0.0, 3.50)):
        try:
            got = shipping_for(subtotal)
        except Exception as error:
            wrong = f"για {subtotal}: {type(error).__name__}: {error}"
            break
        if round(float(got), 2) != want:
            wrong = f"για {subtotal} περίμενα {want}, βρήκα {got!r}"
            break
    check(not wrong, "Η shipping_for δίνει 3.50 κάτω από 50 και 0.0 από 50 και πάνω", wrong)

total_with_vat = grab(pricing_mod, "total_with_vat")
if total_with_vat is None:
    check(False, "Η total_with_vat(100.0, 3.5) δίνει 127.5", "δεν βρήκα συνάρτηση total_with_vat")
else:
    try:
        got = total_with_vat(100.0, 3.5)
        check(round(float(got), 2) == 127.5, "Η total_with_vat(100.0, 3.5) δίνει 127.5",
              f"βρήκα {got!r}")
    except Exception as error:
        check(False, "Η total_with_vat(100.0, 3.5) δίνει 127.5", f"{type(error).__name__}: {error}")

totals_by_customer = grab(report_mod, "totals_by_customer")
if totals_by_customer is None or read_orders is None:
    check(False, "Η totals_by_customer βγάζει τα σωστά σύνολα ανά πελάτη",
          "δεν βρήκα συνάρτηση totals_by_customer" if totals_by_customer is None else "χρειάζεται και τη read_orders")
else:
    try:
        totals = totals_by_customer(read_orders(str(HERE / "orders.csv")))
        if not isinstance(totals, dict):
            check(False, "Η totals_by_customer βγάζει τα σωστά σύνολα ανά πελάτη",
                  f"επέστρεψε {type(totals).__name__} αντί για dictionary")
        else:
            bad = next(
                (name for name, want in EXPECTED_TOTALS.items()
                 if round(float(totals.get(name, -1)), 2) != want),
                "",
            )
            extra = set(totals) - set(EXPECTED_TOTALS)
            if bad:
                check(False, "Η totals_by_customer βγάζει τα σωστά σύνολα ανά πελάτη",
                      f"για {bad} περίμενα {EXPECTED_TOTALS[bad]}, βρήκα {totals.get(bad)!r}")
            elif extra:
                check(False, "Η totals_by_customer βγάζει τα σωστά σύνολα ανά πελάτη",
                      f"περισσεύουν πελάτες: {sorted(extra)}")
            else:
                check(True, "Η totals_by_customer βγάζει τα σωστά σύνολα ανά πελάτη")
    except Exception as error:
        check(False, "Η totals_by_customer βγάζει τα σωστά σύνολα ανά πελάτη", f"{type(error).__name__}: {error}")

format_report = grab(report_mod, "format_report")
if format_report is None:
    check(False, "Η format_report επιστρέφει κείμενο και δεν τυπώνει τίποτα", "δεν βρήκα συνάρτηση format_report")
else:
    try:
        with contextlib.redirect_stdout(io.StringIO()) as sink:
            text = format_report(dict(EXPECTED_TOTALS))
        if sink.getvalue():
            check(False, "Η format_report επιστρέφει κείμενο και δεν τυπώνει τίποτα",
                  "τύπωσε στην οθόνη αντί να επιστρέψει")
        elif not isinstance(text, str):
            check(False, "Η format_report επιστρέφει κείμενο και δεν τυπώνει τίποτα",
                  f"επέστρεψε {type(text).__name__} αντί για string")
        else:
            check(text.rstrip("\n") == EXPECTED_REPORT,
                  "Η format_report επιστρέφει κείμενο και δεν τυπώνει τίποτα",
                  "το κείμενο που επιστρέφει δεν είναι η αναφορά")
    except Exception as error:
        check(False, "Η format_report επιστρέφει κείμενο και δεν τυπώνει τίποτα", f"{type(error).__name__}: {error}")

source = (HERE / "main.py").read_text(encoding="utf-8")
code_lines = [
    line for line in source.splitlines()
    if line.strip() and not line.strip().startswith("#")
]
check(len(code_lines) <= 15, "Το main.py έχει το πολύ 15 γραμμές κώδικα",
      f"βρήκα {len(code_lines)}")

guarded = subprocess.run(
    [sys.executable, "-c", "import main"], cwd=HERE, capture_output=True, text=True
)
check(
    guarded.returncode == 0 and not guarded.stdout.strip(),
    "Το import main δεν τρέχει το πρόγραμμα",
    "τύπωσε την αναφορά κατά το import" if guarded.stdout.strip()
    else (guarded.stderr.strip().splitlines() or ["-"])[-1] if guarded.returncode else "",
)

passed = 0
for number, (ok, title, detail) in enumerate(results, start=1):
    if ok:
        passed += 1
        print(f"✅ {number:>2}. {title}")
    else:
        print(f"❌ {number:>2}. {title}")
        if detail:
            print(f"      {detail}")

print()
print(f"{passed}/{len(results)}")
