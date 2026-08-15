# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## api-design-signup-payload

Ένα ενδιάμεσο lab του κεφαλαίου `api-design`. Η εγγραφή πελάτη δέχεται ό,τι
της στείλεις, και ό,τι δεχτεί το πιστεύει.

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 2/8
```

```text
main.py        το service που σου δίνεται
greek_ids.py   ο έλεγχος ΑΦΜ, έτοιμος
checks.py      ο βαθμολογητής
```
