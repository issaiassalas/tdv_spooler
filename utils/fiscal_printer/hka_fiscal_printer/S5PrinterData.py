from .Util import Util
from .PrinterData import PrinterData

@Util.tramaValidator(length=1)
class S5PrinterData(PrinterData):
    _rif = ''
    _registeredMachineNumber = 0
    _auditMemoryNumber = 0
    _auditMemoryTotalCapacity = 0
    _auditMemoryFreeCapacity = 0
    _numberRegisteredDocuments = 0

    def __init__(self, trama):
        properties = Util.splitAndExpectLength(trama[1:-1], 5)
        self._setRIF(properties[0][2:])
        self._setRegisteredMachineNumber(properties[1])
        self._setNumberMemoryAudit(int(properties[2]))
        self._setCapacityTotalMemoryAudit(int(properties[3]))
        self._setAuditMemoryFreeCapacity(int(properties[4]))
        self._setNumberDocumentRegisters(int(properties[5]))

    def RIF(self):
        return self._rif

    def RegisteredMachineNumber(self):
        return self._registeredMachineNumber

    def AuditMemoryNumber(self):
        return self._auditMemoryNumber

    def AuditMemoryTotalCapacity(self):
        return self._auditMemoryTotalCapacity

    def AuditMemoryFreeCapacity(self):
        return self._auditMemoryFreeCapacity

    def NumberRegisteredDocuments(self):
        return self._numberRegisteredDocuments

    def _setRIF(self, RIF):
        self._rif = RIF

    def _setRegisteredMachineNumber(self, registeredMachineNumber):
        self._registeredMachineNumber = registeredMachineNumber

    def _setNumberMemoryAudit(self, numberMemoryAudit):
        self._auditMemoryNumber = numberMemoryAudit

    def _setCapacityTotalMemoryAudit(self, capacityTotalMemoryAudit):
        self._auditMemoryTotalCapacity = capacityTotalMemoryAudit

    def _setAuditMemoryFreeCapacity(self, pAuditMemoryFreeCapacity):
        self._auditMemoryFreeCapacity = pAuditMemoryFreeCapacity

    def _setNumberDocumentRegisters(self, numberDocumentRegisters):
        self._numberRegisteredDocuments = numberDocumentRegisters

    def getData(self):
        return {
            "rif": self._rif,
            "register_num": self._registeredMachineNumber,
            "audit_memory_num": self._auditMemoryNumber,
            "audit_memory_total_cap": self._auditMemoryTotalCapacity,
            "available_space": self._auditMemoryFreeCapacity,
            "registered_documents_quantity": self._numberRegisteredDocuments,
        }
