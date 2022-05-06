from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=1)
class S4PrinterData(PrinterData):
    _allMeansOfPayment = ''
    def __init__(self, trama):
        properties = Util.splitAndExpectLength(trama[1:-1], 2)
        _numberOfMeansOfPayment = len(properties) - 1
        _iteration = 0
        _valor = ''
        while (_iteration < _numberOfMeansOfPayment):
            _cadena = properties[_iteration]
            if (_iteration == 0):
                _valor = str(_cadena[2:])
            else:
                _valor = str(_cadena)
            self._allMeansOfPayment += "\nMedio de Pago " + \
                str(_iteration+1) + " : " + \
                str(Util.doDouble(_valor))
            _iteration += 1

    def AllMeansOfPayment(self):
        return self._allMeansOfPayment

    def _setAllMeansOfPayment(self, pAllMeansOfPayment):
        self._allMeansOfPayment = pAllMeansOfPayment

    def getData(self):
        return {
            'all_means_of_payment': self._allMeansOfPayment
        }
