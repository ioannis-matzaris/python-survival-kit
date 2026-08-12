# Η αποθήκη ετοιμάζει τις παραγγελίες της ημέρας.
# Πρώτα βγαίνει η λίστα συλλογής για τον υπάλληλο, μετά το δελτίο αποστολής του πελάτη.

needs_manager = False


def print_picking_list(code: str, items: list[str], gift: bool) -> None:
    # Η συσκευασία δώρου είναι κι αυτή αντικείμενο που πρέπει να μαζέψει κάποιος.
    if gift:
        items.append("κουτί δώρου")
    # Αλφαβητικά, για να τα βρίσκει με τη σειρά στα ράφια.
    items.sort()
    print(f"{code}: {len(items)} προς συλλογή")
    for item in items:
        print(f"  - {item}")
    if len(items) > 3:
        needs_manager = True


def print_delivery_note(code: str, items: list[str]) -> None:
    print(f"{code}: {len(items)} προϊόντα")
    for item in items:
        print(f"  * {item}")


order_a = ["καφετιέρα", "φίλτρα"]
order_b = ["ζυγαριά κουζίνας", "βραστήρας", "θερμός", "τοστιέρα"]
order_c = ["μύλος καφέ", "ταψί"]

print("ΛΙΣΤΕΣ ΣΥΛΛΟΓΗΣ")
print_picking_list("ΠΑΡ-3301", order_a, True)
print_picking_list("ΠΑΡ-3301 (επανεκτύπωση)", order_a, True)
print_picking_list("ΠΑΡ-3302", order_b, False)
print_picking_list("ΠΑΡ-3303", order_c, True)

print("ΔΕΛΤΙΑ ΑΠΟΣΤΟΛΗΣ")
print_delivery_note("ΠΑΡ-3301", order_a)
print_delivery_note("ΠΑΡ-3302", order_b)
print_delivery_note("ΠΑΡ-3303", order_c)

if needs_manager:
    print("Προσοχή: παραγγελία με πάνω από 3 αντικείμενα, χρειάζεται δεύτερο άτομο")
