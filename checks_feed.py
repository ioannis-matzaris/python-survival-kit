import json
import subprocess
import sys

PROBE = r'''
import contextlib
import io
import json

buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(buffer):
        import feed
except Exception as exc:
    print(json.dumps({"import_error": f"{type(exc).__name__}: {exc}"}))
    raise SystemExit(0)

answer = {}
printed = io.StringIO()

with contextlib.redirect_stdout(printed):
    try:
        answer["cheapest"] = [
            list(feed.cheapest_for(feed.OFFERS, "ΠΡ-1001")),
            list(feed.cheapest_for(feed.OFFERS, "ΠΡ-1002")),
            list(feed.cheapest_for(feed.OFFERS, "ΠΡ-1003")),
        ]
    except Exception as exc:
        answer["cheapest_error"] = f"{type(exc).__name__}: {exc}"

    family = {}
    for name in ["FeedError", "OfferPriceError", "OfferFieldsError"]:
        kind = getattr(feed, name, None)
        if isinstance(kind, type) and issubclass(kind, BaseException):
            family[name] = True
        else:
            family[name] = False
    answer["family"] = family
    if all(family.values()):
        base = feed.FeedError
        answer["base_is_exception"] = issubclass(base, Exception) and base is not Exception
        answer["price_in_family"] = issubclass(feed.OfferPriceError, base)
        answer["fields_in_family"] = issubclass(feed.OfferFieldsError, base)
        answer["two_names"] = feed.OfferPriceError is not feed.OfferFieldsError

    for key, row in [("price", "ΚΑΤ-05;ΠΡ-1002;35,90"), ("fields", "ΚΑΤ-06;ΠΡ-1003")]:
        try:
            feed.parse_offer(row)
            answer[key] = {"raised": "τίποτα"}
        except Exception as exc:
            answer[key] = {
                "raised": type(exc).__name__,
                "message": str(exc),
                "cause": type(exc.__cause__).__name__ if exc.__cause__ is not None else "",
            }

print(json.dumps(answer, ensure_ascii=False))
'''

EXPECTED_CHEAPEST = [
    ["ΚΑΤ-02", 89.90],
    ["ΚΑΤ-03", 7.90],
    ["ΚΑΤ-01", 12.00],
]

EXPECTED_OUTPUT = [
    "ΦΘΗΝΟΤΕΡΟ ΚΑΤΑΣΤΗΜΑ ΑΝΑ ΠΡΟΪΟΝ",
    "ΠΡ-1001: ΚΑΤ-02 με 89.90 ευρώ",
    "ΠΡ-1002: ΚΑΤ-03 με 7.90 ευρώ",
    "ΠΡ-1003: ΚΑΤ-01 με 12.00 ευρώ",
    "ΕΛΕΓΧΟΣ ΝΕΩΝ ΠΡΟΣΦΟΡΩΝ",
    "Προσφορά εκτός: Το ΚΑΤ-05 έδωσε τιμή '35,90' που δεν είναι αριθμός",
    "Προσφορά εκτός: Η προσφορά 'ΚΑΤ-06;ΠΡ-1003' δεν έχει τρία πεδία",
    "Δεκτές 2 από 4 προσφορές",
]

probe = subprocess.run(
    [sys.executable, "-c", PROBE], capture_output=True, text=True, stdin=subprocess.DEVNULL
)
if "BdbQuit" in probe.stdout or "BdbQuit" in probe.stderr:
    facts = {"import_error": "έμεινε ένα breakpoint() στον κώδικα, σβήσ' το"}
else:
    try:
        facts = json.loads(probe.stdout.strip().splitlines()[-1])
    except Exception:
        tail = probe.stderr.strip().splitlines()
        facts = {"import_error": tail[-1] if tail else "καμία απάντηση"}

results: list[tuple[bool, str, str]] = []


def report(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


label = "Η cheapest_for δίνει το πραγματικά φθηνότερο κατάστημα"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
elif "cheapest_error" in facts:
    report(False, label, str(facts["cheapest_error"]))
elif facts["cheapest"] != EXPECTED_CHEAPEST:
    report(False, label, f"περίμενα {EXPECTED_CHEAPEST} και πήρα {facts['cheapest']}")
else:
    report(True, label)

label = "Τα τρία σφάλματα υπάρχουν και είναι μία οικογένεια"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
else:
    family = facts.get("family", {})
    missing = [name for name, found in family.items() if not found]
    if missing:
        report(False, label, f"δεν βρήκα σφάλμα με όνομα {', '.join(missing)}")
    elif not facts.get("base_is_exception"):
        report(False, label, "η FeedError πρέπει να κληρονομεί από Exception")
    elif not facts.get("price_in_family") or not facts.get("fields_in_family"):
        report(False, label, "τα δύο ειδικά σφάλματα πρέπει να κληρονομούν από FeedError")
    elif not facts.get("two_names"):
        report(False, label, "χρειάζονται δύο ξεχωριστά ονόματα, όχι ένα με δύο ετικέτες")
    else:
        report(True, label)

label = "Η parse_offer πετάει OfferPriceError και κρατάει από κάτω την αρχική αιτία"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
else:
    price = facts.get("price", {})
    if price.get("raised") != "OfferPriceError":
        report(False, label, f"περίμενα OfferPriceError και πήρα {price.get('raised')}")
    elif "ΚΑΤ-05" not in price.get("message", "") or "35,90" not in price.get("message", ""):
        report(False, label, f"το μήνυμα θέλει και το κατάστημα και την τιμή: {price.get('message')!r}")
    elif price.get("cause") != "ValueError":
        report(False, label, "λείπει το from error, δεν φαίνεται η αρχική ValueError")
    else:
        report(True, label)

label = "Η parse_offer πετάει OfferFieldsError με ολόκληρη τη γραμμή στο μήνυμα"
if "import_error" in facts:
    report(False, label, str(facts["import_error"]))
else:
    fields = facts.get("fields", {})
    if fields.get("raised") != "OfferFieldsError":
        report(False, label, f"περίμενα OfferFieldsError και πήρα {fields.get('raised')}")
    elif "ΚΑΤ-06;ΠΡ-1003" not in fields.get("message", ""):
        report(False, label, f"το μήνυμα δεν έχει μέσα τη γραμμή: {fields.get('message')!r}")
    else:
        report(True, label)

label = "Το feed.py τρέχει ως το τέλος και τυπώνει τις σωστές γραμμές"
run = subprocess.run(
    [sys.executable, "feed.py"], capture_output=True, text=True, stdin=subprocess.DEVNULL
)
if "BdbQuit" in run.stderr or "(Pdb)" in run.stdout:
    report(False, label, "έμεινε ένα breakpoint() μέσα στο feed.py, σβήσ' το")
elif run.returncode != 0:
    tail = run.stderr.strip().splitlines()
    report(False, label, tail[-1] if tail else "άγνωστο σφάλμα")
else:
    output = [line.strip() for line in run.stdout.splitlines() if line.strip()]
    if output == EXPECTED_OUTPUT:
        report(True, label)
    else:
        report(False, label, f"περίμενα {EXPECTED_OUTPUT} και πήρα {output}")

passed = 0
for ok, text, detail in results:
    print(f"{'✅' if ok else '❌'} {text}" + ("" if ok else f" - {detail}"))
    passed += ok
print()
print(f"{passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
