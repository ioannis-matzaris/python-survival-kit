import ast
import json
import subprocess
import sys

SOURCE = "didaktra.py"

EXPECTED = [
    "ΔΙΔΑΚΤΡΑ ΜΑΡΤΙΟΥ",
    "",
    "Ελένη Παπαδάκη           180.00",
    "Γιώργος Αντωνίου         162.00",
    "Μαρία Δημητρίου          165.00",
    "Νίκος Σαββίδης           148.50",
    "Άννα Βλαχάκη             220.00",
    "Θοδωρής Καρράς           238.00",
    "",
    "ΣΥΝΟΛΟ                  1113.50",
]

CASES = [
    (180.0, [], False, 180.00),
    (180.0, [0.10], False, 162.00),
    (220.0, [0.25], False, 165.00),
    (220.0, [0.25, 0.10], False, 148.50),
    (180.0, [], True, 220.00),
    (220.0, [0.10], True, 238.00),
    (220.0, [0.25], True, 205.00),
    (220.0, [0.25, 0.10], True, 188.50),
]

PROBE = r'''
import contextlib
import inspect
import io
import json

CASES = json.loads(r"""%s""")

answer = {}
try:
    with contextlib.redirect_stdout(io.StringIO()):
        import didaktra
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

student = getattr(didaktra, "Student", None)
answer["has_class"] = isinstance(student, type)

if answer["has_class"]:
    try:
        answer["fees"] = [
            student("Δοκιμή", base, list(discounts), bus).fee()
            for base, discounts, bus, _ in CASES
        ]
    except Exception as exc:
        answer["fee_error"] = f"{type(exc).__name__}: {exc}"
    try:
        one = student("Δοκιμή", 200.0, [0.10], False)
        answer["before_bus"] = one.fee()
        one.bus = True
        answer["after_bus"] = one.fee()
    except Exception as exc:
        answer["bus_error"] = f"{type(exc).__name__}: {exc}"

for name in ("report_title", "fee_line"):
    answer[name] = inspect.isfunction(getattr(didaktra, name, None))
if answer["report_title"]:
    answer["title_text"] = didaktra.report_title()
if answer["fee_line"]:
    answer["line_text"] = didaktra.fee_line("Δοκιμή", 7.5)

print(json.dumps(answer, ensure_ascii=False))
''' % json.dumps(CASES)

run = subprocess.run([sys.executable, "-B", SOURCE], capture_output=True, text=True)
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


def class_names() -> list[str]:
    tree = ast.parse(open(SOURCE, encoding="utf-8").read())
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


label = "Η έξοδος του didaktra.py δεν άλλαξε ούτε κατά χαρακτήρα"
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

label = "Έμεινε μία μόνο class, η Student"
found_classes = class_names()
if found_classes == ["Student"]:
    report(True, label)
else:
    report(False, label, f"βρήκα {len(found_classes)}: " + ", ".join(found_classes))

label = "Η Student βγάζει σωστά δίδακτρα σε κάθε συνδυασμό"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif not facts.get("has_class"):
    report(False, label, "δεν βρήκα class με το όνομα Student")
elif "fee_error" in facts:
    report(False, label, facts["fee_error"])
else:
    wrong = [
        f"base {base} με {discounts} και bus={bus}: {got} αντί για {want:.2f}"
        for (base, discounts, bus, want), got in zip(CASES, facts.get("fees", []))
        if got != want
    ]
    if wrong:
        report(False, label, wrong[0])
    else:
        report(True, label)

label = "Ο μαθητής αλλάζει γνώμη με μία ανάθεση στο bus"
if "import_error" in facts or not facts.get("has_class"):
    report(False, label, "δεν έτρεξε η Student")
elif "bus_error" in facts:
    report(False, label, facts["bus_error"])
elif facts.get("before_bus") != 180.0:
    report(False, label, f"χωρίς λεωφορείο βγήκαν {facts.get('before_bus')} αντί για 180.0")
elif facts.get("after_bus") != 220.0:
    report(False, label, f"μετά το student.bus = True βγήκαν {facts.get('after_bus')} αντί για 220.0")
else:
    report(True, label)

label = "Η report_title και η fee_line είναι συναρτήσεις του module"
missing = [name for name in ("report_title", "fee_line") if not facts.get(name)]
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif missing:
    report(False, label, "δεν βρήκα συνάρτηση " + ", ".join(missing))
elif facts.get("title_text") != "ΔΙΔΑΚΤΡΑ ΜΑΡΤΙΟΥ":
    report(False, label, f"η report_title επέστρεψε {facts.get('title_text')!r}")
elif facts.get("line_text") != f"{'Δοκιμή':<22}{7.5:>9.2f}":
    report(False, label, f"η fee_line επέστρεψε {facts.get('line_text')!r}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
