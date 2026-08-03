import ast
import contextlib
import importlib.util
import io
import subprocess
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent

EXPECTED_FULL = [
    "ΠΑΡ-8814: αξία 56.16 + μεταφορικά 0.00 + ΦΠΑ 13.48 = 69.64",
    "ΠΑΡ-8815: αξία 38.00 + μεταφορικά 6.40 + ΦΠΑ 10.66 = 55.06",
    "ΠΑΡ-8816: αξία 90.00 + μεταφορικά 0.00 + ΦΠΑ 21.60 = 111.60",
    "ΠΑΡ-8817: αξία 24.00 + μεταφορικά 3.90 + ΦΠΑ 6.70 = 34.60",
    "ΠΑΡ-8818: αξία 63.00 + μεταφορικά 2.50 + ΦΠΑ 15.72 = 81.22",
    "ΠΑΡ-8819: αξία 18.00 + μεταφορικά 6.40 + ΦΠΑ 5.86 = 30.26",
    "ΠΑΡ-8822: αξία 52.00 + μεταφορικά 0.00 + ΦΠΑ 12.48 = 64.48",
    "ΠΑΡ-8820: απορρίφθηκε, λείπει η αξία",
    "ΠΑΡ-8821: απορρίφθηκε, λάθος πλήθος πεδίων",
    "Παραγγελίες: 7",
    "Αξία: 341.16",
    "Πληρωτέο: 446.86",
    "Προς νησιά: ΠΑΡ-8815, ΠΑΡ-8818, ΠΑΡ-8819",
    "Μεγαλύτερη: ΠΑΡ-8816 με 111.60",
]

EXPECTED_SMALL = [
    "ΠΑΡ-8814: αξία 56.16 + μεταφορικά 0.00 + ΦΠΑ 13.48 = 69.64",
    "ΠΑΡ-8817: αξία 24.00 + μεταφορικά 3.90 + ΦΠΑ 6.70 = 34.60",
    "ΠΑΡ-8820: απορρίφθηκε, λείπει η αξία",
    "Παραγγελίες: 2",
    "Αξία: 80.16",
    "Πληρωτέο: 104.24",
    "Προς νησιά: καμία",
    "Μεγαλύτερη: ΠΑΡ-8814 με 69.64",
]


def run(data_file: str) -> tuple[int, list[str]]:
    path = HERE / "report.py"
    if not path.exists():
        return 1, ["δεν βρέθηκε αρχείο report.py"]
    text = (HERE / data_file).read_text(encoding="utf-8")
    finished = subprocess.run(
        [sys.executable, str(path)],
        input=text,
        capture_output=True,
        text=True,
    )
    return finished.returncode, finished.stdout.splitlines()


def first_difference(found: list[str], expected: list[str]) -> str:
    for index in range(max(len(found), len(expected))):
        mine = found[index] if index < len(found) else "<λείπει>"
        theirs = expected[index] if index < len(expected) else "<περισσεύει>"
        if mine != theirs:
            return f"γραμμή {index + 1}: περίμενα {theirs!r}, βρήκα {mine!r}"
    return ""


def load_report() -> tuple[ModuleType | None, str]:
    path = HERE / "report.py"
    if not path.exists():
        return None, "δεν βρέθηκε αρχείο report.py"
    spec = importlib.util.spec_from_file_location("report", path)
    if spec is None or spec.loader is None:
        return None, "το report.py δεν φορτώνεται"
    module = importlib.util.module_from_spec(spec)
    feed = (HERE / "orders-small.txt").read_text(encoding="utf-8")
    original_stdin = sys.stdin
    sys.stdin = io.StringIO(feed)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"
    finally:
        sys.stdin = original_stdin
    return module, ""


def tree() -> ast.Module | None:
    path = HERE / "report.py"
    if not path.exists():
        return None
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return None


def functions(node: ast.Module) -> list[ast.FunctionDef]:
    return [item for item in node.body if isinstance(item, ast.FunctionDef)]


