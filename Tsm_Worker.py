from __future__ import annotations
from itertools import count
from ntpath import join
from threading import *
from PyQt5.QtCore import (QRunnable,pyqtSignal, pyqtSlot, QTimer)
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)

import time
from abc import ABC, abstractmethod
import serial
import serial.tools.list_ports
from Tsm_Config import QC_PORT_SERIAL_BAUDRATE


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
    def __init__(self, worker):
        self._worker = worker

    def pass_function(self) -> None:
        self._worker._parent.update("STANDBY MODE")
        print("STATE : QC_STATE_STANDBY.")
        # print("QC_STATE_STANDBY now changes the state of the context.")

    def fail_function(self):
        print("if fail back to STANDBY MODE")
        # self.context.setState(QC_STATE_STANDBY(self))

    
class QC_STATE_TEST_POWER_RAIL(State):  
    def __init__(self, worker):
        self._worker = worker
    
    
    def pass_function(self) -> None:
        print("STATE : QC_STATE_TEST_POWER_RAIL.")
        self._worker._parent._parent.label_instruction.setText("TESTING POWER RAIL")
        # time.sleep(2)
        # self._worker._parent._parent.label_instruction.setText("PASS")
        # self._worker._parent.update("PASS")

        #  7B 90 01 F4 01 7D 0A
        self.serialInst = serial.Serial()    
        # val = input("SELECT PORT : ")   
        # cb_port_qc = qc_ports.currentData.itemData(self._worker._parent._parent.port_qc.currentIndex())
        qc_ports:QComboBox = self._worker._parent._parent.port_qc   
        port_text = qc_ports.itemText(qc_ports.currentIndex())
        self.selected_port = port_text[port_text.index("(")+1 : port_text.index(")")]

        self.serialInst.port = self.selected_port
        self.serialInst.baudrate = QC_PORT_SERIAL_BAUDRATE
        self.serialInst.bytesize = 8
        self.serialInst.timeout = 10
        self.serialInst.stopbits= serial.STOPBITS_ONE
        self.serialInst.open()
        list_buffer = []
        self.serialInst.write(b"{P?}")
         
        timeout = time.time() + 5 #in second 
        
        
        while True:
            flag = 0
            if flag == 1 or time.time() > timeout:
                print("there's no data recieved")
                self._worker._parent._parent.button_start.setEnabled(True)
                # self._worker._parent.handleNG()
                self.serialInst.close()
                return 
            
            if self.serialInst.in_waiting:
                data1 = self.serialInst.read()
                list_buffer.append(data1.decode('utf-8'))
                # print(list_buffer)
                if list_buffer[-1] == "}":
                    val1 = list_buffer[1:]
                    val2 = val1[0:-1]
                    print(val2) 
                    realVal1 = val2[val2.index(",")+1:]
                    realVal2 = val2[:val2.index(",")]
                    
                    value_str1 = ''.join(realVal1)
                    value_str2 = ''.join(realVal2)
                    value1 = int(value_str1)
                    value2 = int(value_str2)
                    print(value1)
                    print(value2)
                    
                    th1 = 1.6
                    th2 = 1.1
                    final_val1 = (value1/1023) * 1.8
                    final_val2 = (value2/1023) * 1.2
                    # self._worker._parent._parent.value_test_power.setText(f"Value1 : {str(final_val1)}, Value2 : {str(final_val2)}")  
                    self._worker._parent._parent.value_test_power.setText(f"Value1 : {final_val1}, Value2 : {final_val2}")  
                    # tes sample 
                    # if final_val1 > th1 and final_val2 > th2: #test fail value
                    if final_val1 < th1 and final_val2 < th2: #test pass value
                        print("PASS")
                        self._worker._parent.update("PASS")
                        break
                    else:
                        print("FAIL")
                        self._worker._parent.update("FAIL")
                        # return self.fail_function()
                                
                #     self._worker._parent.update("PASS")

        
        print("NEXT step")
            # break

        print("QC_STATE_TEST_POWER_RAIL wants to next State")
        time.sleep(2)
        self.context.setState(QC_STATE_SENSOR(Worker))     
        
    def fail_function(self) -> None:
        pass

class QC_STATE_SENSOR(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        # self._worker._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_TEST_SENSOR.")
        self._worker._parent._parent.label_instruction.setText("TESTING SENSOR")
        # time.sleep(2)
        
        self._worker._parent._parent.label_instruction.setText("PASS")
        time.sleep(2)
        print("QC_STATE_TEST_SENSOR wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_TAMPER(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        # self._worker._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_TEST_TAMPER.")
        self._worker._parent._parent.label_instruction.setText("TESTING TAMPER & PRESS THE BUTTON IN 3 SECONDS")
        time.sleep(2)
        # self._worker._parent._parent.label_instruction.setText("FAIL")

        
        print("QC_STATE_TEST_TAMPER wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
class QC_STATE_MODEM_ON(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        # self._worker._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_MODEM_ON.") 
        self._worker._parent._parent.label_instruction.setText("MODEM ON")
        time.sleep(2)
        self._worker._parent._parent.label_instruction.setText("PASS")

        print("QC_STATE_MODEM ON wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIMCARD(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        # self._worker._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_SIMCARD.") 
        self._worker._parent._parent.label_instruction.setText("TESTING SIMCARD")
        time.sleep(2)
        self._worker._parent._parent.label_instruction.setText("PASS")

        print("QC_STATE_SIMCARD wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIGNAL(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        # self._worker._parent._parent.pass_button.setStyleSheet("background-color: {}".format("#fff"))
        print("STATE : QC_STATE_SIGNAL.") 
        self._worker._parent._parent.label_instruction.setText("TESTING SIGNAL")
        time.sleep(2)
        self._worker._parent._parent.label_instruction.setText("PASS")

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

        
        if update_status_test_power == "PASS":
            self._parent._parent.value_test_sensor.setText("ON GOING")
            test_sensor.pass_function()
            
        #     update_status_test_sensor = self._parent._parent.label_instruction.text()
        #     if update_status_test_sensor == "PASS":
        #         test_tamper.pass_function()
        #         update_status_test_tamper = self._parent._parent.label_instruction.text()
        #         print(update_status_test_tamper)
        #         if update_status_test_tamper == "PASS":
        #             test_modem_on.pass_function()
        #             update_status_test_modem_on = self._parent._parent.label_instruction.text()
        #             if update_status_test_modem_on == "PASS":
        #                 test_simcard.pass_function()
        #                 update_status_test_simcard = self._parent._parent.label_instruction.text()
        #                 if update_status_test_simcard == "PASS":
        #                     test_signal.pass_function()
        #                     update_status_test_signal = self._parent._parent.label_instruction.text()
        #                     if update_status_test_signal == "PASS":       
        #                         self._parent._parent.pass_button.setStyleSheet("background-color:#4DAF50;")

        #                     elif update_status_test_signal =="FAIL":
        #                         self._parent.handleNG()
        #                 elif update_status_test_simcard =="FAIL":
        #                     self._parent.handleNG()                            
        #             elif update_status_test_modem_on =="FAIL":
        #                 self._parent.handleNG()
        #         elif update_status_test_tamper == "FAIL":
        #             self._parent.handleNG()
        #     elif update_status_test_sensor == "FAIL":
        #         self._parent.handleNG()
        elif update_status_test_power == "FAIL":
            self._parent._parent.value_test_power.setText("FAIL")
            standby.pass_function()
            self._parent.handleNG()
        # test_tamper.pass_function()
        

if __name__ == "__main__":
    pass
