import ast
import builtins
import pathlib
import subprocess
import sys

results: list[tuple[bool, str, str]] = []

proc = subprocess.run([sys.executable, "till.py"], capture_output=True, text=True)
out = proc.stdout.strip()
lines = out.splitlines()
crash = proc.stderr.strip().splitlines()[-1] if proc.returncode != 0 and proc.stderr.strip() else ""
results.append((proc.returncode == 0, "Το till.py τρέχει χωρίς σφάλμα", crash or f"exit {proc.returncode}"))

source = pathlib.Path("till.py").read_text(encoding="utf-8")
tree = ast.parse(source)
taken = sorted({
    target.id
    for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    for target in node.targets
    if isinstance(target, ast.Name) and hasattr(builtins, target.id)
})
results.append((not taken, "Κανένα εργαλείο της Python δεν έχασε το όνομά του", f"το όνομα {', '.join(taken)} το πήρε δική σου μεταβλητή"))


def line_after(prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


net_line = line_after("Καθαρό σύνολο:")
results.append((net_line == "15.00", "Τυπώνει Καθαρό σύνολο: 15.00", f"πήρα {net_line!r}"))

agrees = line_after("Συμφωνεί με το ταμείο:")
results.append((agrees == "True", "Τυπώνει Συμφωνεί με το ταμείο: True", f"πήρα {agrees!r}"))

floats = sorted({
    repr(node.value)
    for node in ast.walk(tree)
    if isinstance(node, ast.Constant) and isinstance(node.value, float)
})
results.append((not floats, "Κανένα ποσό δεν είναι γραμμένο ως δεκαδικός αριθμός", f"βρήκα ακόμα {', '.join(floats)}"))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
