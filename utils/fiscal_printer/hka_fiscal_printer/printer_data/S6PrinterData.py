from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=1)
class S6PrinterData(PrinterData):
    _bit_Facturacion = 0
    _bit_Slip = 0
    _bit_Validacion = 0
    def __init__(self, trama):
        properties = str(Util.splitAndExpectLength(trama[1:-1], 2))
        self._setBit_Facturacion(str(properties[0][2:]))
        self._setBit_Slip(properties[1])
        self._setBit_Validacion(properties[2])

    def Bit_Facturacion(self):
        return self._bit_Facturacion

    def Bit_Slip(self):
        return self._bit_Slip

    def Bit_Validacion(self):
        return self._bit_Validacion

    def _setBit_Facturacion(self, bitFacturacion):
        self._bit_Facturacion = bitFacturacion

    def _setBit_Slip(self, bitSlip):
        self._bit_Slip = bitSlip

    def _setBit_Validacion(self, bitValidacion):
        self._bit_Validacion = bitValidacion

    def getData(self):
        return {
            "invoice_mode": self._bit_Facturacion,
            "slip_mode": self._bit_Slip,
            "validation_mode": self._bit_Validacion
        }
