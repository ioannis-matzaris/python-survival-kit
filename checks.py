"""Οι έλεγχοι του lab. Τρέξε: python3 checks.py"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_LINES = 36
EXPECTED_METERS = 12
EXPECTED_TOP3 = [("ΜΤ-1007", 3140), ("ΜΤ-1012", 2135), ("ΜΤ-1004", 1830)]
EXPECTED_TOTAL_COST = 2079.60

results: list[tuple[bool, str, str]] = []


def check(passed: bool, title: str, detail: str = "") -> None:
    results.append((passed, title, detail))


def data_lines() -> list[str]:
    path = HERE / "readings.txt"
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


lines = data_lines()
check(
    len(lines) == EXPECTED_LINES,
    "Το readings.txt υπάρχει με 36 γραμμές",
    f"βρήκα {len(lines)} γραμμές, τρέξε python3 make_data.py",
)

run = subprocess.run(
    [sys.executable, "billing.py"], cwd=HERE, capture_output=True, text=True
)
check(
    run.returncode == 0,
    "Το billing.py τρέχει από την αρχή ως το τέλος χωρίς σφάλμα",
    (run.stderr.strip().splitlines() or ["-"])[-1],
)

try:
    import billing
except Exception as error:
    print(f"❌ Το billing.py δεν κάνει καν import: {error}")
    raise SystemExit(1)


def call(name: str, *args: object) -> object:
    function = getattr(billing, name, None)
    if function is None:
        return f"δεν υπάρχει συνάρτηση {name}"
    try:
        return function(*args)
    except Exception as error:
        return f"{type(error).__name__}: {error}"


totals = call("kwh_per_meter", lines)
check(
    isinstance(totals, dict) and len(totals) == EXPECTED_METERS,
    "Η kwh_per_meter βρίσκει ακριβώς 12 μετρητές",
    f"βρήκα {len(totals) if isinstance(totals, dict) else totals}",
)

meter_1011 = totals.get("ΜΤ-1011") if isinstance(totals, dict) else None
check(
    meter_1011 == 1015,
    "Ο ΜΤ-1011 βγάζει 1015 kWh, με όλες τις μετρήσεις του μαζί",
    f"βρήκα {meter_1011}",
)

top3 = call("top_consumers", totals if isinstance(totals, dict) else {}, 3)
check(
    top3 == EXPECTED_TOP3,
    "Η top_consumers δίνει τους τρεις κορυφαίους, από τον μεγαλύτερο",
    f"βρήκα {top3}",
)

top5 = call("top_consumers", totals if isinstance(totals, dict) else {}, 5)
check(
    isinstance(top5, list) and len(top5) == 5,
    "Η top_consumers σέβεται το limit και με 5",
    f"βρήκα {top5}",
)

price_high = call("price_for", 3140)
price_low = call("price_for", 300)
check(
    price_high == 0.18 and price_low == 0.09,
    "Η price_for δίνει τιμή και για κατανάλωση πάνω από τη μεγαλύτερη ζώνη",
    f"για 3140 βρήκα {price_high}, για 300 βρήκα {price_low}",
)

cost_high = call("cost_of", 3140)
check(
    cost_high == 565.20,
    "Η cost_of χρεώνει σωστά τον ΜΤ-1007 με 3140 kWh",
    f"βρήκα {cost_high}",
)

swallowed = call("cost_of", "3140")
check(
    isinstance(swallowed, str) and swallowed.startswith("TypeError"),
    "Η cost_of δεν καταπίνει σφάλματα που δεν ξέρει να χειριστεί",
    f"με string όρισμα επέστρεψε {swallowed} αντί να σκάσει",
)

if isinstance(totals, dict) and totals:
    costs = [call("cost_of", kwh) for kwh in totals.values()]
    total_cost = round(sum(c for c in costs if isinstance(c, float)), 2)
else:
    total_cost = None
check(
    total_cost == EXPECTED_TOTAL_COST,
    "Το συνολικό κόστος όλων των μετρητών είναι 2079.60 ευρώ",
    f"βρήκα {total_cost}",
)

passed = 0
for ok, title, detail in results:
    if ok:
        print(f"✅ {title}")
        passed += 1
    else:
        print(f"❌ {title}")
        if detail:
            print(f"   {detail}")

print()
print(f"{passed}/{len(results)}")
