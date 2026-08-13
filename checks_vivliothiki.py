import ast
import json
import subprocess
import sys

SOURCE = "vivliothiki.py"

EXPECTED = [
    "ΒΙΒ-204: δεν υπάρχουν 3 διαθέσιμα αντίτυπα",
    "ΒΙΒ-315: δεν υπάρχουν 2 διαθέσιμα αντίτυπα",
    "",
    "ΔΙΑΘΕΣΙΜΑ ΑΝΤΙΤΥΠΑ",
    "",
    "ΒΙΒ-101  Ο Μεγάλος Περίπατος        2",
    "ΒΙΒ-204  Το Κιβώτιο                 2",
    "ΒΙΒ-315  Άξιον Εστί                 1",
    "ΒΙΒ-420  Η Φόνισσα                  0",
]

PROBE = r'''
import contextlib
import io
import json

answer = {}
try:
    with contextlib.redirect_stdout(io.StringIO()):
        import vivliothiki
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

library = getattr(vivliothiki, "Library", None)
answer["has_class"] = isinstance(library, type)

if answer["has_class"]:
    try:
        shelf = library()
        shelf.add_title("Α-1", 2)
        shelf.add_title("Α-2", 5)
        try:
            shelf.borrow("Α-1", 3)
            answer["refused"] = False
        except ValueError as exc:
            answer["refused"] = True
            answer["message"] = str(exc)
        answer["after_refusal"] = shelf.available("Α-1")
        shelf.borrow("Α-1", 2)
        answer["after_exact"] = shelf.available("Α-1")
        shelf.give_back("Α-1", 1)
        answer["after_return"] = shelf.available("Α-1")
        answer["untouched"] = shelf.available("Α-2")
        answer["lists"] = sorted(
            name for name, value in vars(shelf).items() if isinstance(value, list)
        )
        answer["keyed"] = any(
            isinstance(value, dict) and set(value) == {"Α-1", "Α-2"}
            for value in vars(shelf).values()
        )
        answer["state"] = sorted(vars(shelf))
    except Exception as exc:
        answer["api_error"] = f"{type(exc).__name__}: {exc}"

print(json.dumps(answer, ensure_ascii=False))
'''

run = subprocess.run([sys.executable, "-B", SOURCE], capture_output=True, text=True)
crash = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ""
output = run.stdout.rstrip("\n").splitlines()

probe = subprocess.run([sys.executable, "-B", "-c", PROBE], capture_output=True, text=True)
try:
    facts = json.loads(probe.stdout.strip().splitlines()[-1])
except Exception:
    detail = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "καμία απάντηση"
    facts = {"import_error": detail}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def leaked_fields() -> list[str]:
    tree = ast.parse(open(SOURCE, encoding="utf-8").read())
    body = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Library"]
    if not body:
        return ["δεν βρήκα class Library"]
    inside = {id(node) for node in ast.walk(body[0])}
    fields = {
        node.attr
        for node in ast.walk(body[0])
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        and isinstance(node.ctx, ast.Store)
    }
    seen = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and id(node) not in inside
    }
    return sorted(fields & seen)


label = "Η έξοδος του vivliothiki.py είναι ακριβώς η αναμενόμενη"
if crash:
    report(False, label, crash)
elif output == EXPECTED:
    report(True, label)
else:
    for wanted, found in zip(EXPECTED, output):
        if wanted != found:
            report(False, label, f"περίμενα {wanted!r} και βρήκα {found!r}")
            break
    else:
        report(False, label, f"περίμενα {len(EXPECTED)} γραμμές και βρήκα {len(output)}")

label = "Η Library αρνείται τον δανεισμό που δεν έχει αντίτυπα"
if "import_error" in facts:
    report(False, label, facts["import_error"])
elif not facts.get("has_class"):
    report(False, label, "δεν βρήκα class με το όνομα Library")
elif "api_error" in facts:
    report(False, label, facts["api_error"])
elif not facts.get("refused"):
    report(False, label, "ο δανεισμός 3 από 2 αντίτυπα πέρασε χωρίς ValueError")
elif facts.get("after_refusal") != 2:
    report(False, label, f"μετά την άρνηση έμειναν {facts.get('after_refusal')} αντί για 2")
elif facts.get("after_exact") != 0 or facts.get("after_return") != 1:
    report(
        False,
        label,
        f"δανεισμός και επιστροφή έδωσαν {facts.get('after_exact')} και {facts.get('after_return')}",
    )
elif facts.get("untouched") != 5:
    report(False, label, f"ο άλλος τίτλος έγινε {facts.get('untouched')} αντί για 5")
else:
    report(True, label)

label = "Κανένα σημείο έξω από τη Library δεν αγγίζει τα εσωτερικά της"
leaks = leaked_fields()
if leaks:
    report(False, label, "από έξω διαβάζεται το " + ", ".join(leaks))
else:
    report(True, label)

label = "Η αποθήκευση μέσα στη Library είναι dictionary με κλειδί τον κωδικό"
if "import_error" in facts or not facts.get("has_class"):
    report(False, label, "δεν έτρεξε η Library")
elif "api_error" in facts:
    report(False, label, facts["api_error"])
elif facts.get("lists"):
    report(False, label, "υπάρχει ακόμα λίστα στο " + ", ".join(facts["lists"]))
elif not facts.get("keyed"):
    report(False, label, f"δεν βρήκα dictionary με κλειδιά τους κωδικούς, έχεις {facts.get('state')}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
