"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Δεν σε ρωτάει τι διάλεξες. Μετράει πόσο κάνει η κάθε δουλειά, και κοιτάει σε
πόσα processes απλώθηκε.
"""

import hashlib
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK_FINGERPRINT = "62e4fe40b02d272afda416e893627d54"

results: list[tuple[bool, str]] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


def clear_marks() -> None:
    for kind in ("fetch", "crunch"):
        (HERE / f"pids-{kind}.txt").unlink(missing_ok=True)


def processes_seen(kind: str) -> int:
    marks = HERE / f"pids-{kind}.txt"
    if not marks.exists():
        return 0
    return len({line for line in marks.read_text(encoding="utf-8").split() if line})


if not (HERE / "report.py").exists():
    print("Δεν βρήκα το report.py στη ρίζα του repo.")
    sys.exit(1)

work_now = hashlib.md5((HERE / "work.py").read_bytes()).hexdigest()

sys.path.insert(0, str(HERE))
import report as student  # noqa: E402

from work import CHUNKS_TO_CRUNCH, CHUNKS_TO_FETCH, crunch_chunk  # noqa: E402

clear_marks()

started = time.time()
downloaded = student.download_all()
download_seconds = time.time() - started
download_processes = processes_seen("fetch")

started = time.time()
crunched = student.crunch_all()
crunch_seconds = time.time() - started
crunch_processes = processes_seen("crunch")

clear_marks()
expected_crunch = [crunch_chunk(index) for index in range(CHUNKS_TO_CRUNCH)]
clear_marks()

report(
    "Το download_all επιστρέφει τα οκτώ κομμάτια, στη σειρά τους",
    downloaded == [index * 100 for index in range(CHUNKS_TO_FETCH)],
)
report(
    "Το crunch_all επιστρέφει τα τέσσερα σύνολα, στη σειρά τους",
    crunched == expected_crunch,
)
report(
    f"Το κατέβασμα τελειώνει κάτω από 0,8 δευτερόλεπτα ({download_seconds:.2f}s)",
    download_seconds < 0.8,
)
report(
    f"Το κατέβασμα δεν ξοδεύει processes για να περιμένει ({download_processes})",
    download_processes == 1,
)
report(
    f"Ο υπολογισμός τελειώνει κάτω από 1,6 δευτερόλεπτα ({crunch_seconds:.2f}s)",
    crunch_seconds < 1.6,
)
report(
    f"Ο υπολογισμός απλώνεται σε πάνω από ένα process ({crunch_processes})",
    crunch_processes > 1,
)
report("Το work.py δεν πειράχτηκε", work_now == WORK_FINGERPRINT)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(66) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
