# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε lab έχει το δικό του branch. Δεν ανοίγεις αυτό το repo με το χέρι: κάθε lab
έχει ένα κουμπί που σου φτιάχνει ένα Codespace στο σωστό branch, με το περιβάλλον
ήδη στημένο.

## data-structures-orders

Το περιβάλλον του lab «Ξεδίπλωσε τις παραγγελίες ενός e-shop», ανάμεσα στα
μαθήματα του κεφαλαίου `data-structures`. Περιέχει ένα `orders.py` με ένα export
σε σχήμα dictionary από λίστες από dictionaries. Τίποτα δεν κρασάρει και τα
νούμερα είναι λάθος: η `order_total` διαβάζει μόνο την πρώτη γραμμή κάθε
παραγγελίας, η `cheap_labels` είναι μια μονογραμμή με δύο `for` και ένα λάθος
όριο μέσα της, και η `products_per_category` αναθέτει προϊόν αντί να προσθέτει σε
λίστα, οπότε το `join` τυπώνει γράμμα γράμμα. Η `product_names` δουλεύει σωστά σε
τέσσερις γραμμές και είναι η μία θέση όπου το comprehension κερδίζει.

Το `checks_orders.py` καλεί τις τέσσερις συναρτήσεις με δικά του δεδομένα,
διαβάζει το `orders.py` με το `ast` για να δει το σχήμα των comprehensions, και
τρέχει ολόκληρο το αρχείο.

```bash
python3 orders.py
python3 checks_orders.py
```
