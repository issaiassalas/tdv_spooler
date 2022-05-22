
from functools import reduce

import json
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
        self.ser = None

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

    def is_open(self) -> bool:
        if self.ser and type(self.ser) == serial.Serial:
            return self.ser.is_open
        return False

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

    def _QueryCmd(self, cmd: str = '', modify: bool = True) -> bool:
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
                rt = chr(0X15)
                self.ser.setRTS(False)
                raise Exception(json.dumps({
                    'message': "Error... CTS in False",
                    'status_error': (0, 128)
                }))
        except serial.SerialException:
            rt = chr(0X15)
        return rt

    def _FetchRow(self, read_bytes: int = 1, wait_time: float = 1/5) -> str:
        '''retrieves msg from cmd if any'''
        while True:
            time.sleep(wait_time)
            bytes = self.ser.in_waiting
            if bytes <= 1:
                return self._read(read_bytes).decode('utf8')
            msg = (self._read(bytes)).decode('utf-8')
            lrc = self._Lrc(msg[1:-1])
            if lrc:
                self.ser.flushInput()
                self.ser.flushOutput()
                return msg
            else:
                return ''

    def _FetchRow_Report(self, r: int) -> str:
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

    def _write(self, msg: str):
        '''write in the opened serial port'''
        self.ser.write(msg.encode())

    def _read(self, bytes: int) -> str:
        '''read the response of the serial port'''
        return self.ser.read(bytes)

    def _AssembleQueryToSend(self, line: str) -> str:
        '''concats the given params to respective format'''
        data = line + chr(0x03)
        return chr(0x02)+data+self._Lrc(data)

    def _Lrc(self, line: str) -> str:
        '''calculate block check character'''
        return chr(reduce(operator.xor, map(ord, str(line))))

    def _Debug(self, line: str) -> str:
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

    def _States(self, cmd: str, time: float = 1/5, bytes: int = 1, modify: bool = True) -> str:
        '''get trama setup'''
        self._QueryCmd(cmd = cmd, modify = modify)
        return self._FetchRow(read_bytes = bytes, wait_time = time)

    def _States_Report(self, cmd: str, r: int) -> str:
        '''cmd reports'''
        self._QueryCmd(cmd)
        return self._FetchRow_Report(r)

    def _UploadDataReport(self, cmd: str) -> str:
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


class FPPrinterController:
    '''Default printer controller'''

    def __init__(self):
        self.printer = FPPrinter()

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

    def is_open(self):
        return self.printer.is_open()

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

    def send_cmd(self, *args, **kwargs):
        return self.printer._States(*args, **kwargs)
