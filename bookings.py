"""Η λογική των κρατήσεων. Έτοιμη, σωστή, και δεν την πειράζεις.

Ό,τι δεν στέκει, το λέει σηκώνοντας ένα δικό της exception.
"""


class BookingError(Exception):
    """Ό,τι μπορεί να πάει στραβά σε μια κράτηση."""


class UnknownWorkshop(BookingError):
    pass


class DuplicateBooking(BookingError):
    pass


class SoldOut(BookingError):
    pass


WORKSHOPS = {
    "PY-101": {"title": "Python από το μηδέν", "seats": 2},
    "API-201": {"title": "APIs στην πράξη", "seats": 0},
}

BOOKED: list[dict] = []


def workshop(code: str) -> dict:
    if code not in WORKSHOPS:
        raise UnknownWorkshop(f"Δεν υπάρχει σεμινάριο με κωδικό {code}")
    return {"code": code, **WORKSHOPS[code]}


def book(code: str, email: str) -> dict:
    details = workshop(code)
    if any(one["code"] == code and one["email"] == email for one in BOOKED):
        raise DuplicateBooking(f"Το {email} έχει ήδη κράτηση στο {code}")
    if details["seats"] - sum(1 for one in BOOKED if one["code"] == code) <= 0:
        raise SoldOut(f"Το σεμινάριο {code} είναι πλήρες")
    booking = {"code": code, "email": email}
    BOOKED.append(booking)
    return booking


def attendance_rate(code: str) -> float:
    details = workshop(code)
    return len([one for one in BOOKED if one["code"] == code]) / details["seats"]
