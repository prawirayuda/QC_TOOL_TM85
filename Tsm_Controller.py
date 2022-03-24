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
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
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
            self._parent.pass_button.setStyleSheet("background-color: {}".format("#86b721"))
        elif update_str == "FAIL":
            self._parent.fail_button.setStyleSheet("background-color: {}".format("#fe1818"))
        elif update_str == "STANDBY MODE":
            self._parent.pass_button.setEnabled(False)
            self._parent.fail_button.setEnabled(False)

    def update_label(self, update_label):
        self._parent.label2.setText(update_label)
        if update_label == "PASS":
            self._parent.label3.setText("On Progress")
        elif update_label == "FAIL":
            self._parent.label3.setText("NG")
    
    def handleNG(self):
        self.ui_standby()

    def ui_standby(self):
        # self._parent.label_instruction.setText("MODE STANDBY")
        self._parent.button1.setEnabled(True)
        self._parent.pass_button.setStyleSheet('background: palette(window)')
        self._parent.fail_button.setStyleSheet('background: palette(window)')
        
if __name__ == "__main__":
    pass