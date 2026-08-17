# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## auth-and-security-token-check

Ένα ενδιάμεσο lab του κεφαλαίου `auth-and-security`. Το service διαβάζει το
token και εμπιστεύεται ό,τι βρει μέσα.

```bash
python3 mint.py             # φτιάχνει tokens για δοκιμές
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 2/8
```

```text
main.py      το service, εδώ δουλεύεις
mint.py      φτιάχνει tokens για να δοκιμάζεις με curl
checks.py    ο βαθμολογητής
```
