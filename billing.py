"""Μηνιαία κατανάλωση ανά μετρητή, με χρέωση ανά ζώνη."""

from pathlib import Path

TIER_LIMITS: list[int] = [500, 1000, 2000]
TIER_PRICES: list[float] = [0.09, 0.11, 0.14]


def read_lines(path: str) -> list[str]:
    return Path(path).read_text(encoding="utf-8").splitlines()


def parse_reading(line: str) -> tuple[str, int]:
    fields = line.split(";")
    return fields[0], int(fields[2])


def kwh_per_meter(lines: list[str]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for line in lines:
        meter, kwh = parse_reading(line)
        totals[meter] = totals.get(meter, 0) + kwh
    return totals


def price_for(kwh: int) -> float:
    tier = 0
    while kwh > TIER_LIMITS[tier]:
        tier += 1
    return TIER_PRICES[tier]


def cost_of(kwh: int) -> float:
    try:
        return round(kwh * price_for(kwh), 2)
    except Exception:
        return 0.0


def by_kwh(pair: tuple[str, int]) -> int:
    return pair[1]


def top_consumers(totals: dict[str, int], limit: int) -> list[tuple[str, int]]:
    items = list(totals.items())
    items = items.sort(key=by_kwh, reverse=True)
    return items[:limit]


def main() -> None:
    lines = read_lines("readings.txt")
    totals = kwh_per_meter(lines)
    print(f"Μετρητές: {len(totals)}")
    for meter, kwh in sorted(totals.items()):
        print(f"{meter}: {kwh} kWh, {cost_of(kwh):.2f} ευρώ")
    print(f"Σύνολο χρέωσης: {sum(cost_of(kwh) for kwh in totals.values()):.2f} ευρώ")
    print("Κορυφαίοι τρεις:")
    for meter, kwh in top_consumers(totals, 3):
        print(f"  {meter}: {kwh} kWh")


if __name__ == "__main__":
    main()
