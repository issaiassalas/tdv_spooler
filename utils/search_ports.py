
from serial.tools.list_ports import comports

def get_available_ports():
    return list(comports())