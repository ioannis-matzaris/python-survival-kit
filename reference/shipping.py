import math

# οι σταθερές του e-shop
FREE_SHIPPING_FROM = 40.0
BASE_COST = 3.20
EXTRA_PER_KG = 0.90
INCLUDED_KG = 2.0


def subtotal(items: list[dict]) -> float:
    """Αξία των προϊόντων, χωρίς μεταφορικά."""
    total = 0.0
    for item in items:
        total += item["price"] * item["quantity"]
    return round(total, 2)


def shipping_cost(subtotal_amount: float, weight_kg: float) -> float:
    """Μεταφορικά για ένα δέμα."""
    if subtotal_amount >= FREE_SHIPPING_FROM:
        return 0.0
    extra_kg = max(weight_kg - INCLUDED_KG, 0.0)
    return round(BASE_COST + EXTRA_PER_KG * math.ceil(extra_kg), 2)


def apply_coupon(amount: float, code: str) -> float:
    """Εφαρμόζει κουπόνι στο ποσό."""
    if code == "ΚΑΛΟΚΑΙΡΙ10":
        discounted = amount * 0.90
    elif code == "ΠΡΩΤΗ5":
        discounted = amount - 5.0
    else:
        raise ValueError(f"Άγνωστος κωδικός κουπονιού: {code}")
    return round(max(discounted, 0.0), 2)
