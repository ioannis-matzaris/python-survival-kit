import os
import shutil
import subprocess
import sys
import tempfile

SOURCE = "apografi.py"
HEADERS = ["ΤΙ ΕΧΕΙΣ", "ΗΡΘΑΝ ΜΕ ΤΑ ΑΛΛΑ", "ΤΑ ΖΗΤΗΣΕΣ ΕΣΥ"]

HERE_INSTALLED = [
    "python-dateutil==2.9.0.post0",
    "six==1.17.0",
    "tabulate==0.9.0",
]
HERE_INDIRECT = ["six <- python-dateutil"]
HERE_DIRECT = ["python-dateutil", "tabulate"]

OTHER_FILES = {
    "alfa_tools-2.0.0.dist-info/METADATA": (
        "Metadata-Version: 2.1\n"
        "Name: Alfa_Tools\n"
        "Version: 2.0.0\n"
        "Summary: ergaleia grafeiou\n"
        "Requires-Python: >=3.8\n"
        "Provides-Extra: dev\n"
        "Requires-Dist: beta-utils >=1.2\n"
        "Requires-Dist: gamma >=2\n"
        "Requires-Dist: pytest ; extra == 'dev'\n"
        "\n"
        "Perigrafi tou package.\n"
    ),
    "beta_utils-1.4.2.dist-info/METADATA": (
        "Metadata-Version: 2.1\n"
        "Name: beta_utils\n"
        "Version: 1.4.2\n"
        "Requires-Python: >=3.7\n"
        "\n"
        "Perigrafi tou package.\n"
    ),
    "delta-0.3.dist-info/METADATA": (
        "Metadata-Version: 2.1\n"
        "Name: delta\n"
        "Version: 0.3\n"
        "Provides-Extra: fancy\n"
        "Requires-Dist: beta_utils ; extra == 'fancy'\n"
        "\n"
        "Perigrafi tou package.\n"
    ),
    "epsilon-1.0.dist-info/METADATA": (
        "Metadata-Version: 2.1\n"
        "Name: epsilon\n"
        "Version: 1.0\n"
        "Requires-Dist: beta-utils\n"
        "\n"
        "Perigrafi tou package.\n"
    ),
    "alfa_tools/__init__.py": "",
    "beta_utils.py": "",
    "bin/delta": "",
    "notes.txt": "",
}
OTHER_INSTALLED = [
    "alfa-tools==2.0.0",
    "beta-utils==1.4.2",
    "delta==0.3",
    "epsilon==1.0",
]
OTHER_INDIRECT = ["beta-utils <- alfa-tools, epsilon"]
OTHER_DIRECT = ["alfa-tools", "delta", "epsilon"]

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def run(folder: str) -> tuple[str, str]:
    done = subprocess.run(
        [sys.executable, "-B", SOURCE],
        capture_output=True,
        text=True,
        cwd=folder,
    )
    error = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else ""
    return done.stdout, error


def split_sections(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    current = ""
    for raw in text.splitlines():
        line = raw.rstrip()
        if line in HEADERS:
            current = line
            found[current] = []
        elif current and line:
            found[current].append(line)
    return found


def build_other(folder: str) -> None:
    for path, body in OTHER_FILES.items():
        full = os.path.join(folder, "site-packages", path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as target:
            target.write(body)
    shutil.copy(SOURCE, os.path.join(folder, SOURCE))


def section_problem(where: str, sections: dict[str, list[str]], header: str, wanted: list[str]) -> str:
    if header not in sections:
        return f"{where}: δεν βρήκα την επικεφαλίδα {header} στην έξοδο"
    if sections[header] != wanted:
        return f"{where}, {header}: περίμενα {wanted} και βρήκα {sections[header]}"
    return ""


here_out, here_error = run(".")
here = split_sections(here_out)

with tempfile.TemporaryDirectory() as folder:
    build_other(folder)
    other_out, other_error = run(folder)
other = split_sections(other_out)

label = "Η απογραφή δίνει κάθε εγκατεστημένο package με την έκδοσή του"
if here_error or other_error:
    report(False, label, here_error or other_error)
else:
    problem = section_problem("εδώ", here, "ΤΙ ΕΧΕΙΣ", HERE_INSTALLED)
    problem = problem or section_problem("σε άλλο site-packages", other, "ΤΙ ΕΧΕΙΣ", OTHER_INSTALLED)
    report(not problem, label, problem)

label = "Ξεχωρίζεις όσα ήρθαν μαζί με άλλα από όσα ζήτησες εσύ"
if here_error or other_error:
    report(False, label, here_error or other_error)
else:
    problem = section_problem("εδώ", here, "ΗΡΘΑΝ ΜΕ ΤΑ ΑΛΛΑ", HERE_INDIRECT)
    problem = problem or section_problem("εδώ", here, "ΤΑ ΖΗΤΗΣΕΣ ΕΣΥ", HERE_DIRECT)
    problem = problem or section_problem("σε άλλο site-packages", other, "ΗΡΘΑΝ ΜΕ ΤΑ ΑΛΛΑ", OTHER_INDIRECT)
    problem = problem or section_problem("σε άλλο site-packages", other, "ΤΑ ΖΗΤΗΣΕΣ ΕΣΥ", OTHER_DIRECT)
    report(not problem, label, problem)

label = "Ένα requirement που δεν είναι εγκατεστημένο δεν μπαίνει στην απογραφή"
if other_error:
    report(False, label, other_error)
elif "gamma" in other_out:
    report(False, label, "το gamma το ζητάει το alfa-tools αλλά δεν είναι εγκατεστημένο, και το τυπώνεις")
elif other.get("ΤΙ ΕΧΕΙΣ") != OTHER_INSTALLED:
    report(False, label, "σε άλλο site-packages δεν βγήκε καν σωστή απογραφή")
else:
    report(True, label)

label = "Τα extras δεν μετράνε ως εξαρτήσεις"
if here_error or other_error:
    report(False, label, here_error or other_error)
elif "wcwidth" in here_out:
    report(False, label, "το wcwidth το ζητάει το tabulate μόνο ως extra, και το τυπώνεις")
elif "pytest" in other_out:
    report(False, label, "το pytest το ζητάει το alfa-tools μόνο ως extra, και το τυπώνεις")
elif other.get("ΗΡΘΑΝ ΜΕ ΤΑ ΑΛΛΑ") != OTHER_INDIRECT:
    report(False, label, f"περίμενα {OTHER_INDIRECT} και βρήκα {other.get('ΗΡΘΑΝ ΜΕ ΤΑ ΑΛΛΑ')}")
else:
    report(True, label)

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
