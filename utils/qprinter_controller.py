from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QThread
from .fiscal_printer.printer_controller import PrinterController
from datetime import datetime
from time import sleep

class QPrinterController(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    disconected = pyqtSignal(str)

    def __init__(
            self, 
            *args, 
            bind_function:PrinterController=None,
            parent=None,
            lock=False,
            bind_dict={},
            **kwargs):
        super().__init__(*args, **kwargs)
        self.bind_function = bind_function
        self.bind_dict = bind_dict
        self.parent = parent
        self.lock = lock
        self.hash = str(hash(datetime.now()))

    def call_binded_function(self):
        try:
            self.bind_function(progress=self.progress, **self.bind_dict)
        # except Exception as e:
        #     self.disconected.emit(str(e))
        #     sleep(.5)
        finally:
            self.finished.emit()

    def threadConnection(self):
        self.thread = QThread()
        # Step 3: Create a process object
        # Step 4: Move process to the thread
        self.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.call_binded_function)
        self.finished.connect(self.thread.quit)
        self.finished.connect(self.deleteLater)
        self.disconected.connect(self.parent.connection_error)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.parent.delete_finished_thread)
        self.progress.connect(self.parent.append_to_output)
        # Step 6: Start the thread
        self.thread.start()

        if self.lock:
            self.shuffle_lock_buttons()
            self.thread.finished.connect(
                lambda: self.shuffle_lock_buttons()
            )