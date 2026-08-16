"""Φτιάχνει το shop.db από το μηδέν. Τρέξε: python3 seed.py"""

import random
from pathlib import Path

from sqlalchemy.orm import Session

from models import Base, Customer, Order, OrderLine, Product
from shop import engine

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.db"

if DB.exists():
    DB.unlink()

Base.metadata.create_all(engine)

generator = random.Random(20260816)

with Session(engine) as session:
    customers = [
        Customer(name=f"Πελάτης {number}", email=f"customer{number}@example.gr")
        for number in range(1, 41)
    ]
    products = [
        Product(code=f"PRO-{number:03d}", price_cents=generator.randrange(200, 9000), stock=500)
        for number in range(1, 21)
    ]
    session.add_all(customers + products)
    session.flush()

    for number in range(200):
        month = generator.choice(["2026-06", "2026-07", "2026-08"])
        day = generator.randrange(1, 29)
        session.add(
            Order(
                customer_id=generator.choice(customers).id,
                created=f"{month}-{day:02d}",
                total_cents=generator.randrange(500, 40000),
            )
        )
    session.commit()

print(f"Έτοιμο: {DB.name} με 40 πελάτες, 20 προϊόντα και 200 παραγγελίες")
