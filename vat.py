# Ο τιμοκατάλογος έρχεται ως export από ελληνικό e-shop, οπότε όλα είναι κείμενο.
code = "  ΚΩΔ-9012  "
price_text = "25.00"


def with_vat(amount: float) -> float:
    return amount * 1.24


def print_line(product_code: str, total: float) -> None:
    print(product_code, total)


def print_sample_line() -> None:
    print_line("ΚΩΔ-3300", "12.90")


print(code)
print(with_vat(price_text))
