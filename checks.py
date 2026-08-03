"""Ο μόνος βαθμολογητής του lab. Τρέξε: python3 checks.py"""

import contextlib
import importlib.util
import io
import os
import time
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
os.chdir(HERE)

FUNCTION_SECONDS = 3.0
PROGRAM_SECONDS = 5.0

SALES_LINES = 50_000
PRODUCT_LINES = 4_000
SALES_FIRST = "ΠΑΡ-000001;2024-03-08;322313699;ΠΡ-3839;5;231.40;"
SALES_LAST = "ΠΑΡ-050000;2024-07-21;293179353;ΠΡ-3462;1;70.98;XMAS20"
PRODUCTS_FIRST = "ΠΡ-0001;Ένδυση"
PRODUCTS_LAST = "ΠΡ-4000;Ηλεκτρονικά"

CATEGORY_SAMPLES = {
    "ΠΡ-0001": "Ένδυση",
    "ΠΡ-0500": "Καθαριστικά",
    "ΠΡ-2603": "Καθαριστικά",
    "ΠΡ-4000": "Ηλεκτρονικά",
}

EXPECTED_REVENUE = {
    "Βιβλία": 6025014.77,
    "Ένδυση": 5953285.07,
    "Ηλεκτρονικά": 6438376.71,
    "Καθαριστικά": 6146680.08,
    "Παιχνίδια": 5525501.29,
    "Τρόφιμα": 6008336.09,
}

EXPECTED_CUSTOMERS = 28_662

EXPECTED_TOP = [
    ("ΠΡ-2717", 23271.75),
    ("ΠΡ-0904", 20964.04),
    ("ΠΡ-2871", 20771.05),
    ("ΠΡ-3487", 20472.63),
    ("ΠΡ-3262", 20330.51),
    ("ΠΡ-3730", 19868.88),
    ("ΠΡ-2055", 19554.59),
    ("ΠΡ-0571", 19450.02),
    ("ΠΡ-3438", 19378.04),
    ("ΠΡ-2242", 19177.38),
]

EXPECTED_COUPONS = ["PASXA15", "WELCOME5", "BLACKFRIDAY25", "KALOKAIRI10", "XMAS20"]

results: list[tuple[bool, str, str]] = []


def check(ok: bool, title: str, detail: str = "") -> None:
    results.append((ok, title, detail))


def read(path: str) -> list[str]:
    file = HERE / path
    if not file.exists():
        return []
    return [line.strip() for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]


sales_lines = read("sales.txt")
product_lines = read("products.txt")

data_detail = ""
if not sales_lines or not product_lines:
    data_detail = "λείπει το sales.txt ή το products.txt, τρέξε python3 make_data.py"
elif len(sales_lines) != SALES_LINES or len(product_lines) != PRODUCT_LINES:
    data_detail = f"βρήκα {len(sales_lines)} και {len(product_lines)} γραμμές"
elif (
    sales_lines[0] != SALES_FIRST
    or sales_lines[-1] != SALES_LAST
    or product_lines[0] != PRODUCTS_FIRST
    or product_lines[-1] != PRODUCTS_LAST
):
    data_detail = "τα αρχεία δεν είναι αυτά που φτιάχνει το make_data.py, σβήσ' τα και ξανατρέξ' το"
check(not data_detail, "Τα δύο αρχεία δεδομένων υπάρχουν και είναι τα σωστά", data_detail)


def load_analyze() -> tuple[ModuleType | None, str, float]:
    path = HERE / "analyze.py"
    if not path.exists():
        return None, "δεν βρέθηκε αρχείο analyze.py", 0.0
    spec = importlib.util.spec_from_file_location("analyze", path)
    if spec is None or spec.loader is None:
        return None, "το analyze.py δεν φορτώνεται", 0.0
    module = importlib.util.module_from_spec(spec)
    start = time.perf_counter()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
    except Exception as error:
        return None, f"{type(error).__name__}: {error}", time.perf_counter() - start
    return module, "", time.perf_counter() - start


analyze, load_error, program_seconds = load_analyze()
check(analyze is not None, "Το analyze.py τρέχει από την αρχή ως το τέλος χωρίς σφάλμα", load_error)


def call(name: str, *args: object) -> tuple[bool, object, str]:
    if analyze is None:
        return False, None, "το analyze.py δεν φορτώνεται"
    function = getattr(analyze, name, None)
    if function is None:
        return False, None, f"δεν βρήκα συνάρτηση {name}"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            value = function(*args)
    except Exception as error:
        return False, None, f"{type(error).__name__}: {error}"
    return True, value, ""


def close(found: object, expected: float) -> bool:
    return isinstance(found, (int, float)) and abs(float(found) - expected) <= 0.01


