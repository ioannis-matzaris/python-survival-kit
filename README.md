# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## api-design-status-codes

Ένα ενδιάμεσο lab του κεφαλαίου `api-design`. Το service των παραγγελιών
απαντάει σε όλα, και σε όλα απαντάει «όλα καλά».

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 3/8
```

```text
main.py      το service που σου δίνεται
checks.py    ο βαθμολογητής
```
