import PyInstaller.__main__
PyInstaller.__main__.run([
    'tdv_fiscal_printer.py',
    '--onefile',
    '--clean',
    '--noconsole',
    '--icon=./assets/tdv_logo.ico',
])

