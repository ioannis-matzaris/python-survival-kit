# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε κεφάλαιο έχει το δικό του branch, με το όνομα του κεφαλαίου. Δεν ανοίγεις
αυτό το repo με το χέρι: το lab κάθε κεφαλαίου έχει ένα κουμπί που σου φτιάχνει
ένα Codespace στο σωστό branch, με το περιβάλλον ήδη στημένο.

## io-and-formats

Το lab του όγδοου κεφαλαίου. Ζητάς πρόγνωση καιρού από ένα δημόσιο API και
βγάζεις ένα report ανά μέρα.

```bash
python3 fetch.py     # μία φορά, γεμίζει το data/athens.json
python3 report.py    # όσες φορές θέλεις, χωρίς δίκτυο
python3 checks.py    # οι έλεγχοι
```

Τα δεδομένα και το report δεν μπαίνουν στο git. Το `checks.py` δεν βγαίνει στο
internet: ξαναϋπολογίζει τα min και max από το αρχείο που κατέβασες.
