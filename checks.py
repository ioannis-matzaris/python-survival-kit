"""Ο βαθμολογητής του lab. Τρέξε: python3 checks.py

Καλεί τις τρεις συναρτήσεις σου, μετράει πόσα ερωτήματα έστειλαν στη βάση, και
κοιτάει τι έμεινε πίσω όταν κάτι πήγε στραβά. Φτιάχνει δική του βάση κάθε φορά,
οπότε δεν χαλάει το shop.db σου.
"""

import shutil
import sys
from pathlib import Path

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "shop.db"
COPY = HERE / "checks.db"

results: list[tuple[bool, str]] = []
statements: list[str] = []


def report(label: str, passed: bool) -> None:
    results.append((passed, label))


if not SOURCE.exists():
    print("Δεν βρήκα το shop.db. Τρέξε πρώτα: python3 seed.py")
    sys.exit(1)

try:
    import shop
    from models import Order, OrderLine, Product
except Exception as error:
    print(f"Το shop.py δεν φορτώνει: {error}")
    sys.exit(1)

shutil.copy(SOURCE, COPY)
engine = create_engine(f"sqlite:///{COPY}")


@event.listens_for(engine, "before_cursor_execute")
def record(conn, cursor, statement, parameters, context, executemany):
    statements.append(statement)


with Session(engine) as session:
    product = session.scalars(select(Product)).first()
    product.stock = 3
    session.commit()

    statements.clear()
    order_id = None
    try:
        order_id = shop.place_order(session, 1, {product.code: 2})
    except Exception as error:
        order_id = f"σφάλμα: {error}"

    lines = session.scalars(select(OrderLine).where(OrderLine.order_id == order_id)).all()
    order = session.get(Order, order_id) if isinstance(order_id, int) else None
    report(
        "Μια κανονική παραγγελία γράφεται με τη γραμμή της και σωστό σύνολο",
        order is not None and len(lines) == 1 and order.total_cents == lines[0].price_cents * 2,
    )

with Session(engine) as session:
    product = session.scalars(select(Product)).first()
    before_stock = product.stock
    before_orders = len(session.scalars(select(Order)).all())
    before_lines = len(session.scalars(select(OrderLine)).all())

    second = session.scalars(select(Product)).all()[1]
    try:
        shop.place_order(session, 1, {product.code: 1, second.code: 10_000})
    except Exception:
        session.rollback()

    after_orders = len(session.scalars(select(Order)).all())
    after_lines = len(session.scalars(select(OrderLine)).all())
    after_stock = session.scalars(select(Product)).first().stock

    report("Παραγγελία που σκάει στη μέση δεν αφήνει παραγγελία πίσω", after_orders == before_orders)
    report("Ούτε γραμμές παραγγελίας", after_lines == before_lines)
    report("Ούτε πειραγμένο απόθεμα", after_stock == before_stock)

with Session(engine) as session:
    how_many = len(session.scalars(select(Order)).all())
    statements.clear()
    pairs = shop.orders_with_customer(session)
    queries = len(statements)
    report(
        "Η orders_with_customer δίνει ένα ζεύγος ανά παραγγελία, με όνομα",
        len(pairs) == how_many and all(isinstance(one[1], str) and one[1] for one in pairs),
    )
    report(
        f"Και τα φέρνει με λίγα ερωτήματα, όχι ένα ανά παραγγελία ({queries})",
        queries <= 3,
    )

with Session(engine) as session:
    statements.clear()
    total = shop.month_total(session, "2026-07")
    expected = session.scalar(
        select(func.sum(Order.total_cents)).where(
            Order.created >= "2026-07-01", Order.created < "2026-08-01"
        )
    )
    month_sql = " ".join(statements).lower()
    report("Το month_total(2026-07) δίνει το σωστό σύνολο", total == expected)
    report(
        "Και το ρωτάει χωρίς συνάρτηση πάνω στη στήλη created",
        "substr" not in month_sql and "strftime" not in month_sql,
    )

COPY.unlink(missing_ok=True)

total_checks = len(results)
for index, (passed, label) in enumerate(results, start=1):
    mark = "✅" if passed else "❌"
    print(f"[{index}/{total_checks}] {label}".ljust(66) + f" {mark}")

score = sum(1 for passed, _ in results if passed)
print()
print(f"Σκορ: {score}/{total_checks}")
