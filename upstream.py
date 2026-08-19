"""Ο client του προμηθευτή. Μην τον πειράξεις.

Κάθε κλήση κάνει 0,3 δευτερόλεπτα, όπως και στην πραγματικότητα. Σου δίνει
δύο τρόπους να τον καλέσεις. Ο ένας περιμένει, ο άλλος μπλοκάρει.
"""

import asyncio
import time

DELAY_SECONDS = 0.3


def price_of(sku: str) -> int:
    return 1000 + sum(ord(letter) for letter in sku) % 9000


def fetch_price_blocking(sku: str) -> int:
    time.sleep(DELAY_SECONDS)
    return price_of(sku)


async def fetch_price(sku: str) -> int:
    await asyncio.sleep(DELAY_SECONDS)
    return price_of(sku)
