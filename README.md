# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## auth-and-security-someone-elses-order

Ένα ενδιάμεσο lab του κεφαλαίου `auth-and-security`. Το token ελέγχεται
σωστά. Ποιος ζητάει τι, δεν το ελέγχει κανείς.

```bash
python3 seed.py             # φτιάχνει τις παραγγελίες δύο πελατών
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 5/8
```

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το service, εδώ δουλεύεις
mint.py      φτιάχνει tokens για να δοκιμάζεις με curl
checks.py    ο βαθμολογητής
```
