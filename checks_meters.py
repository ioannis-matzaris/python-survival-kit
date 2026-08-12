import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / "meters.py"

SANDBOX_READINGS = "2026-05-04;Γ1;150\n2026-05-04;Γ2;275\n"

SANDBOX_HISTORY = [
    "2026-05-02;Γ1;140;21.28",
    "2026-05-02;Γ2;262;39.82",
    "2026-05-03;Γ1;145;22.04",
    "2026-05-03;Γ2;270;41.04",
]

SANDBOX_NEW = [
    "2026-05-04;Γ1;150;22.80",
    "2026-05-04;Γ2;275;41.80",
]

FIRST_RUN_OUTPUT = [
    "Καταχωρήθηκαν 2 μετρήσεις",
    "Γραμμές στο ιστορικό: 6",
]

SECOND_RUN_OUTPUT = [
    "Καταχωρήθηκαν 2 μετρήσεις",
    "Γραμμές στο ιστορικό: 8",
]

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def opens_outside_with(source: str) -> int:
    tree = ast.parse(source)
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                guarded.add(id(item.context_expr))
    loose = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "open" and id(node) not in guarded:
                loose += 1
    return loose


def run_in_sandbox(times: int) -> list[tuple[subprocess.CompletedProcess[str], list[str]]]:
    # Δικά μας δεδομένα, σε δικό μας φάκελο. Ό,τι έχει το istoriko.txt του lab
    # αυτή τη στιγμή δεν επηρεάζει τους ελέγχους, και οι έλεγχοι δεν το πειράζουν.
    runs: list[tuple[subprocess.CompletedProcess[str], list[str]]] = []
    with tempfile.TemporaryDirectory() as folder:
        box = Path(folder)
        shutil.copy(PROGRAM, box / "meters.py")
        (box / "metriseis.txt").write_text(SANDBOX_READINGS, encoding="utf-8")
        (box / "istoriko.txt").write_text(
            "\n".join(SANDBOX_HISTORY) + "\n", encoding="utf-8"
        )
        for _ in range(times):
            run = subprocess.run(
                [sys.executable, "-B", "meters.py"],
                cwd=box,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            history = (box / "istoriko.txt").read_text(encoding="utf-8").splitlines()
            runs.append((run, history))
    return runs


label = "Κάθε open του meters.py είναι μέσα σε with"
try:
    loose_opens = opens_outside_with(PROGRAM.read_text(encoding="utf-8"))
except SyntaxError as exc:
    report(False, label, f"το meters.py δεν διαβάζεται: {exc}")
else:
    if loose_opens:
        report(False, label, f"βρήκα {loose_opens} open έξω από with")
    else:
        report(True, label)

runs = run_in_sandbox(2)
first_run, first_history = runs[0]
second_run, second_history = runs[1]

label = "Το ιστορικό κρατάει ό,τι είχε και προσθέτει τις νέες μετρήσεις"
if first_run.returncode != 0:
    tail = first_run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "άγνωστο σφάλμα")
elif first_history[: len(SANDBOX_HISTORY)] != SANDBOX_HISTORY:
    report(False, label, f"οι παλιές γραμμές χάθηκαν, βρήκα {first_history}")
elif first_history[len(SANDBOX_HISTORY) :] != SANDBOX_NEW:
    report(
        False,
        label,
        f"περίμενα {SANDBOX_NEW} και πήρα {first_history[len(SANDBOX_HISTORY):]}",
    )
else:
    report(True, label)

label = "Το script μετράει το ιστορικό αφού το γράψει"
if first_run.returncode != 0:
    tail = first_run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "άγνωστο σφάλμα")
else:
    printed = [line.strip() for line in first_run.stdout.splitlines() if line.strip()]
    if printed == FIRST_RUN_OUTPUT:
        report(True, label)
    else:
        report(False, label, f"περίμενα {FIRST_RUN_OUTPUT} και πήρα {printed}")

label = "Δεύτερο τρέξιμο προσθέτει, δεν αντικαθιστά"
if second_run.returncode != 0:
    tail = second_run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "άγνωστο σφάλμα")
elif second_history != SANDBOX_HISTORY + SANDBOX_NEW + SANDBOX_NEW:
    report(False, label, f"περίμενα 8 γραμμές και πήρα {len(second_history)}")
else:
    printed = [line.strip() for line in second_run.stdout.splitlines() if line.strip()]
    if printed == SECOND_RUN_OUTPUT:
        report(True, label)
    else:
        report(False, label, f"περίμενα {SECOND_RUN_OUTPUT} και πήρα {printed}")

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
