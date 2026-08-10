# Ο υπάλληλος περνάει την παραγγελία όπως τη διαβάζει από τη φόρμα.
quantity = input()
unit_price = input()
invoice = input()

# Οι πάγιες χρεώσεις κάθε παραγγελίας του e-shop.
BASE_CHARGES = [3.50]

# Αυτή η παραγγελία πάει με αντικαταβολή, οπότε μπαίνει και αυτή η χρέωση.
charges = BASE_CHARGES
charges.append(2.00)

subtotal = unit_price * int(quantity)
print("Αξία:", subtotal)
print("Τιμολόγιο:", bool(invoice))

total = subtotal + sum(charges)
print(f"Σύνολο: {total:.2f}")
print("Πάγιες χρεώσεις:", BASE_CHARGES)
