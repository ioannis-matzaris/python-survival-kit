import json
import subprocess
import sys

PROBE = r'''
import contextlib
import io
import json

buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(buffer):
        import signups
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

FIX_SIGNUPS = [
    "9107;ΟΜΙΛΟΣ",
    "9113;ΕΚΔΡΟΜΗ",
    "9102;ΕΚΔΡΟΜΗ",
    "9107;ΕΚΔΡΟΜΗ",
    "9119;ΟΜΙΛΟΣ",
    "9104;ΕΚΔΡΟΜΗ",
    "9121;ΕΚΔΡΟΜΗ",
    "9113;ΟΜΙΛΟΣ",
    "9110;ΕΚΔΡΟΜΗ",
    "9116;ΕΚΔΡΟΜΗ",
    "9101;ΕΚΔΡΟΜΗ",
    "9119;ΕΚΔΡΟΜΗ",
    "9124;ΕΚΔΡΟΜΗ",
    "9102;ΟΜΙΛΟΣ",
    "9108;ΕΚΔΡΟΜΗ",
    "9105;ΕΚΔΡΟΜΗ",
    "9130;ΟΜΙΛΟΣ",
]

FIX_STUDENTS = [
    "9130;Άννα Ρήγα;Α1",
    "9107;Πέτρος Λαμπρόπουλος;Β3",
    "9113;Χρύσα Μανωλά;Γ4",
]

answer = {}
printed = io.StringIO()

with contextlib.redirect_stdout(printed):
    try:
        answer["queue"] = signups.trip_queue(FIX_SIGNUPS)
    except Exception as exc:
        answer["queue_error"] = f"{type(exc).__name__}: {exc}"

    try:
        labels = signups.student_labels(FIX_STUDENTS)
        answer["labels_type"] = type(labels).__name__
        answer["labels"] = dict(labels) if isinstance(labels, dict) else str(labels)
    except Exception as exc:
        answer["labels_error"] = f"{type(exc).__name__}: {exc}"

    try:
        answer["distinct"] = signups.distinct_students(FIX_SIGNUPS)
    except Exception as exc:
        answer["distinct_error"] = f"{type(exc).__name__}: {exc}"

answer["printed"] = printed.getvalue()
print(json.dumps(answer, ensure_ascii=False))
'''

EXPECTED_QUEUE = [
    "9113",
    "9102",
    "9107",
    "9104",
    "9121",
    "9110",
    "9116",
    "9101",
    "9119",
    "9124",
    "9108",
    "9105",
]

EXPECTED_LABELS = {
    "9130": "Άννα Ρήγα (Α1)",
    "9107": "Πέτρος Λαμπρόπουλος (Β3)",
    "9113": "Χρύσα Μανωλά (Γ4)",
}

EXPECTED_DISTINCT = 13

EXPECTED_OUTPUT = [
    "ΣΕΙΡΑ ΓΙΑ ΤΗΝ ΕΚΔΡΟΜΗ",
    "1. 7412 - Μαρία Ιωάννου (Α3)",
    "2. 7208 - Ελένη Βασιλείου (Β2)",
    "3. 7561 - Θανάσης Κούρτης (Β1)",
    "4. 7315 - Νίκος Παπαδάκης (Γ1)",
    "5. 7690 - Δήμητρα Σαββίδου (Γ2)",
    "ΔΙΑΦΟΡΕΤΙΚΟΙ ΜΑΘΗΤΕΣ: 5",
]

probe = subprocess.run([sys.executable, "-c", PROBE], capture_output=True, text=True)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    detail = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"
    facts = {"import_error": detail}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def runs() -> list[list[str]]:
    collected: list[list[str]] = []
    for _ in range(3):
        run = subprocess.run([sys.executable, "signups.py"], capture_output=True, text=True)
        if run.returncode != 0:
            crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else "άγνωστο σφάλμα"
            collected.append([f"ΣΦΑΛΜΑ: {crash}"])
        else:
            collected.append([line.strip() for line in run.stdout.splitlines() if line.strip()])
    return collected


label = "Η trip_queue δίνει τα ΑΜ της εκδρομής με τη σειρά που δηλώθηκαν"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "queue_error" in facts:
    report(False, label, facts["queue_error"])
elif facts["queue"] != EXPECTED_QUEUE:
    report(False, label, f"περίμενα {EXPECTED_QUEUE} και πήρα {facts['queue']}")
elif facts["printed"]:
    report(False, label, f"οι συναρτήσεις τύπωσαν {facts['printed']!r}")
else:
    report(True, label)

label = "Η student_labels δίνει dictionary από ΑΜ σε όνομα και τμήμα"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "labels_error" in facts:
    report(False, label, facts["labels_error"])
elif facts["labels_type"] != "dict":
    report(False, label, f"επέστρεψε {facts['labels_type']} και όχι dict")
elif facts["labels"] != EXPECTED_LABELS:
    report(False, label, f"περίμενα {EXPECTED_LABELS} και πήρα {facts['labels']}")
else:
    report(True, label)

label = "Η distinct_students μετράει τους διαφορετικούς μαθητές"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "distinct_error" in facts:
    report(False, label, facts["distinct_error"])
elif facts["distinct"] != EXPECTED_DISTINCT:
    report(False, label, f"περίμενα {EXPECTED_DISTINCT} και πήρα {facts['distinct']}")
else:
    report(True, label)

label = "Το signups.py βγάζει την ίδια σωστή κατάσταση σε τρία συνεχόμενα τρεξίματα"
collected = runs()
if collected[0] != EXPECTED_OUTPUT:
    report(False, label, f"περίμενα {EXPECTED_OUTPUT} και πήρα {collected[0]}")
elif collected[1] != EXPECTED_OUTPUT or collected[2] != EXPECTED_OUTPUT:
    report(False, label, f"το δεύτερο ή το τρίτο τρέξιμο έδωσε {collected[1]} και {collected[2]}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
