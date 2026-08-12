import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / "synopsi.py"
SOURCE_FILE = HERE / "timologia.json"

EXPECTED = {
    "afm": "800451233",
    "pelatis": "Παπαδοπούλου Μαρία ΙΚΕ",
    "plithos": 3,
    "synolo": "674.17",
}

OTHER_EXPORT = {
    "periodos": "2026-03",
    "timologia": [
        {
            "arithmos": "ΤΔΑ-2001",
            "afm": "111222333",
            "pelatis": "Καφενείο Ζάχος ΟΕ",
            "imerominia": "2026-03-02",
            "poso": "75.40",
        },
        {
            "arithmos": "ΤΔΑ-2002",
            "afm": "444555666",
            "pelatis": "Αφοί Στεργίου ΑΕ",
            "imerominia": "2026-03-06",
            "poso": "980.00",
        },
        {
            "arithmos": "ΤΔΑ-2003",
            "afm": "111222333",
            "pelatis": "Καφενείο Ζάχος ΟΕ",
            "imerominia": "2026-03-19",
            "poso": "18.60",
        },
    ],
}

OTHER_EXPECTED = {
    "afm": "111222333",
    "pelatis": "Καφενείο Ζάχος ΟΕ",
    "plithos": 2,
    "synolo": "94.00",
}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(PROGRAM), *args],
        cwd=HERE,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )


def crashed(finished: subprocess.CompletedProcess[str]) -> bool:
    return "Traceback (most recent call last)" in finished.stderr


def calls_float(source: str) -> int:
    tree = ast.parse(source)
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "float"
    )


label = "Χωρίς ορίσματα, το script λέει πώς τρέχεται και τερματίζει με 1"
no_args = run()
if no_args.returncode == 0:
    report(False, label, "τερμάτισε με 0 σαν να ήταν όλα εντάξει")
elif crashed(no_args):
    report(False, label, "έβγαλε traceback αντί για μήνυμα προς τον χρήστη")
elif "Χρήση" not in no_args.stdout + no_args.stderr:
    report(False, label, "δεν τύπωσε μήνυμα χρήσης")
else:
    report(True, label)

label = "Η έξοδος είναι σκέτο JSON, με τα ελληνικά ελληνικά"
main_run = run(str(SOURCE_FILE), "800451233")
parsed: object = None
if main_run.returncode != 0:
    tail = main_run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "τερμάτισε με σφάλμα")
else:
    try:
        parsed = json.loads(main_run.stdout)
    except json.JSONDecodeError as exc:
        report(False, label, f"η έξοδος δεν διαβάζεται ως JSON: {exc}")
    else:
        if "Παπαδοπούλου" not in main_run.stdout:
            report(False, label, "τα ελληνικά βγήκαν ως κωδικοί \\u, λείπει το ensure_ascii=False")
        elif main_run.stdout.count("\n") < 4:
            report(False, label, "το JSON βγήκε σε μία γραμμή, λείπει το indent=2")
        else:
            report(True, label)

label = "Η σύνοψη του ΑΦΜ 800451233 έχει τα σωστά νούμερα"
if parsed is None:
    report(False, label, "δεν πήρα JSON για να το ελέγξω")
elif parsed != EXPECTED:
    report(False, label, f"περίμενα {EXPECTED} και πήρα {parsed}")
else:
    report(True, label)

label = "Διαβάζει το αρχείο και το ΑΦΜ που του δίνεις, όχι κάτι σταθερό"
with tempfile.TemporaryDirectory() as folder:
    other = Path(folder) / "allo_export.json"
    other.write_text(
        json.dumps(OTHER_EXPORT, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    other_run = run(str(other), "111222333")
if other_run.returncode != 0:
    tail = other_run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "τερμάτισε με σφάλμα")
else:
    try:
        other_parsed = json.loads(other_run.stdout)
    except json.JSONDecodeError:
        report(False, label, "η έξοδος δεν διαβάζεται ως JSON")
    else:
        if other_parsed != OTHER_EXPECTED:
            report(False, label, f"περίμενα {OTHER_EXPECTED} και πήρα {other_parsed}")
        else:
            report(True, label)

label = "ΑΦΜ χωρίς τιμολόγια βγάζει μήνυμα, όχι traceback"
missing = run(str(SOURCE_FILE), "999888777")
if crashed(missing):
    tail = missing.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "traceback")
elif missing.returncode == 0:
    report(False, label, "τερμάτισε με 0 σαν να βρήκε τιμολόγια")
elif not (missing.stdout + missing.stderr).strip():
    report(False, label, "δεν τύπωσε τίποτα")
else:
    report(True, label)

label = "Τα ποσά δεν περνάνε από float"
try:
    floats = calls_float(PROGRAM.read_text(encoding="utf-8"))
except SyntaxError as exc:
    report(False, label, f"το synopsi.py δεν διαβάζεται: {exc}")
else:
    if floats:
        times = "μία φορά" if floats == 1 else f"{floats} φορές"
        report(False, label, f"το synopsi.py καλεί ακόμα την float() {times}")
    else:
        report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
