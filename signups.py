# Οι δηλώσεις για τις δύο δράσεις του σχολείου, με τη σειρά που ήρθαν στη γραμματεία.
# ΑΜ;δράση
SIGNUPS = [
    "7412;ΕΚΔΡΟΜΗ",
    "7315;ΟΜΙΛΟΣ",
    "7208;ΕΚΔΡΟΜΗ",
    "7412;ΟΜΙΛΟΣ",
    "7561;ΕΚΔΡΟΜΗ",
    "7315;ΕΚΔΡΟΜΗ",
    "7208;ΟΜΙΛΟΣ",
    "7690;ΕΚΔΡΟΜΗ",
    "7561;ΟΜΙΛΟΣ",
]

# Το μητρώο των μαθητών. ΑΜ;όνομα;τμήμα
STUDENTS = [
    "7208;Ελένη Βασιλείου;Β2",
    "7315;Νίκος Παπαδάκης;Γ1",
    "7412;Μαρία Ιωάννου;Α3",
    "7561;Θανάσης Κούρτης;Β1",
    "7690;Δήμητρα Σαββίδου;Γ2",
]


def trip_queue(signups: list[str]) -> list[str]:
    # Οι θέσεις της εκδρομής είναι λιγότερες από τους μαθητές, οπότε μετράει η σειρά.
    queue: set[str] = set()
    for line in signups:
        am, activity = line.split(";")
        if activity == "ΕΚΔΡΟΜΗ":
            queue.add(am)
    return list(queue)


def distinct_students(signups: list[str]) -> int:
    # Πόσα διαφορετικά παιδιά δήλωσαν οτιδήποτε.
    seen: list[str] = []
    for line in signups:
        seen.append(line.split(";")[0])
    return len(seen)


queue = trip_queue(SIGNUPS)

print("ΣΕΙΡΑ ΓΙΑ ΤΗΝ ΕΚΔΡΟΜΗ")
for position in range(len(queue)):
    # το μητρώο είναι γραμμένο με την ίδια σειρά, οπότε η θέση ταιριάζει
    fields = STUDENTS[position].split(";")
    print(f"{position + 1}. {queue[position]} - {fields[1]} ({fields[2]})")

print(f"ΔΙΑΦΟΡΕΤΙΚΟΙ ΜΑΘΗΤΕΣ: {distinct_students(SIGNUPS)}")
