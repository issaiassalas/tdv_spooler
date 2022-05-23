import PyInstaller.__main__
PyInstaller.__main__.run([
    'main.py',
    '--clean',
    '--noconsole',
    '--icon=./assets/tdv_logo.ico',
    '--name=odoovenezuela'
])

