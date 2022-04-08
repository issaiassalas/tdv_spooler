import sys
from PyQt5.QtWidgets import QApplication
from controllers import main
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = main.MainWindow()
    ui.show()
    sys.exit(app.exec_())