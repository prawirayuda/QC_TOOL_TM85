from __future__ import annotations
from PyQt5.QtWidgets import *
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
from PyQt5.QtCore import QThreadPool, QTimer
from Tsm_Worker import Worker

       
class Controller:
    def __init__(self, parent):
        self._parent = parent
        self._threadpool = QThreadPool()
        
    def start_worker(self):
        self._worker = Worker(self)
        self._threadpool.start(self._worker)
    
        
    def update(self, update_str):
        self._parent.label_instruction.setText(update_str)
        if update_str =="PASS":
            self._parent.label_test_power.setStyleSheet("background-color: {}".format("#86b721"))
        elif update_str == "FAIL":
            self._parent.label_test_power.setStyleSheet("background-color: {}".format("#fe1818"))
        # elif update_str == "STANDBY MODE":
        #     self._parent.pass_button.setEnabled(False)
        #     self._parent.fail_button.setEnabled(False)

    def update_label(self, update_label):
        self._parent.value_test_power.setText(update_label)
        if update_label == "PASS":
            self._parent.value_test_sensor.setText("On Progress")
        elif update_label == "FAIL":
            self._parent.value_test_sensor.setText("NG")
    
    def handleNG(self):
        self.standby_mode()

    def standby_mode(self):
        self._parent.label_instruction.setText("MODE STANDBY")
        update_status_label_instruction = self._parent.label_instruction.text()
        if update_status_label_instruction =="MODE STANDBY":
        
            self._parent.value_test_power.setText("N/A")
            self._parent.value_test_sensor.setText("N/A")
            self._parent.value_test_tamper.setText("N/A")
            self._parent.value_test_modem_on.setText("N/A")
            self._parent.value_test_simcard.setText("N/A")
            self._parent.value_test_signal.setText("N/A")
            self._parent.pass_button.setStyleSheet('background: palette(window)')
            self._parent.fail_button.setStyleSheet('background: palette(window)')
            self._parent.button_start.setEnabled(True)
            
        
        

        
if __name__ == "__main__":
    pass