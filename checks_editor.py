import ast
import pathlib
import subprocess
import sys

proc = subprocess.run([sys.executable, "vat.py"], capture_output=True, text=True)
lines = proc.stdout.splitlines()
first = lines[0] if lines else ""
second = lines[1] if len(lines) > 1 else ""

results = [
    (first == "ΚΩΔ-9012", "Ο κωδικός τυπώνεται χωρίς κενά", f"πήρα {first!r}"),
    (proc.returncode == 0 and second == "31.0", "Η τιμή με ΦΠΑ τυπώνεται ως 31.0", f"πήρα {second!r} (exit {proc.returncode})"),
]

tree = ast.parse(pathlib.Path("vat.py").read_text(encoding="utf-8"))
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print_line"]
if not calls:
    ok, detail = False, "δεν βρήκα καμία κλήση της print_line"
else:
    arg = calls[0].args[1] if len(calls[0].args) > 1 else None
    ok = isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)) and not isinstance(arg.value, bool)
    detail = f"το δεύτερο όρισμα είναι {ast.unparse(arg) if arg is not None else 'ανύπαρκτο'}"
results.append((ok, "Η print_line καλείται με αριθμό, όχι με κείμενο", detail))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
