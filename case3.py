# Ένα export από το λογιστήριο, με τις τιμές γραμμένες όπως τις γράφει ο καθένας.
# κωδικός παραγγελίας;τεμάχια;τιμή μονάδας
ROWS: list[str] = [
    "ΠΑΡ-4401;2;12.90",
    "ΠΑΡ-4402;1;89,90",
]


def row_total(row: str) -> float:
    fields = row.split(";")
    return int(fields[1]) * float(fields[2])


def day_total(rows: list[str]) -> float:
    total = 0.0
    for row in rows:
        total += row_total(row)
    return total


print(f"Σύνολο ημέρας: {day_total(ROWS):.2f} ευρώ")
