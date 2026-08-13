import ypenthymisi

INVOICES = [
    {
        "number": "ΤΔΑ-1041",
        "amount": 248.00,
        "due": "2026-03-10",
        "phone": "6971234567",
        "paid": False,
    },
    {
        "number": "ΤΔΑ-1042",
        "amount": 96.50,
        "due": "2026-03-18",
        "phone": "6944556677",
        "paid": True,
    },
    {
        "number": "ΤΔΑ-1043",
        "amount": 512.40,
        "due": "2026-03-25",
        "phone": "6988112233",
        "paid": False,
    },
    {
        "number": "ΤΔΑ-1044",
        "amount": 74.00,
        "due": "2026-04-10",
        "phone": "6900111222",
        "paid": False,
    },
]


def test_remind_overdue_runs():
    ypenthymisi.remind_overdue(INVOICES, "2026-04-01")


def test_message_for_returns_text(monkeypatch):
    monkeypatch.setattr(ypenthymisi, "message_for", lambda invoice: "Υπενθύμιση.")
    assert ypenthymisi.message_for(INVOICES[0]) == "Υπενθύμιση."


def test_send_sms_takes_a_phone_and_a_text():
    ypenthymisi.send_sms("6971234567", "δοκιμή")
