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
        import picking
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

order = ["φίλτρα", "καφετιέρα"]
printed = io.StringIO()
try:
    with contextlib.redirect_stdout(printed):
        first = picking.picking_list(order, True)
        second = picking.picking_list(order, True)
    answer["first"] = first
    answer["second"] = second
    answer["order_after"] = order
    answer["printed"] = printed.getvalue()
except Exception as exc:
    answer["error"] = f"{type(exc).__name__}: {exc}"

print(json.dumps(answer, ensure_ascii=False))
'''

PICKING_BLOCKS = [
    ("ΠΑΡ-3301: 3 προς συλλογή", ["καφετιέρα", "κουτί δώρου", "φίλτρα"]),
    ("ΠΑΡ-3301 (επανεκτύπωση): 3 προς συλλογή", ["καφετιέρα", "κουτί δώρου", "φίλτρα"]),
    (
        "ΠΑΡ-3302: 4 προς συλλογή",
        ["βραστήρας", "ζυγαριά κουζίνας", "θερμός", "τοστιέρα"],
    ),
    ("ΠΑΡ-3303: 3 προς συλλογή", ["κουτί δώρου", "μύλος καφέ", "ταψί"]),
]

NOTE_BLOCKS = [
    ("ΠΑΡ-3301: 2 προϊόντα", ["καφετιέρα", "φίλτρα"]),
    (
        "ΠΑΡ-3302: 4 προϊόντα",
        ["ζυγαριά κουζίνας", "βραστήρας", "θερμός", "τοστιέρα"],
    ),
    ("ΠΑΡ-3303: 2 προϊόντα", ["μύλος καφέ", "ταψί"]),
]

WARNING = "Προσοχή: παραγγελία με πάνω από 3 αντικείμενα, χρειάζεται δεύτερο άτομο"

FIRST_PICK = ["καφετιέρα", "κουτί δώρου", "φίλτρα"]


def blocks(lines: list[str], marker: str, bullet: str) -> list[tuple[str, list[str]]]:
    found: list[tuple[str, list[str]]] = []
    for line in lines:
        if marker in line:
            found.append((line, []))
        elif line.startswith(bullet) and found:
            found[-1][1].append(line[len(bullet):].strip())
    return found


run = subprocess.run([sys.executable, "picking.py"], capture_output=True, text=True)
crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ""
output = [line.strip() for line in run.stdout.splitlines() if line.strip()]

probe = subprocess.run([sys.executable, "-c", PROBE], capture_output=True, text=True)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    detail = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"
    facts = {"import_error": detail}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


label = "Η picking_list φτιάχνει καινούρια λίστα και αφήνει την παραγγελία άθικτη"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "error" in facts:
    report(False, label, facts["error"])
elif facts["first"] != FIRST_PICK:
    report(False, label, f"η πρώτη κλήση επέστρεψε {facts['first']}")
elif facts["second"] != FIRST_PICK:
    report(False, label, f"η δεύτερη κλήση επέστρεψε {facts['second']}")
elif facts["order_after"] != ["φίλτρα", "καφετιέρα"]:
    report(False, label, f"η παραγγελία έγινε {facts['order_after']}")
elif facts["printed"]:
    report(False, label, f"η picking_list τύπωσε {facts['printed']!r}")
else:
    report(True, label)

label = "Οι τέσσερις λίστες συλλογής είναι σωστές και η επανεκτύπωση βγαίνει ίδια"
if crash:
    report(False, label, crash)
else:
    found = blocks(output, "προς συλλογή", "-")
    if found == PICKING_BLOCKS:
        report(True, label)
    else:
        report(False, label, f"βρήκα {found}")

label = "Τα δελτία αποστολής δείχνουν ό,τι παρήγγειλε ο πελάτης, με τη σειρά του"
if crash:
    report(False, label, crash)
else:
    found = blocks(output, "προϊόντα", "*")
    if found == NOTE_BLOCKS:
        report(True, label)
    else:
        report(False, label, f"βρήκα {found}")

label = "Η προειδοποίηση για δεύτερο άτομο τυπώνεται"
if crash:
    report(False, label, crash)
elif WARNING in output:
    report(True, label)
else:
    report(False, label, "καμία γραμμή με την προειδοποίηση")

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
