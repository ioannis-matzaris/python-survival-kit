"""Έλεγχοι ελληνικών αναγνωριστικών. Έτοιμοι, δεν τους πειράζεις."""


def afm_is_valid(afm: str) -> bool:
    if len(afm) != 9 or not afm.isdigit():
        return False
    total = 0
    for position, digit in enumerate(afm[:8]):
        total += int(digit) * 2 ** (8 - position)
    return total % 11 % 10 == int(afm[8])
