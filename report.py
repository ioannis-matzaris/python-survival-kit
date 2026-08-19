"""Η νυχτερινή αναφορά. Τρέξε: python3 report.py

Κατεβάζει οκτώ κομμάτια από τον προμηθευτή και υπολογίζει τέσσερα σύνολα.
Κάνει και τα δύο ένα ένα, και κάνει πάνω από τέσσερα δευτερόλεπτα.
"""

import time

from work import CHUNKS_TO_CRUNCH, CHUNKS_TO_FETCH, crunch_chunk, fetch_chunk


def download_all() -> list[int]:
    return [fetch_chunk(index) for index in range(CHUNKS_TO_FETCH)]


def crunch_all() -> list[int]:
    return [crunch_chunk(index) for index in range(CHUNKS_TO_CRUNCH)]


if __name__ == "__main__":
    started = time.time()
    downloaded = download_all()
    middle = time.time()
    crunched = crunch_all()
    print(f"Κατέβασμα: {middle - started:.2f}s, {len(downloaded)} κομμάτια")
    print(f"Υπολογισμός: {time.time() - middle:.2f}s, {len(crunched)} σύνολα")
