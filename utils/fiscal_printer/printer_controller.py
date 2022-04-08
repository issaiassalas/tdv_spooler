from .model_selector import model_selector
from .thcontroller import TDVHKAController
from time import sleep
import serial

DEFAULT_PORT = {
    'bytesize':serial.EIGHTBITS,
    'stopbits': serial.STOPBITS_ONE,
    'parity': serial.PARITY_EVEN,
    'timeout': 2,
    'writeTimeout': 5
}

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class PrinterController(object):
    __metaclass__ = Singleton

    def __init__(self, port:str='COM4', baudrate:int=9600, model:str=''):
        self.printer_formatter = model_selector(model)
        self.printer_controller = TDVHKAController()
        self._port = port
        self._baudrate = baudrate
        self._is_connected = False
        self.is_busy = False

    @property
    def trace(self):
        return self.printer_formatter.printer_trace()

    @property
    def connected(self):
        return self._is_connected

    def try_connection(self):
        resp = self.printer_controller.open_port(
            port=self._port,
            baudrate=self._baudrate,
            **DEFAULT_PORT
        )
        if resp:
            self._is_connected = True

    def close_connection(self):
        if self._is_connected:
            resp = self.printer_controller.close_port()
            if resp:
                self._is_connected = False

    def print_programation(self, progress=None):
        progress.emit('Imprimiendo Programacion')
        self.is_busy = True
        self.printer_formatter.print_programation()
        self.printer_controller.send_cmds(self.trace)
        sleep(3)
        self.is_busy = False

    def get_state(self, state: str= 'S1'):
        self.is_busy = True
        response = self.printer_controller.get_state(state=state)
        self.is_busy = False
        return response

    def get_s1(self, *args, **kwargs):
        report = self.get_state(state='S1')
        # print(self.printer_formatter.get_state(state='S1', trama=report))
        print(report)