function_start = time.perf_counter()

called, categories, detail = call("load_categories", product_lines)
category_title = "Η load_categories δίνει dictionary κωδικός προς κατηγορία"
if not called:
    check(False, category_title, detail)
elif not isinstance(categories, dict):
    check(False, category_title, f"επέστρεψε {type(categories).__name__} αντί για dictionary")
elif len(categories) != PRODUCT_LINES:
    check(False, category_title, f"βρήκα {len(categories)} κλειδιά αντί για {PRODUCT_LINES}")
else:
    wrong = [code for code, name in CATEGORY_SAMPLES.items() if categories.get(code) != name]
    check(
        not wrong,
        category_title,
        "" if not wrong else f"για {wrong[0]} περίμενα {CATEGORY_SAMPLES[wrong[0]]!r}, βρήκα {categories.get(wrong[0])!r}",
    )

lookup: dict[str, str]
if isinstance(categories, dict) and len(categories) == PRODUCT_LINES:
    lookup = dict(categories)
else:
    lookup = dict(line.split(";", 1) for line in product_lines)

revenue_title = "Η revenue_per_category δίνει τα σωστά έσοδα και για τις έξι κατηγορίες"
called, revenue, detail = call("revenue_per_category", sales_lines, lookup)
if not called:
    check(False, revenue_title, detail)
elif not isinstance(revenue, dict):
    check(False, revenue_title, f"επέστρεψε {type(revenue).__name__} αντί για dictionary")
else:
    problem = ""
    if set(revenue) != set(EXPECTED_REVENUE):
        problem = f"περίμενα τις κατηγορίες {sorted(EXPECTED_REVENUE)}, βρήκα {sorted(revenue)}"
    else:
        for name, expected in EXPECTED_REVENUE.items():
            if not close(revenue[name], expected):
                problem = f"για {name} περίμενα {expected}, βρήκα {revenue[name]!r}"
                break
    check(not problem, revenue_title, problem)

called, customers, detail = call("unique_customers", sales_lines)
check(
    called and customers == EXPECTED_CUSTOMERS,
    "Η unique_customers μετράει τα διαφορετικά ΑΦΜ",
    detail if not called else f"περίμενα {EXPECTED_CUSTOMERS}, βρήκα {customers!r}",
)

top_title = "Η top_products δίνει τα δέκα προϊόντα με τα μεγαλύτερα έσοδα, με σειρά"
called, top, detail = call("top_products", sales_lines, 10)
if not called:
    check(False, top_title, detail)
elif not isinstance(top, list) or len(top) != 10:
    check(False, top_title, f"περίμενα λίστα με 10 στοιχεία, βρήκα {top!r}"[:160])
else:
    problem = ""
    for position, (code, total) in enumerate(EXPECTED_TOP):
        item = top[position]
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            problem = f"στη θέση {position + 1} περίμενα ζευγάρι κωδικού και ποσού, βρήκα {item!r}"
            break
        if item[0] != code or not close(item[1], total):
            problem = f"στη θέση {position + 1} περίμενα {(code, total)}, βρήκα {tuple(item)!r}"
            break
    if not problem:
        called_three, three, _ = call("top_products", sales_lines, 3)
        if not called_three or not isinstance(three, list) or len(three) != 3:
            problem = f"με limit 3 περίμενα 3 στοιχεία, βρήκα {three!r}"[:160]
    check(not problem, top_title, problem)

called, coupons, detail = call("coupons_first_seen", sales_lines)
found_coupons = list(coupons) if isinstance(coupons, list) else coupons
check(
    called and found_coupons == EXPECTED_COUPONS,
    "Η coupons_first_seen δίνει τα κουπόνια με τη σειρά που πρωτοεμφανίστηκαν",
    detail if not called else f"περίμενα {EXPECTED_COUPONS}, βρήκα {found_coupons!r}",
)

function_seconds = time.perf_counter() - function_start
all_five_ran = all(ok for ok, title, _ in results if title.startswith("Η "))

check(
    all_five_ran and function_seconds < FUNCTION_SECONDS,
    f"Οι πέντε συναρτήσεις μαζί τελειώνουν σε λιγότερο από {FUNCTION_SECONDS:.0f} δευτερόλεπτα",
    f"έκαναν {function_seconds:.2f} δευτερόλεπτα" if all_five_ran else "δεν έτρεξαν σωστά και οι πέντε",
)

check(
    analyze is not None and program_seconds < PROGRAM_SECONDS,
    f"Ολόκληρο το analyze.py τελειώνει σε λιγότερο από {PROGRAM_SECONDS:.0f} δευτερόλεπτα",
    load_error if analyze is None else f"έκανε {program_seconds:.2f} δευτερόλεπτα",
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
