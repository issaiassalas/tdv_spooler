from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=1)
class S3PrinterData(PrinterData):
    _typeTax1 = 0
    _tax1 = 0
    _typeTax2 = 0
    _tax2 = 0
    _typeTax3 = 0
    _tax3 = 0
    _systemFlags = []
    def __init__(self, trama):
        properties = Util.splitAndExpectLength(trama[1:-1], 2)

        self._setTypeTax1(properties[0][2])
        self._setTax1(Util.doDouble(properties[0][3:]))
        self._setTypeTax2(properties[1][0])
        self._setTax2(Util.doDouble(properties[1][1:]))
        self._setTypeTax3(properties[2][0])
        self._setTax3(Util.doDouble(properties[2][1:]))

        _flagsQuantity = int(len(properties[3]) / 2)
        self._systemFlags = []
        _index = 0
        _iteration = 0
        while (_iteration < _flagsQuantity):
            self._systemFlags.append(int(properties[3][_index: _index+2]))
            _index += 2
            _iteration += 1

    def TypeTax1(self):
        return self._typeTax1

    def Tax1(self):
        return self._tax1

    def TypeTax2(self):
        return self._typeTax2

    def Tax2(self):
        return self._tax2

    def TypeTax3(self):
        return self._typeTax3

    def Tax3(self):
        return self._tax3

    def AllSystemFlags(self):
        return self._systemFlags

    def _setTypeTax1(self, typeTax1):
        self._typeTax1 = typeTax1

    def _setTax1(self, tax1):
        self._tax1 = tax1

    def _setTypeTax2(self, typeTax2):
        self._typeTax2 = typeTax2

    def _setTax2(self, tax2):
        self._tax2 = tax2

    def _setTypeTax3(self, typeTax3):
        self._typeTax3 = typeTax3

    def _setTax3(self, tax3):
        self._tax3 = tax3

    def _setSystemFlags(self, pSystemFlags):  # []
        self._systemFlags = pSystemFlags

    def getData(self):
        return {
            "rate1_type":self._typeTax1,
            "rate1":self._tax1,
            "rate2_type":self._typeTax2,
            "rate2: ":self._tax2,
            "rate3_type":self._typeTax3,
            "rate3: ":self._tax3,
            "flags":self._systemFlags
        }