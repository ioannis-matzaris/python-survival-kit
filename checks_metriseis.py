import json
import subprocess
import sys

EXPECTED = [
    "ΚΑΤΑΝΑΛΩΣΗ ΔΙΜΗΝΟΥ",
    "",
    "Ε-4471       350 kWh     39.50",
    "Ε-2210       375 kWh     43.25",
    "Ε-8837       424 kWh     50.60",
    "Ε-9002       330 kWh     36.50",
    "",
    "ΣΥΝΟΛΟ                  169.85",
]

PROBE = r'''
import contextlib
import io
import json

answer = {}
try:
    with contextlib.redirect_stdout(io.StringIO()):
        import metriseis
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

reading = getattr(metriseis, "Reading", None)
answer["has_class"] = isinstance(reading, type)

if answer["has_class"]:
    try:
        one = reading("Δ-1", 1000, 1350)
        answer["fields"] = sorted(name for name in vars(one) if not name.startswith("_"))
        answer["has_fields"] = all(hasattr(one, name) for name in ("meter", "previous", "current"))
        answer["kwh_before"] = one.kwh()
        one.current = 1500
        answer["kwh_after"] = one.kwh()
    except Exception as exc:
        answer["model_error"] = f"{type(exc).__name__}: {exc}"
    try:
        answer["charge_300"] = reading("Δ-2", 0, 300).charge()
        answer["charge_500"] = reading("Δ-3", 1000, 1500).charge()
        answer["charge_0"] = reading("Δ-4", 700, 700).charge()
    except Exception as exc:
        answer["charge_error"] = f"{type(exc).__name__}: {exc}"

    readings = getattr(metriseis, "readings", None)
    if isinstance(readings, list):
        answer["readings"] = len(readings)
        answer["readings_ok"] = all(isinstance(item, reading) for item in readings)
    else:
        answer["readings"] = -1
        answer["readings_ok"] = False

leftovers = []
for name, value in vars(metriseis).items():
    if name.startswith("_") or not isinstance(value, list) or not value:
        continue
    if all(isinstance(item, (str, int, float)) and not isinstance(item, bool) for item in value):
        leftovers.append(name)
answer["leftovers"] = sorted(leftovers)

print(json.dumps(answer, ensure_ascii=False))
'''

run = subprocess.run(
    [sys.executable, "-B", "metriseis.py"], capture_output=True, text=True
)
crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ""
output = run.stdout.rstrip("\n").splitlines()

probe = subprocess.run([sys.executable, "-B", "-c", PROBE], capture_output=True, text=True)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    detail = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"
    facts = {"import_error": detail}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


label = "Η αναφορά βγαίνει σωστή και για τους τέσσερις μετρητές"
if crash:
    report(False, label, crash)
elif output == EXPECTED:
    report(True, label)
else:
    for wanted, found in zip(EXPECTED, output):
        if wanted != found:
            report(False, label, f"περίμενα {wanted!r} και βρήκα {found!r}")
            break
    else:
        report(False, label, f"περίμενα {len(EXPECTED)} γραμμές και βρήκα {len(output)}")

label = "Υπάρχει class Reading με meter, previous, current"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif not facts.get("has_class"):
    report(False, label, "δεν βρήκα class με το όνομα Reading")
elif "model_error" in facts:
    report(False, label, facts["model_error"])
elif not facts.get("has_fields"):
    report(False, label, f"βρήκα πεδία {facts.get('fields')}")
elif not facts.get("readings_ok") or facts.get("readings", 0) != 4:
    report(False, label, f"η λίστα readings έχει {facts.get('readings')} αντικείμενα Reading")
else:
    report(True, label)

label = "Η κατανάλωση υπολογίζεται, δεν είναι αποθηκευμένη"
if "import_error" in facts or not facts.get("has_class"):
    report(False, label, "δεν έτρεξε η Reading")
elif "model_error" in facts:
    report(False, label, facts["model_error"])
elif facts.get("kwh_before") != 350:
    report(False, label, f"η kwh() έδωσε {facts.get('kwh_before')} αντί για 350")
elif facts.get("kwh_after") != 500:
    report(False, label, f"μετά τη διόρθωση η kwh() έδωσε {facts.get('kwh_after')} αντί για 500")
else:
    report(True, label)

label = "Η charge() χρεώνει σωστά και τα δύο κλιμάκια"
if "import_error" in facts or not facts.get("has_class"):
    report(False, label, "δεν έτρεξε η Reading")
elif "charge_error" in facts:
    report(False, label, facts["charge_error"])
else:
    wanted = {"charge_0": 5.0, "charge_300": 32.0, "charge_500": 62.0}
    wrong = [f"{key}: {facts.get(key)}" for key, value in wanted.items() if facts.get(key) != value]
    if wrong:
        report(False, label, "λάθος ποσά - " + ", ".join(wrong))
    else:
        report(True, label)

label = "Δεν έμεινε καμία παράλληλη λίστα στο metriseis.py"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif facts.get("leftovers"):
    report(False, label, "βρήκα ακόμα " + ", ".join(facts["leftovers"]))
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
