import csv

VAT = 0.24

rows = []
with open("orders.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

subtotals = {}
for row in rows:
    net = float(row["unit_price"]) * int(row["quantity"])
    if row["category"] == "student":
        net = net * 0.90
    elif row["category"] == "senior":
        net = net * 0.85
    name = row["customer"]
    if name in subtotals:
        subtotals[name] = subtotals[name] + net
    else:
        subtotals[name] = net

totals = {}
for name in subtotals:
    subtotal = subtotals[name]
    if subtotal >= 50:
        shipping = 0.0
    else:
        shipping = 3.50
    totals[name] = round(subtotal * (1 + VAT) + shipping, 2)

print("ΠΑΡΑΓΓΕΛΙΕΣ ΑΝΑ ΠΕΛΑΤΗ")
print()
for name in sorted(totals, key=lambda n: (-totals[n], n)):
    print(f"{name:<20}{totals[name]:>9.2f}")
print()
print(f"{'ΣΥΝΟΛΟ':<20}{round(sum(totals.values()), 2):>9.2f}")
