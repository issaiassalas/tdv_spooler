from ..base_formatter import BaseFormatter
from datetime import datetime
import os
import time
import json

class Printer(object):
    def __init__(self, printer_controller = None):
        self.printer_controller = printer_controller
        self.commands = []
        self._ext = '.001'

    @property
    def extention(self):
        return self._ext

    @extention.setter
    def extention(self, ext):
        self._ext = ext

    def SendCmd(self, cmd):
        self.commands.append(cmd)

    def print_file(self, file_name = '3dvodoo', path = ''):
        with open(f'{path}{file_name}{self.extention}', 'w') as f:
            f.write(
                '\n'.join(self.commands) + '\n'
            )

class FileFormatter(BaseFormatter):
    '''Rigazsa Fiscal printer tramas formatter'''
    def __init__(self, *args, **kwargs):
        self.printer = Printer(*args, **kwargs)
        self.files_config = 'files_config.json'
        self._sequence = 32
        self.db_invoice = None
        self.sub_total = 0
        self.configuration = self.build_config_file()

    def build_config_file(self):
        if not os.path.exists(self.files_config):
            with open(self.files_config, 'w') as f:
                f.write(json.dumps({
                    'FACTURAS': '',
                    'RESPUESTAS': '',
                    'RESPUESTAS-EXTENSION': '.RES',
                    'FACTURAS-PRE': 'FA',
                    'NOTASCREDITO-PRE': 'NC'
                }))
        with open(self.files_config, 'r') as f:
            return json.loads(f.read())

    def append_data(self, invoice = None):
        self.db_invoice = invoice

    def printer_trace(self):
        return self.printer.commands

    def send_cmd(self, cmd):
        self.printer.SendCmd(cmd)

    def invoice(self, products: list = [], payments: list = [], reversed = False):
        # Factura sin Personalizar*
        self.print_invoice_products(products)
        self.print_subtotal()
        self.process_payment(payments=payments)
        self.printer.SendCmd('NOTA 1:        ')
        self.printer.SendCmd('NOTA 2:        ')
        self.printer.SendCmd('NOTA 3:        ')
        self.printer.SendCmd('NOTA 4:        ')
        if reversed:
            reversed = str(reversed)
            reversed = '0'*(9-len(reversed)) + reversed
            self.printer.SendCmd(f'FACTURAAFECTADA:       {reversed}')
        self.printer.print_file(path=self.configuration.get('FACTURAS'))

    def fiscal_printer_response(self, filename, tries=3):
        if tries == 0:
            return False
        time.sleep(5)
        if not os.path.exists(filename):
            return self.fiscal_printer_response(filename, tries=tries-1)
        else:
            with open(filename, 'r') as f:
                return [
                    data.strip('"') 
                    for data in str(f.read()).split('\t')
                ]

    def custom_invoice(self,
                   client: dict = {},
                   products: list = [],
                   payments: list = [], **kwargs):
        # self.new_sequence()
        invoice_id = str(self.db_invoice.ref_id)
        invoice_id = '0'*(9-len(invoice_id)) + invoice_id
        today = datetime.now().strftime('%d/%M/%Y')
        self.printer.SendCmd(f'FACTURA:         {invoice_id}')
        self.printer.SendCmd(f'FECHA:           {today}')
        self.print_client_data(client=client)
        
        self.invoice(products=products, payments=payments)
        response = self.fiscal_printer_response(
            self.configuration.get('RESPUESTAS') +
            self.configuration.get('FACTURAS-PRE') +
            invoice_id +
            self.configuration.get('RESPUESTAS-EXTENSION')
        )
        if not response:
            return {}
        else:
            return {
                'current_printer_date': response[0],
                'last_invoice_number': int(response[3]),
                'last_nc_number': 0,
                'daily_closure_counter': int(response[6]) - 1,
                'registered_machine_number': response[7]
            }

    def credit_note(self, 
                    client: dict = {}, 
                    products: list = [], 
                    document: int = 0, 
                    serial: str = 'xxxZSerialxxx', 
                    date: str = '22/12/1980',
                    payments: list = [], 
                    reversed: int = False,
                    **kw
            ):
        invoice_id = str(self.db_invoice.ref_id)
        invoice_id = '0'*(9-len(invoice_id)) + invoice_id
        today = datetime.now().strftime('%d/%M/%Y')
        self.printer.SendCmd(f'DEVOLUCION:      {invoice_id}')
        self.printer.SendCmd(f'FECHA:           {today}')
        self.print_client_data(client=client)
        
        self.invoice(products=products, payments=payments, reversed=reversed)
        response = self.fiscal_printer_response(
            self.configuration.get('RESPUESTAS') +
            self.configuration.get('NOTASCREDITO-PRE') +
            invoice_id +
            self.configuration.get('RESPUESTAS-EXTENSION')
        )
        if not response:
            return {}
        else:
            return {
                'current_printer_date': response[0],
                'last_nc_number': int(response[3]),
                'daily_closure_counter': int(response[6]) - 1,
                'registered_machine_number': response[7]
            }

    def print_client_data(self, client={}, credit_note={}):
        cr = client.get('ced_rif', 'J012345678')
        if type(cr) == str:
            cr = cr[:12]
        else:
            cr = 'J012345678'
        name = client.get('name', 'Cliente final')
        if type(name) == str:
            name = name[:30]
        else:
            name = 'Cliente final'
        address = client.get('street', 'xxxxxxxx')
        if type(address) == str:
            address = address[:33]
        else:
            address = 'xxxxxxxxxxx'
        phone = client.get('phone', '0412-12345879')
        if type(phone) == str:
            phone = phone[:34]
        else:
            phone = '0412-12345879'

        self.printer.SendCmd(f'CLIENTE:         {name}')
        self.printer.SendCmd(f'RIF:             {cr}')
        self.printer.SendCmd(f'DIRECCION1:      {address}')
        self.printer.SendCmd(f'DIRECCION2:')
        self.printer.SendCmd(f'TELEFONO:        {phone}')

    def get_tax_type(self, tax: int = 0):
        return { 
            0: '  0.00', 1: ' 16.00', 2: '  8.00', 3: ' 31.00'
        }.get(tax, 'E')

    def print_invoice_products(self, products: list = []):
        self.printer.SendCmd('DESCRIPCION............................................................ CANT..... IVA..  PRECIO UNIT.........')
        for product in products:
            product_name = product.get('name').replace('\n', ' ')[:71]
            if len(product_name) < 71:
                product_name = product_name + ' '*(71-len(product_name))

            product_units = round(product.get('product_qty'), 3)
            unit_price = round(product.get('price_unit'), 2)

            self.sub_total += product_units * unit_price

            trunk_units = str(int(product_units))
            if len(trunk_units) < 6:
                product_units = ' '*(6-len(trunk_units)) + str(product_units)
                decimal_units = product_units.split('.')[1]
                if len(decimal_units) < 3:
                    product_units += '0'*(3-len(decimal_units))

            product_tax = self.get_tax_type(product.get('tax'))
            unit_price = '  ' + str(unit_price)
            decimal_units = unit_price.split('.')[1]
            if len(decimal_units) < 2:
                unit_price += '0'*(2-len(decimal_units))

            self.printer.SendCmd(
                product_name + product_units + product_tax + unit_price
            )

    def fixed_spaces(self, amount, spaces):
        str_amount = str(amount)
        if len(str(amount)) < spaces:
            return ' '*(spaces - len(str_amount)) + str_amount
        return str_amount

    def print_subtotal(self):
        sub_total = round(self.sub_total, 2)
        sub_total = self.fixed_spaces(sub_total, 15)
        if len(sub_total.split('.')[1]) < 2:
            sub_total += '0'
        self.printer.SendCmd('SUB-TOTAL:' + sub_total)
        self.printer.SendCmd('DESCUENTO:            0.00')
        total = self.db_invoice.amount_total
        total = self.fixed_spaces(total, 11)
        if len(total.split('.')[1]) < 2:
            total += '0'
        self.printer.SendCmd('TOTAL A PAGAR:' + total)

    def format_payment(self, payments, type, spaces):
        payment = float(sum(
            payment.get('amount', 0.0)
            for payment in list(
                filter(
                    lambda x: x.get('type') == type,
                    payments
                )
            )
        ))
        entire, decimal = str(round(payment, 2)).split('.')
        if len(entire) < spaces:
            entire = ' '*(spaces-len(entire)) + entire
        if len(decimal) < 2:
            decimal += '0'
        return f'{entire}.{decimal}'

    def process_payment(self, payments: list = []):
        self.printer.SendCmd('EFECTIVO:' + self.format_payment(
            payments, 'm1', 14
        ))
        self.printer.SendCmd('CHEQUES:' + self.format_payment(
            payments, 'm2', 15
        ))
        self.printer.SendCmd('TARJ/DEBITO:' + self.format_payment(
            payments, 'm3', 11
        ))
        self.printer.SendCmd('TARJ/CREDITO:' + self.format_payment(
            payments, 'm4', 10
        ))
        self.printer.SendCmd('Tranf en Bs:' + self.format_payment(
            payments, 'm5', 11
        ))
        self.printer.SendCmd('Transf en USD:' + self.format_payment(
            payments, 'm6', 9
        ))
        self.printer.SendCmd('Transf EURO:' + self.format_payment(
            payments, 'm7', 11
        ))
        self.printer.SendCmd('Efect USD:' + self.format_payment(
            payments, 'm8', 13
        ))
        self.printer.SendCmd('Efect EURO:' + self.format_payment(
            payments, 'm9', 12
        ))
        self.printer.SendCmd('Pago movil:' + self.format_payment(
            payments, 'm10', 12
        ))
        self.printer.SendCmd('CREDITO:' + self.format_payment(
            payments, 'm11', 15
        ))
        # if not payments or len(payments) == 0:
        #     self.cancel_current()
        # else:
        #     for payment in payments:
        #         self.pay(payment=payment)

    def get_fiscal_status(self, *args, **kwargs):
        return 'No implementado'

    def __str__(self):
        return '\n'.join(f'"{trama}"' for trama in self.printer_trace())

