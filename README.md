# python-survival-kit

Τα lab environments του course «Python Survival Kit».

Κάθε lab έχει το δικό του branch. Δεν ανοίγεις αυτό το repo με το χέρι: κάθε lab
έχει ένα κουμπί που σου φτιάχνει ένα Codespace στο σωστό branch, με το περιβάλλον
ήδη στημένο.

## dependencies-site-packages

Το περιβάλλον του lab «Διάβασε τι άφησε στον δίσκο το pip», ανάμεσα στα μαθήματα
του κεφαλαίου `dependencies`. Ο φάκελος `site-packages/` είναι πραγματικός: βγήκε
από ένα `pip install --target site-packages --no-compile "tabulate==0.9.0"
"python-dateutil==2.9.0.post0"` και μπήκε αυτούσιος στο branch, με τα `.dist-info`
του όπως τα έγραψε το pip (`METADATA`, `RECORD`, `WHEEL`, `INSTALLER`,
`top_level.txt`). Το `apografi.py` υποτίθεται ότι απαντάει «τι έχω εγκατεστημένο»,
αλλά τυπώνει σκέτα τα ονόματα των φακέλων.

Τίποτα εδώ δεν χρειάζεται internet, ούτε το lab ούτε ο έλεγχος: όλα τα δεδομένα
είναι μέσα στο branch. Δεν γίνεται και δεν χρειάζεται κανένα `pip install`.

Το `checks_apografi.py` τρέχει το `apografi.py` δύο φορές: μία εδώ, και μία μέσα σε
προσωρινό φάκελο με δικό του `site-packages` και άλλα packages, οπότε μια
γραμμένη στο χέρι απάντηση παίρνει 0/4.

```bash
python3 apografi.py          # η απογραφή, όπως είναι τώρα
python3 checks_apografi.py   # οι έλεγχοι, ξεκινάς από 0/4
```
