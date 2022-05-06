from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=1)
class S7PrinterData(PrinterData):
    def __init__(self, trama):
        properties = Util.splitAndExpectLength(trama[1:-2], 1)
        self._setMICR(str(properties[0][2:]))

    def MICR(self):
        return self._micr

    def _setMICR(self, micr):
        self._micr = micr
