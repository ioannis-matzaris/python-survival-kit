# Ο πελάτης κάθε παραγγελίας, όπως ήρθε από το CRM.
CUSTOMERS: dict[str, str] = {
    "ΠΑΡ-4401": "Παπαδοπούλου Μαρία",
    "ΠΑΡ-4402": "Καραγιάννης Στέλιος",
}


def customer_of(order: str) -> str:
    name = CUSTOMERS.get(order)
    return name.upper()


def label_for(order: str) -> str:
    return f"{order} -> {customer_of(order)}"


for code in ["ΠΑΡ-4401", "ΠΑΡ-4402", "ΠΑΡ-4403"]:
    print(label_for(code))
