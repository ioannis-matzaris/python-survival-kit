"""Το data layer του καταστήματος. Εδώ δουλεύεις.

Οι τρεις συναρτήσεις δουλεύουν. Η μία αφήνει μισοτελειωμένη παραγγελία όταν
κάτι πάει στραβά, η άλλη ρωτάει τη βάση διακόσιες φορές, και η τρίτη βάζει
συνάρτηση πάνω στη στήλη που έχει δείκτη.
"""

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import Base, Customer, Order, OrderLine, Product

engine = create_engine("sqlite:///shop.db")


class OutOfStock(Exception):
    pass


def place_order(session: Session, customer_id: int, wanted: dict[str, int]) -> int:
    """Καταχωρεί παραγγελία: μία γραμμή ανά προϊόν, και μειώνει το απόθεμα."""
    order = Order(customer_id=customer_id, created="2026-08-16", total_cents=0)
    session.add(order)
    session.commit()

    total = 0
    for code, quantity in wanted.items():
        product = session.scalars(select(Product).where(Product.code == code)).one()
        if product.stock < quantity:
            raise OutOfStock(f"Δεν υπάρχει απόθεμα για το {code}")
        product.stock -= quantity
        session.add(
            OrderLine(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_cents=product.price_cents,
            )
        )
        total += product.price_cents * quantity
        session.commit()

    order.total_cents = total
    session.commit()
    return order.id


def orders_with_customer(session: Session) -> list[tuple[int, str]]:
    """Ζεύγη κωδικού παραγγελίας και ονόματος πελάτη, για κάθε παραγγελία."""
    pairs = []
    for order in session.scalars(select(Order)):
        pairs.append((order.id, order.customer.name))
    return pairs


def month_total(session: Session, month: str) -> int:
    """Το σύνολο των παραγγελιών ενός μήνα, π.χ. "2026-07"."""
    total = session.scalar(
        select(func.sum(Order.total_cents)).where(
            func.substr(Order.created, 1, 7) == month
        )
    )
    return total or 0
