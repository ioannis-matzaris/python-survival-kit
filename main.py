"""Το προφίλ του χρήστη. Τρέξε: uvicorn main:app --reload

Διαβάζει το token και εμπιστεύεται ό,τι βρει μέσα.
"""

import jwt
from fastapi import FastAPI, Header, HTTPException

SECRET = "to-mystiko-tou-service-pou-den-fevgei-pote"
ALGORITHM = "HS256"

app = FastAPI()

PEOPLE = {
    1: "Μαρία Παπαδοπούλου",
    2: "Γιώργος Δήμου",
}


def current_user(authorization: str = Header(default="")) -> int:
    token = authorization.removeprefix("Bearer ").strip()
    payload = jwt.decode(token, options={"verify_signature": False})
    return int(payload["sub"])


@app.get("/me")
def me(authorization: str = Header(default="")) -> dict[str, str]:
    user_id = current_user(authorization)
    name = PEOPLE.get(user_id)
    if name is None:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει τέτοιος χρήστης")
    return {"id": str(user_id), "name": name}
