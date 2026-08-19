# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## concurrency-double-booking

Δέκα κομμάτια στο ράφι και είκοσι πελάτες που πατάνε «Αγορά» την ίδια στιγμή.
Το API ελέγχει το απόθεμα πριν το μειώσει, και περνάνε και οι είκοσι.

```bash
python3 seed.py             # φτιάχνει τη βάση
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 6/9
```

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το API, εδώ δουλεύεις
checks.py    ο βαθμολογητής
```
