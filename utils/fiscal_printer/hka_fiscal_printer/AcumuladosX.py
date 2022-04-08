from .Util import Util


@Util.tramaValidator(length=1)
class AcumuladosX(object):
    def __init__(self, trama):
        properties = Util.splitExpectAndDoDouble(trama, 7)
        self._freeTax = properties[0]
        self._generalRate1 = properties[1]
        self._reducedRate2 = properties[2]
        self._additionalRate3 = properties[3]
        self._generalRate1Tax = properties[4]
        self._reducedRate2Tax = properties[5]
        self._additionalRate3Tax = properties[6]

    def FreeTax(self):
        return self._freeTax

    def GeneralRate1(self):
        return self._generalRate1

    def GeneralRate1Tax(self):
        return self._generalRate1Tax

    def ReducedRate2(self):
        return self._reducedRate2

    def ReducedRate2Tax(self):
        return self._reducedRate2Tax

    def AdditionalRate3(self):
        return self._additionalRate3

    def AdditionalRate3Tax(self):
        return self._additionalRate3Tax
