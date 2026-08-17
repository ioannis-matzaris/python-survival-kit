"""Φτιάχνει tokens για δοκιμές. Τρέξε: python3 mint.py"""

from datetime import datetime, timedelta, timezone

import jwt

SECRET = "to-mystiko-tou-service-pou-den-fevgei-pote"


def token_for(user_id: int, minutes: int = 30) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user_id), "exp": now + timedelta(minutes=minutes), "iat": now},
        SECRET,
        algorithm="HS256",
    )


if __name__ == "__main__":
    print("έγκυρο       ", token_for(1))
    print("ληγμένο      ", token_for(1, minutes=-5))
