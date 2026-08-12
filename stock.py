# Η απογραφή της αποθήκης. Κάθε γραμμή: κωδικός;όνομα;απόθεμα
PRODUCTS = [
    "ΚΩΔ-1180;Θήκη κινητού;14",
    "ΚΩΔ-2245;Καλώδιο USB-C;3",
    "ΚΩΔ-3390;Powerbank;25",
    "ΚΩΔ-4418;Ακουστικά;6",
    "ΚΩΔ-5502;Φορτιστής αυτοκινήτου;2",
]

REORDER_POINT = 8

i = 0
while i < len(PRODUCTS) - 1:
    code, name, stock_text = PRODUCTS[i].split(";")
    stock = int(stock_text)
    if stock < REORDER_POINT:
        print(f"Κάτω από το όριο: {code} {name} {stock}")
    i = i + 1

# Ο φορτιστής αυτοκινήτου έχει 2 τεμάχια και θέλουμε να φτάσει τα 30.
# Ο προμηθευτής στέλνει μόνο κιβώτια των 12.
stock = 2
boxes = 0

while stock < 30:
    boxes = boxes + 1

print(f"Κιβώτια για ΚΩΔ-5502: {boxes} (απόθεμα {stock})")
