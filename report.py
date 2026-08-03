import sys

# Αναφορά παραγγελιών του e-shop.
# Διαβάζει το export από την είσοδο και τυπώνει τις χρεώσεις.
# Τρέχει έτσι: python3 report.py < orders.txt

VAT_RATE = 0.24
SHIPPING = 3.90
FREE_SHIPPING_OVER = 50.00
ISLAND_SURCHARGE = 2.50

raw_input_text = sys.stdin.read()
all_lines = raw_input_text.splitlines()

rejected_lines = []
order_count = 0
value_total = 0.0
payable_total = 0.0

# Πρώτο πέρασμα: οι χρεώσεις κάθε παραγγελίας.
for raw_line in all_lines:
    line = raw_line.strip()
    if not line:
        continue
    if line.startswith("#"):
        continue
    fields = line.split(";")
    if len(fields) != 6:
        rejected_lines.append(fields[0].strip() + ": απορρίφθηκε, λάθος πλήθος πεδίων")
        continue
    if not fields[3].strip():
        rejected_lines.append(fields[0].strip() + ": απορρίφθηκε, λείπει η αξία")
        continue

    code = fields[0].strip()
    postal_code = fields[2].strip()
    net_value = float(fields[3].strip())
    member = fields[4].strip() == "ΝΑΙ"
    coupon = fields[5].strip()

    # Έκπτωση κουπονιού.
    discount = 0.0
    if coupon == "KALOKAIRI10":
        discount = 0.10
    if coupon == "BLACKFRIDAY25":
        discount = 0.25
    if coupon == "WELCOME5":
        discount = 0.05

    value = round(net_value * (1 - discount), 2)

    # Μεταφορικά, με την επιβάρυνση νησιού από πάνω.
    shipping = SHIPPING
    if member:
        shipping = 0.00
    if value > FREE_SHIPPING_OVER:
        shipping = 0.00
    island = postal_code.startswith("84") or postal_code.startswith("85")
    if island:
        shipping = shipping + ISLAND_SURCHARGE

    vat = round((value + shipping) * VAT_RATE, 2)
    total = round(value + shipping + vat, 2)

    order_count = order_count + 1
    value_total = value_total + value
    payable_total = payable_total + total

    print(f"{code}: αξία {value:.2f} + μεταφορικά {shipping:.2f} + ΦΠΑ {vat:.2f} = {total:.2f}")

for rejected in rejected_lines:
    print(rejected)

print(f"Παραγγελίες: {order_count}")
print(f"Αξία: {value_total:.2f}")
print(f"Πληρωτέο: {payable_total:.2f}")

# Δεύτερο πέρασμα: οι παραγγελίες προς νησιά.
island_codes = []
for raw_line in all_lines:
    line = raw_line.strip()
    if not line:
        continue
    if line.startswith("#"):
        continue
    fields = line.split(";")
    if len(fields) != 6:
        continue
    if not fields[3].strip():
        continue

    code = fields[0].strip()
    postal_code = fields[2].strip()

    island = postal_code.startswith("84") or postal_code.startswith("85")
    if island:
        island_codes.append(code)

if island_codes:
    print("Προς νησιά: " + ", ".join(island_codes))
else:
    print("Προς νησιά: καμία")

# Τρίτο πέρασμα: η μεγαλύτερη παραγγελία του αρχείου.
biggest_code = ""
biggest_total = 0.0
for raw_line in all_lines:
    line = raw_line.strip()
    if not line:
        continue
    if line.startswith("#"):
        continue
    fields = line.split(";")
    if len(fields) != 6:
        continue
    if not fields[3].strip():
        continue

    code = fields[0].strip()
    postal_code = fields[2].strip()
    net_value = float(fields[3].strip())
    member = fields[4].strip() == "ΝΑΙ"
    coupon = fields[5].strip()

    # Έκπτωση κουπονιού.
    discount = 0.0
    if coupon == "KALOKAIRI10":
        discount = 0.10
    if coupon == "BLACKFRIDAY25":
        discount = 0.25
    if coupon == "WELCOME5":
        discount = 0.05

    value = round(net_value * (1 - discount), 2)

    # Μεταφορικά, με την επιβάρυνση νησιού από πάνω.
    shipping = SHIPPING
    if member:
        shipping = 0.00
    if value > FREE_SHIPPING_OVER:
        shipping = 0.00
    island = postal_code.startswith("84") or postal_code.startswith("85")
    if island:
        shipping = shipping + ISLAND_SURCHARGE

    vat = round((value + shipping) * VAT_RATE, 2)
    total = round(value + shipping + vat, 2)

    if total > biggest_total:
        biggest_total = total
        biggest_code = code

if biggest_code:
    print(f"Μεγαλύτερη: {biggest_code} με {biggest_total:.2f}")
else:
    print("Μεγαλύτερη: καμία")
