from __future__ import annotations
from threading import *
from PyQt5.QtCore import (QRunnable,pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)

import time
from abc import ABC, abstractmethod


class Context:

    _state = None
    def __init__(self, state: State) -> None:
        self.setState(state)
        # self._parent = parent

    def setState(self, state: State):

        print(f"Context: Transitioning to {type(state).__name__}")
        self._state = state
        self._state.context = self
    
#the method for executing the state functionality, These depends on the current state of the object..

    def pass_function(self):
        self._state.pass_function()
        
    def fail_function(self):
        self._state.fail_function()
        

class State(ABC):
    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def pass_function(self) -> None:
        pass
    
    @abstractmethod
    def fail_function(self) -> None:
        pass
    
           
class QC_STATE_STANDBY(State):
    def __init__(self, controller):
        self._controller = controller

    def pass_function(self) -> None:
        self._controller._parent.update("STANDBY MODE")
        print("STATE : QC_STATE_STANDBY.")
        # print("QC_STATE_STANDBY now changes the state of the context.")

    def fail_function(self):
        print("if fail stay in standby mode")
        # self.context.setState(QC_STATE_STANDBY(self))

    
class QC_STATE_TEST_POWER_RAIL(State):  
    def __init__(self, controller):
        self._controller = controller
    
    
    def pass_function(self) -> None:
        print("STATE : QC_STATE_TEST_POWER_RAIL.")
        self._controller._parent.update("FAIL")
        # ser = serial.Serial("COM20", 9600)
        # ser.write(b"{P?}")
        # data = ser.readline()
        # # print(data)
        # input1 = data[1:5]
        # input2 = input1[0:2]
        # input3 = input1[2:]
        # integer1 = int.from_bytes(input2,"little")
        # integer2 = int.from_bytes(input3,"little")
        # th1 = 1.6
        # th2 = 1.1
        # while True:
        #     val1 = (integer1/1023) * 1.8
        #     val2 = (integer2/1023) * 1.2
        #     # print(val1)
        #     # print(val2)
        #     if val1 > th1 and val2 > th2: #test pass value
        #     # if val1 < th1 and val2 < th2: #test fail value
        #         print("PASS")
        #         self._controller._parent.update("PASS")
        #         break
        #     else:
        #         print("FAIL")
        #         self._controller._parent.update("FAIL")
        #         return self.fail_function()
                

        print("QC_STATE_TEST_POWER_RAIL wants to change the state of the context.")
        time.sleep(3)
        self.context.setState(QC_STATE_SENSOR(Worker))     
        
    def fail_function(self) -> None:
        print("if fail back to standby mode")
        self.context.setState(QC_STATE_STANDBY(QC_STATE_STANDBY))
        print("STANDBY MODE")
        self._controller._parent.handleNG()
        # close_port = serial.Serial()
        # close_port.close()
        # print(close_port)


class QC_STATE_SENSOR(State):
    def __init__(self, controller):
        self._controller = controller
        
    def pass_function(self) -> None:
        # self._controller._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_TEST_SENSOR.")
        # ser = serial.Serial("COM20", 9600)
        # ser.write(b"{S?}")
        # data = ser.readline()
        # print(data)
        # input1 = data[1:5]
        # input2 = input1[0:2]
        # input3 = input1[2:]
        # integer1 = int.from_bytes(input2,"little")
        # integer2 = int.from_bytes(input3,"little")
        # print(integer1)
        # print(integer2)  
        # th1 = 1.6
        # th2 = 1.1
        # while True:
        #     val1 = (integer1/1023) * 1.8
        #     val2 = (integer2/1023) * 1.2
        #     # print(val1)
        #     # print(val2)
        #     # if val1 > th1 and val2 > th2: #test pass value
        #     if val1 < th1 and val2 < th2: #test fail value
        #         print("PASS")
        #         self._controller._parent.update("PASS")
        #         break
        #     else:
        #         print("FAIL")
        #         self._controller._parent.update("FAIL")
        #         time.sleep(2)
        #         return self.fail_function()      
        
        print("QC_STATE_TEST_SENSOR wants to change to next state.")

    def fail_function(self) -> None:
        print("if fail back to standby mode")
        self.context.setState(QC_STATE_STANDBY(QC_STATE_STANDBY))
        print("STANDBY MODE")
        self._controller._parent.handleNG()
        

class Worker(QRunnable):
    my_signal = pyqtSignal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        


    @pyqtSlot()
    def run(self):
        
        self._parent._parent.button1.setEnabled(False)
        # self._parent._parent.label3.setText("PASS")
        standby = Context(QC_STATE_STANDBY(self))
        test_power_rail = Context(QC_STATE_TEST_POWER_RAIL(self))
        test_sensor = Context(QC_STATE_SENSOR(self))
        standby.pass_function()
        test_power_rail.pass_function()
        data_update = self._parent._parent.label_instruction.text()
        print(data_update)
        if data_update == "PASS":
            self._parent._parent.label2.setText("PASS")
            self._parent._parent.label3.setText("ON GOING")
            test_sensor.pass_function()
        elif data_update == "FAIL":
            self._parent._parent.label2.setText("FAIL")
            standby.pass_function()
            self._parent.handleNG()

if __name__ == "__main__":
    pass
