# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## caching-and-jobs-slow-endpoint

Ένα ενδιάμεσο lab του κεφαλαίου `caching-and-jobs`. Η αναφορά του μήνα
ξαναδιαβάζει ένα εκατομμύριο γραμμές σε κάθε κλήση.

```bash
python3 seed.py             # φτιάχνει το shop.db, θέλει λίγα δευτερόλεπτα
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 3/7
```

Το Redis τρέχει ήδη στο Codespace. Αν το σταματήσεις, ξεκίνα το ξανά με
`sudo service redis-server start`.

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το service, εδώ δουλεύεις
checks.py    ο βαθμολογητής
```
