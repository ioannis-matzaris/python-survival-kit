# Μία γραμμή παραγγελίας, όπως βγαίνει από το export του e-shop.
# Τα πεδία με τη σειρά: κωδικός, προϊόν, κωδικός έκπτωσης, τιμή.
order_line = "ΚΩΔ-4471;Καφετιέρα;;41.60"


def line_total(line: str, shipping: float) -> str:
    price = float(line.split(";")[2])
    return price + shipping


print("Σύνολο:", line_total(order_line, 3.50)
