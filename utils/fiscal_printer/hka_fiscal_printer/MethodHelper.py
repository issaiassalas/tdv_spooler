from .printer_data import *

import datetime

class MethodHelper(object):
    def __init__(self):
        self.commands = []

    def SendCmd(self, cmd):
        self.commands.append(cmd)

    def GetS1PrinterData(self, trama: str = ''):
        return S1PrinterData(trama)

    def GetS2PrinterData(self, trama: str = ''):
        return S2PrinterData(trama)
        
    def GetS3PrinterData(self, trama: str = ''):
        return S3PrinterData(trama)

    def GetS4PrinterData(self, trama: str = ''):
        return S4PrinterData(trama)

    def GetS5PrinterData(self, trama: str = ''):
        return S5PrinterData(trama)

    def GetS6PrinterData(self, trama: str = ''):
        return S6PrinterData(trama)

    def GetS7PrinterData(self, trama: str = ''):
        return S7PrinterData(trama)

    def GetS8EPrinterData(self, trama: str = ''):
        return S8EPrinterData(trama)

    def GetS8PPrinterData(self, trama: str = ''):
        return S8PPrinterData(trama)

    def GetXReport(self, trama: str = ''):
        return ReportData(trama)

    def GetX2Report(self, trama: str = ''):
        return ReportData(trama)

    def GetX4Report(self, trama: str = ''):
        return AcumuladosX(trama)

    def GetX5Report(self, trama: str = ''):
        return AcumuladosX(trama)

    def GetX7Report(self, trama: str = ''):
        return AcumuladosX(trama)

    # (self, mode, startParam, endParam): #(self, startDate, endDate):
    def GetZReport(self, *items):
        if(len(items) > 0):
            mode = items[0]
            startParam = items[1]
            endParam = items[2]
            if (type(startParam) == datetime.date and type(endParam) == datetime.date):
                starString = startParam.strftime("%d%m%y")
                endString = endParam.strftime("%d%m%y")
                cmd = "U2"+mode+starString+endString
                self.trama = self._ReadFiscalMemoryByDate(cmd)
            else:
                starString = str(startParam)
                while (len(starString) < 6):
                    starString = "0" + starString
                endString = str(endParam)
                while (len(endString) < 6):
                    endString = "0" + endString
                cmd = "U3"+mode+starString+endString
                self.trama = self._ReadFiscalMemoryByNumber(cmd)
            self.ReportData = []
            i = 0
            for report in self.trama[0:-1]:
                self.Z = ReportData(report)
                self.ReportData.append(self.Z)
                i += 1
        else:
            self.trama = self._UploadDataReport("U0Z")
            self.ReportData = ReportData(self.trama)
        return self.ReportData

    def PrintXReport(self):
        self.trama = self._States_Report("I0X", 4)
        return self.trama

    def PrintZReport(self, *items):  # (self, mode, startParam, endParam):
        if(len(items) > 0):
            mode = items[0]
            startParam = items[1]
            endParam = items[2]

            rep = False

            # if(type(startParam)==int and (type(endParam)==int)):
            if (type(startParam) == datetime.date and type(endParam) == datetime.date):
                starString = startParam.strftime("%d%m%y")
                endString = endParam.strftime("%d%m%y")
                cmd = "I2"+mode+starString+endString
                rep = self.SendCmd("I2" + mode + starString + endString)
            else:
                starString = str(startParam)
                while (len(starString) < 6):
                    starString = "0" + starString
                endString = str(endParam)
                while (len(endString) < 6):
                    endString = "0" + endString
                rep = self.SendCmd("I3" + mode + starString + endString)
                if (rep == False):
                    if (starString > endString):
                        # raise(Estado)
                        estado = "The original number can not be greater than the final number"
        else:
            self.trama = self._States_Report("I0Z", 9)
            return self.trama