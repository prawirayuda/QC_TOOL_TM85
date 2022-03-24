from __future__ import annotations

from enum import IntEnum, auto
import time
from enum import IntEnum, auto
import sys
from PyQt5.QtWidgets import *
import time
import serial
from threading import *
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow, QWidget, 
    QWidget, 
    QGridLayout, 
    QVBoxLayout, 
    QHBoxLayout, 
    QGridLayout,
    QLabel,
    QComboBox,
    QProgressBar,
    QPlainTextEdit,
    QFrame,
    QPushButton)
from PyQt5.QtCore import pyqtSignal , Qt, pyqtSlot
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
from Tsm_Controller import Controller
from Tsm_Serial import SerialUtil

class TaskRow(IntEnum):
    # PORT_MODEM = 0
    # PORT_QC = auto()
    # BUTTON = 2
    LINE = 2
    TEST_POWER_RAIL = auto()
    TEST_SENSOR = auto()
    TEST_TAMPER = auto()
    MODEM_ON = auto()
    TEST_SIMCARD = auto()
    TEST_SIGNAL = auto()
    
class ComboBox(QComboBox):
    clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def show_pop_up(self):
        self.clicked.emit()
        return super().show_pop_up


class MainWindow(QMainWindow,QWidget):
    
    my_signal = pyqtSignal()
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("QC TOOLS")
        self.setFixedSize(600,400)
        self._controller = Controller(self)
        self.parent = parent
        
        self.container = QVBoxLayout()
        self.inner = QGridLayout()
        self.task_container = QGridLayout()
        self.label_instruction_container = QHBoxLayout()
        self.pass_fail_container = QHBoxLayout()
        self.container.addLayout(self.inner)
        self.container.addLayout(self.task_container)
        self.container.addLayout(self.label_instruction_container)
        self.container.addLayout(self.pass_fail_container)
        self.label_modem_port = QLabel("MODEM PORT     :")
        self.label_qctool_port = QLabel("QC TOOLS PORT :")
        self.port_modem = ComboBox()
        self.port_modem.clicked.connect(self.combo_box_modem_port)
        self.port_qc = ComboBox()
        self.port_qc.clicked.connect(self.combo_box_qc_tools_port)
        
        self.button_start = QPushButton("START")
        self.button_start.clicked.connect(self.button_start_control)

        configToTaskDevider = QFrame()
        configToTaskDevider.setFrameShadow(QFrame.Sunken)
        configToTaskDevider.setFrameShape(QFrame.HLine)   

        self.label_test_power = QLabel("TEST POWER")
        self.label_test_power.setAlignment(Qt.AlignCenter)
        self.value_test_power = QLabel("N/A")
        self.value_test_power.setAlignment(Qt.AlignCenter)

        self.label_test_sensor = QLabel("TEST SENSOR")
        self.label_test_sensor.setAlignment(Qt.AlignCenter)
        self.value_test_sensor = QLabel("N/A")
        self.value_test_sensor.setAlignment(Qt.AlignCenter)

        self.label_test_tamper = QLabel("TEST TAMPER")
        self.label_test_tamper.setAlignment(Qt.AlignCenter)
        self.value_test_tamper = QLabel("N/A")
        self.value_test_tamper.setAlignment(Qt.AlignCenter)
        
        self.label_test_modem_on = QLabel("MODEM ON")
        self.label_test_modem_on.setAlignment(Qt.AlignCenter)
        self.value_test_modem_on = QLabel("N/A")
        self.value_test_modem_on.setAlignment(Qt.AlignCenter)

        self.label_test_simcard = QLabel("TEST SIMCARD")
        self.label_test_simcard.setAlignment(Qt.AlignCenter)
        self.value_test_simcard = QLabel("N/A")
        self.value_test_simcard.setAlignment(Qt.AlignCenter)

        self.label_test_signal = QLabel("TEST SIGNAL")
        self.label_test_signal.setAlignment(Qt.AlignCenter)
        self.value_test_signal = QLabel("N/A")
        self.value_test_signal.setAlignment(Qt.AlignCenter)


        self.pass_button = QPushButton("PASS")
        self.fail_button = QPushButton("FAIL")
        
        self.label_instruction = QLabel("PRESS THE BUTTON START FOR TESTING PROCESS")
        self.label_instruction.setStyleSheet("border: 1px solid black;")
        self.label_instruction.setAlignment(Qt.AlignCenter)
        
        self.inner.addWidget(self.label_modem_port,0,0)
        self.inner.addWidget(self.label_qctool_port,1,0)
        self.inner.addWidget(self.port_modem, 0,1,1,2)
        self.inner.addWidget(self.port_qc, 1,1,1,2)
        self.inner.addWidget(self.button_start,0,3,2,1)
        
        self.inner.addWidget(configToTaskDevider,TaskRow.LINE,0,1,4)
        self.task_container.addWidget(self.label_test_power,TaskRow.TEST_POWER_RAIL,0)
        self.task_container.addWidget(self.value_test_power,TaskRow.TEST_POWER_RAIL,1)
        self.task_container.addWidget(self.label_test_sensor,TaskRow.TEST_SENSOR,0)
        self.task_container.addWidget(self.value_test_sensor,TaskRow.TEST_SENSOR,1)
        self.task_container.addWidget(self.label_test_tamper,TaskRow.TEST_TAMPER,0)
        self.task_container.addWidget(self.value_test_tamper,TaskRow.TEST_TAMPER,1)
        self.task_container.addWidget(self.label_test_modem_on,TaskRow.MODEM_ON,0)
        self.task_container.addWidget(self.value_test_modem_on,TaskRow.MODEM_ON,1)
        self.task_container.addWidget(self.label_test_simcard,TaskRow.TEST_SIMCARD,0)
        self.task_container.addWidget(self.value_test_simcard,TaskRow.TEST_SIMCARD,1)
        self.task_container.addWidget(self.label_test_signal,TaskRow.TEST_SIGNAL,0)
        self.task_container.addWidget(self.value_test_signal,TaskRow.TEST_SIGNAL,1)
        self.label_instruction_container.addWidget(self.label_instruction)
        self.pass_fail_container.addWidget(self.pass_button)
        self.pass_fail_container.addWidget(self.fail_button)
        
        widget = QWidget()
        widget.setLayout(self.container)
        self.setCentralWidget(widget) 
        
    def button_start_control(self):
        self._controller.start_worker()
    
    def combo_box_modem_port(self):
        available_ports = SerialUtil.get_serial_ports()      
        
        if self.port_modem.count():
            for index in range(0, self.port_modem.count()):
                self.port_modem.removeItem(index)
            for port in available_ports:
                item = port["port_name"]
                self.port_modem.addItem(item)

    def combo_box_qc_tools_port(self):
        available_ports = SerialUtil.get_serial_ports()      
        
        if self.port_qc.count():
            for index in range(0, self.port_qc.count()):
                self.port_qc.removeItem(index)
            for port in available_ports:
                item = port["port_name"]
                self.port_qc.addItem(item)

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())