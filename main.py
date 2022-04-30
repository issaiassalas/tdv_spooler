import sys
from PyQt5.QtWidgets import QApplication
from controllers import main_controller
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = main_controller.MainWindow()
    ui.show()
    sys.exit(app.exec_())