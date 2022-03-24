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
        print("if fail back to STANDBY MODE")
        # self.context.setState(QC_STATE_STANDBY(self))

    
class QC_STATE_TEST_POWER_RAIL(State):  
    def __init__(self, controller):
        self._controller = controller
    
    
    def pass_function(self) -> None:
        print("STATE : QC_STATE_TEST_POWER_RAIL.")
        self._controller._parent._parent.label_instruction.setText("TESTING POWER RAIL")
        time.sleep(2)
        self._controller._parent._parent.label_instruction.setText("PASS")
        # self._controller._parent.update("PASS")
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
        # print("if fail back to standby mode")
        # self.context.setState(QC_STATE_STANDBY(QC_STATE_STANDBY))
        # print("STANDBY MODE")
        # self._controller._parent.handleNG()
        pass
        # close_port = serial.Serial()
        # close_port.close()
        # print(close_port)


class QC_STATE_SENSOR(State):
    def __init__(self, controller):
        self._controller = controller
        
    def pass_function(self) -> None:
        # self._controller._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_TEST_SENSOR.")
        self._controller._parent._parent.label_instruction.setText("TESTING SENSOR")
        time.sleep(2)
        self._controller._parent._parent.label_instruction.setText("PASS")
        time.sleep(2)
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
        # print("if fail back to standby mode")
        # self.context.setState(QC_STATE_STANDBY(QC_STATE_STANDBY))
        # print("STANDBY MODE")
        # self._controller._parent.handleNG()
        pass
        
        
class QC_STATE_TAMPER(State):
    def __init__(self, controller):
        self._controller = controller
        
    def pass_function(self) -> None:
        # self._controller._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_TEST_TAMPER.")
        self._controller._parent._parent.label_instruction.setText("TESTING TAMPER & PRESS THE BUTTON IN 3 SECONDS")
        time.sleep(2)
        self._controller._parent._parent.label_instruction.setText("PASS")

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
        
        print("QC_STATE_TEST_TAMPER wants to change to next state.")

    def fail_function(self) -> None:
        # print("if fail back to standby mode")
        # self.context.setState(QC_STATE_STANDBY(QC_STATE_STANDBY))
        # print("STANDBY MODE")
        # self._controller._parent.handleNG()
        pass
        
class QC_STATE_MODEM_ON(State):
    def __init__(self, controller):
        self._controller = controller
        
    def pass_function(self) -> None:
        # self._controller._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_MODEM_ON.") 
        self._controller._parent._parent.label_instruction.setText("MODEM ON")
        time.sleep(2)
        self._controller._parent._parent.label_instruction.setText("PASS")

        print("QC_STATE_MODEM ON wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIMCARD(State):
    def __init__(self, controller):
        self._controller = controller
        
    def pass_function(self) -> None:
        # self._controller._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_SIMCARD.") 
        self._controller._parent._parent.label_instruction.setText("TESTING SIMCARD")
        time.sleep(2)
        self._controller._parent._parent.label_instruction.setText("PASS")

        print("QC_STATE_SIMCARD wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIGNAL(State):
    def __init__(self, controller):
        self._controller = controller
        
    def pass_function(self) -> None:
        # self._controller._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_SIGNAL.") 
        self._controller._parent._parent.label_instruction.setText("TESTING SIGNAL")
        time.sleep(2)
        self._controller._parent._parent.label_instruction.setText("PASS")

        print("QC_STATE_SIGNAL wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
        
                
        

class Worker(QRunnable):
    my_signal = pyqtSignal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        


    @pyqtSlot()
    def run(self):
        
        self._parent._parent.button_start.setEnabled(False)
        # self._parent._parent.value_test_sensor.setText("PASS")
        standby = Context(QC_STATE_STANDBY(self))
        test_power_rail = Context(QC_STATE_TEST_POWER_RAIL(self))
        test_sensor = Context(QC_STATE_SENSOR(self))
        test_tamper = Context(QC_STATE_TAMPER(self))
        test_modem_on = Context(QC_STATE_MODEM_ON(self))
        test_simcard = Context(QC_STATE_SIMCARD(self))
        test_signal = Context(QC_STATE_SIGNAL(self))
        
        standby.pass_function()
        test_power_rail.pass_function()
        update_status_test_power = self._parent._parent.label_instruction.text()
        print(update_status_test_power)
        
        if update_status_test_power == "PASS":
            self._parent._parent.value_test_power.setText("PASS")
            self._parent._parent.value_test_sensor.setText("ON GOING")
            test_sensor.pass_function()
            
            update_status_test_sensor = self._parent._parent.label_instruction.text()
            if update_status_test_sensor == "PASS":
                test_tamper.pass_function()
                
                update_status_test_tamper = self._parent._parent.label_instruction.text()
                if update_status_test_tamper == "PASS":
                    test_modem_on.pass_function()
                    
                    update_status_test_modem_on = self._parent._parent.label_instruction.text()
                    if update_status_test_modem_on == "PASS":
                        test_simcard.pass_function()
                        
                        update_status_test_simcard = self._parent._parent.label_instruction.text()
                        if update_status_test_simcard == "PASS":
                            test_simcard.pass_function()
                            
                            update_status_test_signal = self._parent._parent.label_instruction.text()
                            if update_status_test_signal == "PASS":
                                
                                self._parent._parent.pass_button.setStyleSheet("background-color:#4DAF50;")
        elif update_status_test_power == "FAIL":
            self._parent._parent.value_test_power.setText("FAIL")
            standby.pass_function()
            self._parent.handleNG()
        # test_tamper.pass_function()
        

if __name__ == "__main__":
    pass
