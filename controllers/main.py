from PyQt5.QtWidgets import QMainWindow, QMessageBox, QSystemTrayIcon, QAction, QMenu, qApp
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QIcon, QPixmap
from views import Ui_main_window
from utils import get_available_ports, PrinterController, QPrinterController
from db import *

class MainWindow(QMainWindow, Ui_main_window.Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.menu_opened = True
        self._ports = []
        self.configuration = None
        self._outputText = []
        self._printer = None
        self._locked_buttons = True
        self._thread_pool = dict()
        self._active_thread = ''
        self.connect_database()
        self.set_output_timer()
        self.read_ports()
        self.connect_custom_actions()
        self.window_pages.setCurrentWidget(self.main_page)
        self.toggle_menu()

        icon = QIcon()
        icon.addPixmap(QPixmap(":/img/assets/tdv_logo.ico"), QIcon.Normal, QIcon.Off)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.set_main_user()

    @property
    def is_printer_connected(self):
        if self._printer:
            return self._printer.connected

    def connection_error(self, message):
        self._printer = None
        self.append_to_output(message)

    def connect_database(self):
        self.clear_output()

    def exit_fiscal_printer(self):
        quit_msg = "Seguro que desea quitar el programa?"
        reply = QMessageBox.question(self, 'Quitar', 
                        quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.force_disconnection()
            db.close()
            qApp.quit()

    def printer_action_setup(self):
        self._outputText.append('Intentando conexion...')
        if not self._printer:
            self._printer = PrinterController(
                port = self.ports.currentText(),
                baudrate = self.baud_rate.currentText(),
                model = self.printer_model.currentText()
            )

        if not self._printer.connected:
            try:
                self._printer.try_connection()
            except Exception as e:
                self._outputText.append(str(e))
            if self._printer.connected:
                port = self._printer._port
                self._outputText.append(f'La impresora ha sido conectada en el puerto {port}')
        else:
            window_message = "Seguro que desea terminar la conexion?"
            reply = QMessageBox.question(self, 'Terminar', window_message,
                        QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.force_disconnection()
                self._outputText.append('Se ha terminado la conexion..')

    def force_disconnection(self):
        if self._printer:
            self._printer.close_connection()

    def closeEvent(self, event):
        event.ignore()
        self.minimize_window()

    def minimize_window(self):
        self.hide()
        self.tray_icon.showMessage(
            "TDV - Impresora Fiscal", 
            "La aplicacion ha sido minimizada",
            QSystemTrayIcon.Information,
            2000
        )   

    def print_x_report(self):
        if self.is_printer_connected:
            pcontroller = QPrinterController(
                bind_function=self._printer.print_programation,
                parent=self
            )
            self._thread_pool[pcontroller.hash] = pcontroller

    def toggle_menu(self):
        self.menu_opened = not self.menu_opened
        if not self.menu_opened:
            self.left_menu_frame.setMaximumWidth(50)
        else:
            self.left_menu_frame.setMaximumWidth(180)

    def refresh_ports(self):
        self.ports.clear()
        for port in get_available_ports():
            self.ports.addItem(port.device)

    def set_main_user(self):
        if db_user:
            self.odoo_url.setText(db_user.url),
            self.odoo_user.setText(db_user.username),
            self.odoo_password.setText(db_user.api_key)
            self.odoo_db_name.setText(db_user.odoo_db_name)

    def save_user(self):
        if self.odoo_url.text() \
            and self.odoo_user.text() \
            and self.odoo_password.text() \
            and self.odoo_db_name.text():

            update_db_user(
                url=self.odoo_url.text(),
                username=self.odoo_user.text(),
                api_key=self.odoo_password.text(),
                odoo_db_name=self.odoo_db_name.text()
            )
        else:
            print('todos los campos son requeridos')

    def connect_custom_actions(self):
        self.connection_button.clicked.connect(self.refresh_ports)
        self.print_x.clicked.connect(self.print_x_report)
        self.exit_button.clicked.connect(self.exit_fiscal_printer)
        self.header_frame.mouseMoveEvent = self.move_window
        self.toggle_menu_button.clicked.connect(self.toggle_menu)
        self.minimize_button.clicked.connect(self.minimize_window)
        self.save_user_button.clicked.connect(self.save_user)
        self.main_button.clicked.connect(
            lambda: self.window_pages.setCurrentWidget(self.main_page)
        )
        self.connection_button.clicked.connect(
            lambda: self.window_pages.setCurrentWidget(self.config_page)
        )
        self.connect_button.clicked.connect(self.printer_action_setup)
        self.connect_button.clicked.connect(
            lambda: self.window_pages.setCurrentWidget(self.main_page)
        )

    def clear_output(self):
        self._outputText = []
        self.outputText.setPlainText('')

    def read_ports(self):
        self._ports = get_available_ports()
        if not self._ports:
            self.outputText.append('No hay puertos disponibles')
        else:
            devices = ', '.join([str(x.device) for x in self._ports])
            self.outputText.append(f'Se han detectado los siguientes puertos disponibles: {devices}')
            

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()

    def check_printer_status(self):
        if self.is_printer_connected:
            if not self._printer.is_busy:
                if self._thread_pool:
                    thread = self.get_thread()
                    if thread:
                        self._active_thread = thread.hash
                        thread.threadConnection()
                else:
                    pcontroller = QPrinterController(
                        bind_function = self._printer.get_s1,
                        lock = False,
                        parent = self
                    )
                    self._thread_pool[pcontroller.hash] = pcontroller

    def get_thread(self):
        available = list(filter(
            lambda x: x != self._active_thread,
            self._thread_pool.keys()
        ))
        if available:
            return self._thread_pool[available[0]]
        return ''

    def delete_finished_thread(self):
        del self._thread_pool[self._active_thread]

    def set_output_timer(self):
        self.qtimer = QTimer()
        self.qtimer.setInterval(100)
        self.qtimer.timeout.connect(self.update_all)
        self.qtimer.start()

        self.printer_status_timer = QTimer()
        self.printer_status_timer.setInterval(1000)
        self.printer_status_timer.timeout.connect(self.check_printer_status)
        self.printer_status_timer.start()

    def shuffle_lock_buttons(self):
        self._locked_buttons = not self._locked_buttons
        self.connection_button.setEnabled(self._locked_buttons)
        self.print_x.setEnabled(self._locked_buttons)
        self.print_z.setEnabled(self._locked_buttons)

    def append_to_output(self, text):
        self._outputText.append(text)

    def update_all(self):
        if self._outputText:
            text = self._outputText.pop(0)
            self.outputText.append(text)