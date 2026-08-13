# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε lab έχει το δικό του branch. Δεν ανοίγεις αυτό το repo με το χέρι: κάθε lab
έχει ένα κουμπί που σου φτιάχνει ένα Codespace στο σωστό branch, με το περιβάλλον
ήδη στημένο.

## dependencies-drift

Το περιβάλλον του lab «Βρες γιατί τα δύο μηχανήματα διαφέρουν», ανάμεσα στα
μαθήματα του κεφαλαίου `dependencies`. Το `apaitiseis.txt` είναι η λίστα
εξαρτήσεων του project, γραμμένη στο χέρι και χωρίς εκδόσεις. Τα
`freeze-maria.txt` και `freeze-giorgos.txt` είναι δύο καταγεγραμμένες εξόδους
`pip freeze` από δύο μηχανήματα που εγκατέστησαν από την ίδια λίστα σε άλλη
στιγμή. Το `diafores.py` υποτίθεται ότι δείχνει τι διαφέρει, αλλά συγκρίνει
γραμμές αντί για packages.

Όλα τα δεδομένα είναι μέσα στο branch. Δεν χρειάζεται internet, ούτε το lab ούτε
ο έλεγχος, και δεν γίνεται κανένα `pip install`.

Το `checks_diafores.py` τρέχει το `diafores.py` και πάνω σε άλλα δύο αρχεία, σε
προσωρινό φάκελο με δικό του `apaitiseis.txt`, οπότε μια γραμμένη στο χέρι
απάντηση δεν περνάει.

```bash
python3 diafores.py freeze-maria.txt freeze-giorgos.txt   # η σύγκριση, όπως είναι τώρα
python3 checks_diafores.py                                # οι έλεγχοι, ξεκινάς από 0/4
```
