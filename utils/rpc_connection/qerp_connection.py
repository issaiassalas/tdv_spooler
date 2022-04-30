import json
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer
from .erp_connection import ERPConnection
from db import *
from time import sleep
from ..format_invoices import format_invoices
from ..qprinter_controller import QPrinterController

class QERPConnection(QObject):
    finished = pyqtSignal()
    start_connection = pyqtSignal()
    progress = pyqtSignal(str)
    def __init__(
            self, 
            *args, 
            url = '',
            db = '',
            username = '',
            password = '',
            parent = None,
            **kwargs
            ):
        super().__init__(*args, **kwargs)
        self._erp_connection = ERPConnection(
            url = url, db = db, username = username, password = password
        )
        self._parent = parent
        self.paused = False
        self.thread = None
        self.mutex = parent.mutex
        self.threadConnection()

    def authenticated(self):
        return self._erp_connection.uid

    def print_new_invoice(self, invoice):
        self._parent.new_thread_signal.emit(
            # QPrinterController(
                {
                    'bind_function':
                        self._parent._printer.custom_invoice 
                        if invoice.invoice_type == 'out_invoice'
                        else self._parent._printer.credit_note,
                    'parent':self._parent,
                    'bind_dict':{
                        'db_invoice': invoice,
                        **json.loads(invoice.data)
                    },
                }
            # )
        )
        invoice.state = "PROCESSING"
        invoice.save()

    def retrieve_invoices(self):
        invoices = self._erp_connection.retrive_invoices()
        if invoices:
            invoice_ids = [
                invoice.get('id') for invoice in invoices
            ]
            saved_invoice_ids = [
                invoice.ref_id
                for invoice in Invoice.select().where(Invoice.ref_id.in_(invoice_ids))
            ]
            invoices = list(filter(
                lambda invoice: invoice.get('id') not in saved_invoice_ids,
                invoices
            ))

        if invoices:
            with db.atomic():
                Invoice.insert_many(format_invoices(invoices)).execute()


    def send_completed_invoices(self):
        db_invoices = Invoice.select().where(Invoice.state == 'DONE')
        invoices = self._erp_connection.update_invoices(
            invoices=[
            {
                'id': invoice.ref_id,
                'ticket_ref': invoice.ticket_ref,
                'num_report_z': invoice.num_report_z,
                'fp_serial_num': invoice.fp_serial_num,
                'fp_serial_date': invoice.fp_serial_date,
                'cn_ticket_ref': invoice.cn_ticket_ref,
            }
            for invoice in db_invoices
        ])

        print(invoices)

        if db_invoices:
            Invoice.update(state='SENT').where(Invoice.id.in_(
                [inv.id for inv in db_invoices]
            )).execute()

    def connection_handler(self):
        try:
            self.mutex.lock()
            self._parent.stop_connection.emit()
            invoice = Invoice.select().where(Invoice.state == 'PENDING').first()
            if invoice:
                self.print_new_invoice(invoice)
            else:
                self.retrieve_invoices()

            self.send_completed_invoices()
            
        except ConnectionRefusedError:
            self.progress.emit('Hay problemas con la conexion...')
            sleep(3)
        finally:
            self.mutex.unlock()
            self._parent.start_connection.emit()


    def threadConnection(self):
        self.thread = QThread()
        # Step 3: Create a process object
        # Step 4: Move process to the thread
        self.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        # self.thread.started.connect(self.call_binded_function)
        self.finished.connect(self.thread.quit)
        self.finished.connect(self.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.start_connection.connect(self.connection_handler)
        self.progress.connect(self._parent.append_to_output)
        # Step 6: Start the thread
        self.thread.start()