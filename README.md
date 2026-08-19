# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## production-code-timeouts

Ένα service που ρωτάει τον πάροχο για ισοτιμίες. Όταν ο πάροχος αργεί,
περιμένει όσο χρειαστεί. Όταν αποτυγχάνει, ξαναρωτάει αμέσως, όσες φορές
χρειαστεί.

```bash
uvicorn upstream:app --port 8001   # ο πάροχος, σε δικό του terminal
uvicorn main:app --reload          # το service σου, στο http://127.0.0.1:8000
python3 checks.py                  # ο βαθμολογητής, ξεκινάς από 3/10
```

Ο βαθμολογητής σηκώνει και τα δύο μόνος του, οπότε σταμάτα τα δικά σου πριν
τον τρέξεις.

```text
upstream.py   ο πάροχος, μην τον πειράξεις
main.py       το service, εδώ δουλεύεις
checks.py     ο βαθμολογητής
```
