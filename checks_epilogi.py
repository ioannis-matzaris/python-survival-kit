import json
import os
import shutil
import subprocess
import sys
import tempfile

SOURCE = "epilogi.py"

HERE_EXPECTED = {
    "requests>=2.28,<3": ("2.34.2", "15/158"),
    "urllib3<2": ("1.26.20", "77/100"),
    "tabulate~=0.8.9": ("0.8.10", "2/29"),
    "idna>=3": ("3.18", "19/40"),
}

OTHER_RELEASED = {
    "alfa": ["1.10.0", "1.9.3", "1.9.0", "1.2.0", "0.9.9"],
    "beta": ["3.0.0", "2.4.1", "2.4.0", "2.3.7", "2.0.0b2", "1.8.0"],
    "gamma": ["0.12.4", "0.12.3", "0.11.2", "0.11.0", "0.3.0"],
    "delta": ["2.0.0rc1", "1.9.0", "1.8.5", "1.8.0"],
}
OTHER_CONSTRAINTS = "# alli lista\nalfa>=1.9\nbeta>=2,<2.4\ngamma~=0.11.0\ndelta<2\n"
OTHER_EXPECTED = {
    "alfa>=1.9": ("1.10.0", "3/5"),
    "beta>=2,<2.4": ("2.3.7", "1/6"),
    "gamma~=0.11.0": ("0.11.2", "2/5"),
    "delta<2": ("1.9.0", "3/4"),
}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def run(folder: str) -> tuple[dict[str, tuple[str, str]], str]:
    done = subprocess.run(
        [sys.executable, "-B", SOURCE],
        capture_output=True,
        text=True,
        cwd=folder,
    )
    error = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else ""
    found: dict[str, tuple[str, str]] = {}
    for raw in done.stdout.splitlines():
        fields = raw.split()
        if len(fields) == 3:
            found[fields[0]] = (fields[1], fields[2])
    return found, error


def build_other(folder: str) -> None:
    with open(os.path.join(folder, "ekdoseis.json"), "w", encoding="utf-8") as target:
        json.dump(OTHER_RELEASED, target, indent=2)
    with open(os.path.join(folder, "constraints.txt"), "w", encoding="utf-8") as target:
        target.write(OTHER_CONSTRAINTS)
    shutil.copy(SOURCE, os.path.join(folder, SOURCE))


def line_problem(
    where: str,
    found: dict[str, tuple[str, str]],
    expected: dict[str, tuple[str, str]],
    constraint: str,
) -> str:
    if constraint not in found:
        return f"{where}: δεν βρήκα γραμμή για το {constraint}"
    if found[constraint] != expected[constraint]:
        chosen, count = expected[constraint]
        return f"{where}, {constraint}: περίμενα {chosen} και {count}, βρήκα {found[constraint][0]} και {found[constraint][1]}"
    return ""


here, here_error = run(".")

with tempfile.TemporaryDirectory() as folder:
    build_other(folder)
    other, other_error = run(folder)


def both(label: str, here_line: str, other_line: str) -> None:
    if here_error or other_error:
        report(False, label, here_error or other_error)
        return
    problem = line_problem("εδώ", here, HERE_EXPECTED, here_line)
    problem = problem or line_problem("σε άλλα δεδομένα", other, OTHER_EXPECTED, other_line)
    report(not problem, label, problem)


both("Οι εκδόσεις συγκρίνονται ως αριθμοί, όχι ως κείμενο", "idna>=3", "alfa>=1.9")
both("Δύο κανόνες χωρισμένοι με κόμμα ισχύουν και οι δύο", "requests>=2.28,<3", "beta>=2,<2.4")
both("Το ~= κρατάει κλειδωμένο το minor", "tabulate~=0.8.9", "gamma~=0.11.0")
both("Τα pre-release μένουν έξω από την απάντηση", "urllib3<2", "delta<2")

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
