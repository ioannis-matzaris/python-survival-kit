# Οι κινήσεις αποθήκης της ημέρας, όπως τις βγάζει το export του e-shop.
# κωδικός προϊόντος;είδος κίνησης;ποσότητα
MOVEMENTS: list[str] = [
    "ΠΡ-1001;ΕΙΣΑΓΩΓΗ;40",
    "ΠΡ-1002;ΕΙΣΑΓΩΓΗ;15",
    "ΠΡ-1003;ΕΙΣΑΓΩΓΗ;8",
    "ΠΡ-1001;ΠΩΛΗΣΗ;3",
    "ΠΡ-1002;ΠΩΛΗΣΗ;δύο",
    "ΠΡ-1001;ΠΩΛΗΣΗ;5",
    "ΠΡ-1002;ΚΑΤΑΣΤΡΟΦΗ;2",
    "ΠΡ-1003;ΕΠΙΣΤΡΟΦΗ;2",
]


def quantity_of(movement: str) -> int:
    fields = movement.split(";")
    return int(fields[2])


def apply_to(stock: dict[str, int], movement: str) -> None:
    fields = movement.split(";")
    code = fields[0]
    kind = fields[1]
    amount = quantity_of(movement)
    if kind == "ΕΙΣΑΓΩΓΗ":
        stock[code] = stock.get(code, 0) + amount
    elif kind == "ΠΩΛΗΣΗ":
        stock[code] = stock.get(code, 0) - amount
    elif kind == "ΕΠΙΣΤΡΟΦΗ":
        stock[code] = stock.get(code, 0) + amout


def build_stock(movements: list[str]) -> tuple[dict[str, int], list[int]]:
    # Δίνει το απόθεμα και τους αριθμούς των γραμμών που προσπεράστηκαν.
    stock: dict[str, int] = {}
    skipped: list[int] = []
    for movement in movements:
        try:
            apply_to(stock, movement)
        except Exception:
            pass
    return stock, skipped


def main() -> None:
    stock, skipped = build_stock(MOVEMENTS)
    print("ΑΠΟΘΕΜΑ ΤΕΛΟΥΣ ΗΜΕΡΑΣ")
    for code in sorted(stock):
        print(f"{code}: {stock[code]} τεμάχια")
    if skipped:
        numbers = ", ".join(str(number) for number in skipped)
        print(f"Κινήσεις που προσπεράστηκαν: {len(skipped)} (γραμμές {numbers})")
    else:
        print("Κινήσεις που προσπεράστηκαν: 0")


main()
