from __future__ import annotations

from enum import IntEnum, auto
import time
from enum import IntEnum, auto
import sys
import os
from PyQt5.QtWidgets import *
import time
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
    QDialog, 
    QDialogButtonBox,
    QFrame,
    QPushButton)
from PyQt5.QtCore import pyqtSignal , Qt, pyqtSlot
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
from Tsm_Controller import Controller
from Tsm_Serial import SerialUtil
from PyQt5.QtGui import QColor, QFont, QIcon, QFontDatabase


class TaskRow(IntEnum):

    LINE = 2
    TEST_POWER_RAIL = auto()
    TEST_CRYSTAL = auto()
    TEST_SENSOR = auto()
    TEST_TAMPER = auto()
    # MODEM_ON = auto()
    TEST_SIMCARD = auto()
    TEST_SIGNAL = auto()
    
class ComboBox(QComboBox):
    clicked = pyqtSignal()
    
    def __init__(self,*args, **kwargs):
        super(ComboBox,self).__init__(*args, **kwargs)
        
    def showPopup(self)-> None:
        self.clicked.emit()
        return super().showPopup()
    
class TMDialog(QDialog):
    def __init__(self, name, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        
        self.setWindowTitle(name)
        self.setWindowFlags(Qt.WindowTitleHint |  Qt.WindowMinimizeButtonHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        self.dialogButtons =QDialogButtonBox(QDialogButtonBox.Ok)
        self.dialogButtons.setCenterButtons(True)
        self.dialogButtons.accepted.connect(self.accept)

        self._standarizedFont = QFont("Roboto", 11)

        if "informative_text" in kwargs.keys():
            self.lblInformation = QLabel()
            self.lblInformation.setText(kwargs['informative_text'])
            self.lblInformation.setFont(self._standarizedFont)
            self.lblInformation.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.lblInformation.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(self.lblInformation)

        if "additional_text" in kwargs.keys():
            self.lblAdditional = QLabel()
            self.lblAdditional.setText(kwargs['additional_text'])
            self.lblAdditional.setFont(self._standarizedFont)
            self.lblAdditional.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.lblAdditional.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(self.lblAdditional)

        if "detail_text" in kwargs.keys():
            self.lbldetail = QLabel()
            self.lbldetail.setText(kwargs['detail_text'])
            self.lbldetail.setFont(self._standarizedFont)
            self.lbldetail.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.lbldetail.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(self.lbldetail)

        self._layout.addWidget(self.dialogButtons)
    

class MainWindow(QMainWindow,QWidget):
    
    my_signal = pyqtSignal()
    
    def __init__(self, name = None, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("QC TOOLS")
        self.setStyleSheet(stylesheet(self))
        self.setFixedSize(900,600)
        self._controller = Controller(self)
        self.parent = parent
        self.name = name
        
        self.container = QVBoxLayout()
        self.inner = QGridLayout()
        self.task_container = QGridLayout()
        self.task_container.setSpacing(40)
        self.label_instruction_container = QHBoxLayout()
        self.label_error_container = QHBoxLayout()
        self.pass_fail_container = QHBoxLayout()
        self.container.addLayout(self.inner)
        self.container.addLayout(self.task_container)
        self.container.addLayout(self.label_instruction_container)
        self.container.addLayout(self.label_error_container)
        self.container.addLayout(self.pass_fail_container)
        #setting font 
        CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        # print(CURRENT_DIRECTORY)
        
        font_path = os.path.join(CURRENT_DIRECTORY, "Roboto", "Roboto-Bold.ttf")
        _id =QFontDatabase.addApplicationFont(font_path)
        font = QFont('Roboto')   
        self.label_qctool_port = QLabel("QC TOOLS PORT :")
        self.label_qctool_port.setFont(font)
        self.label_qctool_port.setStyleSheet("""
                                             font-size : 16px;
                                             """)

        self.port_qc = ComboBox()
        self.port_qc.setStyleSheet("""
                                    background-color : #fff;
                                       
                                   """)
        self.port_qc.addItem("SELECT QC PORT")
        self.port_qc.clicked.connect(self.populate_combo_box_qc_tools_port)
        
        self.button_start = QPushButton("START")
        self.button_start.setEnabled(False)
        self.button_start.clicked.connect(self.button_start_control)

        configToTaskDevider = QFrame()
        configToTaskDevider.setFrameShadow(QFrame.Sunken)
        configToTaskDevider.setFrameShape(QFrame.HLine)   

        self.label_test_power = QLabel("TEST POWER")
        self.label_test_power.setFont(font)
        self.label_test_power.setAlignment(Qt.AlignCenter)
        self.value_test_power = QLabel("N/A")
        self.value_test_power.setAlignment(Qt.AlignCenter)
        
        self.label_test_crystal = QLabel("TEST CRYSTAL")
        self.label_test_crystal.setFont(font)
        self.label_test_crystal.setAlignment(Qt.AlignCenter)
        self.value_test_crystal = QLabel("N/A")
        self.value_test_crystal.setAlignment(Qt.AlignCenter)
        

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
        self.pass_button.setEnabled(False)
        self.pass_button.setStyleSheet("""
                                       QPushButton{
                                           background-color:#D9E3DA;
                                           border: 1px solid black;
                                       }
                                       """)
        
        self.fail_button = QPushButton("FAIL")
        self.fail_button.setEnabled(False)
        self.fail_button.setFont(QFont('Times',12))
        self.fail_button.setStyleSheet("""
                                       QPushButton{
                                           background-color:#D9E3DA;
                                           border: 1px solid black;
                                       }
                                       """)        
        
        self.label_instruction = QLabel("SELECT THE PORT FIRST")
        self.label_instruction.setStyleSheet("""border: 1px solid black;
                                                border-radius:5px;
                                                background-color:#fff;
                                                font-size: 20px;""")
        self.label_instruction.setAlignment(Qt.AlignCenter)
        
        self.label_error = QLabel("ERROR MESSAGE : N/A")
        self.label_error.setStyleSheet("""border: 1px solid black;
                                            border-radius:5px;
                                            background-color:#fff;
                                            font-size: 20px;""")
        self.label_error.setAlignment(Qt.AlignCenter)
        self.inner.addWidget(self.label_qctool_port,0,0,2,0)
        self.inner.addWidget(self.port_qc, 0,1,2,2)
        self.inner.addWidget(self.button_start,0,3,2,1)
        
        self.inner.addWidget(configToTaskDevider,TaskRow.LINE,0,1,4)
        self.task_container.addWidget(self.label_test_power,TaskRow.TEST_POWER_RAIL,0)
        self.task_container.addWidget(self.value_test_power,TaskRow.TEST_POWER_RAIL,1)
        self.task_container.addWidget(self.label_test_crystal,TaskRow.TEST_CRYSTAL,0)
        self.task_container.addWidget(self.value_test_crystal,TaskRow.TEST_CRYSTAL,1)
        self.task_container.addWidget(self.label_test_sensor,TaskRow.TEST_SENSOR,0)
        self.task_container.addWidget(self.value_test_sensor,TaskRow.TEST_SENSOR,1)
        self.task_container.addWidget(self.label_test_tamper,TaskRow.TEST_TAMPER,0)
        self.task_container.addWidget(self.value_test_tamper,TaskRow.TEST_TAMPER,1)
        self.task_container.addWidget(self.label_test_simcard,TaskRow.TEST_SIMCARD,0)
        self.task_container.addWidget(self.value_test_simcard,TaskRow.TEST_SIMCARD,1)
        self.task_container.addWidget(self.label_test_signal,TaskRow.TEST_SIGNAL,0)
        self.task_container.addWidget(self.value_test_signal,TaskRow.TEST_SIGNAL,1)
        self.label_instruction_container.addWidget(self.label_instruction)
        self.label_error_container.addWidget(self.label_error)
        self.pass_fail_container.addWidget(self.pass_button)
        self.pass_fail_container.addWidget(self.fail_button)
        
        widget = QWidget()
        widget.setLayout(self.container)
        self.setCentralWidget(widget) 
        
    def button_start_control(self):
        if self.button_start.text() == "START":
            self.button_start.setEnabled(False)
            self._controller.start_worker()
            
            # self.dialog = TMDialog(self.name, informative_text="Error Message")
            # self.dialog.exec()
        # elif self.button_start.text() == "SET": 
        #     self.button_start.setText("START")                                      
    
    def populate_combo_box_modem_port(self):
        # print("CLIKC")
        available_ports = SerialUtil.get_serial_ports()      
        
        if self.port_modem.count():
            for index in range(0, self.port_modem.count()):
                self.port_modem.removeItem(index)
        for port in available_ports:
            # item = port["port_name"]
            self.port_modem.addItem(port["port_name"], port["port"])

    def populate_combo_box_qc_tools_port(self):
        available_ports = SerialUtil.get_serial_ports()      
        
        if self.port_qc.count():
            for index in range(0, self.port_qc.count()):
                self.port_qc.removeItem(index)
        for port in available_ports:
            item = port["port_name"]
            self.port_qc.addItem(item)
        self.button_start.setEnabled(True)
      
def stylesheet(self):
    return """
    QMainWindow{
                background-color: #D9E3DA;        
    }

    QLabel{
            font: bold 14px Roboto;
            color:#0B002A;
    }  


    QComboBox{
        background-color:#fff;
        padding:10px;
        font-family: Poppins;
        font-size: 10pt;
    }
    QPushButton#pass_button {
        color: blue;
        font-weight: bold;
    }

    QPushButton{
        background-color:#0078D7;
        color : #050F03;
        border-radius: 8px;
        padding:8px;
        font: bold 24px Open Sans;
    }
    
    QPushButton::hover{
        background-color:#15a2d7;     
    }

"""        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())