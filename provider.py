"""Ο πάροχος πληρωμών. Μην τον πειράξεις.

Επιστρέφει χρήματα για ό,τι υπάρχει, και σκάει για ό,τι δεν υπάρχει, όπως
ακριβώς θα έκανε και ο αληθινός.
"""

REFUNDABLE = {1001: 4520, 1002: 1990}


class ProviderError(RuntimeError):
    pass


def refund(order_id: int) -> int:
    if order_id not in REFUNDABLE:
        raise ProviderError(f"Η παραγγελία {order_id} δεν είναι επιστρέψιμη")
    return REFUNDABLE[order_id]
