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
        import stock
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

answer = {}
printed = io.StringIO()

with contextlib.redirect_stdout(printed):
    try:
        totals, skipped = stock.build_stock(stock.MOVEMENTS)
        answer["totals"] = dict(totals)
        answer["skipped"] = list(skipped)
    except Exception as exc:
        answer["build_error"] = f"{type(exc).__name__}: {exc}"

    try:
        stock.apply_to({}, "ΠΡ-1009;ΚΑΤΑΣΤΡΟΦΗ;2")
        answer["unknown_kind"] = "καμία αντίδραση"
    except Exception as exc:
        answer["unknown_kind"] = type(exc).__name__
        answer["unknown_message"] = str(exc)

    try:
        stock.build_stock(["ΠΡ-1009;ΕΙΣΑΓΩΓΗ"])
        answer["short_row"] = "καμία αντίδραση"
    except Exception as exc:
        answer["short_row"] = type(exc).__name__

print(json.dumps(answer, ensure_ascii=False))
'''

EXPECTED_TOTALS = {"ΠΡ-1001": 32, "ΠΡ-1002": 15, "ΠΡ-1003": 10}
EXPECTED_SKIPPED = [5, 7]

EXPECTED_OUTPUT = [
    "ΑΠΟΘΕΜΑ ΤΕΛΟΥΣ ΗΜΕΡΑΣ",
    "ΠΡ-1001: 32 τεμάχια",
    "ΠΡ-1002: 15 τεμάχια",
    "ΠΡ-1003: 10 τεμάχια",
    "Κινήσεις που προσπεράστηκαν: 2 (γραμμές 5, 7)",
]

probe = subprocess.run(
    [sys.executable, "-c", PROBE], capture_output=True, text=True, stdin=subprocess.DEVNULL
)
if "BdbQuit" in probe.stdout or "BdbQuit" in probe.stderr:
    facts = {"import_error": "έμεινε ένα breakpoint() στον κώδικα, σβήσ' το"}
else:
    try:
        facts = json.loads(probe.stdout.strip().splitlines()[-1])
    except Exception:
        tail = probe.stderr.strip().splitlines()
        facts = {"import_error": tail[-1] if tail else "καμία απάντηση"}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


label = "Το stock.py τρέχει ως το τέλος και τυπώνει το σωστό απόθεμα"
run = subprocess.run(
    [sys.executable, "stock.py"], capture_output=True, text=True, stdin=subprocess.DEVNULL
)
if run.returncode != 0:
    tail = run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "άγνωστο σφάλμα")
else:
    output = [line.strip() for line in run.stdout.splitlines() if line.strip()]
    if output == EXPECTED_OUTPUT:
        report(True, label)
    else:
        report(False, label, f"περίμενα {EXPECTED_OUTPUT} και πήρα {output}")

label = "Η build_stock μετράει κάθε κίνηση που ξέρει, την ΕΠΙΣΤΡΟΦΗ μαζί"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif "build_error" in facts:
    report(False, label, str(facts["build_error"]))
elif facts["totals"] != EXPECTED_TOTALS:
    report(False, label, f"περίμενα {EXPECTED_TOTALS} και πήρα {facts['totals']}")
else:
    report(True, label)

label = "Η build_stock σημειώνει ποιες γραμμές προσπέρασε"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif "build_error" in facts:
    report(False, label, str(facts["build_error"]))
elif facts["skipped"] != EXPECTED_SKIPPED:
    report(False, label, f"περίμενα {EXPECTED_SKIPPED} και πήρα {facts['skipped']}")
else:
    report(True, label)

label = "Η apply_to δεν αγνοεί σιωπηλά ένα είδος κίνησης που δεν ξέρει"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif facts.get("unknown_kind") != "ValueError":
    report(False, label, f"περίμενα ValueError και πήρα {facts.get('unknown_kind')}")
elif "ΚΑΤΑΣΤΡΟΦΗ" not in facts.get("unknown_message", ""):
    report(False, label, f"το μήνυμα δεν λέει ποιο είδος ήταν: {facts.get('unknown_message')!r}")
else:
    report(True, label)

label = "Η build_stock δεν καταπίνει σφάλματα που δεν ξέρει να χειριστεί"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif facts.get("short_row") != "IndexError":
    report(False, label, f"μια γραμμή χωρίς ποσότητα έπρεπε να βγάλει IndexError, πήρα {facts.get('short_row')}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
