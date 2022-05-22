from .printer_data import *
from ..thcontroller import FPPrinterController
import serial
import datetime
import time
import json

class MethodHelper(object):
    def __init__(self, printer_controller = None):
        self.printer_controller = printer_controller
        self.commands = []

    def execute(self, *args, **kwargs):
        try:
            result = self.printer_controller.send_cmd(*args, **kwargs)
            print(result)
            return result
        except Exception as e:
            message = self.get_status_error(
                *json.loads(str(e)).get('status_error')
            )
            print(message)

    def ReadFpStatus(self):
        '''
            get status of fiscal printer as errorInterface

            returns: ErrorInterface
        '''
        if self._HandleCTSRTS():
            msg = chr(0x05)
            self._write(msg)
            time.sleep(0.05)
            r = self._read(5)
            if len(r) == 5:
                if ord(r[1]) ^ ord(r[2]) ^ 0x03 == ord(r[4]):
                    return self.get_status_error(ord(r[1]), ord(r[2]))
                else:
                    return self.get_status_error(0, 144)
            else:
                return self.get_status_error(0, 114)
        else:
            return self.get_status_error(0, 128)

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

    def _ReadFiscalMemoryByNumber(self, cmd:str) -> str:
        '''reads the fiscal memory at the given cmd params'''
        msg = ""
        msg_list = []
        counter = 0
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                m = ""
                msg = self._AssembleQueryToSend(cmd)
                self._write(msg)
                rt = self._read(1)
                while True:
                    while msg != chr(0x04):
                        time.sleep(0.5)
                        msg = self._Debug('ACK')
                        self._write(msg)
                        time.sleep(0.5)
                        msg = self._FetchRow_Report(1.3)
                        if(msg == None):
                            counter += 1
                        else:
                            msg_list.append(msg)
                    return msg_list
            else:
                self.get_status_error(0, 128)
                self.message = "Error... CTS in False"
                m = None
                self.ser.setRTS(False)
        except serial.SerialException:
            m = None
        return m

    def _ReadFiscalMemoryByDate(self, cmd:str) -> str:
        '''reads the fiscal memory at the given cmd params'''
        msg = ""
        msg_list = []
        counter = 0
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                m = ""
                msg = self._AssembleQueryToSend(cmd)
                self._write(msg)
                rt = self._read(1)
                while True:
                    while msg != chr(0x04):
                        time.sleep(0.5)
                        msg = self._Debug('ACK')
                        self._write(msg)
                        time.sleep(0.5)
                        msg = self._FetchRow_Report(1.5)
                        if(msg == None):
                            counter += 1
                        else:
                            msg_list.append(msg)
                    return msg_list
            else:
                self.get_status_error(0, 128)
                self.message = "Error... CTS in False"
                m = None
                self.ser.setRTS(False)
        except serial.SerialException:
            m = None
        return m

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

    def get_status_error(self, st, er):
        st_aux = st
        st = st & ~0x04

        if (st & 0x6A) == 0x6A:  # En modo fiscal, carga completa de la memoria fiscal y emisi�n de documentos no fiscales
            self.status = 'En modo fiscal, carga completa de la memoria fiscal y emisi�n de documentos no fiscales'
            status = "12"
        # En modo fiscal, carga completa de la memoria fiscal y emisi�n de documentos  fiscales
        elif (st & 0x69) == 0x69:
            self.status = 'En modo fiscal, carga completa de la memoria fiscal y emisi�n de documentos  fiscales'
            status = "11"
        elif (st & 0x68) == 0x68:  # En modo fiscal, carga completa de la memoria fiscal y en espera
            self.status = 'En modo fiscal, carga completa de la memoria fiscal y en espera'
            status = "10"
        elif (st & 0x72) == 0x72:  # En modo fiscal, cercana carga completa de la memoria fiscal y en emisi�n de documentos no fiscales
            self.status = 'En modo fiscal, cercana carga completa de la memoria fiscal y en emisi�n de documentos no fiscales'
            status = "9 "
        elif (st & 0x71) == 0x71:  # En modo fiscal, cercana carga completa de la memoria fiscal y en emisi�n de documentos no fiscales
            self.status = 'En modo fiscal, cercana carga completa de la memoria fiscal y en emisi�n de documentos no fiscales'
            status = "8 "
        elif (st & 0x70) == 0x70:  # En modo fiscal, cercana carga completa de la memoria fiscal y en espera
            self.status = 'En modo fiscal, cercana carga completa de la memoria fiscal y en espera'
            status = "7 "
        elif (st & 0x62) == 0x62:  # En modo fiscal y en emisi�n de documentos no fiscales
            self.status = 'En modo fiscal y en emisi�n de documentos no fiscales'
            status = "6 "
        elif (st & 0x61) == 0x61:  # En modo fiscal y en emisi�n de documentos fiscales
            self.status = 'En modo fiscal y en emisi�n de documentos fiscales'
            status = "5 "
        elif (st & 0x60) == 0x60:  # En modo fiscal y en espera
            self.status = 'En modo fiscal y en espera'
            status = "4 "
        elif (st & 0x42) == 0x42:  # En modo prueba y en emisi�n de documentos no fiscales
            self.status = 'En modo prueba y en emisi�n de documentos no fiscales'
            status = "3 "
        elif (st & 0x41) == 0x41:  # En modo prueba y en emisi�n de documentos fiscales
            self.status = 'En modo prueba y en emisi�n de documentos fiscales'
            status = "2 "
        elif (st & 0x40) == 0x40:  # En modo prueba y en espera
            self.status = 'En modo prueba y en espera'
            status = "1 "
        elif (st & 0x00) == 0x00:  # Status Desconocido
            self.status = 'Status Desconocido'
            status = "0 "

        if (er & 0x6C) == 0x6C:  # Memoria Fiscal llena
            self.error = 'Memoria Fiscal llena'
            error = "108"
        elif (er & 0x64) == 0x64:  # Error en memoria fiscal
            self.error = 'Error en memoria fiscal'
            error = "100"
        elif (er & 0x60) == 0x60:  # Error Fiscal
            self.error = 'Error Fiscal'
            error = "96 "
        elif (er & 0x5C) == 0x5C:  # Comando Invalido
            self.error = 'Comando Invalido'
            error = "92 "
        elif (er & 0x58) == 0x58:  # No hay asignadas  directivas
            self.error = 'No hay asignadas  directivas'
            error = "88 "
        elif (er & 0x54) == 0x54:  # Tasa Invalida
            self.error = 'Tasa Invalida'
            error = "84 "
        elif (er & 0x50) == 0x50:  # Comando Invalido/Valor Invalido
            self.error = 'Comando Invalido/Valor Invalido'
            error = "80 "
        elif (er & 0x43) == 0x43:  # Fin en la entrega de papel y error mec�nico
            self.error = 'Fin en la entrega de papel y error mec�nico'
            error = "3  "
        elif (er & 0x42) == 0x42:  # Error de indole mecanico en la entrega de papel
            self.error = 'Error de indole mecanico en la entrega de papel'
            error = "2  "
        elif (er & 0x41) == 0x41:  # Fin en la entrega de papel
            self.error = 'Fin en la entrega de papel'
            error = "1  "
        elif (er & 0x40) == 0x40:  # Sin error
            self.error = 'Sin error'
            error = "0  "

        if (st_aux & 0x04) == 0x04:  # Buffer Completo
            self.error = ''
            error = "112 "
        elif er == 128:     # Error en la comunicacion
            self.error = 'CTS en falso'
            error = "128 "
        elif er == 137:     # No hay respuesta
            self.error = 'No hay respuesta'
            error = "137 "
        elif er == 144:     # Error LRC
            self.error = 'Error LRC'
            error = "144 "
        elif er == 114:
            self.error = 'Impresora no responde o ocupada'
            error = "114 "
        return status+"   " + error+"   " + self.error