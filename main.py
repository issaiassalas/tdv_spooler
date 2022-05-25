import sys
import traceback
from PyQt5.QtWidgets import QApplication
from controllers import main_controller
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ui = main_controller.MainWindow()
        ui.show()
        sys.exit(app.exec_())
    except Exception:
        with open('exceptions.log', 'w') as f:
            f.write(traceback.format_exc())