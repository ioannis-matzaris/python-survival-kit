CATALOGUE = [
    ("ΒΙΒ-101", "Ο Μεγάλος Περίπατος", 3),
    ("ΒΙΒ-204", "Το Κιβώτιο", 2),
    ("ΒΙΒ-315", "Άξιον Εστί", 1),
    ("ΒΙΒ-420", "Η Φόνισσα", 4),
]

BORROWINGS = [("ΒΙΒ-101", 2), ("ΒΙΒ-204", 3), ("ΒΙΒ-420", 4)]
CLASS_BORROWINGS = [("ΒΙΒ-315", 2)]
RETURNS = [("ΒΙΒ-101", 1)]


class Library:
    def __init__(self) -> None:
        self.copies: list[tuple[str, int]] = []

    def add_title(self, code: str, copies: int) -> None:
        self.copies.append((code, copies))


library = Library()
for code, title, copies in CATALOGUE:
    library.add_title(code, copies)

# ο δανεισμός από το γραφείο
for code, count in BORROWINGS:
    for index, (item_code, available) in enumerate(library.copies):
        if item_code == code:
            if available >= count:
                library.copies[index] = (item_code, available - count)
            else:
                print(f"{code}: δεν υπάρχουν {count} διαθέσιμα αντίτυπα")

# ο δανεισμός για ολόκληρο τμήμα, γράφτηκε τον Νοέμβριο σε άλλο σημείο
for code, count in CLASS_BORROWINGS:
    for index, (item_code, available) in enumerate(library.copies):
        if item_code == code:
            library.copies[index] = (item_code, available - count)

# οι επιστροφές της ημέρας
for code, count in RETURNS:
    for index, (item_code, available) in enumerate(library.copies):
        if item_code == code:
            library.copies[index] = (item_code, available + count)

print()
print("ΔΙΑΘΕΣΙΜΑ ΑΝΤΙΤΥΠΑ")
print()
for code, title, copies in CATALOGUE:
    for item_code, available in library.copies:
        if item_code == code:
            print(f"{code}  {title:<24}{available:>4}")
