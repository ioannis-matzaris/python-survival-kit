# Οι προσφορές των καταστημάτων για ένα προϊόν, όπως έρχονται από το feed
# της σύγκρισης τιμών. Η τιμή και τα μεταφορικά έρχονται ξεχωριστά.


def final_price(offer: dict) -> float:
    """Τιμή προϊόντος συν μεταφορικά."""
    return round(offer["price"] + offer["shipping"], 2)


def in_stock(offers: list[dict]) -> list[dict]:
    """Μόνο τα καταστήματα που έχουν το προϊόν διαθέσιμο."""
    return [offer for offer in offers if offer["stock"]]


def set_stock(offers: list[dict], shop: str, value: bool) -> None:
    """Ενημερώνει τη διαθεσιμότητα ενός καταστήματος."""
    for offer in offers:
        if offer["shop"] == shop:
            offer["stock"] = value


def cheapest(offers: list[dict]) -> dict | None:
    """Η φθηνότερη διαθέσιμη προσφορά, ή None όταν δεν υπάρχει καμία."""
    candidates = in_stock(offers)
    if not candidates:
        return None
    return min(candidates, key=lambda offer: offer["price"])
