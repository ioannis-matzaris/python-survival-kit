class Student:
    def __init__(self, name: str, base: float) -> None:
        self.name = name
        self.base = base

    def fee(self) -> float:
        return round(self.base, 2)


class SiblingStudent(Student):
    def fee(self) -> float:
        return round(super().fee() * 0.90, 2)


class ScholarshipStudent(Student):
    def fee(self) -> float:
        return round(super().fee() * 0.75, 2)


class SiblingScholarshipStudent(ScholarshipStudent):
    def fee(self) -> float:
        return round(super().fee() * 0.90, 2)


class StudentWithBus(Student):
    def fee(self) -> float:
        return round(super().fee() + 40.0, 2)


class SiblingStudentWithBus(SiblingStudent):
    def fee(self) -> float:
        return round(super().fee() + 40.0, 2)


class FeeFormatter:
    def title(self) -> str:
        return "ΔΙΔΑΚΤΡΑ ΜΑΡΤΙΟΥ"

    def line(self, name: str, amount: float) -> str:
        return f"{name:<22}{amount:>9.2f}"


students: list[Student] = [
    Student("Ελένη Παπαδάκη", 180.0),
    SiblingStudent("Γιώργος Αντωνίου", 180.0),
    ScholarshipStudent("Μαρία Δημητρίου", 220.0),
    SiblingScholarshipStudent("Νίκος Σαββίδης", 220.0),
    StudentWithBus("Άννα Βλαχάκη", 180.0),
    SiblingStudentWithBus("Θοδωρής Καρράς", 220.0),
]

print(FeeFormatter().title())
print()

total = 0.0
for student in students:
    total = total + student.fee()
    print(FeeFormatter().line(student.name, student.fee()))

print()
print(FeeFormatter().line("ΣΥΝΟΛΟ", round(total, 2)))
