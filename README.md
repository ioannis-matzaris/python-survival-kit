# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## production-code-config

Ένα service που ξεκινάει ό,τι κι αν του δώσεις. Χωρίς βάση, με θύρα που δεν
είναι αριθμός, με το `DEBUG=false` να σημαίνει αληθές. Και με το κλειδί του
παρόχου γραμμένο μέσα στον κώδικα.

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 2/12
```

```text
.env.example  οι μεταβλητές που χρειάζεται το service
main.py       το service, εδώ δουλεύεις
checks.py     ο βαθμολογητής
```
