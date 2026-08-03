"""Οι έλεγχοι του lab. Τρέξε: python3 checks.py"""

import contextlib
import importlib.util
import io
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent
ORDER_LINE = "ΚΩΔ-4471;Καφετιέρα;;41.60"


def load_orders() -> tuple[ModuleType | None, str]:
    path = ROOT / "orders.py"
    if not path.exists():
        return None, "δεν υπάρχει αρχείο orders.py"
    spec = importlib.util.spec_from_file_location("orders", path)
    if spec is None or spec.loader is None:
        return None, "το orders.py δεν φορτώνεται"
    module = importlib.util.module_from_spec(spec)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
    except SyntaxError as error:
        return None, f"SyntaxError στη γραμμή {error.lineno}"
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"
    return module, ""


def check_interpreter() -> tuple[bool, str]:
    major, minor = sys.version_info[:2]
    if (major, minor) == (3, 11):
        return True, ""
    return False, f"βρήκα {major}.{minor}"


def check_orders_compiles(orders: ModuleType | None, reason: str) -> tuple[bool, str]:
    if orders is None:
        return False, reason
    return True, ""


def check_line_total(orders: ModuleType | None, reason: str) -> tuple[bool, str]:
    if orders is None:
        return False, reason
    function = getattr(orders, "line_total", None)
    if function is None:
        return False, "δεν βρήκα συνάρτηση line_total"
    try:
        result = function(ORDER_LINE, 3.50)
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"
    if result == 45.1:
        return True, ""
    return False, f"επέστρεψε {result!r}"


def check_return_hint(orders: ModuleType | None, reason: str) -> tuple[bool, str]:
    if orders is None:
        return False, reason
    function = getattr(orders, "line_total", None)
    if function is None:
        return False, "δεν βρήκα συνάρτηση line_total"
    hint = getattr(function, "__annotations__", {}).get("return")
    if hint is float:
        return True, ""
    name = getattr(hint, "__name__", repr(hint))
    return False, f"το hint λέει {name}"


def check_discount() -> tuple[bool, str]:
    path = ROOT / "discount.py"
    if not path.exists():
        return False, "δεν υπάρχει αρχείο discount.py"
    finished = subprocess.run(
        [sys.executable, str(path)], capture_output=True, text=True
    )
    if finished.returncode != 0:
        last_line = finished.stderr.strip().splitlines()[-1:]
        return False, last_line[0] if last_line else "τερμάτισε με σφάλμα"
    lines = finished.stdout.strip().splitlines()
    if lines == ["3.33", "38.27"]:
        return True, ""
    return False, f"τύπωσε {lines}"


def main() -> None:
    orders, reason = load_orders()
    results = [
        ("Ο interpreter είναι Python 3.11", check_interpreter()),
        ("Το orders.py μεταφράζεται χωρίς SyntaxError", check_orders_compiles(orders, reason)),
        ("Η line_total επιστρέφει 45.1", check_line_total(orders, reason)),
        ("Το type hint επιστροφής της line_total είναι float", check_return_hint(orders, reason)),
        ("Το discount.py τυπώνει 3.33 και 38.27", check_discount()),
    ]
    passed = 0
    for label, (ok, detail) in results:
        if ok:
            passed += 1
            print(f"✅ {label}")
        else:
            print(f"❌ {label} ({detail})")
    print()
    print(f"{passed}/{len(results)}")


if __name__ == "__main__":
    main()
