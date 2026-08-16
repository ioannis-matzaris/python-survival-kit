# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## auth-and-security-passwords

Ένα ενδιάμεσο lab του κεφαλαίου `auth-and-security`. Η εγγραφή και η σύνδεση
δουλεύουν, και ο κωδικός του καθενός είναι διαβάσιμος από όποιον ανοίξει τη
βάση.

```bash
python3 seed.py      # φτιάχνει το users.db από την αρχή
python3 checks.py    # ο βαθμολογητής, ξεκινάς από 4/9
```

```text
seed.py      φτιάχνει τη βάση, τρέξ' το πρώτο
users.py     η εγγραφή και η σύνδεση, εδώ δουλεύεις
checks.py    ο βαθμολογητής
```
