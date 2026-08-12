# Το script του διαχειριστή της πολυκατοικίας: παίρνει τις μετρήσεις της ημέρας
# και τις προσθέτει στο ιστορικό, με τη χρέωση υπολογισμένη.
READINGS_FILE = "metriseis.txt"
HISTORY_FILE = "istoriko.txt"
PRICE_PER_KWH = 0.152


def parse_reading(line: str) -> tuple[str, str, int]:
    # ημερομηνία;διαμέρισμα;κιλοβατώρες
    day, apartment, kwh = line.split(";")
    return day, apartment, int(kwh)


def charge_for(kwh: int) -> float:
    return kwh * PRICE_PER_KWH


def main() -> None:
    source = open(READINGS_FILE, encoding="utf-8")
    readings = source.read().splitlines()

    history = open(HISTORY_FILE, "w", encoding="utf-8")
    for line in readings:
        day, apartment, kwh = parse_reading(line)
        history.write(f"{day};{apartment};{kwh};{charge_for(kwh):.2f}\n")

    check = open(HISTORY_FILE, encoding="utf-8")
    total = len(check.read().splitlines())

    print(f"Καταχωρήθηκαν {len(readings)} μετρήσεις")
    print(f"Γραμμές στο ιστορικό: {total}")


main()
