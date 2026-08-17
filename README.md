# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## caching-and-jobs

Το lab του δέκατου έκτου κεφαλαίου. Ένα service που ξαναδιαβάζει τιμές σε κάθε
κλήση, στέλνει την απόδειξη μέσα από το request, και στέλνει δεύτερη αν το
ίδιο job τρέξει δεύτερη φορά.

```bash
python3 seed.py             # φτιάχνει τη βάση
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
rq worker                   # ο worker, σε δεύτερο terminal
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 4/8
```

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το service, εδώ δουλεύεις
tasks.py     οι δουλειές του worker, εδώ δουλεύεις κι εδώ
checks.py    ο βαθμολογητής
```
