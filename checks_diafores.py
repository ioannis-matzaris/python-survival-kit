import os
import shutil
import subprocess
import sys
import tempfile

SOURCE = "diafores.py"
IN_LIST = "στη λίστα σου"
NOT_ASKED = "δεν το ζήτησε κανείς"

HERE_CHANGED = [
    ["pyyaml", "6.0.2", "6.0.1"],
    ["requests", "2.34.2", "2.28.2"],
    ["tabulate", "0.10.0", "0.9.0"],
    ["urllib3", "2.7.0", "1.26.20"],
]
HERE_ONLY_LEFT = [["python-dateutil", "2.9.0.post0"], ["six", "1.17.0"]]
HERE_ONLY_RIGHT = [["python-dotenv", "1.1.1"]]
HERE_SAME = 3
HERE_ORIGINS = [
    ("pyyaml", IN_LIST),
    ("requests", IN_LIST),
    ("tabulate", IN_LIST),
    ("urllib3", NOT_ASKED),
    ("python-dateutil", NOT_ASKED),
    ("six", NOT_ASKED),
    ("python-dotenv", NOT_ASKED),
]

OTHER_FILES = {
    "apaitiseis.txt": "# alli lista\nFlask\n",
    "freeze-a.txt": "Flask==3.1.0\nJinja2==3.1.6\nclick==8.1.8\nitsdangerous==2.2.0\n",
    "freeze-b.txt": "Flask==3.0.3\nJinja2==3.1.6\nclick==8.2.1\nmarkupsafe==3.0.2\n",
}
OTHER_CHANGED = [["click", "8.1.8", "8.2.1"], ["flask", "3.1.0", "3.0.3"]]
OTHER_ONLY_LEFT = [["itsdangerous", "2.2.0"]]
OTHER_ONLY_RIGHT = [["markupsafe", "3.0.2"]]
OTHER_SAME = 1
OTHER_ORIGINS = [
    ("click", NOT_ASKED),
    ("flask", IN_LIST),
    ("itsdangerous", NOT_ASKED),
    ("markupsafe", NOT_ASKED),
]

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def run(folder: str, left: str, right: str) -> tuple[str, str, int]:
    done = subprocess.run(
        [sys.executable, "-B", SOURCE, left, right],
        capture_output=True,
        text=True,
        cwd=folder,
    )
    error = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else ""
    return done.stdout, error, done.returncode


def parse_line(line: str) -> tuple[list[str], str]:
    for origin in (NOT_ASKED, IN_LIST):
        if line.endswith(origin):
            return line[: -len(origin)].split(), origin
    return line.split(), ""


class Report:
    def __init__(self, text: str) -> None:
        self.changed: list[list[str]] = []
        self.only: list[list[list[str]]] = []
        self.headers: list[str] = []
        self.origins: list[tuple[str, str]] = []
        self.same = -1
        target: list[list[str]] | None = None
        for raw in text.splitlines():
            line = raw.rstrip()
            if not line:
                continue
            if line == "ΔΙΑΦΟΡΕΤΙΚΗ ΕΚΔΟΣΗ":
                target = self.changed
            elif line.startswith("ΜΟΝΟ ΣΤΟ "):
                self.headers.append(line[len("ΜΟΝΟ ΣΤΟ ") :].strip())
                self.only.append([])
                target = self.only[-1]
            elif line.startswith("ΙΔΙΕΣ:"):
                target = None
                digits = line.split(":", 1)[1].strip()
                self.same = int(digits) if digits.isdigit() else -1
            elif target is not None:
                fields, origin = parse_line(line)
                target.append(fields)
                if fields:
                    self.origins.append((fields[0], origin))

    def only_at(self, index: int) -> list[list[str]]:
        return self.only[index] if len(self.only) > index else []


here_out, here_error, here_code = run(".", "freeze-maria.txt", "freeze-giorgos.txt")
here = Report(here_out)

with tempfile.TemporaryDirectory() as folder:
    for path, body in OTHER_FILES.items():
        with open(os.path.join(folder, path), "w", encoding="utf-8") as target_file:
            target_file.write(body)
    shutil.copy(SOURCE, os.path.join(folder, SOURCE))
    other_out, other_error, other_code = run(folder, "freeze-a.txt", "freeze-b.txt")
    same_out, same_error, same_code = run(folder, "freeze-a.txt", "freeze-a.txt")
other = Report(other_out)

label = "Η σύγκριση γίνεται ανά package, όχι ανά γραμμή"
if here_error or other_error:
    report(False, label, here_error or other_error)
elif here.changed != HERE_CHANGED:
    report(False, label, f"εδώ περίμενα {HERE_CHANGED} και βρήκα {here.changed}")
elif other.changed != OTHER_CHANGED:
    report(False, label, f"σε άλλα δύο αρχεία περίμενα {OTHER_CHANGED} και βρήκα {other.changed}")
else:
    report(True, label)

label = "Ό,τι υπάρχει μόνο σε ένα από τα δύο αρχεία μπαίνει στη δική του ενότητα"
if here_error or other_error:
    report(False, label, here_error or other_error)
elif here.headers != ["freeze-maria.txt", "freeze-giorgos.txt"]:
    report(False, label, f"οι επικεφαλίδες ΜΟΝΟ ΣΤΟ λένε {here.headers}")
elif here.only_at(0) != HERE_ONLY_LEFT or here.only_at(1) != HERE_ONLY_RIGHT:
    report(
        False,
        label,
        f"εδώ περίμενα {HERE_ONLY_LEFT} και {HERE_ONLY_RIGHT}, βρήκα {here.only_at(0)} και {here.only_at(1)}",
    )
elif here.same != HERE_SAME:
    report(False, label, f"εδώ περίμενα ΙΔΙΕΣ: {HERE_SAME} και βρήκα {here.same}")
elif other.only_at(0) != OTHER_ONLY_LEFT or other.only_at(1) != OTHER_ONLY_RIGHT:
    report(
        False,
        label,
        f"σε άλλα δύο αρχεία περίμενα {OTHER_ONLY_LEFT} και {OTHER_ONLY_RIGHT}, βρήκα {other.only_at(0)} και {other.only_at(1)}",
    )
elif other.same != OTHER_SAME:
    report(False, label, f"σε άλλα δύο αρχεία περίμενα ΙΔΙΕΣ: {OTHER_SAME} και βρήκα {other.same}")
else:
    report(True, label)

label = "Κάθε γραμμή λέει αν το package είναι γραμμένο στο apaitiseis.txt"
if here_error or other_error:
    report(False, label, here_error or other_error)
elif sorted(here.origins) != sorted(HERE_ORIGINS):
    report(False, label, f"εδώ περίμενα {sorted(HERE_ORIGINS)} και βρήκα {sorted(here.origins)}")
elif sorted(other.origins) != sorted(OTHER_ORIGINS):
    report(
        False,
        label,
        f"σε άλλα δύο αρχεία περίμενα {sorted(OTHER_ORIGINS)} και βρήκα {sorted(other.origins)}",
    )
else:
    report(True, label)

label = "Ο κωδικός εξόδου είναι 1 όταν υπάρχει διαφορά και 0 όταν δεν υπάρχει"
if same_error:
    report(False, label, same_error)
elif here_code != 1:
    report(False, label, f"τα δύο μηχανήματα διαφέρουν και ο κωδικός εξόδου ήταν {here_code}")
elif same_code != 0:
    report(False, label, f"το ίδιο αρχείο με τον εαυτό του έδωσε κωδικό εξόδου {same_code}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
