"""Η δουλειά της αναφοράς. Μην την πειράξεις.

Δύο είδη. Το ένα κατεβάζει και περιμένει, το άλλο υπολογίζει. Και τα δύο
γράφουν σε ένα αρχείο ποιο process τα έτρεξε, για να φαίνεται μετά.
"""

import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHUNKS_TO_FETCH = 8
CHUNKS_TO_CRUNCH = 4


def _note(kind: str) -> None:
    with open(HERE / f"pids-{kind}.txt", "a", encoding="utf-8") as marks:
        marks.write(f"{os.getpid()}\n")


def fetch_chunk(index: int) -> int:
    _note("fetch")
    time.sleep(0.25)
    return index * 100


def crunch_chunk(index: int) -> int:
    _note("crunch")
    total = 0
    for number in range(12_000_000):
        total += number % (index + 2)
    return total
