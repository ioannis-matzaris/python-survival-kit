"""Οι έλεγχοι του lab. Τρέξε: python3 checks.py

Δεν βγαίνει στο internet. Ξαναϋπολογίζει τα min και max από το data/athens.json
που κατέβασες εσύ, οπότε δίνει την ίδια απάντηση σήμερα και σε τρεις εβδομάδες.
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "athens.json"
REPORT = HERE / "output" / "report.txt"
HEADER = "Πρόγνωση για Αθήνα"
NETWORK_WORDS = ("urllib", "urlopen", "http")


class Failed(Exception):
    pass


def days_from_data() -> tuple[dict[str, list[float]], int]:
    if not DATA.exists():
        raise Failed("δεν βρήκα το data/athens.json, τρέξε πρώτα το fetch.py")
    try:
        payload = json.loads(DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise Failed(f"το data/athens.json δεν είναι έγκυρο JSON: {error}")
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise Failed("το data/athens.json δεν έχει hourly, δες τι σου απάντησε το API")
    times = hourly.get("time")
    temps = hourly.get("temperature_2m")
    if not isinstance(times, list) or not isinstance(temps, list):
        raise Failed("το hourly δεν έχει time και temperature_2m ως λίστες")
    if not times or len(times) != len(temps):
        raise Failed(f"time και temperature_2m έχουν μήκη {len(times)} και {len(temps)}")
    grouped: dict[str, list[float]] = {}
    for stamp, value in zip(times, temps):
        grouped.setdefault(str(stamp)[:10], []).append(float(value))
    return grouped, len(times)


def check_data() -> tuple[dict[str, list[float]], str]:
    grouped, hours = days_from_data()
    return grouped, f"data/athens.json: {hours} ώρες, {len(grouped)} μέρες"


def check_report_is_offline() -> str:
    path = HERE / "report.py"
    if not path.exists():
        raise Failed("δεν βρήκα το report.py")
    text = path.read_text(encoding="utf-8")
    found = [word for word in NETWORK_WORDS if word in text]
    if found:
        raise Failed(f"το report.py αναφέρει ακόμα {found[0]}, σβήσ' το εντελώς")
    return "report.py: δεν αγγίζει το δίκτυο"


def check_report_runs(day_count: int) -> str:
    expected = f"Γράφτηκαν {day_count} μέρες στο output/report.txt"
    finished = subprocess.run(
        [sys.executable, "report.py"], cwd=HERE, capture_output=True, text=True
    )
    if finished.returncode != 0:
        last = (finished.stderr.strip().splitlines() or ["-"])[-1]
        raise Failed(f"το report.py έσκασε: {last}")
    printed = finished.stdout.strip().splitlines()
    if len(printed) != 1:
        raise Failed(f"περίμενα μία γραμμή στην οθόνη, βρήκα {len(printed)}")
    if printed[0] != expected:
        raise Failed(f'τύπωσε "{printed[0]}", περίμενα "{expected}"')
    return f'report.py: τύπωσε "{expected}"'


def report_lines() -> list[str]:
    if not REPORT.exists():
        raise Failed("δεν βρήκα το output/report.txt")
    try:
        text = REPORT.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise Failed(f"το output/report.txt δεν διαβάζεται ως UTF-8: {error}")
    return text.splitlines()


def check_header() -> str:
    lines = report_lines()
    if not lines:
        raise Failed("το output/report.txt είναι άδειο")
    if lines[0] != HEADER:
        raise Failed(f'η πρώτη γραμμή είναι "{lines[0]}", περίμενα "{HEADER}"')
    return "output/report.txt: σωστή επικεφαλίδα, έγκυρο UTF-8"


def check_days(grouped: dict[str, list[float]]) -> str:
    lines = report_lines()[1:]
    if len(lines) != len(grouped):
        raise Failed(f"βρήκα {len(lines)} γραμμές μετά την επικεφαλίδα, περίμενα {len(grouped)}")
    for line, day in zip(lines, grouped):
        values = grouped[day]
        expected = f"{day}: min {min(values):.1f}C max {max(values):.1f}C"
        if line != expected:
            raise Failed(f'γραμμή "{line}", περίμενα "{expected}"')
    return f"output/report.txt: {len(grouped)} γραμμές, min/max σύμφωνα με τα δεδομένα"


def main() -> None:
    number = 0
    try:
        number = 1
        grouped, label = check_data()
        print(f"✅ 1. {label}")

        number = 2
        print(f"✅ 2. {check_report_is_offline()}")

        number = 3
        print(f"✅ 3. {check_report_runs(len(grouped))}")

        number = 4
        print(f"✅ 4. {check_header()}")

        number = 5
        print(f"✅ 5. {check_days(grouped)}")
    except Failed as problem:
        print(f"❌ {number}. {problem}")
        raise SystemExit(1)

    print()
    print("Όλα πέρασαν.")


if __name__ == "__main__":
    main()
