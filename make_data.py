"""Φτιάχνει το readings.txt. Τα δεδομένα δεν μπαίνουν στο git, ο κώδικας που τα φτιάχνει ναι."""

from pathlib import Path

READINGS: dict[str, list[int]] = {
    "ΜΤ-1001": [180, 210, 195],
    "ΜΤ-1002": [420, 390, 445],
    "ΜΤ-1003": [95, 120, 88],
    "ΜΤ-1004": [610, 580, 640],
    "ΜΤ-1005": [310, 275, 330],
    "ΜΤ-1006": [150, 165, 140],
    "ΜΤ-1007": [980, 1120, 1040],
    "ΜΤ-1008": [230, 260, 245],
    "ΜΤ-1009": [520, 495, 555],
    "ΜΤ-1010": [75, 90, 82],
    "ΜΤ-1011": [340, 315, 360],
    "ΜΤ-1012": [700, 745, 690],
}

MONTHS: list[str] = ["2024-01", "2024-02", "2024-03"]

# Οι μετρήσεις του ΜΤ-1011 για Φεβρουάριο και Μάρτιο ήρθαν από άλλο export.
DIRTY: set[tuple[str, str]] = {("ΜΤ-1011", "2024-02"), ("ΜΤ-1011", "2024-03")}


def main() -> None:
    lines: list[str] = []
    for meter, monthly in READINGS.items():
        for month, kwh in zip(MONTHS, monthly):
            name = f"{meter} " if (meter, month) in DIRTY else meter
            lines.append(f"{name};{month};{kwh}")
    Path("readings.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Έγραψα readings.txt με {len(lines)} γραμμές")


if __name__ == "__main__":
    main()
