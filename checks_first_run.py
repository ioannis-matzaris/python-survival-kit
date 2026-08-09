import ast
import pathlib
import subprocess
import sys

results: list[tuple[bool, str, str]] = []


def run(path: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, path], capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip()


code, out = run("delivery.py")
results.append((code == 0 and out == "45.1", "Το delivery.py τυπώνει 45.1", f"πήρα {out!r} (exit {code})"))

source = pathlib.Path("delivery.py").read_text(encoding="utf-8")
tree = ast.parse(source)
has_text = any(isinstance(n, ast.Constant) and n.value == "3,50" for n in ast.walk(tree))
has_number = any(isinstance(n, ast.Constant) and isinstance(n.value, float) and n.value == 3.5 for n in ast.walk(tree))
results.append((has_text and not has_number, 'Τα μεταφορικά βγαίνουν από το κείμενο "3,50"', "το 3.50 είναι ακόμα γραμμένο ως αριθμός" if has_number else "δεν βρήκα το κείμενο \"3,50\""))

copy = pathlib.Path("delivery")
if copy.is_file():
    code, out = run("delivery")
    ok, detail = code == 0 and out == "45.1", f"πήρα {out!r} (exit {code})"
else:
    ok, detail = False, "δεν υπάρχει αρχείο delivery"
results.append((ok, "Το delivery τρέχει και χωρίς κατάληξη .py", detail))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
