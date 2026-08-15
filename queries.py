"""Οι πέντε ερωτήσεις του καταστήματος.

Κάθε συνάρτηση παίρνει μια ανοιχτή σύνδεση και επιστρέφει την απάντηση.
Καμία δεν είναι γραμμένη. Όλες επιστρέφουν κάτι που δεν είναι απάντηση.
"""

import sqlite3


def total_customers(connection: sqlite3.Connection) -> int:
    """Πόσοι πελάτες υπάρχουν."""
    return 0


def orders_over(connection: sqlite3.Connection, cents: int) -> list[str]:
    """Οι κωδικοί των παραγγελιών πάνω από ένα ποσό, από τη μεγαλύτερη προς τη μικρότερη."""
    return []


def orders_in_month(connection: sqlite3.Connection, month: str) -> int:
    """Πόσες παραγγελίες έγιναν σε έναν μήνα, π.χ. "2026-07"."""
    return 0


def customer_of(connection: sqlite3.Connection, reference: str) -> str | None:
    """Το όνομα του πελάτη μιας παραγγελίας, ή None αν δεν υπάρχει η παραγγελία."""
    return None


def spend_by_customer(connection: sqlite3.Connection) -> list[tuple[str, int]]:
    """Πόσα ξόδεψε ο καθένας, από τον μεγαλύτερο προς τον μικρότερο."""
    return []
