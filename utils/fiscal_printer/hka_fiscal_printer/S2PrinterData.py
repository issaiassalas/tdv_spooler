from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=70)
class S2PrinterData(PrinterData):
    _subTotalBases = 0.0
    _subTotalTax = 0.0
    _datadummy = ''
    _quantityArticles = 0
    _amountPayable = 0.0
    _numberPaymentsMade = 0
    _typeDocument = 0

    def __init__(self, trama):
        properties = Util.splitAndExpectLength(trama[1:-1], 2)
        if (len(properties) > 1):
            self._setSubTotalBases(Util.doDouble(properties[0][3:]))
            self._setSubTotalTax(Util.doDouble(properties[1][1:]))
            self._setDataDummy(properties[2][1:])
            self._setQuantityArticles(int(properties[3]))
            self._setAmountPayable(Util.doDouble(properties[4][1:]))
            self._setNumberPaymentsMade(int(properties[5]))
            self._setTypeDocument(int(properties[6]))

    def SubTotalBases(self):
        return self._subTotalBases

    def SubTotalTax(self):
        return self._subTotalTax

    def DataDummy(self):
        return self._dataDummy

    def AmountPayable(self):
        return self._amountPayable

    def NumberPaymentsMade(self):
        return self._numberPaymentsMade

    def QuantityArticles(self):
        return self._quantityArticles

    def TypeDocument(self):
        return self._typeDocument

    def Condition(self):
        return self._condition

    def _setQuantityArticles(self, value):
        self._quantityArticles = value

    def _setTypeDocument(self, type):
        self._typeDocument = type

    def _setCondition(self, condition):
        self._condition = condition

    def _setSubTotalBases(self, subTotalBases):
        self._subTotalBases = subTotalBases

    def _setSubTotalTax(self, subTotalTax):
        self._subTotalTax = subTotalTax

    def _setDataDummy(self, dataDummy):
        self._dataDummy = dataDummy

    def _setAmountPayable(self, amountPayable):
        self._amountPayable = amountPayable

    def _setNumberPaymentsMade(self, numberPaymentsMade):
        self._numberPaymentsMade = numberPaymentsMade

    def getData(self):
        return {
            'subtotal_ib': self._subTotalBases,
            'taxes_subtotal': self._subTotalTax,
            'data_dummy': self._dataDummy,
            'articles_quantity': self._quantityArticles,
            'payable_amount': self._amountPayable,
            'quantity_payments_made': self._numberPaymentsMade,
            'doc_type': self._typeDocument
        }