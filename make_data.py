"""Φτιάχνει τα δύο αρχεία δεδομένων του lab.

Τρέξ' το μία φορά:

    python3 make_data.py

Τα αρχεία δεν είναι στο git επειδή το sales.txt είναι πάνω από 2 MB.
Ο κώδικας που τα φτιάχνει είναι, οπότε βγαίνουν ακριβώς τα ίδια σε κάθε μηχάνημα.
"""

import random

CATEGORIES = [
    "Τρόφιμα",
    "Ηλεκτρονικά",
    "Ένδυση",
    "Βιβλία",
    "Καθαριστικά",
    "Παιχνίδια",
]

COUPONS = [""] * 12 + [
    "KALOKAIRI10",
    "BLACKFRIDAY25",
    "WELCOME5",
    "PASXA15",
    "XMAS20",
]

PRODUCT_COUNT = 4_000
SALE_COUNT = 50_000
CUSTOMER_COUNT = 40_000


def write_products(generator: random.Random) -> list[str]:
    codes: list[str] = []
    lines: list[str] = []
    for number in range(1, PRODUCT_COUNT + 1):
        code = f"ΠΡ-{number:04d}"
        codes.append(code)
        lines.append(f"{code};{generator.choice(CATEGORIES)}")
    with open("products.txt", "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return codes


def write_sales(generator: random.Random, codes: list[str]) -> None:
    customers = [str(100_000_000 + generator.randrange(800_000_000)) for _ in range(CUSTOMER_COUNT)]
    lines: list[str] = []
    for number in range(1, SALE_COUNT + 1):
        order = f"ΠΑΡ-{number:06d}"
        day = generator.randrange(365)
        date = f"2024-{day // 31 + 1:02d}-{day % 28 + 1:02d}"
        afm = generator.choice(customers)
        code = generator.choice(codes)
        quantity = generator.randint(1, 5)
        price = round(generator.uniform(1.20, 480.00), 2)
        coupon = generator.choice(COUPONS)
        lines.append(f"{order};{date};{afm};{code};{quantity};{price:.2f};{coupon}")
    with open("sales.txt", "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> None:
    generator = random.Random(20240301)
    codes = write_products(generator)
    write_sales(generator, codes)
    print(f"products.txt: {PRODUCT_COUNT} γραμμές")
    print(f"sales.txt: {SALE_COUNT} γραμμές")


main()
