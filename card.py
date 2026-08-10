# Η καρτέλα του πελάτη, όπως ήρθε από το export του e-shop.
name_from_file = "Γιώργος Παπαδόπουλος"

# Το ίδιο όνομα, όπως το έχει η βάση μας.
name_in_db = "Γιώργος Παπαδόπουλος"

# Ο πελάτης δεν συμπλήρωσε ποτέ τηλέφωνο στη φόρμα.
phone = None

# Το SMS που θα φύγει, και το πεδίο του παρόχου που το κρατάει.
message = "Η παραγγελία σου έφυγε από την αποθήκη"
FIELD_LIMIT = 64

print("Πελάτης:", name_from_file)
print("Χαρακτήρες:", len(message))
print("Bytes:", len(message))
print("Χωράει:", len(message) <= FIELD_LIMIT)
print("Τηλέφωνο:", phone.strip())
print("Ίδιο όνομα με τη βάση:", name_from_file == name_in_db)
