import json
import subprocess
import sys

PROBE = r'''
import contextlib
import io
import json

answer = {}
buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(buffer):
        import shares
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

printed = io.StringIO()
try:
    with contextlib.redirect_stdout(printed):
        value = shares.share_of(1010.00, 180)
    answer["share_of"] = f"{value:.2f}"
    answer["share_of_printed"] = printed.getvalue()
except Exception as exc:
    answer["share_of_error"] = f"{type(exc).__name__}: {exc}"

printed = io.StringIO()
try:
    with contextlib.redirect_stdout(printed):
        shares.print_month("ΔΟΚΙΜΗ", 500.00)
    answer["print_month"] = printed.getvalue()
except Exception as exc:
    answer["print_month_error"] = f"{type(exc).__name__}: {exc}"

print(json.dumps(answer))
'''

FLAT_LINES = [
    "Α1: 150 χιλιοστά - 126.00 €",
    "Α2: 180 χιλιοστά - 151.20 €",
    "Β1: 200 χιλιοστά - 168.00 €",
    "Β2: 220 χιλιοστά - 184.80 €",
    "Γ1: 250 χιλιοστά - 210.00 €",
    "Α1: 150 χιλιοστά - 151.50 €",
    "Α2: 180 χιλιοστά - 181.80 €",
    "Β1: 200 χιλιοστά - 202.00 €",
    "Β2: 220 χιλιοστά - 222.20 €",
    "Γ1: 250 χιλιοστά - 252.50 €",
]

TOTAL_LINES = ["Σύνολο: 840.00 €", "Σύνολο: 1010.00 €"]

SAMPLE_MONTH = [
    "ΔΟΚΙΜΗ",
    "Α1: 150 χιλιοστά - 75.00 €",
    "Α2: 180 χιλιοστά - 90.00 €",
    "Β1: 200 χιλιοστά - 100.00 €",
    "Β2: 220 χιλιοστά - 110.00 €",
    "Γ1: 250 χιλιοστά - 125.00 €",
    "Σύνολο: 500.00 €",
]


def clean(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


run = subprocess.run(
    [sys.executable, "shares.py"], capture_output=True, text=True
)
crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ""
output = clean(run.stdout)

probe = subprocess.run(
    [sys.executable, "-c", PROBE], capture_output=True, text=True
)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    facts = {"import_error": probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


if crash:
    report(False, "Οι γραμμές των διαμερισμάτων βγαίνουν σωστές και για τους δύο μήνες", crash)
else:
    found = [line for line in output if "χιλιοστά" in line]
    if found == FLAT_LINES:
        report(True, "Οι γραμμές των διαμερισμάτων βγαίνουν σωστές και για τους δύο μήνες")
    else:
        report(
            False,
            "Οι γραμμές των διαμερισμάτων βγαίνουν σωστές και για τους δύο μήνες",
            f"βρήκα {len(found)} γραμμές: {found}",
        )

totals = [line for line in output if line.startswith("Σύνολο")]
if totals == TOTAL_LINES:
    report(True, "Κάθε μήνας τυπώνει το σύνολό του, 840.00 και 1010.00")
else:
    report(
        False,
        "Κάθε μήνας τυπώνει το σύνολό του, 840.00 και 1010.00",
        f"βρήκα {totals}" if totals else "καμία γραμμή που να αρχίζει με Σύνολο",
    )

label = "Η share_of επιστρέφει το μερίδιο, το ποσό του μήνα το παίρνει ως όρισμα, και δεν τυπώνει"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "share_of_error" in facts:
    report(False, label, facts["share_of_error"])
elif facts["share_of"] != "181.80":
    report(False, label, f"η share_of(1010.00, 180) επέστρεψε {facts['share_of']} αντί για 181.80")
elif facts["share_of_printed"]:
    report(False, label, f"η share_of τύπωσε {facts['share_of_printed']!r}")
else:
    report(True, label)

label = "Η print_month βγάζει έναν ολόκληρο μήνα με μία κλήση"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "print_month_error" in facts:
    report(False, label, facts["print_month_error"])
elif clean(facts["print_month"]) != SAMPLE_MONTH:
    report(
        False,
        label,
        f"η print_month(\"ΔΟΚΙΜΗ\", 500.00) τύπωσε {clean(facts['print_month'])}",
    )
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
