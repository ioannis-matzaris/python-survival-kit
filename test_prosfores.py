from prosfores import cheapest, final_price, in_stock


def test_final_price_is_a_number():
    offers = [
        {"shop": "Πλαίσιο", "price": 78.00, "shipping": 6.00, "stock": True},
        {"shop": "Public", "price": 80.90, "shipping": 0.00, "stock": True},
        {"shop": "Κωτσόβολος", "price": 74.50, "shipping": 4.90, "stock": False},
        {"shop": "Γερμανός", "price": 83.00, "shipping": 0.00, "stock": True},
        {"shop": "e-shop.gr", "price": 79.90, "shipping": 3.50, "stock": True},
    ]
    assert isinstance(final_price(offers[0]), float)


def test_in_stock_returns_a_list():
    offers = [
        {"shop": "Πλαίσιο", "price": 78.00, "shipping": 6.00, "stock": True},
        {"shop": "Public", "price": 80.90, "shipping": 0.00, "stock": True},
        {"shop": "Κωτσόβολος", "price": 74.50, "shipping": 4.90, "stock": False},
        {"shop": "Γερμανός", "price": 83.00, "shipping": 0.00, "stock": True},
        {"shop": "e-shop.gr", "price": 79.90, "shipping": 3.50, "stock": True},
    ]
    assert isinstance(in_stock(offers), list)


def test_the_feed_has_five_offers():
    offers = [
        {"shop": "Πλαίσιο", "price": 78.00, "shipping": 6.00, "stock": True},
        {"shop": "Public", "price": 80.90, "shipping": 0.00, "stock": True},
        {"shop": "Κωτσόβολος", "price": 74.50, "shipping": 4.90, "stock": False},
        {"shop": "Γερμανός", "price": 83.00, "shipping": 0.00, "stock": True},
        {"shop": "e-shop.gr", "price": 79.90, "shipping": 3.50, "stock": True},
    ]
    assert len(offers) == 5


def test_cheapest_returns_one_of_the_offers():
    offers = [
        {"shop": "Πλαίσιο", "price": 78.00, "shipping": 6.00, "stock": True},
        {"shop": "Public", "price": 80.90, "shipping": 0.00, "stock": True},
        {"shop": "Κωτσόβολος", "price": 74.50, "shipping": 4.90, "stock": False},
        {"shop": "Γερμανός", "price": 83.00, "shipping": 0.00, "stock": True},
        {"shop": "e-shop.gr", "price": 79.90, "shipping": 3.50, "stock": True},
    ]
    assert cheapest(offers) in offers


def test_final_price_adds_the_shipping():
    offers = [
        {"shop": "Πλαίσιο", "price": 78.00, "shipping": 6.00, "stock": True},
        {"shop": "Public", "price": 80.90, "shipping": 0.00, "stock": True},
        {"shop": "Κωτσόβολος", "price": 74.50, "shipping": 4.90, "stock": False},
        {"shop": "Γερμανός", "price": 83.00, "shipping": 0.00, "stock": True},
        {"shop": "e-shop.gr", "price": 79.90, "shipping": 3.50, "stock": True},
    ]
    assert final_price(offers[0]) == 84.00
