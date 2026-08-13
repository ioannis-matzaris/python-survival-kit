# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε lab έχει το δικό του branch. Δεν ανοίγεις αυτό το repo με το χέρι: κάθε lab
έχει ένα κουμπί που σου φτιάχνει ένα Codespace στο σωστό branch, με το περιβάλλον
ήδη στημένο.

## dependencies-constraints

Το περιβάλλον του lab «Υπολόγισε τι επιτρέπει ο περιορισμός σου», ανάμεσα στα
μαθήματα του κεφαλαίου `dependencies`. Το `ekdoseis.json` είναι καταγεγραμμένη
έξοδος του `pip index versions --pre` για τέσσερα πραγματικά packages
(`requests`, `urllib3`, `tabulate`, `idna`), μαζί με τα pre-release τους. Το
`constraints.txt` έχει τους περιορισμούς του project. Το `epilogi.py` υποτίθεται
ότι λέει τι θα διάλεγε το pip, αλλά συγκρίνει τις εκδόσεις σαν κείμενο και
αγνοεί εντελώς το `~=`.

Η λίστα εκδόσεων είναι μέσα στο branch, οπότε τίποτα εδώ δεν χρειάζεται internet
και η απάντηση είναι πάντα η ίδια. Δεν γίνεται κανένα `pip install`.

Το `checks_epilogi.py` τρέχει το `epilogi.py` και πάνω σε άλλα δεδομένα, σε
προσωρινό φάκελο με δικό του `ekdoseis.json` και `constraints.txt`, οπότε μια
γραμμένη στο χέρι απάντηση παίρνει 0/4.

```bash
python3 epilogi.py           # οι επιλογές, όπως τις βγάζει τώρα
python3 checks_epilogi.py    # οι έλεγχοι, ξεκινάς από 0/4
```
