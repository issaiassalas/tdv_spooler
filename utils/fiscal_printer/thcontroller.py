
from functools import reduce

import serial
import operator
import time


class TFBase:
    '''
      TFHKA base class with connection to ports
    '''

    def __init__(self):
        self.ctrlFlag = False
        self.mDebug = False
        self.status = ''
        self.message = ''
        self.error = ''

# Funcion ABRIR
    def OpenFpctrl(self, **kwargs):
        '''
            try to open the selected port with COM3 setup and return if is successfull

            params: 
                port: int

            returns: bool
        '''
        if not self.ctrlFlag:
            try:
                self.ser = serial.Serial(**kwargs)
                self.ctrlFlag = True
                return True
            except serial.SerialException:
                self.ctrlFlag = False
                self.message = f"Impresora no conectada o error accediendo al puerto {kwargs.get('port')}"
                return False

# Funcion CERRAR
    def CloseFpctrl(self):
        '''
            Closes the current port and return the inner flag

            returns: bool
        '''
        if self.ctrlFlag:
            self.ser.close()
            self.ctrlFlag = False
            return self.ctrlFlag

    def getState(self, state):
        return self._States(state)

# Funcion MANIPULA
    def _HandleCTSRTS(self):
        '''
            handles the try of using RTS protocol
            and return the CTS status as bool

            returns: bool
        '''
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

    def SendCmd(self, cmd):
        '''
            return a cmd response

            params:
                cmd: str

            returns: str or bool
        '''
        if cmd in ["I0X", "I1X", "I1Z"]:
            self.trama = self._States_Report(cmd, 4)
            return self.trama
        if cmd == "I0Z":
            self.trama = self._States_Report(cmd, 9)
            return self.trama
        else:
            try:
                self.ser.flushInput()
                self.ser.flushOutput()
                if self._HandleCTSRTS():
                    msj = self._AssembleQueryToSend(cmd)
                    self._write(msj)
                    rt = self._read(1)
                    if rt == chr(0x06):
                        self.message = "Status: 00  Error: 00"
                        rt = True
                    else:
                        self.message = "Status: 00  Error: 89"
                        rt = False
                else:
                    self._GetStatusError(0, 128)
                    self.message = "Error... CTS in False"
                    rt = False
                self.ser.setRTS(False)
            except serial.SerialException:
                rt = False
            return rt

    def SendCmdFile(self, f):
        '''
            sends cmd file format
        '''
        for linea in f:
            if (linea != ""):
                self.SendCmd(linea)

    def _QueryCmd(self, cmd, modify=True):
        '''
            sends query to cmd if is valid

            params:
                cmd: str

            returns: bool
        '''
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                msj = cmd
                if modify:
                    msj = self._AssembleQueryToSend(cmd)
                self._write(msj)
                rt = True
            else:
                self._GetStatusError(0, 128)
                self.message = "Error... CTS in False"
                rt = False
                self.ser.setRTS(False)
        except serial.SerialException:
            rt = False
        return rt

    def _FetchRow(self):
        '''
            retrieves msj from cmd if any

            returns: str or None
        '''
        while True:
            time.sleep(2)
            bytes = self.ser.inWaiting()
            if bytes <= 1:
                break
            msj = (self._read(bytes)).decode('utf-8')
            linea = msj[1:-1]
            lrc = chr(self._Lrc(linea))
            if lrc:
                self.ser.flushInput()
                self.ser.flushOutput()
                return msj
            else:
                break
        return None

    def _FetchRow_Report(self, r):
        '''
            get rows in the given time if any

            params:
                r: int

            returns: str or None
        '''
        while True:
            time.sleep(r)
            bytes = self.ser.inWaiting()
            if bytes > 0:
                msj = self._read(bytes)
                linea = msj
                lrc = chr(self._Lrc(linea))
                if lrc == msj:
                    self.ser.flushInput()
                    self.ser.flushOutput()
                    return msj
                else:
                    return msj
            else:
                break
        return None

    def ReadFpStatus(self):
        '''
            get status of fiscal printer as errorInterface

            returns: ErrorInterface
        '''
        if self._HandleCTSRTS():
            msj = chr(0x05)
            self._write(msj)
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

    def _write(self, msj):
        '''
            write in the opened serial port

            params:
                msj: str
        '''
        self.ser.write(msj.encode())

    def _read(self, bytes):
        '''
            read the response of the serial port

            params:
                bytes: int

            returns: str
        '''
        msj = self.ser.read(bytes)
        return msj

    def _AssembleQueryToSend(self, linea):
        '''
            concats the given params to respective format

            params:
                linea: str

            returns: str
        '''
        lrc = self._Lrc(linea+chr(0x03))
        previo = chr(0x02)+linea+chr(0x03)+chr(lrc)
        return previo

    def _Lrc(self, linea):
        '''
            format the given line

            params:
                linea: str

            returns: str
        '''
        return reduce(operator.xor, map(ord, str(linea)))

    def _Debug(self, linea):
        '''
            debugs the given line

            params:
                linea: str

            returns: str
        '''
        if linea != None:
            if len(linea) == 0:
                return 'null'
            if len(linea) > 3:
                lrc = linea[-1]
                linea = linea[0:-1]
                adic = ' LRC('+str(ord(lrc))+')'
            else:
                adic = ''
            linea = linea.replace('STX', chr(0x02), 1)
            linea = linea.replace('ENQ', chr(0x05), 1)
            linea = linea.replace('ETX', chr(0x03), 1)
            linea = linea.replace('EOT', chr(0x04), 1)
            linea = linea.replace('ACK', chr(0x06), 1)
            linea = linea.replace('NAK', chr(0x15), 1)
            linea = linea.replace('ETB', chr(0x17), 1)

        return linea+adic

    def _States(self, cmd):
        '''
            get trama setup

            params: 
                cmd: str

            returns: str or None
        '''
        self._QueryCmd(cmd)
        while True:
            trama = self._FetchRow()
            if trama == None:
                break
            return trama

    def _States_Report(self, cmd, r):
        '''
            cmd reports

            params:
                cmd: str
                r: int

            returns: str or None
        '''
        ret = r
        self._QueryCmd(cmd)
        while True:
            trama = self._FetchRow_Report(ret)
            if trama == None:
                break
            return trama

    def _UploadDataReport(self, cmd):
        '''
            uploads data to cmd

            params:
                cmd: str

            returns: str or None
        '''
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                msj = 1
                msj = self._AssembleQueryToSend(cmd)
                self._write(msj)
                rt = self._read(1)
                while rt == chr(0x05):
                    rt = self._read(1)
                    if rt != None:
                        time.sleep(0.05)
                        msj = self._Debug('ACK')
                        self._write(msj)
                        time.sleep(0.05)
                        msj = self._FetchRow()
                        return msj
                    else:
                        self._GetStatusError(0, 128)
                        self.message = "Error... CTS in False"
                        rt = None
                        self.ser.setRTS(False)
        except serial.SerialException:
            rt = None
            return rt

    def _ReadFiscalMemoryByNumber(self, cmd):
        '''
            reads the fiscal memory at the given cmd params

            params:
                cmd: str

            returns: [str] or None
        '''
        msj = ""
        arreglodemsj = []
        counter = 0
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                m = ""
                msj = self._AssembleQueryToSend(cmd)
                self._write(msj)
                rt = self._read(1)
                while True:
                    while msj != chr(0x04):
                        time.sleep(0.5)
                        msj = self._Debug('ACK')
                        self._write(msj)
                        time.sleep(0.5)
                        msj = self._FetchRow_Report(1.3)
                        if(msj == None):
                            counter += 1
                        else:
                            arreglodemsj.append(msj)
                    return arreglodemsj
            else:
                self._GetStatusError(0, 128)
                self.message = "Error... CTS in False"
                m = None
                self.ser.setRTS(False)
        except serial.SerialException:
            m = None
        return m

    def _ReadFiscalMemoryByDate(self, cmd):
        '''
            reads the fiscal memory at the given cmd params

            params:
                cmd: str

            returns: [str] or None
        '''
        msj = ""
        arreglodemsj = []
        counter = 0
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                m = ""
                msj = self._AssembleQueryToSend(cmd)
                self._write(msj)
                rt = self._read(1)
                while True:
                    while msj != chr(0x04):
                        time.sleep(0.5)
                        msj = self._Debug('ACK')
                        self._write(msj)
                        time.sleep(0.5)
                        msj = self._FetchRow_Report(1.5)
                        if(msj == None):
                            counter += 1
                        else:
                            arreglodemsj.append(msj)
                    return arreglodemsj
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


class TDVHKAController:
    def __init__(self):
        self.printer = TFBase()

    def open_port(self, **kwargs):
        try:
            resp = self.printer.OpenFpctrl(**kwargs)
            if not resp:
                raise Exception(
                    'Impresora no Conectada o Error Accediendo al Puerto')
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
        for cmd in cmds:
            self.send_cmd(cmd)

    def get_state(self, state: str = 'S1') -> str:
        '''
            get the given state Sx
        '''
        return self.printer.getState(state)

    def send_cmd(self, cmd):
        self.printer.SendCmd(cmd)
