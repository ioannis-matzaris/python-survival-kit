import subprocess
import sys

CASES = {
    "Ελένη": "Ελένη\n9\nΚΑΝΟΝΙΚΗ\n",
    "Νίκος": "Νίκος\n6\nΝΥΧΤΕΡΙΝΗ\n",
    "Δήμητρα": "Δήμητρα\n0\nΡΕΠΟ\n",
    "Παύλος": "Παύλος\n8\nΑΡΓΙΑ\n",
    "Κώστας": "Κώστας\n7\nΔΙΠΛΟΒΑΡΔΙΑ\n",
}

runs: dict[str, tuple[list[str], str]] = {}
for who, stdin in CASES.items():
    proc = subprocess.run(
        [sys.executable, "shifts.py"], input=stdin, capture_output=True, text=True
    )
    crash = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""
    runs[who] = (proc.stdout.strip().splitlines(), crash)


def payment(who: str) -> str:
    lines, crash = runs[who]
    if crash:
        return crash
    for line in lines:
        if line.startswith("Πληρωμή:"):
            return line[len("Πληρωμή:"):].strip()
    return "καμία γραμμή Πληρωμή:"


def warning(who: str) -> str:
    lines, _ = runs[who]
    for line in lines:
        if line.startswith("Άγνωστο είδος βάρδιας"):
            return line
    return ""


def wrong(expected: dict[str, str]) -> list[str]:
    return [
        f"{who}: {payment(who)!r} αντί για {amount}"
        for who, amount in expected.items()
        if payment(who) != amount
    ]


results: list[tuple[bool, str, str]] = []

problems = wrong({"Ελένη": "59.00", "Νίκος": "48.20"})
results.append(
    (
        not problems,
        "Η κανονική βάρδια πληρώνεται 6.00 και η νυχτερινή 7.20",
        ", ".join(problems),
    )
)

problems = wrong({"Δήμητρα": "0.00"})
if warning("Δήμητρα"):
    problems.append("το ρεπό βγάζει μήνυμα για άγνωστο είδος")
results.append(
    (not problems, "Το ρεπό δεν παίρνει επίδομα παρουσίας", ", ".join(problems))
)

problems = wrong({"Παύλος": "89.00"})
results.append((not problems, "Η αργία πληρώνεται 10.50 την ώρα", ", ".join(problems)))

problems = wrong({"Κώστας": "47.00"})
message = warning("Κώστας")
if not message:
    problems.append("καμία γραμμή που να αρχίζει με Άγνωστο είδος βάρδιας")
elif "ΔΙΠΛΟΒΑΡΔΙΑ" not in message:
    problems.append(f"το μήνυμα δεν αναφέρει το είδος: {message!r}")
results.append(
    (
        not problems,
        "Το άγνωστο είδος βάρδιας αφήνει μήνυμα και πληρώνεται 6.00",
        ", ".join(problems),
    )
)

passed = 0
for ok, label, detail in results:
    print(f"{'✅' if ok else '❌'} {label}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
