# Το export των παραγγελιών, όπως έρχεται από το e-shop.
# Κωδικός παραγγελίας προς τις γραμμές της. Όλες οι τιμές είναι κείμενο.
ORDERS: dict[str, list[dict[str, str]]] = {
    "ΠΑΡ-8814": [
        {"product": "Καφετιέρα", "category": "Οικιακά", "qty": "1", "price": "62.40"},
        {"product": "Φίλτρα καφέ", "category": "Οικιακά", "qty": "3", "price": "2.80"},
    ],
    "ΠΑΡ-8815": [
        {"product": "Ακουστικά", "category": "Ηλεκτρονικά", "qty": "1", "price": "129.00"},
    ],
    "ΠΑΡ-8816": [
        {"product": "Τοστιέρα", "category": "Οικιακά", "qty": "1", "price": "45.50"},
        {"product": "Θήκη κινητού", "category": "Ηλεκτρονικά", "qty": "2", "price": "9.90"},
        {"product": "Φίλτρα καφέ", "category": "Οικιακά", "qty": "5", "price": "2.80"},
    ],
}

# Κωδικός παραγγελίας προς τα στοιχεία του πελάτη.
CUSTOMERS: dict[str, dict[str, str]] = {
    "ΠΑΡ-8814": {"name": "Μαρία Ιωάννου", "city": "Θεσσαλονίκη"},
    "ΠΑΡ-8815": {"name": "Νίκος Παπαδάκης", "city": "Λάρισα"},
    "ΠΑΡ-8816": {"name": "Ελένη Βασιλείου", "city": "Θεσσαλονίκη"},
}


def order_total(items: list[dict[str, str]]) -> float:
    # Το σύνολο μιας παραγγελίας, τεμάχια επί τιμή.
    item = items[0]
    return round(int(item["qty"]) * float(item["price"]), 2)


def product_names(items: list[dict[str, str]]) -> list[str]:
    # Μόνο τα ονόματα των προϊόντων μιας παραγγελίας.
    names: list[str] = []
    for item in items:
        names.append(item["product"])
    return names


def cheap_labels(orders: dict[str, list[dict[str, str]]]) -> list[str]:
    # Ετικέτα για κάθε γραμμή κάτω από 100 ευρώ, από όλες τις παραγγελίες.
    return [item["product"] + " (" + ("πολλά" if int(item["qty"]) >= 1 else "ένα") + ")" for code in orders for item in orders[code] if float(item["price"]) < 100]


def products_per_category(orders: dict[str, list[dict[str, str]]]) -> dict[str, list[str]]:
    # Κατηγορία προς τα προϊόντα που πουλήθηκαν σε αυτήν, με τη σειρά τους.
    by_category: dict[str, list[str]] = {}
    for code in orders:
        for item in orders[code]:
            by_category[item["category"]] = item["product"]
    return by_category


print("ΠΑΡΑΓΓΕΛΙΕΣ")
for code in ORDERS:
    customer = CUSTOMERS[code]
    print(f"{code} - {customer['name']} ({customer['city']}): {order_total(ORDERS[code]):.2f} ευρώ")
    print("  " + ", ".join(product_names(ORDERS[code])))

print("ΕΤΙΚΕΤΕΣ ΚΑΤΩ ΑΠΟ 100 ΕΥΡΩ")
for label in cheap_labels(ORDERS):
    print(f"  {label}")

print("ΠΡΟΪΟΝΤΑ ΑΝΑ ΚΑΤΗΓΟΡΙΑ")
sold = products_per_category(ORDERS)
for category in sorted(sold):
    print(f"{category}: {', '.join(sold[category])}")
