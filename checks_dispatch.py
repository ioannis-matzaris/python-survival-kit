import json
import re
import shutil
import subprocess
import sys

PROBE = r'''
import contextlib
import io
import json

buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(buffer):
        import dispatch
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

answer = {}
printed = io.StringIO()

with contextlib.redirect_stdout(printed):
    try:
        answer["shipping"] = [
            dispatch.shipping_for("ΠΕΛ-11"),
            dispatch.shipping_for("ΠΕΛ-12"),
            dispatch.shipping_for("ΠΕΛ-13"),
        ]
    except Exception as exc:
        answer["shipping_error"] = f"{type(exc).__name__}: {exc}"

    try:
        answer["lines"] = [
            dispatch.line_for("ΠΑΡ-4404;ΠΕΛ-13;1;41.60"),
            dispatch.line_for("ΠΑΡ-4401;ΠΕΛ-11;2;12.90"),
        ]
    except Exception as exc:
        answer["lines_error"] = f"{type(exc).__name__}: {exc}"

print(json.dumps(answer, ensure_ascii=False))
'''

ANSWERS_PROBE = r'''
import json

try:
    import diagnosis
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

given = {}
for key, value in getattr(diagnosis, "ANSWERS", {}).items():
    given[str(key)] = [str(part) for part in value]
print(json.dumps({"answers": given}, ensure_ascii=False))
'''

EXPECTED_SHIPPING = [2.5, 3.2, 4.1]

EXPECTED_LINES = [
    "ΠΑΡ-4404: 45.70 ευρώ",
    "ΠΑΡ-4401: 28.30 ευρώ",
]

EXPECTED_OUTPUT = [
    "ΠΑΡΑΓΓΕΛΙΕΣ ΤΗΣ ΗΜΕΡΑΣ",
    "ΠΑΡ-4401: 28.30 ευρώ",
    "ΠΑΡ-4402: 93.10 ευρώ",
    "ΠΑΡ-4403: 16.00 ευρώ",
    "ΠΑΡ-4404: 45.70 ευρώ",
]

FRAME = re.compile(r'^\s+File "(?P<path>[^"]+)", line \d+, in (?P<function>\S+)\s*$')


def run_json(source: str) -> dict[str, object]:
    probe = subprocess.run(
        [sys.executable, "-B", "-c", source], capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    if "BdbQuit" in probe.stdout or "BdbQuit" in probe.stderr:
        return {"import_error": "έμεινε ένα breakpoint() στον κώδικα, σβήσ' το"}
    try:
        return json.loads(probe.stdout.strip().splitlines()[-1])
    except Exception:
        tail = probe.stderr.strip().splitlines()
        return {"import_error": tail[-1] if tail else "καμία απάντηση"}


def crash_of(name: str) -> dict[str, str]:
    run = subprocess.run(
        [sys.executable, "-B", f"{name}.py"], capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    if run.returncode == 0:
        return {"no_crash": "τρέχει χωρίς σφάλμα"}
    lines = [line for line in run.stderr.splitlines() if line.strip()]
    if not lines:
        return {"no_crash": "δεν έβγαλε traceback"}
    last = lines[-1].strip()
    error = last.split(":", 1)[0].split(".")[-1]
    function = ""
    for line in lines:
        found = FRAME.match(line)
        if found and found.group("path").endswith(f"{name}.py"):
            function = found.group("function")
    return {"error": error, "function": function}


shutil.rmtree("__pycache__", ignore_errors=True)

facts = run_json(PROBE)
given = run_json(ANSWERS_PROBE)

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


label = "Το dispatch.py τρέχει ως το τέλος και τυπώνει τις σωστές γραμμές"
run = subprocess.run(
    [sys.executable, "-B", "dispatch.py"], capture_output=True, text=True, stdin=subprocess.DEVNULL
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

label = "Η shipping_for παίρνει κωδικό πελάτη και δίνει τα μεταφορικά της πόλης του"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif "shipping_error" in facts:
    report(False, label, str(facts["shipping_error"]))
elif facts["shipping"] != EXPECTED_SHIPPING:
    report(False, label, f"περίμενα {EXPECTED_SHIPPING} και πήρα {facts['shipping']}")
else:
    report(True, label)

label = "Η line_for δίνει το σύνολο της παραγγελίας μαζί με τα μεταφορικά"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif "lines_error" in facts:
    report(False, label, str(facts["lines_error"]))
elif facts["lines"] != EXPECTED_LINES:
    report(False, label, f"περίμενα {EXPECTED_LINES} και πήρα {facts['lines']}")
else:
    report(True, label)

for name in ["case1", "case2", "case3"]:
    label = f"Το {name} είναι διαγνωσμένο σωστά στο diagnosis.py"
    crash = crash_of(name)
    if "import_error" in given:
        report(False, label, str(given["import_error"]))
        continue
    if "no_crash" in crash:
        report(False, label, f"το {name}.py {crash['no_crash']}, ξαναφέρ' το όπως ήταν")
        continue
    answers = given.get("answers", {})
    written = answers.get(name) if isinstance(answers, dict) else None
    if not isinstance(written, list) or len(written) != 2:
        report(False, label, "λείπει η απάντηση από το ANSWERS")
        continue
    error_written = written[0].strip().split(".")[-1]
    function_written = written[1].strip()
    if error_written != crash["error"]:
        report(False, label, f"το σφάλμα είναι {crash['error']} και έγραψες {written[0]!r}")
    elif function_written != crash["function"]:
        report(False, label, f"το τελευταίο δικό σου πλαίσιο είναι η {crash['function']} και έγραψες {written[1]!r}")
    else:
        report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
