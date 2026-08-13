# Η ημερήσια υπενθύμιση του λογιστηρίου για τα ληξιπρόθεσμα τιμολόγια.
# Το send_sms είναι η μόνη συνάρτηση εδώ που μιλάει με τον έξω κόσμο:
# στο πραγματικό project καλεί τον πάροχο, εδώ γράφει στο apestalmena.log
# ώστε να βλέπεις τι θα είχε φύγει. Κάθε γραμμή του είναι ένα χρεωμένο SMS.

LOG = "apestalmena.log"


def send_sms(phone: str, text: str) -> None:
    """Παραδίδει το μήνυμα στον πάροχο. Κάθε κλήση χρεώνεται."""
    with open(LOG, "a", encoding="utf-8") as log:
        log.write(f"{phone}\t{text}\n")


def message_for(invoice: dict) -> str:
    """Το κείμενο της υπενθύμισης για ένα τιμολόγιο."""
    return (
        f"Το τιμολόγιο {invoice['number']} των {invoice['amount']:.2f} ευρώ "
        f"έληξε στις {invoice['due']}."
    )


def remind_overdue(invoices: list[dict], today: str) -> int:
    """Στέλνει μία υπενθύμιση για κάθε ληξιπρόθεσμο απλήρωτο τιμολόγιο."""
    sent = 0
    for invoice in invoices:
        if invoice["due"] < today:
            send_sms(invoice["phone"], message_for(invoice))
            sent += 1
    return sent
