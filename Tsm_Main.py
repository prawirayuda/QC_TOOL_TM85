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

class TaskRow(IntEnum):
    TEST1 = 0
    TEST_POWER_RAIL = auto()
    TEST3 = auto()
    TEST4 = auto()


class MainWindow(QMainWindow,QWidget):
    
    my_signal = pyqtSignal()
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("FSM")
        self.setFixedSize(500,200)
        self._controller = Controller(self)
        self.parent = parent
        
        self.container = QVBoxLayout()
        self.inner = QGridLayout()
        self.container.addLayout(self.inner)
        
        
        self.button1 = QPushButton("START")
        self.button1.clicked.connect(self.control_btn)
        self.label1 = QLabel("N/A")

        self.button2 = QPushButton("TEST POWER")
        self.label2 = QLabel("N/A")

        self.button3 = QPushButton("TEST SENSOR")
        # self.button3.clicked.connect(self.sensor_btn)
        self.label3 = QLabel("N/A")

        self.button4 = QPushButton("TEST TAMPER")
        self.label4 = QLabel("N/A")
        
        self.pass_button = QPushButton("PASS")
        self.fail_button = QPushButton("FAIL")
        
        self.label_instruction = QLabel("PRESS THE BUTTON START FOR TESTING PROCESS")
        self.label_instruction.setStyleSheet("border: 1px solid black;")
        self.label_instruction.setAlignment(Qt.AlignCenter)
        
        self.inner.addWidget(self.button1,TaskRow.TEST1,0,1,2)
        # self.inner.addWidget(self.label1,TaskRow.TEST1,1)
        self.inner.addWidget(self.button2,TaskRow.TEST_POWER_RAIL,0)
        self.inner.addWidget(self.label2,TaskRow.TEST_POWER_RAIL,1)
        self.inner.addWidget(self.button3,TaskRow.TEST3,0)
        self.inner.addWidget(self.label3,TaskRow.TEST3,1)
        self.inner.addWidget(self.button4,TaskRow.TEST4,0)
        self.inner.addWidget(self.label4,TaskRow.TEST4,1)
        self.inner.addWidget(self.label_instruction,8,0,1,2)
        self.inner.addWidget(self.pass_button,9,0)
        self.inner.addWidget(self.fail_button,9,1)
        
        widget = QWidget()
        widget.setLayout(self.container)
        self.setCentralWidget(widget) 
        
    def control_btn(self):
        self._controller.start_worker()
    
    def power_btn(self):
        pass
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())