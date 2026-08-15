# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## api-design

Το lab του δέκατου τέταρτου κεφαλαίου. Ένα service κρατήσεων που πιάνει μόνο
του κάθε σφάλμα και απαντάει σε όλα «όλα καλά».

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 2/8
```

```text
main.py       τα endpoints, εδώ δουλεύεις
bookings.py   η λογική των κρατήσεων, έτοιμη, δεν την πειράζεις
checks.py     ο βαθμολογητής
```
