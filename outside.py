"""Ό,τι δεν είναι δικό σου: ο πάροχος και ο υπολογισμός. Μην τα πειράξεις.

Ο πάροχος αργεί 0,2 δευτερόλεπτα σε κάθε κλήση. Σου δίνει δύο πόρτες, μία που
περιμένει και μία που μπλοκάρει. Ο υπολογισμός καίει επεξεργαστή, όποιος κι αν
τον τρέξει.
"""

import asyncio
import time

DELAY_SECONDS = 0.2


def occupancy_of(hall: str) -> int:
    return sum(ord(letter) for letter in hall) % 100


def fetch_occupancy_blocking(hall: str) -> int:
    time.sleep(DELAY_SECONDS)
    return occupancy_of(hall)


async def fetch_occupancy(hall: str) -> int:
    await asyncio.sleep(DELAY_SECONDS)
    return occupancy_of(hall)


def crunch(seed: int) -> int:
    total = 0
    for number in range(12_000_000):
        total += number % (seed + 2)
    return total
