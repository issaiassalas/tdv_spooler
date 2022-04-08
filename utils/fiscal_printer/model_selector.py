from .hka_fiscal_printer import TDVHKAFormatter

def model_selector(model):
    if model == 'HKA': 
        return TDVHKAFormatter()
    else:
        raise ValueError('El modelo indicado no existe')