# Το κλείσιμο μιας βάρδιας στην καφετέρια.
# Ο υπεύθυνος περνάει το όνομα, τις ώρες και το είδος της βάρδιας.
name = input()
hours_text = input()
kind = input()

hours = int(hours_text)

if hours > 0:
    rate = 6.00
elif kind == "ΝΥΧΤΕΡΙΝΗ":
    rate = 7.20
else:
    rate = 0.00

pay = hours * rate

# Επίδομα παρουσίας για όποιον ήρθε στη δουλειά.
if hours_text:
    pay = pay + 5.00

print(f"{name}: {hours} ώρες x {rate:.2f}")
print(f"Πληρωμή: {pay:.2f}")