def top_level_lines(node: ast.Module) -> int:
    counted = 0
    for item in node.body:
        if isinstance(item, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
            continue
        if isinstance(item, ast.Assign) and all(
            isinstance(target, ast.Name) and target.id.isupper() for target in item.targets
        ):
            continue
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
            continue
        counted += (item.end_lineno or item.lineno) - item.lineno + 1
    return counted


results: list[tuple[bool, str, str]] = []


def check(ok: bool, title: str, detail: str = "") -> None:
    results.append((ok, title, detail))


def call(module: ModuleType | None, name: str, *args: object) -> tuple[bool, object, str]:
    if module is None:
        return False, None, "το report.py δεν φορτώνεται"
    function = getattr(module, name, None)
    if function is None:
        return False, None, f"δεν βρήκα συνάρτηση {name}"
    try:
        with contextlib.redirect_stdout(io.StringIO()) as sink:
            value = function(*args)
    except Exception as error:
        return False, None, f"{type(error).__name__}: {error}"
    return True, value, sink.getvalue()


full_code, full = run("orders.txt")
small_code, small = run("orders-small.txt")

check(
    full_code == 0 and small_code == 0,
    "Το report.py τρέχει χωρίς σφάλμα και με τα δύο αρχεία",
    f"κωδικοί εξόδου: {full_code} και {small_code}",
)

difference = first_difference(full, EXPECTED_FULL) or first_difference(small, EXPECTED_SMALL)
check(
    not difference,
    "Η έξοδος είναι ίδια με την αρχική, γραμμή προς γραμμή",
    difference,
)

report, load_error = load_report()

coupons = {"KALOKAIRI10": 0.10, "BLACKFRIDAY25": 0.25, "WELCOME5": 0.05, "": 0.0, "ΑΝΟΙΞΗ20": 0.0}
coupon_ok = True
coupon_detail = ""
for code, expected in coupons.items():
    called, value, extra = call(report, "coupon_discount", code)
    if not called or value != expected:
        coupon_ok = False
        coupon_detail = extra if not called else f"για {code!r} περίμενα {expected}, βρήκα {value!r}"
        break
check(coupon_ok, "Η coupon_discount επιστρέφει το ποσοστό κάθε κουπονιού", coupon_detail)

island_ok = True
island_detail = ""
for postal, expected in (("84600", True), ("85300", True), ("15232", False), ("54622", False)):
    called, value, extra = call(report, "is_island", postal)
    if not called or value is not expected:
        island_ok = False
        island_detail = extra if not called else f"για {postal} περίμενα {expected}, βρήκα {value!r}"
        break
check(island_ok, "Η is_island ξεχωρίζει τα νησιά από την ηπειρωτική Ελλάδα", island_detail)

shipping_cases = [
    ((24.00, False, "11527"), 3.90),
    ((63.00, True, "11527"), 0.00),
    ((38.00, False, "84600"), 6.40),
    ((63.00, True, "85300"), 2.50),
]
shipping_ok = True
shipping_detail = ""
for args, expected in shipping_cases:
    called, value, extra = call(report, "shipping_cost", *args)
    if not called or round(float(value), 2) != expected:
        shipping_ok = False
        shipping_detail = extra if not called else f"για {args} περίμενα {expected}, βρήκα {value!r}"
        break
check(shipping_ok, "Η shipping_cost χρεώνει σωστά και τις τέσσερις περιπτώσεις", shipping_detail)

vat_ok = True
vat_detail = ""
for taxable, expected in ((100.00, 24.00), (56.16, 13.48)):
    called, value, extra = call(report, "vat_amount", taxable)
    if not called or round(float(value), 2) != expected:
        vat_ok = False
        vat_detail = extra if not called else f"για {taxable} περίμενα {expected}, βρήκα {value!r}"
        break
check(vat_ok, "Η vat_amount επιστρέφει τον ΦΠΑ στρογγυλοποιημένο στο λεπτό", vat_detail)

called, value, extra = call(report, "order_total", 56.16, 0.00, 13.48)
check(
    called and round(float(value), 2) == 69.64,
    "Η order_total επιστρέφει το σύνολο μιας παραγγελίας",
    extra if not called else f"περίμενα 69.64, βρήκα {value!r}",
)

expected_line = "ΠΑΡ-8815: αξία 38.00 + μεταφορικά 6.40 + ΦΠΑ 10.66 = 55.06"
called, value, printed = call(report, "order_line", "ΠΑΡ-8815", 38.00, 6.40, 10.66)
if not called:
    check(False, "Η order_line επιστρέφει τη γραμμή αντί να την τυπώνει", printed)
elif printed:
    check(False, "Η order_line επιστρέφει τη γραμμή αντί να την τυπώνει", "τύπωσε στην οθόνη αντί να επιστρέψει")
else:
    check(
        value == expected_line,
        "Η order_line επιστρέφει τη γραμμή αντί να την τυπώνει",
        f"περίμενα {expected_line!r}, βρήκα {value!r}",
    )

parsed = tree()
defined = functions(parsed) if parsed else []
check(
    len(defined) >= 8,
    "Το report.py ορίζει τουλάχιστον 8 συναρτήσεις",
    f"βρήκα {len(defined)}",
)

longest = max(
    (((item.end_lineno or item.lineno) - item.lineno + 1, item.name) for item in defined),
    default=(0, ""),
)
check(
    bool(defined) and longest[0] <= 20,
    "Καμία συνάρτηση δεν ξεπερνάει τις 20 γραμμές",
    "δεν βρήκα καμία συνάρτηση" if not defined else f"η {longest[1]} έχει {longest[0]} γραμμές",
)

body_lines = top_level_lines(parsed) if parsed else -1
check(
    0 <= body_lines <= 10,
    "Το σώμα στο αριστερό περιθώριο δεν ξεπερνάει τις 10 γραμμές",
    f"βρήκα {body_lines} γραμμές",
)

passed = 0
for ok, title, detail in results:
    if ok:
        passed += 1
        print(f"✅ {title}")
    else:
        print(f"❌ {title} - {detail}")

print()
print(f"{passed}/{len(results)}")
