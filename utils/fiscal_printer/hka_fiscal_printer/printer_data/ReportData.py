import datetime
from .Util import Util


@Util.tramaValidator(length=101)
class ReportData(object):
    _numberOfLastZReport = 0
    _zReportDate = 0
    _zReportTime = 0
    _numberOfLastInvoice = 0
    _lastInvoiceDate = 0
    _lastInvoiceTime = 0
    _numberOfLastDebitNote = 0
    _numberOfLastCreditNote = 0
    _numberOfLastNonFiscal = 0
    _freeSalesTax = 0
    _generalRate1Sale = 0
    _generalRate1Tax = 0
    _reducedRate2Sale = 0
    _reducedRate2Tax = 0
    _additionalRate3Sal = 0
    _additionalRate3Tax = 0
    _freeTaxDebit = 0
    _generalRateDebit = 0
    _generalRateTaxDebit = 0
    _reducedRateDebit = 0
    _reducedRateTaxDebit = 0
    _additionalRateDebit = 0
    _additionalRateTaxDebit = 0
    _freeTaxDevolution = 0
    _generalRateDevolution = 0
    _generalRateTaxDevolution = 0
    _reducedRateDevolution = 0
    _reducedRateTaxDevolution = 0
    _additionalRateDevolution = 0
    _additionalRateTaxDevolution = 0
    def __init__(self, trama):
        properties = str(trama[1:-1]).split(chr(0X0A))

        if (len(properties) == 31):
            self._numberOfLastZReport = int(properties[0])
            _hr = properties[2][0:2]
            _mn = properties[2][2:4]
            _dd = properties[1][4:6]
            _mm = properties[1][2:4]
            _aa = int(properties[1][0:2])+2000
            _Date = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            _Time = str(_hr) + ":" + str(_mn)
            self._zReportDate = _Date
            self._zReportTime = _Time

            self._numberOfLastInvoice = int(properties[3])
            _hr = properties[5][0:2]
            _mn = properties[5][2:4]
            _dd = properties[4][4:6]
            _mm = properties[4][2:4]
            _aa = int(properties[4][0:2])+2000
            _Date = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            _Time = str(_hr) + ":" + str(_mn)
            self._lastInvoiceDate = _Date
            self._lastInvoiceTime = _Time

            self._numberOfLastCreditNote = int(properties[6])
            self._numberOfLastDebitNote = int(properties[7])
            self._numberOfLastNonFiscal = int(properties[8])
            self._freeSalesTax = Util.doDouble(properties[9])
            self._generalRate1Sale = Util.doDouble(properties[10])
            self._generalRate1Tax = Util.doDouble(properties[11])
            self._reducedRate2Sale = Util.doDouble(properties[12])
            self._reducedRate2Tax = Util.doDouble(properties[13])
            self._additionalRate3Sal = Util.doDouble(properties[14])
            self._additionalRate3Tax = Util.doDouble(properties[15])
            self._freeTaxDebit = Util.doDouble(properties[16])
            self._generalRateDebit = Util.doDouble(properties[17])
            self._generalRateTaxDebit = Util.doDouble(properties[18])
            self._reducedRateDebit = Util.doDouble(properties[19])
            self._reducedRateTaxDebit = Util.doDouble(properties[20])
            self._additionalRateDebit = Util.doDouble(properties[21])
            self._additionalRateTaxDebit = Util.doDouble(properties[22])
            self._freeTaxDevolution = Util.doDouble(properties[23])
            self._generalRateDevolution = Util.doDouble(properties[24])
            self._generalRateTaxDevolution = Util.doDouble(properties[25])
            self._reducedRateDevolution = Util.doDouble(properties[26])
            self._reducedRateTaxDevolution = Util.doDouble(properties[27])
            self._additionalRateDevolution = Util.doDouble(properties[28])
            self._additionalRateTaxDevolution = Util.doDouble(properties[29])

        if (len(properties) == 21):  # (PP1F3,HSP7000,OKI,SRP350,TALLY1125,SRP270)

            self._numberOfLastZReport = int(properties[0])
            _dd = properties[1][4:6]
            _mm = properties[1][2:4]
            _aa = int(properties[1][0:2])+2000
            _Date = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            self._zReportDate = _Date

            self._numberOfLastInvoice = int(properties[2])
            _hr = properties[4][0:2]
            _mn = properties[4][2:4]
            _dd = properties[3][4:6]
            _mm = properties[3][2:4]
            _aa = int(properties[3][0:2])+2000
            _Date = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            _Time = str(_hr) + ":" + str(_mn)
            self._lastInvoiceDate = _Date
            self._lastInvoiceTime = _Time

            self._freeSalesTax = Util.doDouble(properties[5])
            self._generalRate1Sale = Util.doDouble(properties[6])
            self._generalRate1Tax = Util.doDouble(properties[7])
            self._reducedRate2Sale = Util.doDouble(properties[8])
            self._reducedRate2Tax = Util.doDouble(properties[9])
            self._additionalRate3Sal = Util.doDouble(properties[10])
            self._additionalRate3Tax = Util.doDouble(properties[11])
            self._freeTaxDevolution = Util.doDouble(properties[12])
            self._generalRateDevolution = Util.doDouble(properties[13])
            self._generalRateTaxDevolution = Util.doDouble(properties[14])
            self._reducedRateDevolution = Util.doDouble(properties[15])
            self._reducedRateTaxDevolution = Util.doDouble(properties[16])
            self._additionalRateDevolution = Util.doDouble(properties[17])
            self._additionalRateTaxDevolution = Util.doDouble(properties[18])
            self._numberOfLastCreditNote = int(properties[19])

        if (len(properties) == 22):  # (SRP-280)

            self._numberOfLastZReport = int(properties[0])
            _hr = properties[2][0:2]
            _mn = properties[2][2:4]
            _dd = properties[1][4:6]
            _mm = properties[1][2:4]
            _aa = int(properties[1][0:2])+2000
            _Date = str(_dd) + "-" + str(_mm) + "-" + str(_dd)
            _Time = str(_hr) + ":" + str(_mn)
            self._zReportDate = _Date
            self._zReportTime = _Time

            self._numberOfLastInvoice = int(properties[3])
            _hr = properties[5][0:2]
            _mn = properties[5][2:4]
            _dd = properties[4][0:2]
            _mm = properties[4][2:4]
            _aa = int(properties[4][4:6])+2000
            _Date = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            _Time = str(_hr) + ":" + str(_mn)
            self._lastInvoiceDate = _Date
            self._lastInvoiceTime = _Time

            self._freeSalesTax = Util.doDouble(properties[6])
            self._generalRate1Sale = Util.doDouble(properties[7])
            self._generalRate1Tax = Util.doDouble(properties[8])
            self._reducedRate2Sale = Util.doDouble(properties[9])
            self._reducedRate2Tax = Util.doDouble(properties[10])
            self._additionalRate3Sal = Util.doDouble(properties[11])
            self._additionalRate3Tax = Util.doDouble(properties[12])
            self._freeTaxDevolution = Util.doDouble(properties[13])
            self._generalRateDevolution = Util.doDouble(properties[14])
            self._generalRateTaxDevolution = Util.doDouble(properties[15])
            self._reducedRateDevolution = Util.doDouble(properties[16])
            self._reducedRateTaxDevolution = Util.doDouble(properties[17])
            self._additionalRateDevolution = Util.doDouble(properties[18])
            self._additionalRateTaxDevolution = Util.doDouble(properties[19])
            self._numberOfLastCreditNote = int(properties[20])

    def getData(self):
        return {
            "next_zreport" : self._numberOfLastZReport,
            "last_zreport_date": self._zReportDate,
            "last_zreport_time": self._zReportTime,
            "last_invoice_num": self._numberOfLastInvoice,
            "last_invoice_date": self._lastInvoiceDate,
            "last_invoice_time": self._lastInvoiceTime,
            "last_debit_note_num": self._numberOfLastDebitNote,
            "last_credit_note_num": self._numberOfLastCreditNote,
            "last_non_fiscal_num": self._numberOfLastNonFiscal,
            "free_tax_sales": self._freeSalesTax,
            "rate1_sales": self._generalRate1Sale,
            "rate1_tax": self._generalRate1Tax,
            "rate2_sales": self._reducedRate2Sale,
            "rate2_tax": self._reducedRate2Tax,
            "rate3_sales": self._additionalRate3Sal,
            "rate3_tax": self._additionalRate3Tax,
            "free_tax_debit_note": self._freeTaxDebit,
            "rate1_sales_debit_note": self._generalRateDebit,
            "rate1_tax_debit_note": self._generalRateTaxDebit,
            "rate2_sales_debit_note": self._reducedRateDebit,
            "rate2_tax_debit_note": self._reducedRateTaxDebit,
            "rate3_sales_debit_note": self._additionalRateDebit,
            "rate3_tax_debit_note": self._additionalRateTaxDebit,
            "free_tax_credit_note": self._freeTaxDevolution,
            "rate1_sales_credit_note": self._generalRateDevolution,
            "rate1_tax_credit_note": self._generalRateTaxDevolution,
            "rate2_sales_credit_note": self._reducedRateDevolution,
            "rate2_tax_credit_note": self._reducedRateTaxDevolution,
            "rate3_sales_credit_note": self._additionalRateDevolution,
            "rate3_tax_credit_note": self._additionalRateTaxDevolution
        }
