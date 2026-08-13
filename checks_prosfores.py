import ast
import os
import shutil
import subprocess
import sys
import tempfile

MODULE = "prosfores.py"
TESTS = "test_prosfores.py"
FIXTURE = "offers"
MIN_TESTS = 3
FUNCTIONS = {"final_price", "in_stock", "set_stock", "cheapest"}
DROPPED = {
    "test_final_price_is_a_number",
    "test_in_stock_returns_a_list",
    "test_the_feed_has_five_offers",
    "test_cheapest_returns_one_of_the_offers",
}

HEAD = '''def final_price(offer: dict) -> float:
    return round(offer["price"] + offer["shipping"], 2)


def in_stock(offers: list[dict]) -> list[dict]:
    return [offer for offer in offers if offer["stock"]]


'''

GOOD_STOCK = '''def set_stock(offers: list[dict], shop: str, value: bool) -> None:
    for offer in offers:
        if offer["shop"] == shop:
            offer["stock"] = value


'''

STALE_STOCK = '''def set_stock(offers: list[dict], shop: str, value: bool) -> None:
    for offer in offers:
        if offer["shop"] == shop:
            copy = dict(offer)
            copy["stock"] = value


'''

GOOD_CHEAPEST = '''def cheapest(offers: list[dict]) -> dict | None:
    candidates = in_stock(offers)
    if not candidates:
        return None
    return min(candidates, key=final_price)
'''

NO_SHIPPING = '''def cheapest(offers: list[dict]) -> dict | None:
    candidates = in_stock(offers)
    if not candidates:
        return None
    return min(candidates, key=lambda offer: offer["price"])
'''

CORRECT = HEAD + GOOD_STOCK + GOOD_CHEAPEST
IGNORES_SHIPPING = HEAD + GOOD_STOCK + NO_SHIPPING
FORGETS_STOCK = HEAD + STALE_STOCK + GOOD_CHEAPEST

EXTRA = """

from prosfores import in_stock as _in_stock
from prosfores import set_stock as _set_stock


def test_zz_checker_changes_the_offers(offers):
    _set_stock(offers, "Public", False)
    assert len(_in_stock(offers)) == 3


def test_zz_checker_wants_them_back(offers):
    assert len(_in_stock(offers)) == 4
"""

PROBE = (
    "import prosfores\n"
    'OFFERS = [\n'
    '    {"shop": "Πλαίσιο", "price": 78.00, "shipping": 6.00, "stock": True},\n'
    '    {"shop": "Public", "price": 80.90, "shipping": 0.00, "stock": True},\n'
    '    {"shop": "Κωτσόβολος", "price": 74.50, "shipping": 4.90, "stock": False},\n'
    '    {"shop": "Γερμανός", "price": 83.00, "shipping": 0.00, "stock": True},\n'
    '    {"shop": "e-shop.gr", "price": 79.90, "shipping": 3.50, "stock": True},\n'
    "]\n"
    'print(prosfores.cheapest(OFFERS)["shop"])\n'
    'prosfores.set_stock(OFFERS, "Public", False)\n'
    'print(prosfores.cheapest(OFFERS)["shop"])\n'
    "print(prosfores.cheapest([]))\n"
)
EXPECTED = ["Public", "Γερμανός", "None"]

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


def is_fixture(node: ast.expr) -> bool:
    if isinstance(node, ast.Call):
        node = node.func
    return isinstance(node, ast.Attribute) and node.attr == "fixture"


fixtures = [
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and any(is_fixture(decorator) for decorator in node.decorator_list)
]


def holds_an_offer(node: ast.AST) -> bool:
    for inner in ast.walk(node):
        if not isinstance(inner, ast.Dict):
            continue
        for key in inner.keys:
            if isinstance(key, ast.Constant) and key.value == "shop":
                return True
    return False


def run_pytest(folder: str) -> int:
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"],
        capture_output=True,
        text=True,
        cwd=folder,
    )
    return done.returncode


def suite_against(body: str, extra: str = "") -> int:
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, MODULE), "w", encoding="utf-8") as target:
            target.write(body)
        with open(os.path.join(folder, TESTS), "w", encoding="utf-8") as target:
            target.write(source + extra)
        if os.path.exists("conftest.py"):
            shutil.copy("conftest.py", os.path.join(folder, "conftest.py"))
        return run_pytest(folder)


label = "Οι προσφορές στήνονται σε fixture που δίνει φρέσκα δεδομένα σε κάθε test"
inline = [function.name for function in test_functions if holds_an_offer(function)]
module_data = [
    node
    for node in tree.body
    if isinstance(node, ast.Assign) and holds_an_offer(node)
]
names = [fixture.name for fixture in fixtures]
if FIXTURE not in names:
    report(False, label, f"δεν βρήκα fixture με όνομα {FIXTURE}")
elif inline:
    report(False, label, f"το {inline[0]} ξαναγράφει τις προσφορές μέσα του")
elif module_data:
    report(False, label, "οι προσφορές είναι σταθερά στην κορυφή του αρχείου")
elif suite_against(CORRECT, EXTRA) != 0:
    report(False, label, "το fixture δίνει τα ίδια δεδομένα σε δύο tests, όχι φρέσκα")
else:
    report(True, label)

label = "Κάθε test ελέγχει κανόνα, όχι τύπο ούτε τα ίδια τα δεδομένα"
left = [function.name for function in test_functions if function.name in DROPPED]
type_checks = [
    node
    for node in ast.walk(tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Name)
    and node.func.id == "isinstance"
]
silent = [
    function.name
    for function in test_functions
    if not any(
        isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS)
            or (isinstance(node.func, ast.Attribute) and node.func.attr in FUNCTIONS)
        )
        for node in ast.walk(function)
    )
]
if len(test_functions) < MIN_TESTS:
    report(False, label, f"βρήκα {len(test_functions)} tests και θέλω {MIN_TESTS}")
elif left:
    report(False, label, f"το {left[0]} είναι ακόμα εκεί")
elif type_checks:
    report(False, label, "υπάρχει ακόμα test που ελέγχει τύπο με isinstance")
elif silent:
    report(False, label, f"το {silent[0]} δεν καλεί τίποτα από το {MODULE}")
else:
    report(True, label)


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
    return done.stdout.split("\n")[:3], ""


label = "Το φθηνότερο κατάστημα βγαίνει με τα μεταφορικά μέσα"
values, error = run_probe()
if error:
    report(False, label, error)
elif values != EXPECTED:
    report(False, label, f"περίμενα {EXPECTED} και πήρα {values}")
else:
    report(True, label)

good = suite_against(CORRECT)

label = "Το suite κοκκινίζει όταν το cheapest διαλέγει χωρίς τα μεταφορικά"
blind = suite_against(IGNORES_SHIPPING)
if good != 0:
    report(False, label, f"στη σωστή υλοποίηση το pytest τερμάτισε με {good}")
elif blind != 1:
    report(False, label, "με το cheapest να κοιτάει σκέτη τιμή, το suite έμεινε πράσινο")
else:
    report(True, label)

label = "Το suite κοκκινίζει όταν το set_stock δεν αποθηκεύει τη νέα διαθεσιμότητα"
stale = suite_against(FORGETS_STOCK)
if good != 0:
    report(False, label, f"στη σωστή υλοποίηση το pytest τερμάτισε με {good}")
elif stale != 1:
    report(False, label, "με το set_stock να μην αλλάζει τίποτα, το suite έμεινε πράσινο")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
