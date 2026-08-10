import ast
import pathlib
import subprocess
import sys

results: list[tuple[bool, str, str]] = []

proc = subprocess.run([sys.executable, "card.py"], capture_output=True, text=True)
lines = proc.stdout.strip().splitlines()
crash = proc.stderr.strip().splitlines()[-1] if proc.returncode != 0 and proc.stderr.strip() else ""
results.append((proc.returncode == 0, "Το card.py τρέχει χωρίς σφάλμα", crash or f"exit {proc.returncode}"))

source = pathlib.Path("card.py").read_text(encoding="utf-8")
tree = ast.parse(source)


def line_after(prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


phone_values = [
    node.value
    for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    for target in node.targets
    if isinstance(target, ast.Name) and target.id == "phone"
]
stays_none = len(phone_values) == 1 and isinstance(phone_values[0], ast.Constant) and phone_values[0].value is None
has_phone = line_after("Έχει τηλέφωνο:")
detail = f"πήρα {has_phone!r}" if stays_none else "το phone δεν είναι πια σκέτο None"
results.append((stays_none and has_phone == "False", "Το phone μένει None και τυπώνεται Έχει τηλέφωνο: False", detail))

chars = line_after("Χαρακτήρες:")
size = line_after("Bytes:")
fits = line_after("Χωράει:")
ok = chars == "38" and size == "70" and fits == "False"
results.append((ok, "Τυπώνει Χαρακτήρες: 38, Bytes: 70 και Χωράει: False", f"πήρα {chars!r}, {size!r} και {fits!r}"))

same = line_after("Ίδιο όνομα με τη βάση:")
untouched = "\u0301" in source
detail = f"πήρα {same!r}" if untouched else "το όνομα του αρχείου δεν έχει πια ξεχωριστό τόνο, άρα το άλλαξες αντί να το κανονικοποιήσεις"
results.append((untouched and same == "True", "Τυπώνει Ίδιο όνομα με τη βάση: True, με το όνομα του αρχείου άθικτο", detail))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
