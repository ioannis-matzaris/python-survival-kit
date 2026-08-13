# Το τιμολόγιο του γραφείου: η έκπτωση πέφτει στην καθαρή αξία
# και ο ΦΠΑ υπολογίζεται πάνω σε ό,τι απομένει.

VAT_RATE = 0.24


def discounted_net(net: float, discount_pct: float) -> float:
    """Καθαρή αξία μετά την έκπτωση."""
    return round(net - net * discount_pct / 100, 2)


def invoice_total(net: float, discount_pct: float) -> float:
    """Τελικό ποσό του τιμολογίου, με τον ΦΠΑ."""
    after_discount = discounted_net(net, discount_pct)
    vat = round(net * VAT_RATE, 2)
    return round(after_discount + vat, 2)
