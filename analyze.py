"""Ανάλυση πωλήσεων 2024.

Δουλεύει. Βγάζει σωστά νούμερα. Απλώς κάνει τον χρόνο του.
"""


def read_lines(path: str) -> list[str]:
    with open(path, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def category_of(product_code: str, product_lines: list[str]) -> str:
    for line in product_lines:
        fields = line.split(";")
        if fields[0] == product_code:
            return fields[1]
    return "Άγνωστη"


def main() -> None:
    sales = read_lines("sales.txt")
    products = read_lines("products.txt")

    revenue: dict[str, float] = {}
    for line in sales:
        fields = line.split(";")
        # σε ποια κατηγορία ανήκει το προϊόν αυτής της γραμμής;
        category = category_of(fields[3], products)
        amount = int(fields[4]) * float(fields[5])
        revenue[category] = revenue.get(category, 0.0) + amount

    print(f"Πωλήσεις: {len(sales)}")
    print("Έσοδα ανά κατηγορία:")
    for name in sorted(revenue):
        print(f"  {name}: {revenue[name]:.2f}")


main()
