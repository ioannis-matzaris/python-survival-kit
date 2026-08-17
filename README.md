# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## auth-and-security

Το lab του δέκατου έβδομου κεφαλαίου. Ένα API που δουλεύει ολόκληρο, και δεν
προστατεύει τίποτα: κωδικοί σε καθαρό κείμενο, token που δεν ελέγχεται,
παραγγελίες που τις βλέπει ο καθένας.

```bash
python3 seed.py             # φτιάχνει τη βάση
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 3/8
```

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
main.py      το API, εδώ δουλεύεις
mint.py      φτιάχνει tokens για να δοκιμάζεις με curl
checks.py    ο βαθμολογητής
```
