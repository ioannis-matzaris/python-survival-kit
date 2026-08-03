raw_line = input()
raw_fields = raw_line.split(";")

# Κρατάμε τα αρχικά πεδία, γιατί τα θέλουμε αυτούσια στο τέλος.
clean_fields = raw_fields

clean_fields[2].strip().replace("€", "").replace(",", ".")
clean_fields[3].strip().replace("τεμ", "")
clean_fields[4].strip().replace("%", "")

code = clean_fields[0].strip()
name = clean_fields[1].strip()
unit_price = float(clean_fields[2])
quantity = int(clean_fields[3])
discount_percent = float(clean_fields[4])

subtotal = unit_price * quantity
discount = round(subtotal * discount_percent / 100, 2)
payable = None

print(name)
print("Έγκυρος κωδικός:", code[:3] is "ΚΩΔ")
print(f"Καθαρή αξία: {subtotal:.2f}")
print(f"Έκπτωση: {discount:.2f}")
print(f"Πληρωτέο: {payable:.2f}")
print("Πηγή:", ";".join(raw_fields))
