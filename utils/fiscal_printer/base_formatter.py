
class BaseFormatter(object):
    def __init__(self, *args, **kwargs):
        super.__init__(self, *args, **kwargs)

    def printer_trace(self) -> list:
        '''Get list of print statements'''

    def print_programation(self) -> None:
        '''Sends the programation to queue'''

    def send_cmd(self, cmd: str) -> None:
        '''Sends the command to queue'''

    def cancel_current(self) -> None:
        '''Cancel the current document'''

    def invoice(self, products: list = [], payments: list = []) -> None:
        '''
            Format the given data into a invoice (helper to other functions)

            products is a list of dicts => [
                {
                    'name': 'Article',
                    'price_unit': 19.999,
                    'product_qty': 1500.789,
                    'tax': 1
                },
            ]

            payments is a list of dicts => [
                {
                    'id': 1,
                    'amount': 789.321
                }
            ]

        '''

    def custom_invoice(self, client: dict = {}, products: list = [], payments: list = []) -> None:
        '''
            Format the given data into a invoice (helper to other functions)

            client is a dict => {
                'name': 'Developer 1',
                'ced_rif': 'xxxxxxxx',
                'street': 'Some address',
                'phone': '04xx-xxx-xx-xx'
            }

            products is a list of dicts => [
                {
                    'name': 'Article',
                    'price_unit': 19.999,
                    'product_qty': 1500.789,
                    'tax': 1
                },
            ]

            payments is a list of dicts => [
                {
                    'id': 1,
                    'amount': 789.321
                }
            ]

        '''

    def cancelled_invoice(self, client: dict = {}, products: list = []) -> None:
        '''
            Format the given data into a cancelled invoice (testing)

            client is a dict => {
                'name': 'Developer 1',
                'ced_rif': 'xxxxxxxx',
                'street': 'Some address',
                'phone': '04xx-xxx-xx-xx'
            }

            products is a list of dicts => [
                {
                    'name': 'Article',
                    'price_unit': 19.999,
                    'product_qty': 1500.789,
                    'tax': 1
                },
            ]
        '''

    def nf_document(self) -> None:
        '''Print a non fiscal document (testing)'''

    def credit_note(self,
                    client: dict = {},
                    products: list = [],
                    payments: list = [],
                    document: int = 0,
                    serial: str = '',
                    date: str = '') -> None:
        '''
            Format the given data into a credit note

            client is a dict => {
                'name': 'Developer 1',
                'ced_rif': 'xxxxxxxx',
                'street': 'Some address',
                'phone': '04xx-xxx-xx-xx'
            }

            products is a list of dicts => [
                {
                    'name': 'Article',
                    'price_unit': 19.999,
                    'product_qty': 1500.789,
                    'tax': 1
                },
            ]

            payments is a list of dicts => [
                {
                    'id': 1,
                    'amount': 789.321
                }
            ]

            document is affected invoice => int

            serial is fiscal printer serial of the document => str

            date is the date of the invoice => str
        '''

    def reprint_invoices(self) -> None:
        '''reprint invoices in a range'''

    def print_client_data(self, client: dict = {}) -> None:
        '''
            print the client data in the current invoice

            client is a dict => {
                'name': 'Developer 1',
                'ced_rif': 'xxxxxxxx',
                'street': 'Some address',
                'phone': '04xx-xxx-xx-xx'
            }
        '''

    def format_units(self, unit: float = 0, unit_type: str = 'price') -> str:
        '''converts the given unit into a valid data'''

    def get_tax_type(self, tax: int = 0, invoice_type: str = 'out_invoice') -> str:
        '''get the tax control character'''

    def print_invoice_products(self, products: list = [], invoice_type: str = 'out_invoice') -> list:
        '''
            print the list of products in the current document

            products is a list of dicts => [
                {
                    'name': 'Article',
                    'price_unit': 19.999,
                    'product_qty': 1500.789,
                    'tax': 1
                },
            ]

            invoice_type is a str (enum) => values ('out_invoice', 'out_refund')
        '''

    def reprint_last_invoice(self) -> None: 
        '''Reprint the last document in the work memory'''

    def setup_payment_method(self, id: int = 1, name: str = 'Efectivo'):
        '''
            setup the given payment method in the fiscal printer
            (if is supported)
            could raise an exception
        '''

    def print_subtotal(self):
        '''print the subtotal in the current document'''

    def get_lazy_status(self, status: str = 'S1') -> dict:
        '''get the formatted Sx status'''

    def pay(self, payment: dict = {}, code: str = '1'):
        '''
            make a payment in the current document

            payment is a dict => {
                'id': 1,
                'amount': 789.321
            }

            if "code == '1'" the document will close
        '''

    def process_payment(self, payments: list = []): 
        '''
            process the payments to close the document
            if not payments given the document will be cancelled

            payments is a list of dicts => [
                {
                    'id': 1,
                    'amount': 789.321
                }
            ]
        '''

    def reprint_document(self, ref: int = 0, document_type: str = 'out_invoice'):
        '''reprint a document from the audit memory'''

    def get_x_report(self) -> dict:
        '''get details of the current report x'''

    def print_z_by_number(self):
        '''print report z from audit memory in a range'''

    def get_state(self, state: str = 'S1', trama: str = '') -> dict:
        '''
            get the data from the fiscal printer

            the state is the type of required report

            the trama is the data for the report
        '''

    def error_state(self):
        '''get the error state of the printer'''

    def report_x(self):
        '''print the report x'''

    def report_z(self):
        '''print the report z'''

    