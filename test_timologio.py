from timologio import VAT_RATE, invoice_total


def test_invoice_with_ten_percent_discount():
    invoice_total(100.0, 10.0) == 111.60


def test_vat_is_added_on_top():
    net = 200.0
    discount = 10.0
    expected = net - net * discount / 100 + net * VAT_RATE
    assert invoice_total(net, discount) == round(expected, 2)


def test_total_is_positive():
    total = invoice_total(80.0, 5.0)
    assert total > 0
