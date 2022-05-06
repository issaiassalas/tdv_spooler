from hka_fiscal_printer import TDVHKAFormatter as Formatter

def get_client():
    return {
        'name': 'Desarrollador 1',
        'ced_rif': 'xxxxxxxx',
        'street': 'Puerto Ordaz',
        'phone': '04xx-xxx-xx-xx'
    }

def get_products():
    return [
        {
            'name': 'Articulo generico',
            'price_unit': 19.999,
            'product_qty': 1500.789,
            'tax': 1
        },
        {
            'name': 'Articulo generico2',
            'price_unit': 19.999,
            'product_qty': 1500.789,
            'tax': 1
        }
    ]

def get_payments():
    return [
        {
            'id': 1,
            'amount': 789.321
        }
    ]

def test_invoice():
    print('test invoice')
    rf = Formatter()
    rf.custom_invoice(
        client = get_client(),
        products = get_products(),
        payments = get_payments()
    )
    print(rf)

def test_credit_note():
    print('test invoice')
    rf = Formatter()
    rf.credit_note(
        client = get_client(),
        products = get_products(),
        payments = get_payments()
    )
    print(rf)

def test_cut_papper():
    rf = Formatter()
    print('test cut papper')
    rf.cut_papper()
    print(rf)

def test_print_programation():
    rf = Formatter()
    print('test print programation')
    rf.print_programation()
    print(rf)

if __name__ == '__main__':
    # test_invoice()
    test_credit_note()
    # test_cut_papper()
    # test_print_programation()