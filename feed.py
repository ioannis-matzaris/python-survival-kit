# Οι προσφορές που έχει ήδη το σύστημα, μία ανά κατάστημα και προϊόν.
# κατάστημα;κωδικός προϊόντος;τιμή
OFFERS: list[str] = [
    "ΚΑΤ-01;ΠΡ-1001;129.00",
    "ΚΑΤ-02;ΠΡ-1001;89.90",
    "ΚΑΤ-03;ΠΡ-1001;95.00",
    "ΚΑΤ-01;ΠΡ-1002;41.60",
    "ΚΑΤ-02;ΠΡ-1002;38.00",
    "ΚΑΤ-03;ΠΡ-1002;7.90",
    "ΚΑΤ-01;ΠΡ-1003;12.00",
    "ΚΑΤ-02;ΠΡ-1003;15.50",
]

# Οι καινούριες προσφορές που μόλις κατέβηκαν και δεν έχουν ελεγχθεί ακόμα.
INCOMING: list[str] = [
    "ΚΑΤ-04;ΠΡ-1001;79.90",
    "ΚΑΤ-05;ΠΡ-1002;35,90",
    "ΚΑΤ-06;ΠΡ-1003",
    "ΚΑΤ-07;ΠΡ-1001;88.00",
]


def parse_offer(offer: str) -> tuple[str, str, float]:
    fields = offer.split(";")
    return fields[0], fields[1], float(fields[2])


def cheapest_for(offers: list[str], product: str) -> tuple[str, float]:
    best_shop = ""
    best_price = ""
    for offer in offers:
        fields = offer.split(";")
        if fields[1] != product:
            continue
        price = fields[2]
        if best_shop == "" or price < best_price:
            best_shop = fields[0]
            best_price = price
    return best_shop, float(best_price)


def check_batch(offers: list[str]) -> int:
    accepted = 0
    for offer in offers:
        try:
            parse_offer(offer)
        except ValueError:
            print("Μια προσφορά δεν διαβάστηκε")
            continue
        accepted += 1
    return accepted


def main() -> None:
    print("ΦΘΗΝΟΤΕΡΟ ΚΑΤΑΣΤΗΜΑ ΑΝΑ ΠΡΟΪΟΝ")
    for product in ["ΠΡ-1001", "ΠΡ-1002", "ΠΡ-1003"]:
        shop, price = cheapest_for(OFFERS, product)
        print(f"{product}: {shop} με {price:.2f} ευρώ")
    print("ΕΛΕΓΧΟΣ ΝΕΩΝ ΠΡΟΣΦΟΡΩΝ")
    accepted = check_batch(INCOMING)
    print(f"Δεκτές {accepted} από {len(INCOMING)} προσφορές")


main()
