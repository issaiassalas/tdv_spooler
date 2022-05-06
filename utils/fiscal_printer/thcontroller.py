
from functools import reduce

import serial
import operator
import time


class FPPrinter:
    '''TFHKA base class with connection to ports'''

    def __init__(self):
        self.ctrlFlag = False
        self.mDebug = False
        self.status = ''
        self.message = ''
        self.error = ''

    def OpenFpctrl(self, **kwargs) -> bool:
        '''try to open the selected port and return if is successfull'''
        if not self.ctrlFlag:
            try:
                self.ser = serial.Serial(**kwargs)
                self.ctrlFlag = True
                return True
            except serial.SerialException:
                self.ctrlFlag = False
                self.message = f"Impresora no conectada o error accediendo al puerto {kwargs.get('port')}"
                return False

    def CloseFpctrl(self) -> bool:
        '''Closes the current port and return the inner flag'''
        if self.ctrlFlag:
            self.ser.close()
            self.ctrlFlag = False
            return self.ctrlFlag

    def getState(self, state) -> dict:
        return self._States(state)

    def _HandleCTSRTS(self):
        '''handles the try of using RTS protocol and return the CTS status as bool'''
        try:
            self.ser.setRTS(True)
            lpri = 1
            while not self.ser.getCTS():
                time.sleep(lpri/10)
                lpri = lpri+1
                if lpri > 20:
                    self.ser.setRTS(False)
                    return False
            return True
        except serial.SerialException:
            return False

    def SendCmd(self, cmd) -> str:
        '''return a cmd response'''

        if cmd in ["I0X", "I1X", "I1Z"]:
            return self._States_Report(cmd, 4)
        if cmd == "I0Z":
            return self._States_Report(cmd, 9)
        else:
            try:
                self.ser.flushInput()
                self.ser.flushOutput()
                if self._HandleCTSRTS():
                    msg = self._AssembleQueryToSend(cmd)
                    self._write(msg)
                    rt = self._read(self.ser.in_waiting or 1)
                    if rt == chr(0x06):
                        self.message = "Status: 00  Error: 00"
                    else:
                        self.message = "Status: 00  Error: 89"
                        rt = ''
                else:
                    self._GetStatusError(0, 128)
                    self.message = "Error... CTS in False"
                    rt = ''
                self.ser.setRTS(False)
            except serial.SerialException:
                rt = ''
            return rt

    def SendCmdFile(self, f):
        '''
            sends cmd file format
        '''
        for line in f:
            if (line != ""):
                self.SendCmd(line)

    def _QueryCmd(self, cmd:str, modify=True) -> bool:
        '''sends query to cmd if is valid'''
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                msg = cmd
                if modify:
                    msg = self._AssembleQueryToSend(cmd)
                self._write(msg)
                rt = chr(0x06)
            else:
                self._GetStatusError(0, 128)
                self.message = "Error... CTS in False"
                rt = chr(0X15)
                self.ser.setRTS(False)
        except serial.SerialException:
            rt = chr(0X15)
        return rt

    def _FetchRow(self) -> str:
        '''retrieves msg from cmd if any'''
        while True:
            time.sleep(1/2)
            bytes = self.ser.in_waiting
            if bytes <= 1:
                return self._read(1)
            msg = (self._read(bytes)).decode('utf-8')
            lrc = self._Lrc(msg[1:-1])
            if lrc:
                self.ser.flushInput()
                self.ser.flushOutput()
                return msg
            else:
                return ''

    def _FetchRow_Report(self, r:int) -> str:
        '''get rows in the given time if any'''
        while True:
            time.sleep(r)
            bytes = self.ser.inWaiting()
            if bytes > 0:
                msg = self._read(bytes)
                line = msg
                lrc = self._Lrc(line)
                if lrc == msg:
                    self.ser.flushInput()
                    self.ser.flushOutput()
                    return msg
                else:
                    return msg
            else:
                return ''

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
                    return self._GetStatusError(ord(r[1]), ord(r[2]))
                else:
                    return self._GetStatusError(0, 144)
            else:
                return self._GetStatusError(0, 114)
        else:
            return self._GetStatusError(0, 128)

    def _write(self, msg:str):
        '''write in the opened serial port'''
        self.ser.write(msg.encode())

    def _read(self, bytes:int) -> str:
        '''read the response of the serial port'''
        return self.ser.read(bytes)

    def _AssembleQueryToSend(self, line:str) -> str:
        '''concats the given params to respective format'''
        data = line + chr(0x03)
        return chr(0x02)+data+self._Lrc(data)

    def _Lrc(self, line:str) -> str:
        '''calculate block check character'''
        return chr(reduce(operator.xor, map(ord, str(line))))

    def _Debug(self, line:str) -> str:
        '''debugs the given line'''
        if line != '':
            if len(line) == 0:
                return 'null'
            if len(line) > 3:
                lrc = line[-1]
                line = line[0:-1]
                adic = ' LRC('+str(ord(lrc))+')'
            else:
                adic = ''
            line = line.replace('STX', chr(0x02), 1)
            line = line.replace('ENQ', chr(0x05), 1)
            line = line.replace('ETX', chr(0x03), 1)
            line = line.replace('EOT', chr(0x04), 1)
            line = line.replace('ACK', chr(0x06), 1)
            line = line.replace('NAK', chr(0x15), 1)
            line = line.replace('ETB', chr(0x17), 1)

        return line+adic

    def _States(self, cmd:str) -> str:
        '''get trama setup'''
        self._QueryCmd(cmd)
        return self._FetchRow()

    def _States_Report(self, cmd:str, r:int) -> str:
        '''cmd reports'''
        self._QueryCmd(cmd)
        return self._FetchRow_Report(r)

    def _UploadDataReport(self, cmd:str) -> str:
        '''uploads data to cmd'''
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                msg = 1
                msg = self._AssembleQueryToSend(cmd)
                self._write(msg)
                rt = self._read(1)
                while rt == chr(0x05):
                    rt = self._read(1)
                    if rt != '':
                        time.sleep(0.05)
                        msg = self._Debug('ACK')
                        self._write(msg)
                        time.sleep(0.05)
                        msg = self._FetchRow()
                        return msg
                    else:
                        self._GetStatusError(0, 128)
                        self.message = "Error... CTS in False"
                        rt = ''
                        self.ser.setRTS(False)
        except serial.SerialException:
            rt = ''
            return rt

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
                self._GetStatusError(0, 128)
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
                self._GetStatusError(0, 128)
                self.message = "Error... CTS in False"
                m = None
                self.ser.setRTS(False)
        except serial.SerialException:
            m = None
        return m

    def _GetStatusError(self, st, er):
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


class FPPrinterController:
    def __init__(self):
        self.printer = FPPrinter()

    def open_port(self, **kwargs):
        try:
            resp = self.printer.OpenFpctrl(**kwargs)
            if not resp:
                raise Exception('Impresora no Conectada o Error Accediendo al Puerto')
        except Exception as e:
            raise e
        else:
            return 1

    def close_port(self):
        resp = self.printer.CloseFpctrl()
        if resp:
            raise Exception("Error")
        return 1

    def send_cmds(self, cmds):
        response = []
        for cmd in cmds:
            response.append(self.send_cmd(cmd))
        return response

    def get_state(self, state: str = 'S1') -> str:
        '''get the given state Sx'''
        return self.printer.getState(state)

    def send_cmd(self, cmd):
        return self.printer._States(cmd)
