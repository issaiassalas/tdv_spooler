from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=101)
class S1PrinterData(PrinterData):
    '''
        S1 status formated
    '''
    _cashierNumber = 0
    _totalDailySales = 0
    _lastInvoiceNumber = 0
    _quantityDebtNoteToday = 0
    _lastDebtNoteNumber = 0
    _quantityDebtNoteToday = 0
    _numberNonFiscalDocuments = 0
    _quantityNonFiscalDocuments = 0
    _dailyClosureCounter = 0
    _auditReportsCounter = 0
    _fiscalReportsCounter = 0
    _rif = 0
    _registeredMachineNumber = 0
    _currentPrinterDate = 0
    _currentPrinterTime = 0
    _lastNCNumber = 0
    _quantityOfNCToday = 0

    def __init__(self, trama):
        properties = str(trama[1:-1]).split(chr(0X0A))
        self.properties = properties
        if len(properties) <= 15:
            self._setCashierNumber(properties[0][2:])
            self._setTotalDailySales(Util.doDouble(properties[1]))
            self._setLastInvoiceNumber(int(properties[2]))
            self._setQuantityOfInvoicesToday(int(properties[3]))
            self._setNumberNonFiscalDocuments(int(properties[4]))
            self._setQuantityNonFiscalDocuments(int(properties[5]))
            self._setDailyClosureCounter(int(properties[6]))
            self._setFiscalReportsCounter(int(properties[7]))
            self._setRif(properties[8])
            self._setRegisteredMachineNumber(properties[9])

            _hr = properties[10][0:2]
            _mn = properties[10][2:4]
            _sg = properties[10][4:6]

            _dd = properties[11][0:2]
            _mm = properties[11][2:4]
            _aa = int(properties[11][4:6]) + 2000

            _printerDate = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            _printerTime = str(_hr) + ":" + str(_mn) + ":" + str(_sg)

            self._setCurrentPrinterTime(_printerTime)
            self._setCurrentPrinterDate(_printerDate)
            if len(properties) <= 13:
                self._setLastNCNumber(0)
                self._setQuantityOfNCToday(0)
            else:
                self._setLastNCNumber(int(properties[12]))
                self._setQuantityOfNCToday(int(properties[13]))
        else:
            self._setCashierNumber(properties[0][2:])
            self._setTotalDailySales(Util.doDouble(properties[1]))
            self._setLastInvoiceNumber(int(properties[2]))
            self._setQuantityOfInvoicesToday(int(properties[3]))
            self._setLastDebtNoteNumber(int(properties[4]))
            self._setQuantityDebtNoteToday(int(properties[5]))
            self._setLastNCNumber(int(properties[6]))
            self._setQuantityOfNCToday(int(properties[7]))
            self._setNumberNonFiscalDocuments(int(properties[8]))
            self._setQuantityNonFiscalDocuments(int(properties[9]))
            self._setAuditReportsCounter(int(properties[10]))
            self._setDailyClosureCounter(int(properties[11]))
            self._setRif(properties[12])
            self._setRegisteredMachineNumber(properties[13])

            _hr = properties[14][0:2]
            _mn = properties[14][2:4]
            _sg = properties[14][4:6]

            _dd = properties[15][0:2]
            _mm = properties[15][2:4]
            _aa = int(properties[15][4:6]) + 2000

            _printerDate = str(_dd) + "-" + str(_mm) + "-" + str(_aa)
            _printerTime = str(_hr) + ":" + str(_mn) + ":" + str(_sg)

            self._setCurrentPrinterTime(_printerTime)
            self._setCurrentPrinterDate(_printerDate)

    def CashierNumber(self):
        return self._cashierNumber

    def _setCashierNumber(self, cashierNumber):
        self._cashierNumber = cashierNumber

    def TotalDailySales(self):
        return self._totalDailySales

    def _setTotalDailySales(self, totalDailySales):
        self._totalDailySales = totalDailySales

    def LastInvoiceNumber(self):
        return self._lastInvoiceNumber

    def _setLastInvoiceNumber(self, lastInvoiceNumber):
        self._lastInvoiceNumber = lastInvoiceNumber

    def QuantityOfInvoicesToday(self):
        return self._quantityOfInvoicesToday

    def _setQuantityOfInvoicesToday(self, quantityOfInvoicesToday):
        self._quantityOfInvoicesToday = quantityOfInvoicesToday

    def LastDebtNoteNumber(self):
        return self._lastDebtNoteNumber

    def _setLastDebtNoteNumber(self, lastDebtNoteNumber):
        self._lastDebtNoteNumber = lastDebtNoteNumber

    def QuantityDebtNoteToday(self):
        return self._quantityDebtNoteToday

    def _setQuantityDebtNoteToday(self, quantityDebtNoteToday):
        self._quantityDebtNoteToday = quantityDebtNoteToday

    def NumberNonFiscalDocuments(self):
        return self._numberNonFiscalDocuments

    def _setNumberNonFiscalDocuments(self, numberNonFiscalDocuments):
        self._numberNonFiscalDocuments = numberNonFiscalDocuments

    def QuantityNonFiscalDocuments(self):
        return self._quantityNonFiscalDocuments

    def _setQuantityNonFiscalDocuments(self, quantityNonFiscalDocuments):
        self._quantityNonFiscalDocuments = quantityNonFiscalDocuments

    def DailyClosureCounter(self):
        return self._dailyClosureCounter

    def _setDailyClosureCounter(self, dailyClosureCounter):
        self._dailyClosureCounter = dailyClosureCounter

    def AuditReportsCounter(self):
        return self._auditReportsCounter

    def _setAuditReportsCounter(self, auditReportsCounter):
        self._auditReportsCounter = auditReportsCounter

    def FiscalReportsCounter(self):
        return self._fiscalReportsCounter

    def _setFiscalReportsCounter(self, fiscalReportsCounter):
        self._fiscalReportsCounter = fiscalReportsCounter

    def Rif(self):
        return self._rif

    def _setRif(self, rif):
        self._rif = rif

    def RegisteredMachineNumber(self):
        return self._registeredMachineNumber

    def _setRegisteredMachineNumber(self, registeredMachineNumber):
        self._registeredMachineNumber = registeredMachineNumber

    def CurrentPrinterDate(self):
        return self._currentPrinterDate

    def _setCurrentPrinterDate(self, currentPrinterDate):
        self._currentPrinterDate = currentPrinterDate

    def CurrentPrinterTime(self):
        return self._currentPrinterTime

    def _setCurrentPrinterTime(self, currentPrinterTime):
        self._currentPrinterTime = currentPrinterTime

    def LastNCNumber(self):
        return self._lastNCNumber

    def _setLastNCNumber(self, lastNCNumber):
        self._lastNCNumber = lastNCNumber

    def QuantityOfNCToday(self):
        return self._quantityOfNCToday

    def _setQuantityOfNCToday(self, quantityOfNCToday):
        self._quantityOfNCToday = quantityOfNCToday

    def getData(self):
        try:
            return {
                'cashier_number': self._cashierNumber,
                'total_daily_sales': self._totalDailySales,
                'last_invoice_number': self._lastInvoiceNumber,
                'quantity_of_invoices_today': self._quantityOfInvoicesToday,
                'last_debt_note_number': self._lastDebtNoteNumber,
                'quantity_debt_note_today': self._quantityDebtNoteToday,
                'last_nc_number': self._lastNCNumber,
                'quantity_of_nc_today': self._quantityOfNCToday,
                'number_non_fiscal_document': self._numberNonFiscalDocuments,
                'quantity_non_fiscal_documents': self._quantityNonFiscalDocuments,
                'audit_reports_counter': self._auditReportsCounter,
                'fiscal_reports_counter': self.FiscalReportsCounter(),
                'daily_closure_counter': self._dailyClosureCounter,
                'rif': self._rif,
                'registered_machine_number': self._registeredMachineNumber,
                'current_printer_time': self._currentPrinterTime,
                'current_printer_date': self._currentPrinterDate
            }
        except Exception as e:
            return {
                'message': 'there is a error', 
                'exception': e
            }
