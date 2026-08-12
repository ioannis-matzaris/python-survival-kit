# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε lab έχει το δικό του branch. Δεν ανοίγεις αυτό το repo με το χέρι: κάθε lab
έχει ένα κουμπί που σου φτιάχνει ένα Codespace στο σωστό branch, με το περιβάλλον
ήδη στημένο.

## io-and-formats-cp1253

Το περιβάλλον του lab «Διάβασε ένα CSV που δεν ανοίγει», ανάμεσα στα μαθήματα του
κεφαλαίου `io-and-formats`.

Το `pelates.csv` είναι πραγματικό export από Excel σε ελληνικά Windows, γραμμένο
σε **cp1253**. Είναι δηλωμένο `binary` στο `.gitattributes`, ώστε το git να μην
του πειράξει ούτε byte.

Το `metatropi.py` το διαβάζει με `encoding="utf-8", errors="replace"`, που κάποιος
πρόσθεσε για να φύγει το `UnicodeDecodeError`. Το script τρέχει καθαρά και τυπώνει
ονόματα από `�`, ενώ το αντίγραφο που γράφει έχει τα ίδια χαμένα ονόματα μέσα.

Δύο πράγματα διορθώνονται. Η πηγή διαβάζεται με `encoding="cp1253"`, χωρίς
`errors=`. Και το `pelates_utf8.csv` γράφεται με `encoding="utf-8-sig"`, ώστε να
το ανοίξει σωστά και το Excel της λογίστριας.

Το `checks_pelates.py` σταματάει αμέσως αν το `pelates.csv` δεν είναι πια τα ίδια
bytes, γιατί τότε το lab δεν δείχνει αυτό που λέει ότι δείχνει:

```bash
git checkout pelates.csv
```

```bash
python3 metatropi.py
python3 checks_pelates.py
```
