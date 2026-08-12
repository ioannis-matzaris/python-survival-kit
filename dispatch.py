# Οι παραγγελίες της ημέρας, όπως βγαίνουν από το export του e-shop.
# κωδικός παραγγελίας;κωδικός πελάτη;τεμάχια;τιμή μονάδας
ORDERS: list[str] = [
    "ΠΑΡ-4401;ΠΕΛ-11;2;12.90",
    "ΠΑΡ-4402;ΠΕΛ-12;1;89.90",
    "ΠΑΡ-4403;ΠΕΛ-11;3;4.50",
    "ΠΑΡ-4404;ΠΕΛ-13;1;41.60",
]

# Σε ποια πόλη στέλνουμε τον κάθε πελάτη.
CITIES: dict[str, str] = {
    "ΠΕΛ-11": "Θεσσαλονίκη",
    "ΠΕΛ-12": "Λάρισα",
    "ΠΕΛ-13": "Ηράκλειο",
}

# Τα μεταφορικά ανά πόλη προορισμού.
SHIPPING: dict[str, float] = {
    "Θεσσαλονίκη": 2.50,
    "Λάρισα": 3.20,
    "Ηράκλειο": 4.10,
}


def order_total(row: str) -> float:
    fields = row.split(";")
    return int(fields[2]) * float(fields[3])


def shipping_for(customer: str) -> float:
    city = CITIES[customer]
    return SHIPPING[city]


def line_for(row: str) -> str:
    fields = row.split(";")
    total = order_total(row) + shipping_for(fields[0])
    return f"{fields[0]}: {total:.2f} ευρώ"


def main() -> None:
    print("ΠΑΡΑΓΓΕΛΙΕΣ ΤΗΣ ΗΜΕΡΑΣ")
    for row in ORDERS:
        print(line_for(row))


main()
