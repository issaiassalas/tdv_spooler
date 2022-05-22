from ..base_formatter import BaseFormatter
from .printer_line import PrinterLine

import time
import datetime

class Printer(object):
    def __init__(self, printer_controller = None):
        self.printer_controller = printer_controller
        self.commands = []

    def SendCmd(self, cmd):
        with open('log.txt', 'a') as f:
            f.write(f'CMD: {cmd}')
            response = self.printer_controller.send_cmd(cmd)
            f.write(f'RESPONSE: {response}')

class RigazsaFormatter(BaseFormatter):
    '''Rigazsa Fiscal printer tramas formatter'''
    def __init__(self, *args, **kwargs):
        self.printer = Printer(*args, **kwargs)
        self._sequence = 32

    def new_sequence(self):
        self._sequence = 32

    @property
    def sequence(self):
        sequence = self._sequence
        self._sequence = sequence + 1
        return chr(sequence)

    def new_line(self, *args, **kwargs) -> PrinterLine:
        return PrinterLine(
            *args,
            sequence=self.sequence,
            parent=self,
            **kwargs
        )

    def send_line(self, *args, **kwargs):
        self.new_line(*args, **kwargs).send()

    def printer_trace(self):
        return self.printer.commands

    def print_programation(self):
        self.new_sequence()
        self.send_line(
            command = chr(0x4D),
            fields = ['S']
        )

    def send_cmd(self, cmd):
        self.printer.SendCmd(cmd)

    def cancel_current(self):
        self.send_line(
            command = chr(0x44),
            fields = [
                'Cancelar Factura', '000', 'C', 'E'
            ]
        )

    def invoice(self, products: list = [], payments: list = []):
        # Factura sin Personalizar*
        self.print_invoice_products(products)
        self.print_subtotal()
        self.process_payment(payments=payments)
        self.send_line(
            command = chr(0x45),
            fields = ['E']
        )

    def custom_invoice(self,
                   client: dict = {},
                   products: list = [],
                   payments: list = [], **kw):
        self.new_sequence()
        self.print_client_data(client=client)
        
        return self.invoice(products=products, payments=payments)

    def cancelled_invoice(self, client: dict = {}, products: list = []):
        self.new_sequence()
        self.print_client_data(client=client)
        self.print_invoice_products(products)
        # self.print_subtotal()
        self.cancel_current()

    def nf_document(self):
        # Documento No Fiscal
        self.new_sequence()
        self.send_line(
            command = chr(0x48)
        )
        self.send_line(
            command = chr(0x49),
            fields = ['Esto es un documento no fiscal']
        )
        self.send_line(
            command = chr(0x4A)
        )

    def credit_note(self, 
                    client: dict = {}, 
                    products: list = [], 
                    document: int = 0, 
                    serial: str = 'xxxZSerialxxx', 
                    date: str = '22/12/1980',
                    payments: list = []
            ):
        self.new_sequence()
        self.print_client_data(
            client = client,
            credit_note = {
                3: str(document),
                4: serial,
                5: date,
                7: 'D'
            }
        )
        self.invoice(products=products, payments=payments)

    def reprint_invoices(self):
        n_ini = self.reimp_ini.value()
        n_fin = self.reimp_fin.value()

        starString = str(n_ini)
        while (len(starString) < 7):
            starString = "0" + starString
        endString = str(n_fin)
        while (len(endString) < 7):
            endString = "0" + endString
        self.printer.SendCmd("RF" + starString + endString)

    def print_client_data(self, client={}, credit_note={}):
        cr = client.get('ced_rif')[:12]
        name = client.get('name')[:30]
        address = client.get('street')[:33]
        phone = client.get('phone')[:34]

        self.send_line(
            command = chr(0x40),
            fields = {
                1: name, 
                2: cr,
                **credit_note
            },
            limit = 9
        )
        if address:
            self.send_line(
                command = chr(0x41),
                fields = [f'Direccion: {address}', ''],
            )
        if phone:
            self.send_line(
                command = chr(0x41),
                fields = [f'Telefono: {phone}', ''],
            )

    def cut_papper(self):
        self.send_line(
            command = chr(0x4B),
        )

    def advance_papper(self):
        self.send_line(
            command = chr(0x50)
        )

    def open_casher(self, casher = 1):
        self.send_line(
            command = {
                1: chr(0x7B),
                2: chr(0x7C)
            }.get(casher)
        )

    def format_units(self, unit: float = 0, unit_type: str = 'price'):
        if unit_type == 'price':
            return str(round(unit * 100))
        elif unit_type == 'quantity':
            return str(round(unit * 1000))
        elif unit_type == 'payment':
            return str(round(unit * 100))
        elif unit_type == 'reprint':
            return str(10000000 + int(unit))[1:]

    def get_tax_type(self, tax: int = 0):
        return { 
            0: 'E', 1: 'G', 2: 'R', 3: 'A'
        }.get(tax, 'E')

    def print_invoice_products(self, products: list = []):
        for product in products:
            quantity = self.format_units(
                unit=product.get('product_qty'),
                unit_type='quantity'
            )
            price = self.format_units(
                unit=product.get('price_unit'),
                unit_type='price'
            )
            tax = self.get_tax_type(product.get('tax'))
            self.send_line(
                command = chr(0x42),
                fields = [
                    product.get('name', 'xxx')[:15],
                    quantity,
                    price,
                    tax,
                    'M'
                ],
                limit = 8
            )

    def reprint_last_invoice(self):
        self.printer.SendCmd('RU00000000000000')

    def setup_payment_method(self, id: int = 1, name: str = 'Efectivo'):
        cmd = 'PE'
        cmd += (str(100 + id))[1:]
        cmd += name[:14]
        self.printer.SendCmd(cmd)

    def print_subtotal(self):
        self.send_line(
            command = chr(0x43),
            limit = 2
        )

    def get_lazy_status(self, status):
        time.sleep(1)
        return self.get_state(status)

    def send_fiscal_text(self, text):
        self.send_line(
            command = chr(0x41),
            fields = [
                text
            ]
        )

    def pay(self, payment: dict = {}):
        payment_amount = self.format_units(
            unit=payment.get('amount', 0.0),
            unit_type = 'payment'
        )
        payment_id = payment.get('id')
        if type(payment_id) != str:
            payment_id = 'Efectivo'

        self.send_fiscal_text(
            f'{payment_id}: {payment_amount}'
        )


    def process_payment(self, payments: list = []):
        if not payments or len(payments) == 0:
            self.cancel_current()
        else:
            for payment in payments:
                self.pay(payment=payment)

    def reprint_document(self, ref: int = 0, document_type: str = 'out_invoice'):
        str_ref = str(ref)
        final_document = document_type
        if document_type == 'out_invoice':
            final_document = 'F'
        elif document_type == 'out_refund':
            final_document = 'C'
        self.send_line(
            command = chr(0x3D),
            fields = [str_ref, str_ref, final_document]
        )

        f_ref = self.format_units(unit=ref, unit_type='reprint')
        self.printer.SendCmd(f'RF{f_ref}{f_ref}')

    def get_x_report(self):
        reporte = self.printer.GetXReport()
        return reporte.getData()

    def print_z_by_number(self):
        n_ini = input('valor de inicio: ')
        n_fin = input('valor final: ')
        self.printer.PrintZReport("A", n_ini, n_fin)

    def get_state(self, state: str = '', trama: str = '') -> dict:
        data = None
        if state == "S1":
            data = self.printer.GetS1PrinterData(trama=trama)
        elif state == "S2":
            data = self.printer.GetS2PrinterData(trama=trama)
        elif state == "S3":
            data = self.printer.GetS3PrinterData(trama=trama)
        elif state == "S4":
            data = self.printer.GetS4PrinterData(trama=trama)
        elif state == "S5":
            data = self.printer.GetS5PrinterData(trama=trama)
        elif state == "S6":
            data = self.printer.GetS6PrinterData(trama=trama)
        return data.getData()

    def error_state(self):
        self.estado = self.printer.ReadFpStatus()
        print("Estado: " + self.estado[0] + "\n" + "Error: " + self.estado[5])

    def report_x(self):
        self.new_sequence()
        self.send_line(
            command = chr(0x39),
            fields = [
                chr(0x58), 
                chr(0x54)
            ],
            separator_ends = True
        )

    def report_z(self):
        self.new_sequence()
        self.send_line(
            command = chr(0x39),
            fields = [
                chr(0x5A), 
                chr(0x54)
            ],
            separator_ends = True
        )

    def get_fiscal_status():
        return 'No implementado'

    def __str__(self):
        return '\n'.join(f'"{trama}"' for trama in self.printer_trace())

