# Οι μετρήσεις του διμήνου, μία λίστα ανά στήλη.
meters = ["Ε-4471", "Ε-2210", "Ε-8837", "Ε-9002"]
previous = [12840, 3105, 20477, 7360]
current = [13190, 3560, 20901, 7690]
kwh = [350, 455, 424]

# Ο Ε-2210 ξαναδιαβάστηκε από τον καταμετρητή, η πρώτη ένδειξη ήταν λάθος.
current[1] = 3480

print("ΚΑΤΑΝΑΛΩΣΗ ΔΙΜΗΝΟΥ")
print()

total = 0.0
for meter, used in zip(meters, kwh):
    if used <= 300:
        cost = used * 0.09
    else:
        cost = 300 * 0.09 + (used - 300) * 0.15
    charge = round(cost + 5.0, 2)
    total = total + charge
    print(f"{meter:<10}{used:>6} kWh{charge:>10.2f}")

print()
print(f"{'ΣΥΝΟΛΟ':<10}{round(total, 2):>20.2f}")
