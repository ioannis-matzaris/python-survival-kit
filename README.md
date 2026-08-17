# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## caching-and-jobs-first-job

Ένα ενδιάμεσο lab του κεφαλαίου `caching-and-jobs`. Η παραγγελία γράφεται σε
δέκα χιλιοστά και ο πελάτης περιμένει τρία δευτερόλεπτα, γιατί το email
φεύγει μέσα από το ίδιο request.

```bash
python3 seed.py             # φτιάχνει τη βάση
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
rq worker                   # ο worker, σε δεύτερο terminal
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 4/8
```

Ο βαθμολογητής τρέχει ο ίδιος έναν worker με `--burst`, οπότε δεν χρειάζεται
να έχεις δικό σου ανοιχτό όταν τον καλείς.

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το service, εδώ δουλεύεις
tasks.py     οι δουλειές του worker, εδώ δουλεύεις κι εδώ
checks.py    ο βαθμολογητής
```
