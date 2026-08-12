import ast
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
        import orders
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

FIX_ITEMS = [
    {"product": "Ζυγαριά", "category": "Οικιακά", "qty": "2", "price": "18.50"},
    {"product": "Θερμός", "category": "Οικιακά", "qty": "1", "price": "24.90"},
    {"product": "Πολύπριζο", "category": "Ηλεκτρονικά", "qty": "4", "price": "6.20"},
]

FIX_ORDERS = {
    "ΠΑΡ-1": [
        {"product": "Ζυγαριά", "category": "Οικιακά", "qty": "2", "price": "18.50"},
        {"product": "Οθόνη", "category": "Ηλεκτρονικά", "qty": "1", "price": "189.00"},
    ],
    "ΠΑΡ-2": [
        {"product": "Θερμός", "category": "Οικιακά", "qty": "1", "price": "24.90"},
        {"product": "Πολύπριζο", "category": "Ηλεκτρονικά", "qty": "4", "price": "6.20"},
    ],
}

answer = {}
printed = io.StringIO()

with contextlib.redirect_stdout(printed):
    try:
        answer["total"] = orders.order_total(FIX_ITEMS)
    except Exception as exc:
        answer["total_error"] = f"{type(exc).__name__}: {exc}"

    try:
        answer["names"] = orders.product_names(FIX_ITEMS)
    except Exception as exc:
        answer["names_error"] = f"{type(exc).__name__}: {exc}"

    try:
        answer["labels"] = orders.cheap_labels(FIX_ORDERS)
    except Exception as exc:
        answer["labels_error"] = f"{type(exc).__name__}: {exc}"

    try:
        sold = orders.products_per_category(FIX_ORDERS)
        answer["sold_type"] = type(sold).__name__
        answer["sold"] = {key: value for key, value in sold.items()}
        answer["sold_all_lists"] = all(isinstance(value, list) for value in sold.values())
    except Exception as exc:
        answer["sold_error"] = f"{type(exc).__name__}: {exc}"

answer["printed"] = printed.getvalue()
print(json.dumps(answer, ensure_ascii=False))
'''

EXPECTED_TOTAL = 86.7
EXPECTED_NAMES = ["Ζυγαριά", "Θερμός", "Πολύπριζο"]
EXPECTED_LABELS = ["Ζυγαριά (πολλά)", "Θερμός (ένα)", "Πολύπριζο (πολλά)"]
EXPECTED_SOLD = {
    "Οικιακά": ["Ζυγαριά", "Θερμός"],
    "Ηλεκτρονικά": ["Οθόνη", "Πολύπριζο"],
}

EXPECTED_OUTPUT = [
    "ΠΑΡΑΓΓΕΛΙΕΣ",
    "ΠΑΡ-8814 - Μαρία Ιωάννου (Θεσσαλονίκη): 70.80 ευρώ",
    "Καφετιέρα, Φίλτρα καφέ",
    "ΠΑΡ-8815 - Νίκος Παπαδάκης (Λάρισα): 129.00 ευρώ",
    "Ακουστικά",
    "ΠΑΡ-8816 - Ελένη Βασιλείου (Θεσσαλονίκη): 79.30 ευρώ",
    "Τοστιέρα, Θήκη κινητού, Φίλτρα καφέ",
    "ΕΤΙΚΕΤΕΣ ΚΑΤΩ ΑΠΟ 100 ΕΥΡΩ",
    "Καφετιέρα (ένα)",
    "Φίλτρα καφέ (πολλά)",
    "Τοστιέρα (ένα)",
    "Θήκη κινητού (πολλά)",
    "Φίλτρα καφέ (πολλά)",
    "ΠΡΟΪΟΝΤΑ ΑΝΑ ΚΑΤΗΓΟΡΙΑ",
    "Ηλεκτρονικά: Ακουστικά, Θήκη κινητού",
    "Οικιακά: Καφετιέρα, Φίλτρα καφέ, Τοστιέρα, Φίλτρα καφέ",
]

COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)

probe = subprocess.run([sys.executable, "-c", PROBE], capture_output=True, text=True)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    detail = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"
    facts = {"import_error": detail}

try:
    with open("orders.py", encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    syntax_error = ""
except SyntaxError as exc:
    tree = None
    syntax_error = f"SyntaxError: {exc}"

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def find_function(name: str) -> ast.FunctionDef | None:
    if tree is None:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def nested_comprehensions() -> list[int]:
    if tree is None:
        return []
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, COMPREHENSIONS) and len(node.generators) > 1:
            lines.append(node.lineno)
    return lines


label = "Η order_total αθροίζει όλες τις γραμμές της παραγγελίας"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "total_error" in facts:
    report(False, label, facts["total_error"])
elif facts["total"] != EXPECTED_TOTAL:
    report(False, label, f"περίμενα {EXPECTED_TOTAL} και πήρα {facts['total']}")
else:
    report(True, label)

label = "Η product_names είναι ένα return με comprehension ενός επιπέδου"
node = find_function("product_names")
body = [] if node is None else [stmt for stmt in node.body if not isinstance(stmt, ast.Expr)]
if syntax_error:
    report(False, label, syntax_error)
elif node is None:
    report(False, label, "δεν βρήκα συνάρτηση product_names στο orders.py")
elif "import_error" in facts:
    report(False, label, facts["import_error"])
elif "names_error" in facts:
    report(False, label, facts["names_error"])
elif facts["names"] != EXPECTED_NAMES:
    report(False, label, f"περίμενα {EXPECTED_NAMES} και πήρα {facts['names']}")
elif len(body) != 1 or not isinstance(body[0], ast.Return):
    report(False, label, f"το σώμα της έχει {len(body)} εντολές αντί για ένα return")
elif not isinstance(body[0].value, ast.ListComp):
    report(False, label, "το return δεν επιστρέφει comprehension")
elif len(body[0].value.generators) != 1:
    report(False, label, "το comprehension έχει παραπάνω από ένα for")
else:
    report(True, label)

label = "Η cheap_labels δίνει τις σωστές ετικέτες με τη σειρά τους"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "labels_error" in facts:
    report(False, label, facts["labels_error"])
elif facts["labels"] != EXPECTED_LABELS:
    report(False, label, f"περίμενα {EXPECTED_LABELS} και πήρα {facts['labels']}")
else:
    report(True, label)

label = "Κανένα comprehension του orders.py δεν έχει δύο for"
if syntax_error:
    report(False, label, syntax_error)
else:
    offenders = nested_comprehensions()
    if offenders:
        report(False, label, f"στις γραμμές {offenders}")
    else:
        report(True, label)

label = "Η products_per_category δίνει λίστα προϊόντων ανά κατηγορία"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif "sold_error" in facts:
    report(False, label, facts["sold_error"])
elif facts["sold_type"] != "dict":
    report(False, label, f"επέστρεψε {facts['sold_type']} και όχι dict")
elif not facts["sold_all_lists"]:
    report(False, label, f"οι τιμές του δεν είναι λίστες: {facts['sold']}")
elif facts["sold"] != EXPECTED_SOLD:
    report(False, label, f"περίμενα {EXPECTED_SOLD} και πήρα {facts['sold']}")
else:
    report(True, label)

label = "Το orders.py τυπώνει τα σωστά σύνολα και τις σωστές κατηγορίες"
run = subprocess.run([sys.executable, "orders.py"], capture_output=True, text=True)
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
