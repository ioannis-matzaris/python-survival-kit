# Το ΚΤΕΟ περνάει τα οχήματα της ημέρας και στέλνει ειδοποίηση στον ιδιοκτήτη.


def defects(
    brakes_ok: bool, lights_ok: bool, emissions: float, found: list[str] = []
) -> list[str]:
    if not brakes_ok:
        found.append("φρένα")
    if not lights_ok:
        found.append("φώτα")
    if emissions > 0.30:
        found.append("καυσαέρια")
    return found


def owner_of(plate: str) -> str | None:
    if plate == "ΙΖΡ-4410":
        return "Παπαδοπούλου Μαρία"
    if plate == "ΝΑΤ-2087":
        return "Καραγιάννης Στέλιος"
    if plate == "ΥΒΗ-9931":
        return "Δημητρίου Άννα"
    return None


def notice(plate: str, owner: str) -> str:
    return f"Ειδοποίηση προς {owner}, όχημα {plate}"


def report(plate: str, brakes_ok: bool, lights_ok: bool, emissions: float) -> None:
    problems = defects(brakes_ok, lights_ok, emissions)
    owner = owner_of(plate)
    print(notice(plate, owner))
    if problems:
        for problem in problems:
            print(f"  ! {problem}")
    else:
        print("  καθαρό")


report("ΙΖΡ-4410", False, True, 0.12)
report("ΝΑΤ-2087", True, True, 0.18)
report("ΥΒΗ-9931", True, False, 0.41)
report("ΚΑΤ-5560", True, True, 0.09)
