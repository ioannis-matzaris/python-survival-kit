import sys

# Πάγιο ανά λογαριασμό και συντελεστής ΦΠΑ.
STANDING_CHARGE = 5.00
VAT = 0.06

lines = sys.stdin.read().splitlines()
total = 0.0

for raw_line in lines:
    if raw_line.strip():
        fields = raw_line.split(";")
        if len(fields) == 3:
            supply = fields[0].strip()
            kwh = int(fields[1].strip())
            tariff = fields[2].strip()
            # Κλιμακωτή χρέωση ενέργειας.
            if kwh > 2000:
                energy = 1000 * 0.09 + 1000 * 0.12 + (kwh - 2000) * 0.17
            if kwh > 1000:
                energy = 1000 * 0.09 + (kwh - 1000) * 0.12
            if kwh >= 0:
                energy = kwh * 0.09
            standing = 0.00
            if kwh:
                standing = STANDING_CHARGE
            vat = round((energy + standing) * VAT, 2)
            amount = energy + standing + vat
            total = total + amount
            print(f"{supply}: ενέργεια {energy:.2f} + πάγιο {standing:.2f} + ΦΠΑ {vat:.2f} = {amount:.2f}")

print(f"Σύνολο: {total:.2f}")
