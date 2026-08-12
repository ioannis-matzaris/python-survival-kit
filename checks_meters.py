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
        import meters
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

FIX_READINGS = [
    "70000001;2026-05;100",
    "70000002;2026-05;250",
    "70000001;2026-06;180",
]
FIX_REGISTRY = ["70000003", "70000001", "70000002"]
FIX_CODES = ["ΑΛΦΑ", "ΒΗΤΑ", "ΓΑΜΑ", "ΔΕΛΤΑ"]

answer = {}
printed = io.StringIO()

with contextlib.redirect_stdout(printed):
    try:
        totals = meters.consumption_per_month(FIX_READINGS)
        answer["totals_type"] = type(totals).__name__
        pairs = []
        tuple_keys = True
        for key, value in totals.items():
            if isinstance(key, tuple) and len(key) == 2:
                pairs.append(f"{key[0]};{key[1]};{value}")
            else:
                tuple_keys = False
                pairs.append(f"{key!r};{value}")
        answer["totals_pairs"] = sorted(pairs)
        answer["totals_tuple_keys"] = tuple_keys
    except Exception as exc:
        answer["totals_error"] = f"{type(exc).__name__}: {exc}"

    try:
        answer["missing"] = [
            meters.missing_from_month(FIX_READINGS, FIX_REGISTRY, "2026-05"),
            meters.missing_from_month(FIX_READINGS, FIX_REGISTRY, "2026-06"),
            meters.missing_from_month(FIX_READINGS, FIX_REGISTRY, "2026-07"),
        ]
    except Exception as exc:
        answer["missing_error"] = f"{type(exc).__name__}: {exc}"

    try:
        answer["steps"] = [
            meters.steps_to_find(FIX_CODES, "ΑΛΦΑ"),
            meters.steps_to_find(FIX_CODES, "ΓΑΜΑ"),
            meters.steps_to_find(FIX_CODES, "ΔΕΛΤΑ"),
            meters.steps_to_find(FIX_CODES, "ΕΨΙΛΟΝ"),
            meters.steps_to_find([], "ΑΛΦΑ"),
        ]
    except Exception as exc:
        answer["steps_error"] = f"{type(exc).__name__}: {exc}"

answer["printed"] = printed.getvalue()
print(json.dumps(answer, ensure_ascii=False))
'''

EXPECTED_PAIRS = [
    "70000001;2026-05;100",
    "70000001;2026-06;180",
    "70000002;2026-05;250",
]

EXPECTED_MISSING = [
    ["70000003"],
    ["70000002", "70000003"],
    ["70000001", "70000002", "70000003"],
]

EXPECTED_STEPS = [1, 3, 4, 4, 0]

EXPECTED_OUTPUT = [
    "ΚΑΤΑΝΑΛΩΣΗ ΑΝΑ ΠΑΡΟΧΗ ΚΑΙ ΜΗΝΑ",
    "12345678 2026-01: 318 kWh",
    "12345678 2026-02: 295 kWh",
    "12345678 2026-03: 340 kWh",
    "23456789 2026-01: 540 kWh",
    "23456789 2026-02: 612 kWh",
    "23456789 2026-03: 588 kWh",
    "34567890 2026-01: 127 kWh",
    "45678901 2026-01: 902 kWh",
    "ΧΩΡΙΣ ΜΕΤΡΗΣΗ ΤΟΝ 2026-02",
    "34567890",
    "45678901",
    "56789012",
    "ΒΗΜΑΤΑ ΑΝΑΖΗΤΗΣΗΣ ΣΤΟ ΜΗΤΡΩΟ",
    "πρώτη παροχή: 1",
    "τελευταία παροχή: 5",
    "παροχή που δεν υπάρχει: 5",
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


label = "Η consumption_per_month δίνει dictionary με κλειδί δύο μερών"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "totals_error" in facts:
    report(False, label, facts["totals_error"])
elif facts["totals_type"] != "dict":
    report(False, label, f"επέστρεψε {facts['totals_type']} και όχι dict")
elif not facts["totals_tuple_keys"]:
    report(False, label, f"τα κλειδιά δεν είναι tuple δύο μερών: {facts['totals_pairs']}")
elif facts["totals_pairs"] != EXPECTED_PAIRS:
    report(False, label, f"περίμενα {EXPECTED_PAIRS} και πήρα {facts['totals_pairs']}")
else:
    report(True, label)

label = "Η missing_from_month δίνει τις παροχές χωρίς μέτρηση, ταξινομημένες"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "missing_error" in facts:
    report(False, label, facts["missing_error"])
elif facts["missing"] != EXPECTED_MISSING:
    report(False, label, f"περίμενα {EXPECTED_MISSING} και πήρα {facts['missing']}")
else:
    report(True, label)

label = "Η steps_to_find μετράει και όταν βρίσκει και όταν δεν βρίσκει"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "steps_error" in facts:
    report(False, label, facts["steps_error"])
elif facts["steps"] != EXPECTED_STEPS:
    report(False, label, f"περίμενα {EXPECTED_STEPS} και πήρα {facts['steps']}")
else:
    report(True, label)

label = "Το meters.py τρέχει ως το τέλος και τυπώνει τις σωστές γραμμές"
run = subprocess.run([sys.executable, "meters.py"], capture_output=True, text=True)
if run.returncode != 0:
    crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else "άγνωστο σφάλμα"
    report(False, label, crash)
else:
    output = [line.strip() for line in run.stdout.splitlines() if line.strip()]
    if output == EXPECTED_OUTPUT:
        report(True, label)
    else:
        report(False, label, f"περίμενα {EXPECTED_OUTPUT} και πήρα {output}")

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
