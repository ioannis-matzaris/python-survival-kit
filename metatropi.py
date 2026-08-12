# Το πελατολόγιο ήρθε από το λογιστήριο, export από Excel σε ελληνικά Windows.
# Το script το διαβάζει, τυπώνει τις οφειλές και αφήνει ένα καθαρό αντίγραφο.
SOURCE_FILE = "pelates.csv"
TARGET_FILE = "pelates_utf8.csv"


def parse_row(line: str) -> tuple[str, str, float]:
    # επωνυμία;πόλη;οφειλή
    name, city, debt = line.split(";")
    return name, city, float(debt)


def main() -> None:
    # Το errors="replace" μπήκε εδώ για να σταματήσει να κρασάρει το script.
    with open(SOURCE_FILE, encoding="utf-8", errors="replace") as source:
        text = source.read()

    rows = text.splitlines()[1:]

    print("ΠΕΛΑΤΕΣ ΜΕ ΟΦΕΙΛΗ")
    total = 0.0
    for row in rows:
        name, city, debt = parse_row(row)
        total += debt
        print(f"{name} - {city}: {debt:.2f} ευρώ")
    print(f"Σύνολο: {total:.2f} ευρώ")

    with open(TARGET_FILE, "w", encoding="utf-8") as target:
        target.write(text)


main()
