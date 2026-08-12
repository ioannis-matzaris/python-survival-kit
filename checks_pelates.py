import ast
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / "metatropi.py"
SOURCE_FILE = HERE / "pelates.csv"
TARGET_FILE = HERE / "pelates_utf8.csv"

# Το ακριβές περιεχόμενο του pelates.csv. Στον δίσκο είναι γραμμένο σε cp1253.
EXPECTED_TEXT = (
    "Επωνυμία;Πόλη;Οφειλή\n"
    "Παπαδοπούλου Μαρία;Θεσσαλονίκη;248.50\n"
    "Ντάλας Γιώργος;Λάρισα;132.80\n"
    "Βασιλείου Ελένη;Ηράκλειο;96.40\n"
    "Αθανασόπουλος Κώστας;Πάτρα;310.00\n"
    "Ζέρβα Αγγελική;Ιωάννινα;55.20\n"
)

EXPECTED_OUTPUT = [
    "ΠΕΛΑΤΕΣ ΜΕ ΟΦΕΙΛΗ",
    "Παπαδοπούλου Μαρία - Θεσσαλονίκη: 248.50 ευρώ",
    "Ντάλας Γιώργος - Λάρισα: 132.80 ευρώ",
    "Βασιλείου Ελένη - Ηράκλειο: 96.40 ευρώ",
    "Αθανασόπουλος Κώστας - Πάτρα: 310.00 ευρώ",
    "Ζέρβα Αγγελική - Ιωάννινα: 55.20 ευρώ",
    "Σύνολο: 842.90 ευρώ",
]

BOM = b"\xef\xbb\xbf"

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def open_calls(source: str) -> list[ast.Call]:
    tree = ast.parse(source)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "open"
    ]


# Πριν από κάθε έλεγχο: η πηγή πρέπει να είναι ακριβώς τα bytes που ήρθαν από το
# λογιστήριο. Αν την ξανασώσει ο editor σε άλλη κωδικοποίηση, το lab λέει ψέματα.
if not SOURCE_FILE.exists():
    print("Δεν βρήκα το pelates.csv. Γύρνα το πίσω με: git checkout pelates.csv")
    sys.exit(1)

if SOURCE_FILE.read_bytes() != EXPECTED_TEXT.encode("cp1253"):
    print("Το pelates.csv δεν είναι πια αυτό που ήρθε από το λογιστήριο.")
    print("Γύρνα το πίσω με: git checkout pelates.csv")
    sys.exit(1)

run = subprocess.run(
    [sys.executable, "-B", str(PROGRAM)],
    cwd=HERE,
    capture_output=True,
    text=True,
    stdin=subprocess.DEVNULL,
)

label = "Το metatropi.py διαβάζει τα ονόματα ολόκληρα"
if run.returncode != 0:
    tail = run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "άγνωστο σφάλμα")
else:
    printed = [line.strip() for line in run.stdout.splitlines() if line.strip()]
    if "�" in run.stdout:
        report(False, label, "η έξοδος έχει μέσα χαρακτήρες που χάθηκαν")
    elif printed != EXPECTED_OUTPUT:
        report(False, label, f"περίμενα {EXPECTED_OUTPUT} και πήρα {printed}")
    else:
        report(True, label)

label = "Κανένα open δεν σκεπάζει το πρόβλημα με errors="
try:
    calls = open_calls(PROGRAM.read_text(encoding="utf-8"))
except SyntaxError as exc:
    report(False, label, f"το metatropi.py δεν διαβάζεται: {exc}")
else:
    names = [keyword.arg for call in calls for keyword in call.keywords]
    if "errors" in names:
        report(False, label, "υπάρχει ακόμα open με errors=")
    elif any(
        "encoding" not in [keyword.arg for keyword in call.keywords] for call in calls
    ):
        report(False, label, "υπάρχει open χωρίς encoding=")
    else:
        report(True, label)

target_bytes = TARGET_FILE.read_bytes() if TARGET_FILE.exists() else None

label = "Το pelates_utf8.csv ανοίγει και στο Excel: UTF-8 με BOM"
if target_bytes is None:
    report(False, label, "δεν βρήκα το pelates_utf8.csv")
elif not target_bytes.startswith(BOM):
    report(False, label, f"περίμενα να ξεκινάει με {BOM!r} και ξεκινάει με {target_bytes[:3]!r}")
else:
    try:
        target_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        report(False, label, f"δεν διαβάζεται ως UTF-8: {exc}")
    else:
        report(True, label)

label = "Το αντίγραφο λέει ακριβώς ό,τι το πρωτότυπο"
if target_bytes is None:
    report(False, label, "δεν βρήκα το pelates_utf8.csv")
else:
    try:
        target_text = target_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        report(False, label, f"δεν διαβάζεται ως UTF-8: {exc}")
    else:
        if target_text.rstrip("\n") == EXPECTED_TEXT.rstrip("\n"):
            report(True, label)
        else:
            first = next(
                (
                    line
                    for line in target_text.splitlines()
                    if line not in EXPECTED_TEXT.splitlines()
                ),
                "(λείπουν γραμμές)",
            )
            report(False, label, f"η γραμμή {first!r} δεν είναι αυτή που έχει η πηγή")

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
