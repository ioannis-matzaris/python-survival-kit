# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## caching-and-jobs-stale-price

Ένα ενδιάμεσο lab του κεφαλαίου `caching-and-jobs`. Η τιμή μπαίνει μία φορά
στο Redis και μένει εκεί, ακόμα κι όταν το λογιστήριο την αλλάξει.

```bash
python3 seed.py             # φτιάχνει τον τιμοκατάλογο
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 5/7
```

Ο βαθμολογητής ξαναφτιάχνει τη βάση κάθε φορά που τρέχει, οπότε ξεκινάει
πάντα από τις ίδιες τιμές.

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το service, εδώ δουλεύεις
checks.py    ο βαθμολογητής
```
