import json

# Το εργαλείο του λογιστηρίου: βγάζει τη σύνοψη ενός πελάτη από το export
# των τιμολογίων της περιόδου.
SOURCE = "timologia.json"
AFM = "800451233"


def load_invoices(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["timologia"]


def invoices_for(invoices: list[dict[str, str]], afm: str) -> list[dict[str, str]]:
    return [invoice for invoice in invoices if invoice["afm"] == afm]


def summary_for(mine: list[dict[str, str]], afm: str) -> dict[str, object]:
    total = 0.0
    for invoice in mine:
        total += float(invoice["poso"])
    return {
        "afm": afm,
        "pelatis": mine[0]["pelatis"],
        "plithos": len(mine),
        "synolo": total,
    }


def main() -> None:
    invoices = load_invoices(SOURCE)
    mine = invoices_for(invoices, AFM)
    print(summary_for(mine, AFM))


main()
