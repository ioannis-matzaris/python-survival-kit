# Τα κοινόχρηστα της πολυκατοικίας. Κάθε διαμέρισμα πληρώνει με βάση τα χιλιοστά του.
monthly_cost = 840.00

FLATS = [("Α1", 150), ("Α2", 180), ("Β1", 200), ("Β2", 220), ("Γ1", 250)]


def print_share(flat: str, permilles: int) -> None:
    share = monthly_cost * permilles / 1000
    print(f"{flat}: {permilles} χιλιοστά - {share:.2f} €")


print("ΚΟΙΝΟΧΡΗΣΤΑ ΙΟΥΛΙΟΥ")
for flat, permilles in FLATS:
    print_share(flat, permilles)
