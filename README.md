# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## production-code-logs

Ένα service που λέει τι κάνει, με `print`, σε ελεύθερο κείμενο, χωρίς να λέει
ποιανού request ήταν η κάθε γραμμή. Διαβάζεται μια χαρά όσο το κοιτάς εσύ.

```bash
uvicorn main:app --reload   # το service σου, στο http://127.0.0.1:8000
python3 checks.py           # ο βαθμολογητής, ξεκινάς από 3/11
```

```text
provider.py   ο πάροχος πληρωμών, μην τον πειράξεις
main.py       το service, εδώ δουλεύεις
checks.py     ο βαθμολογητής
```
