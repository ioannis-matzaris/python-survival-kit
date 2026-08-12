from statistics import mean

# Οι γραμμές μιας παραγγελίας: κωδικός;τεμάχια;τιμή μονάδας
LINES: list[str] = [
    "ΠΡ-1001;2;12.90",
    "ΠΡ-1002;1;89.90",
    "ΠΡ-1003;3;4.50",
]


def unit_prices(lines: list[str]) -> list[str]:
    return [line.split(";")[2] for line in lines]


def average_price(lines: list[str]) -> float:
    return mean(unit_prices(lines))


print(f"Μέση τιμή μονάδας: {average_price(LINES):.2f} ευρώ")
