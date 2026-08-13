import ast
import os
import shutil
import subprocess
import sys
import tempfile

MODULE = "timologio.py"
TESTS = "test_timologio.py"
MIN_TESTS = 3

HEAD = '''VAT_RATE = 0.24


def discounted_net(net: float, discount_pct: float) -> float:
    return round(net - net * discount_pct / 100, 2)


def invoice_total(net: float, discount_pct: float) -> float:
    after_discount = discounted_net(net, discount_pct)
'''

CORRECT = HEAD + """    vat = round(after_discount * VAT_RATE, 2)
    return round(after_discount + vat, 2)
"""

ON_GROSS = HEAD + """    vat = round(net * VAT_RATE, 2)
    return round(after_discount + vat, 2)
"""

PROBE = (
    "import timologio\n"
    "print(timologio.invoice_total(100.0, 10.0))\n"
    "print(timologio.invoice_total(80.0, 5.0))\n"
    "print(timologio.invoice_total(250.0, 20.0))\n"
)
EXPECTED = [111.6, 94.24, 248.0]

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


def is_number(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    )


def is_approx(node: ast.expr) -> bool:
    if not isinstance(node, ast.Call):
        return False
    named = isinstance(node.func, ast.Attribute) and node.func.attr == "approx"
    return named and len(node.args) == 1 and is_number(node.args[0])


def known_amount(node: ast.expr) -> bool:
    return is_number(node) or is_approx(node)


def bad_assert(node: ast.Assert) -> str:
    test = node.test
    if not isinstance(test, ast.Compare):
        return "υπάρχει assert που δεν συγκρίνει με τίποτα"
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return "υπάρχει assert που δεν συγκρίνει με =="
    if not known_amount(test.left) and not known_amount(test.comparators[0]):
        return "υπάρχει assert που δεν συγκρίνει με συγκεκριμένο ποσό"
    return ""


label = "Κάθε test συγκρίνει με == ένα συγκεκριμένο ποσό"
if len(test_functions) < MIN_TESTS:
    report(False, label, f"βρήκα {len(test_functions)} tests και θέλω {MIN_TESTS}")
else:
    problem = ""
    for function in test_functions:
        body = list(ast.walk(function))
        asserts = [node for node in body if isinstance(node, ast.Assert)]
        loose = [
            node
            for node in body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Compare)
        ]
        if loose:
            problem = f"το {function.name} έχει σύγκριση χωρίς assert μπροστά της"
            break
        if not asserts:
            problem = f"το {function.name} δεν έχει κανένα assert"
            break
        for node in asserts:
            trouble = bad_assert(node)
            if trouble:
                problem = f"στο {function.name} {trouble}"
                break
        if problem:
            break
    report(not problem, label, problem)

label = "Κανένα test δεν υπολογίζει μόνο του το ποσό που περιμένει"
problem = ""
for function in test_functions:
    for node in ast.walk(function):
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
        ):
            problem = f"το {function.name} κάνει πράξεις αντί να γράφει το ποσό"
            break
        if isinstance(node, ast.Name) and node.id == "VAT_RATE":
            problem = f"το {function.name} διαβάζει το VAT_RATE από τον κώδικα"
            break
        if isinstance(node, ast.Attribute) and node.attr == "VAT_RATE":
            problem = f"το {function.name} διαβάζει το VAT_RATE από τον κώδικα"
            break
    if problem:
        break
report(not problem, label, problem)


def run_probe() -> tuple[list[float], str]:
    done = subprocess.run(
        [sys.executable, "-B", "-c", PROBE],
        capture_output=True,
        text=True,
        cwd=".",
    )
    if done.returncode != 0:
        tail = done.stderr.strip().splitlines()
        return [], tail[-1] if tail else "το timologio.py δεν τρέχει"
    values: list[float] = []
    for line in done.stdout.split():
        try:
            values.append(float(line))
        except ValueError:
            return [], f"περίμενα αριθμούς και πήρα {line!r}"
    return values, ""


label = "Ο ΦΠΑ υπολογίζεται πάνω στην αξία μετά την έκπτωση"
values, error = run_probe()
if error:
    report(False, label, error)
elif values != EXPECTED:
    report(False, label, f"περίμενα {EXPECTED} και πήρα {values}")
else:
    report(True, label)


def pytest_in(folder: str) -> int:
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"],
        capture_output=True,
        text=True,
        cwd=folder,
    )
    return done.returncode


def suite_against(body: str) -> int:
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, MODULE), "w", encoding="utf-8") as target:
            target.write(body)
        shutil.copy(TESTS, os.path.join(folder, TESTS))
        if os.path.exists("conftest.py"):
            shutil.copy("conftest.py", os.path.join(folder, "conftest.py"))
        return pytest_in(folder)


label = "Το suite περνάει στη σωστή υλοποίηση και κοκκινίζει σε αυτήν που φορολογεί την αρχική αξία"
good = suite_against(CORRECT)
bad = suite_against(ON_GROSS)
if good != 0:
    report(False, label, f"στη σωστή υλοποίηση το pytest τερμάτισε με {good}")
elif bad != 1:
    report(False, label, "με τον ΦΠΑ πάνω στην αρχική αξία το suite δεν κοκκίνισε")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
