from PyQt5.QtCore import QMutex
from .model_selector import model_selector
from .thcontroller import FPPrinterController
from time import sleep
import serial

DEFAULT_PORT = {
    'bytesize': serial.EIGHTBITS,
    'stopbits': serial.STOPBITS_ONE,
    'parity': serial.PARITY_EVEN,
    'timeout': 2,
    'writeTimeout': 5
}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PrinterController(object):
    __metaclass__ = Singleton

    def __init__(self, port: str = 'COM4', baudrate: int = 9600, model: str = ''):
        self._model = model
        self.printer_controller = FPPrinterController()
        self.printer_formatter = model_selector(self._model, self.printer_controller)
        self._port = port
        self._baudrate = baudrate
        self._is_busy = False
        self.mutex = QMutex()

    @property
    def is_busy(self):
        self.mutex.lock()
        busy = self._is_busy
        self.mutex.unlock()
        return busy

    @is_busy.setter
    def is_busy(self, busy):
        self.mutex.lock()
        self._is_busy = busy
        self.mutex.unlock()

    @property
    def trace(self):
        return self.printer_formatter.printer_trace()

    @property
    def connected(self):
        if self._model == 'FILE':
            print('hohjfodsfdsjfosdjfoj')
            return True
        return self.printer_controller.is_open()

    @property
    def model_format(self):
        return model_selector(self._model, self.printer_controller)

    def try_connection(self):
        if self._model == 'FILE':
            return True
        else:
            self.printer_controller.open_port(
                port=self._port,
                baudrate=self._baudrate,
                **DEFAULT_PORT
            )

    def close_connection(self):
        if self.connected:
            self.printer_controller.close_port()

    def print_report_x(self, progress=None):
        progress.emit('Imprimiendo Reporte X')
        self.printer_formatter = self.model_format
        self.is_busy = True
        self.printer_formatter.report_x()
        self.printer_controller.send_cmds(self.trace)
        sleep(3)
        self.is_busy = False

    def print_report_z(self, progress=None):
        progress.emit('Imprimiendo Reporte Z')
        self.printer_formatter = self.model_format
        self.is_busy = True
        self.printer_formatter.report_z()
        print(self.printer_controller.send_cmds(self.trace))
        sleep(3)
        self.is_busy = False

    def print_programation(self, progress=None):
        progress.emit('Imprimiendo Programacion')
        self.printer_formatter = self.model_format
        self.is_busy = True
        self.printer_formatter.print_programation()
        sleep(3)
        self.is_busy = False

    def credit_note(self, progress=None, db_invoice=None, **kwargs):
        progress.emit('Imprimiendo Nota de credito: ' + db_invoice.name)
        self.printer_formatter = self.model_format
        self.is_busy = True
        self.printer_formatter.append_data(invoice = db_invoice)
        status_s1 = self.printer_formatter.credit_note(
            document=db_invoice.ticket_ref,
            serial=db_invoice.fp_serial_num,
            date=db_invoice.fp_serial_date,
            **kwargs
        )
        if status_s1:
            db_invoice.cn_ticket_ref = status_s1.get('last_nc_number', 0)
            db_invoice.num_report_z = status_s1.get('daily_closure_counter', 0) + 1
            db_invoice.fp_serial_num = status_s1.get('registered_machine_number', '????????')
            db_invoice.fp_serial_date = status_s1.get('current_printer_date', '????????')
        else:
            progress.emit('No se obtuvo respuesta')
        db_invoice.state = 'DONE'
        db_invoice.save()
        self.is_busy = False
        progress.emit('Listo...')


    def custom_invoice(self, progress=None, db_invoice=None, **kwargs):
        progress.emit('Imprimiendo factura: ' + db_invoice.name)
        self.printer_formatter = self.model_format
        self.is_busy = True
        self.printer_formatter.append_data(invoice = db_invoice)
        status_s1 = self.printer_formatter.custom_invoice(**kwargs)
        if status_s1:
            db_invoice.ticket_ref = status_s1.get('last_invoice_number', 0)
            db_invoice.cn_ticket_ref = status_s1.get('last_nc_number', 0)
            db_invoice.num_report_z = status_s1.get('daily_closure_counter', 0) + 1
            db_invoice.fp_serial_num = status_s1.get('registered_machine_number', '????????')
            db_invoice.fp_serial_date = status_s1.get('current_printer_date', '???????')
        else:
            progress.emit('No se obtuvo la respuesta')
        db_invoice.state = 'DONE'
        db_invoice.save()

        self.is_busy = False
        progress.emit('Listo...')

    def reprint_document(self, progress=None, db_invoice=None, **kwargs):
        progress.emit('Reimprimiendo Documento')
        self.printer_formatter = self.model_format
        self.is_busy = True
        self.printer_formatter.reprint_document(
            ref=db_invoice.ticket_ref
            if db_invoice.invoice_type == 'out_invoice'
            else db_invoice.cn_ticket_ref,
            document_type=db_invoice.invoice_type
        )
        db_invoice.state = 'DONE'
        db_invoice.save()

        self.is_busy = False

    def get_s1(self, *args, **kwargs):
        report = self.printer_controller.get_state(state='S1')
        return self.printer_formatter.get_state(state='S1', trama=report)

    def nf_document(self, progress=None, **kwargs):
        progress.emit('Imprimiendo Documento no fiscal')
        self.printer_formatter = self.model_format
        self.is_busy = True
        status_s1 = self.printer_formatter.nf_document(**kwargs)
        last_document = status_s1.get('number_non_fiscal_document')
        progress.emit(f'Documento no fiscal impreso: {last_document}')

        self.is_busy = False


    def get_fiscal_status(self, progress=None, **kwargs):
        progress.emit('Obteniendo estado fiscal')
        self.printer_formatter = self.model_format
        print(type(self.printer_formatter))
        self.is_busy = True
        response = self.printer_formatter.get_fiscal_status()
        progress.emit(f'Estado fiscal: {response}')

        self.is_busy = False
