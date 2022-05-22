from .hka_fiscal_printer import TDVHKAFormatter
from .rigazsa_fiscal_printer import RigazsaFormatter
from .file_fiscal_printer import FileFormatter

def model_selector(model, printer_controller):
    if model == 'HKA': 
        return TDVHKAFormatter(
            printer_controller = printer_controller
        )
    elif model == 'Rigazsa':
        return RigazsaFormatter(
            printer_controller = printer_controller
        )
    elif model == 'FILE':
        return FileFormatter(
            printer_controller = printer_controller
        )
    else:
        raise ValueError('El modelo indicado no existe')