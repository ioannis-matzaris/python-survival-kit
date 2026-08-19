# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## concurrency-ten-requests

Ένα API που ρωτάει τον προμηθευτή για τιμές. Κάθε κλήση κάνει 0,3
δευτερόλεπτα, και δέκα SKU κάνουν τρία. Όσο τα περιμένει, το service δεν
απαντάει σε τίποτα άλλο.

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 4/7
```

```text
upstream.py   ο client του προμηθευτή, μην τον πειράξεις
main.py       το API, εδώ δουλεύεις
checks.py     ο βαθμολογητής
```
