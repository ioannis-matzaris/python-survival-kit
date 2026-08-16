# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## databases

Το lab του δέκατου πέμπτου κεφαλαίου. Το data layer ενός e-shop, με τρεις
συναρτήσεις που δουλεύουν και τρία διαφορετικά προβλήματα μέσα τους.

```bash
python3 seed.py      # φτιάχνει το shop.db από την αρχή
python3 checks.py    # ο βαθμολογητής, ξεκινάς από 3/8
```

```text
models.py    το σχήμα, έτοιμο, δεν το πειράζεις
shop.py      το data layer, εδώ δουλεύεις
seed.py      φτιάχνει τη βάση
checks.py    ο βαθμολογητής
```
