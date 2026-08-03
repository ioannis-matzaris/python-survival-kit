import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

EXPECTED = {
    "Π-40318": "Π-40318: ενέργεια 120.00 + πάγιο 5.00 + ΦΠΑ 7.50 = 132.50",
    "Π-51204": "Π-51204: ενέργεια 0.00 + πάγιο 5.00 + ΦΠΑ 0.30 = 5.30",
    "Π-77310": "Π-77310: ενέργεια 194.60 + πάγιο 5.00 + ΦΠΑ 11.98 = 211.58",
    "Π-99001": "Π-99001: χωρίς ένδειξη",
    "Π-63855": "Π-63855: ενέργεια 49.14 + πάγιο 5.00 + ΦΠΑ 3.25 = 57.39",
    "Π-21447": "Π-21447: ενέργεια 397.00 + πάγιο 5.00 + ΦΠΑ 24.12 = 426.12",
}


def run(script: str, data_file: str) -> tuple[int, list[str]]:
    path = HERE / script
    if not path.exists():
        return 1, [f"δεν βρέθηκε αρχείο {script}"]
    text = (HERE / data_file).read_text(encoding="utf-8")
    finished = subprocess.run(
        [sys.executable, str(path)],
        input=text,
        capture_output=True,
        text=True,
    )
    return finished.returncode, finished.stdout.splitlines()


def find(output: list[str], supply: str) -> str:
    for line in output:
        if line.startswith(supply):
            return line
    return "<λείπει>"


def max_indent(script: str) -> int:
    path = HERE / script
    if not path.exists():
        return -1
    deepest = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            deepest = max(deepest, len(line) - len(line.lstrip(" ")))
    return deepest


results: list[tuple[bool, str, str]] = []


def check(ok: bool, title: str, detail: str = "") -> None:
    results.append((ok, title, detail))


full_code, full = run("bill.py", "bills.txt")
low_code, low = run("bill.py", "bills-low.txt")

check(
    full_code == 0 and low_code == 0,
    "Το bill.py τρέχει χωρίς σφάλμα και με τα δύο αρχεία",
    f"κωδικοί εξόδου: {full_code} και {low_code}",
)

tiers_ok = all(
    find(full, supply) == EXPECTED[supply]
    for supply in ("Π-40318", "Π-63855", "Π-21447")
)
check(
    tiers_ok,
    "Η κλιμακωτή χρέωση βγαίνει σωστή και στα τρία σκαλοπάτια",
    f"βρήκα: {find(full, 'Π-40318')}",
)
check(
    find(full, "Π-51204") == EXPECTED["Π-51204"],
    "Το κλειστό σπίτι χρεώνεται πάγιο",
    f"βρήκα: {find(full, 'Π-51204')}",
)
check(
    find(full, "Π-99001") == EXPECTED["Π-99001"],
    "Η γραμμή χωρίς ένδειξη περνάει χωρίς χρέωση",
    f"βρήκα: {find(full, 'Π-99001')}",
)
check(
    find(full, "Π-77310") == EXPECTED["Π-77310"],
    "Το κοινωνικό τιμολόγιο κόβει 30% από την ενέργεια",
    f"βρήκα: {find(full, 'Π-77310')}",
)
check(
    find(full, "Σύνολο") == "Σύνολο: 832.89" and find(low, "Σύνολο") == "Σύνολο: 137.80",
    "Τα σύνολα των δύο αρχείων είναι 832.89 και 137.80",
    f"βρήκα: {find(full, 'Σύνολο')} και {find(low, 'Σύνολο')}",
)

deepest = max_indent("bill.py")
check(
    0 <= deepest <= 8,
    "Καμία γραμμή του bill.py δεν ξεπερνάει τα 8 κενά στοίχισης",
    f"βρήκα γραμμή με {deepest} κενά",
)

peak_full_code, peak_full = run("peak.py", "bills.txt")
peak_low_code, peak_low = run("peak.py", "bills-low.txt")
check(
    peak_full_code == 0 and peak_low_code == 0 and peak_full == ["Π-77310"] and peak_low == ["Καμία"],
    "Το peak.py βρίσκει την πρώτη παροχή πάνω από 2000 kWh",
    f"βρήκα: {peak_full} και {peak_low}",
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
