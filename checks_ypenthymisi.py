import ast
import os
import shutil
import subprocess
import sys
import tempfile

MODULE = "ypenthymisi.py"
TESTS = "test_ypenthymisi.py"
LOG = "apestalmena.log"
MIN_TESTS = 3
PROTECTED = {"message_for", "remind_overdue", "LOG"}

HEAD = '''LOG = "apestalmena.log"


def send_sms(phone: str, text: str) -> None:
    with open(LOG, "a", encoding="utf-8") as log:
        log.write(f"{phone}\\t{text}\\n")


def message_for(invoice: dict) -> str:
    return (
        f"Το τιμολόγιο {invoice['number']} των {invoice['amount']:.2f} ευρώ "
        f"έληξε στις {invoice['due']}."
    )


'''

CORRECT = HEAD + '''def remind_overdue(invoices: list[dict], today: str) -> int:
    sent = 0
    for invoice in invoices:
        if invoice["paid"]:
            continue
        if invoice["due"] < today:
            send_sms(invoice["phone"], message_for(invoice))
            sent += 1
    return sent
'''

REMINDS_THE_PAID = HEAD + '''def remind_overdue(invoices: list[dict], today: str) -> int:
    sent = 0
    for invoice in invoices:
        if invoice["due"] < today:
            send_sms(invoice["phone"], message_for(invoice))
            sent += 1
    return sent
'''

REMINDS_NOBODY = HEAD + '''def remind_overdue(invoices: list[dict], today: str) -> int:
    return 0
'''

PROBE = '''import ypenthymisi

sent = []
ypenthymisi.send_sms = lambda phone, text: sent.append(phone)

INVOICES = [
    {"number": "ΤΔΑ-1041", "amount": 248.00, "due": "2026-03-10", "phone": "6971234567", "paid": False},
    {"number": "ΤΔΑ-1042", "amount": 96.50, "due": "2026-03-18", "phone": "6944556677", "paid": True},
    {"number": "ΤΔΑ-1043", "amount": 512.40, "due": "2026-03-25", "phone": "6988112233", "paid": False},
    {"number": "ΤΔΑ-1044", "amount": 74.00, "due": "2026-04-10", "phone": "6900111222", "paid": False},
]

print(ypenthymisi.remind_overdue(INVOICES, "2026-04-01"))
print(",".join(sent))
sent.clear()
print(ypenthymisi.remind_overdue(INVOICES, "2026-03-01"))
'''
EXPECTED = ["2", "6971234567,6988112233", "0"]

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def pytest_works() -> bool:
    try:
        done = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return done.returncode == 0


if not pytest_works():
    print("Δεν βρίσκω το pytest σε αυτό το περιβάλλον. Τρέξε: pip install pytest")
    sys.exit(1)

if not os.path.exists(TESTS):
    print(f"Δεν βρίσκω το {TESTS} στη ρίζα του project.")
    sys.exit(1)

with open(TESTS, encoding="utf-8") as handle:
    source = handle.read()

try:
    tree = ast.parse(source)
except SyntaxError as error:
    print(f"Το {TESTS} δεν είναι έγκυρη Python: {error}")
    sys.exit(1)

test_functions = [
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
]


def run_probe() -> tuple[list[str], str]:
    done = subprocess.run(
        [sys.executable, "-B", "-c", PROBE],
        capture_output=True,
        text=True,
        cwd=".",
    )
    if done.returncode != 0:
        tail = done.stderr.strip().splitlines()
        return [], tail[-1] if tail else f"το {MODULE} δεν τρέχει"
    return done.stdout.strip().split("\n"), ""


label = "Η υπενθύμιση δεν φεύγει για τιμολόγιο που έχει ήδη πληρωθεί"
values, error = run_probe()
if error:
    report(False, label, error)
elif values != EXPECTED:
    report(False, label, f"περίμενα {EXPECTED} και πήρα {values}")
else:
    report(True, label)


def run_suite(body: str) -> tuple[int, bool]:
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, MODULE), "w", encoding="utf-8") as target:
            target.write(body)
        shutil.copy(TESTS, os.path.join(folder, TESTS))
        if os.path.exists("conftest.py"):
            shutil.copy("conftest.py", os.path.join(folder, "conftest.py"))
        done = subprocess.run(
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"],
            capture_output=True,
            text=True,
            cwd=folder,
        )
        return done.returncode, os.path.exists(os.path.join(folder, LOG))


good, touched = run_suite(CORRECT)

label = f"Ολόκληρο το suite τρέχει χωρίς να γράψει γραμμή στο {LOG}"
if len(test_functions) < MIN_TESTS:
    report(False, label, f"βρήκα {len(test_functions)} tests και θέλω {MIN_TESTS}")
elif good != 0:
    report(False, label, f"στη σωστή υλοποίηση το pytest τερμάτισε με {good}")
elif touched:
    report(False, label, "κάποιο test έφτασε στον πάροχο")
else:
    report(True, label)

label = "Το μόνο όνομα που αντικαθιστούν τα tests είναι το send_sms"
taken = sorted(
    {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value in PROTECTED
    }
)
if taken:
    report(False, label, f"κάποιο test αντικαθιστά και το {taken[0]}")
else:
    report(True, label)

label = "Το suite κοκκινίζει όταν η υπενθύμιση φεύγει και για τα πληρωμένα"
paid, _ = run_suite(REMINDS_THE_PAID)
if good != 0:
    report(False, label, f"στη σωστή υλοποίηση το pytest τερμάτισε με {good}")
elif paid != 1:
    report(False, label, "με υπενθύμιση και στα πληρωμένα, το suite έμεινε πράσινο")
else:
    report(True, label)

label = "Το suite κοκκινίζει όταν δεν φεύγει καμία υπενθύμιση"
silent, _ = run_suite(REMINDS_NOBODY)
if good != 0:
    report(False, label, f"στη σωστή υλοποίηση το pytest τερμάτισε με {good}")
elif silent != 1:
    report(False, label, "με μηδέν υπενθυμίσεις, το suite έμεινε πράσινο")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
