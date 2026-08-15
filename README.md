# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## apis-price-search

Ένα ενδιάμεσο lab του κεφαλαίου `apis`. Η αναζήτηση τιμών ενός e-shop
απαντάει σε όλους το ίδιο πράγμα, ό,τι κι αν της ζητήσεις.

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 2/6
```

```text
main.py      το service που σου δίνεται
checks.py    ο βαθμολογητής
```
