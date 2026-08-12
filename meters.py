# Οι μηνιαίες μετρήσεις που έστειλαν οι μετρητές.
# αριθμός παροχής;μήνας;κιλοβατώρες
READINGS = [
    "12345678;2026-01;318",
    "23456789;2026-01;540",
    "12345678;2026-02;295",
    "34567890;2026-01;127",
    "23456789;2026-02;612",
    "12345678;2026-03;340",
    "45678901;2026-01;902",
    "23456789;2026-03;588",
]

# Όλες οι παροχές του μητρώου, και αυτές που δεν έστειλαν ποτέ μέτρηση.
REGISTRY = [
    "12345678",
    "23456789",
    "34567890",
    "45678901",
    "56789012",
]


def consumption_per_month(readings: list[str]) -> dict[tuple[str, str], int]:
    # Η κατανάλωση δεν ανήκει στην παροχή, ανήκει στο ζευγάρι παροχή και μήνας.
    totals: dict[tuple[str, str], int] = {}
    for line in readings:
        supply, month, kwh = line.split(";")
        key = [supply, month]
        totals[key] = int(kwh)
    return totals


def missing_from_month(readings: list[str], registry: list[str], month: str) -> list[str]:
    # Ποιες παροχές του μητρώου δεν έστειλαν μέτρηση αυτόν τον μήνα.
    missing: list[str] = []
    for supply in registry:
        for line in readings:
            fields = line.split(";")
            if fields[1] == month and fields[0] != supply:
                missing.append(supply)
    return missing


def steps_to_find(codes: list[str], target: str) -> int:
    # Πόσα στοιχεία της λίστας διάβασε το ψάξιμο μέχρι να απαντήσει.
    steps = 0
    for code in codes:
        steps = steps + 1
        if code == target:
            return steps
    return 0


totals = consumption_per_month(READINGS)

print("ΚΑΤΑΝΑΛΩΣΗ ΑΝΑ ΠΑΡΟΧΗ ΚΑΙ ΜΗΝΑ")
for key in sorted(totals):
    supply, month = key
    print(f"{supply} {month}: {totals[key]} kWh")

print("ΧΩΡΙΣ ΜΕΤΡΗΣΗ ΤΟΝ 2026-02")
for supply in missing_from_month(READINGS, REGISTRY, "2026-02"):
    print(supply)

print("ΒΗΜΑΤΑ ΑΝΑΖΗΤΗΣΗΣ ΣΤΟ ΜΗΤΡΩΟ")
print(f"πρώτη παροχή: {steps_to_find(REGISTRY, '12345678')}")
print(f"τελευταία παροχή: {steps_to_find(REGISTRY, '56789012')}")
print(f"παροχή που δεν υπάρχει: {steps_to_find(REGISTRY, '99999999')}")
