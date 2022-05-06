from ..base_formatter import BaseFormatter
from .MethodHelper import MethodHelper
import time
import datetime


class TDVHKAFormatter(BaseFormatter):
    def __init__(self):
        self.printer = MethodHelper()

    def printer_trace(self):
        return self.printer.commands

    def print_programation(self):
        self.printer.SendCmd("D")

    def send_cmd(self, cmd):
        self.printer.SendCmd(cmd)

    def cancel_current(self):
        self.printer.SendCmd('7')

    def invoice(self, products: list = [], payments: list = []):
        # Factura sin Personalizar*
        self.print_invoice_products(products)
        self.print_subtotal()
        self.process_payment(payments=payments)

    def custom_invoice(self,
                   client: dict = {},
                   products: list = [],
                   payments: list = []):
        self.print_client_data(client=client)
        return self.invoice(products=products, payments=payments)

    def cancelled_invoice(self, client: dict = {}, products: list = []):
        self.print_client_data(client=client)
        self.print_invoice_products(products)
        self.printer.SendCmd(str("7"))

    def nf_document(self):
        # Documento No Fiscal
        self.printer.SendCmd(str("80$Documento de Prueba"))
        # self.printer.SendCmd(str("80¡Esto es un documento de texto"))
        self.printer.SendCmd(str("80!Es un documento no fiscal"))
        self.printer.SendCmd(str("80*Es bastante util y versatil"))
        self.printer.SendCmd(str("810Fin del Documento no Fiscal"))

    def credit_note(self, 
                    client: dict = {}, 
                    products: list = [], 
                    document: int = 0, 
                    serial: str = '', 
                    date: str = '',
                    payments: list = []
            ):
        invoice = self.format_units(unit=document, unit_type='invoice')
        self.printer.SendCmd(f'iF*{invoice}')
        self.printer.SendCmd(f'iD*{date}')
        self.printer.SendCmd(f'iI*{serial}')
        self.print_client_data(client=client)
        self.print_invoice_products(products=products, invoice_type='out_refund')
        self.print_subtotal()
        self.process_payment(payments=payments)
        # self.printer.SendCmd('101')

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

    def print_client_data(self, client={}):
        personal_counter = 0
        cr = client.get('ced_rif')
        name = client.get('name')
        address = client.get('street')
        phone = client.get('phone')
        if cr:
            self.printer.SendCmd(f'iR*{cr}')
        self.printer.SendCmd(f'iS*{name}')
        if address:
            self.printer.SendCmd(f'i0{personal_counter}Direccion: {address}')
            personal_counter += 1
        if phone:
            self.printer.SendCmd(f'i0{personal_counter}Telefono: {phone}')
            personal_counter += 1

    def format_units(self, unit: float = 0, unit_type: str = 'price'):
        total = ''
        if unit_type == 'price':
            total = str(round(10000000000 + unit * 100))[1:]
        elif unit_type == 'quantity':
            total = str(round(100000000 + unit * 1000))[1:]
        elif unit_type == 'invoice':
            total = str(100000000000 + unit)[1:]
        elif unit_type == 'payment':
            total = str(round(1000000000000 + unit * 100))[1:]
        elif unit_type == 'reprint':
            total = str(10000000 + int(unit))[1:]
        return total

    def get_tax_type(self, tax: int = 0, invoice_type='out_invoice'):
        if invoice_type in ['OUT_INVOICE', 'out_invoice']:
            if tax == 1:
                return '!'
            elif tax == 2:
                return '"'
            elif tax == 3:
                return '#'
            elif tax == 0:
                return ' '
        elif invoice_type in ['OUT_REFUND', 'out_refund']:
            if tax == 1:
                return 'd1'
            elif tax == 2:
                return 'd2'
            elif tax == 3:
                return 'd3'
            elif tax == 0:
                return 'd0'

    def print_invoice_products(self,
                         products: list = [],
                         invoice_type: str = 'out_invoice'):
        response = []
        for product in products:
            line = ''
            line += self.get_tax_type(product.get('tax'),
                                    invoice_type=invoice_type)
            line += self.format_units(unit=product.get('price_unit'),
                                     unit_type='price')
            line += self.format_units(unit=product.get('product_qty'),
                                     unit_type='quantity')
            line += product.get('name')[:33]
            self.printer.SendCmd(line)
            time.sleep(0.1)
            response.append(line)

        return response

    def reprint_last_invoice(self):
        self.printer.SendCmd('RU00000000000000')

    def setup_payment_method(self, id: int = 1, name: str = 'Efectivo'):
        cmd = 'PE'
        cmd += (str(100 + id))[1:]
        cmd += name[:14]
        self.printer.SendCmd(cmd)

    def print_subtotal(self):
        self.printer.SendCmd('3')

    def get_lazy_status(self, status):
        time.sleep(1)
        return self.get_state(status)

    def pay(self, payment: dict = {}, code: str = '1'):
        cmd = code + str(100 + payment.get('id', 1))[1:]
        if code == '2':
            cmd += self.format_units(unit=payment.get('amount', 0.0), unit_type='payment')

        self.printer.SendCmd(cmd)

    def process_payment(self, payments: list = []):
        if not payments or len(payments) == 0:
            self.printer.SendCmd('7')
        elif len(payments) == 1:
            self.pay(payment=payments[0])
        else:
            for payment in payments:
                self.pay(payment=payment, code='2')

    def reprint_document(self, ref: int = 0, document_type: str = 'out_invoice'):
        f_ref = self.format_units(unit=ref, unit_type='reprint')
        if document_type == 'out_invoice':
            self.printer.SendCmd(f'RF{f_ref}{f_ref}')
        elif document_type == 'out_refund':
            self.printer.SendCmd(f'RC{f_ref}{f_ref}')
        else:
            self.printer.SendCmd(f'R{document_type}{f_ref}{f_ref}')

    def get_x_report(self):
        reporte = self.printer.GetXReport()
        return reporte.getData()

    def print_z_by_number(self):
        n_ini = input('valor de inicio: ')
        n_fin = input('valor final: ')
        self.printer.PrintZReport("A", n_ini, n_fin)

    # def ImpZporfecha(self):
    #     n_ini = self.imp_date_ini.date().toPyDate()
    #     n_fin = self.imp_date_fin.date().toPyDate()
    #     self.printer.PrintZReport("A", n_ini, n_fin)

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
        if data:
            return data.getData()
        else:
            raise Exception("Error with the data interface")

    # def enviar_archivo(self):
    #     nombre_fichero = QFileDialog.getOpenFileName(
    #         self, "Abrir fichero", "/Desktop")
    #     if nombre_fichero:
    #         fichero_actual = nombre_fichero
    #         filename = str(QFileInfo(nombre_fichero).fileName())
    #         dirname = str(QFileInfo(nombre_fichero).path())
    #         path = open(os.path.join(dirname, filename), 'r')
    #         self.printer.SendCmdFile(path)

    def error_state(self):
        self.estado = self.printer.ReadFpStatus()
        print("Estado: " + self.estado[0] + "\n" + "Error: " + self.estado[5])

    def report_x(self):
        self.printer.SendCmd('I0X')

    def report_z(self):
        self.printer.SendCmd('I0Z')

    # def print_z_report(self):
    #     self.printer.PrintZReport()

    # def print_x_report(self):
    #     self.printer.PrintXReport()

    def __str__(self):
        return '\n'.join(f'"{trama}"' for trama in self.printer_trace())