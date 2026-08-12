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
        import inspection
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

try:
    answer["defaults"] = repr(inspection.defects.__defaults__)
    with contextlib.redirect_stdout(io.StringIO()):
        first = inspection.defects(False, True, 0.12)
        second = inspection.defects(True, True, 0.18)
        third = inspection.defects(True, True, 0.05)
        by_hand = inspection.defects(True, True, 0.05, ["σκουριά"])
    answer["first"] = first
    answer["second"] = second
    answer["third"] = third
    answer["by_hand"] = by_hand
except Exception as exc:
    answer["defects_error"] = f"{type(exc).__name__}: {exc}"

try:
    answer["owner_return"] = str(inspection.owner_of.__annotations__["return"])
except Exception as exc:
    answer["owner_error"] = f"{type(exc).__name__}: {exc}"

print(json.dumps(answer, ensure_ascii=False))
'''

HEADERS = [
    "Ειδοποίηση προς Παπαδοπούλου Μαρία, όχημα ΙΖΡ-4410",
    "Ειδοποίηση προς Καραγιάννης Στέλιος, όχημα ΝΑΤ-2087",
    "Ειδοποίηση προς Δημητρίου Άννα, όχημα ΥΒΗ-9931",
    "ΚΑΤ-5560: άγνωστος ιδιοκτήτης, δεν στέλνεται ειδοποίηση",
]

FINDINGS = [["φρένα"], ["καθαρό"], ["φώτα", "καυσαέρια"], ["καθαρό"]]

run = subprocess.run([sys.executable, "inspection.py"], capture_output=True, text=True)
crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ""

headers: list[str] = []
findings: list[list[str]] = []
for raw in run.stdout.splitlines():
    line = raw.strip()
    if not line:
        continue
    if line.startswith("!") or line == "καθαρό":
        if findings:
            findings[-1].append(line.lstrip("!").strip())
    else:
        headers.append(line)
        findings.append([])

probe = subprocess.run([sys.executable, "-c", PROBE], capture_output=True, text=True)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    detail = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"
    facts = {"import_error": detail}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


label = "Κάθε όχημα παίρνει μόνο τα δικά του ευρήματα"
if crash:
    report(False, label, crash)
elif findings == FINDINGS:
    report(True, label)
else:
    report(False, label, f"βρήκα {findings}")

label = "Η defects δεν κουβαλάει τίποτα από την προηγούμενη κλήση"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "defects_error" in facts:
    report(False, label, facts["defects_error"])
elif facts["defaults"] != "(None,)":
    report(False, label, f"η προεπιλογή της παραμέτρου είναι {facts['defaults']}")
elif facts["first"] != ["φρένα"]:
    report(False, label, f"η πρώτη κλήση επέστρεψε {facts['first']}")
elif facts["second"] or facts["third"]:
    report(
        False,
        label,
        f"οι επόμενες κλήσεις για καθαρά οχήματα επέστρεψαν {facts['second']} και {facts['third']}",
    )
elif facts["by_hand"] != ["σκουριά"]:
    report(
        False,
        label,
        f"με παρατήρηση γραμμένη από τον τεχνικό επέστρεψε {facts['by_hand']} αντί για ['σκουριά']",
    )
else:
    report(True, label)

label = "Ο άγνωστος αριθμός δεν παίρνει ειδοποίηση, και η owner_of δηλώνει ακόμα str | None"
if crash:
    report(False, label, crash)
elif headers != HEADERS:
    report(False, label, f"βρήκα {headers}")
elif "import_error" in facts:
    report(False, label, facts["import_error"])
elif facts.get("owner_return") != "str | None":
    report(False, label, f"η owner_of δηλώνει {facts.get('owner_return', facts.get('owner_error'))}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
