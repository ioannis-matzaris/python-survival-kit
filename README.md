# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## apis-thin-handler

Ένα ενδιάμεσο lab του κεφαλαίου `apis`. Ο υπολογισμός του λογαριασμού είναι
σωστός και ζει ολόκληρος μέσα στο endpoint, οπότε δοκιμάζεται μόνο με HTTP.

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 3/7
```

```text
main.py      το service που σου δίνεται
checks.py    ο βαθμολογητής
```
