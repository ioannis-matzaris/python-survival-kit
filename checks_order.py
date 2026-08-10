import ast
import subprocess
import sys

CASES = [
    ("3\n4,50\nΟΧΙ\n", 13.5, False, 19.0),
    ("2\n4.50\n Ναι \n", 9.0, True, 14.5),
]

runs: list[tuple[int, list[str], str]] = []
for stdin, _, _, _ in CASES:
    proc = subprocess.run([sys.executable, "order.py"], input=stdin, capture_output=True, text=True)
    crash = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""
    runs.append((proc.returncode, proc.stdout.strip().splitlines(), crash))


def value_after(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def as_number(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:
        return None


results: list[tuple[bool, str, str]] = []

bad = [crash or f"exit {code}" for code, _, crash in runs if code != 0]
results.append((not bad, "Και τα δύο τρεξίματα τελειώνουν χωρίς σφάλμα", "; ".join(bad)))

problems: list[str] = []
for (_, price, _, total), (_, lines, _) in zip(CASES, runs):
    got_price = value_after(lines, "Αξία:")
    got_total = value_after(lines, "Σύνολο:")
    if as_number(got_price) != price:
        problems.append(f"αξία {got_price!r} αντί για {price}")
    if as_number(got_total) != total:
        problems.append(f"σύνολο {got_total!r} αντί για {total:.2f}")
results.append((not problems, "Η αξία και το σύνολο βγαίνουν αριθμοί και στα δύο τρεξίματα", ", ".join(problems)))

problems = []
for (_, _, invoice, _), (_, lines, _) in zip(CASES, runs):
    got = value_after(lines, "Τιμολόγιο:")
    if got != str(invoice):
        problems.append(f"πήρα {got!r} αντί για {invoice}")
results.append((not problems, "Το ΟΧΙ δίνει False και το Ναι δίνει True", ", ".join(problems)))

problems = []
for _, lines, _ in runs:
    got = value_after(lines, "Πάγιες χρεώσεις:")
    try:
        charges = list(ast.literal_eval(got))
    except (ValueError, SyntaxError):
        charges = []
    if charges != [3.5]:
        problems.append(f"πήρα {got!r}")
results.append((not problems, "Οι πάγιες χρεώσεις μένουν [3.5]", ", ".join(problems)))

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
