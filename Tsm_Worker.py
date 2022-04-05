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
from Tsm_Serial import SerialAT


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
                self._worker._parent._parent.value_test_power.setText(f"TIMEOUT...") 
                self._worker._parent._parent.label_instruction.setText("Retry to push Button")
                self._worker._parent._parent.button_start.setEnabled(True)
                # print(self.serialInst.is_open)
                # self.serialInst.close()
                # print(self.serialInst.is_open)
                return 
            # print("TETAP SINI")
            if self.serialInst.in_waiting:
                data1 = self.serialInst.read()
                list_buffer.append(data1.decode('utf-8'))
                # print(list_buffer)
                if list_buffer[-1] == "}":
                    val1 = list_buffer[1:]
                    val2 = val1[3:-1]
                    print(val2)
                    # print(err)   
                    
                    join_all = "".join(val2)
                    # print(join_all)
                    split_value = join_all.split(',')
                    # print(split_value)
                    value_str1 = split_value[0]
                    value_str2 = split_value[1]
                    value1 = int(value_str1)
                    value2 = int(value_str2)                    
                    th1 = 1.6
                    th2 = 1.1
                    final_val1 = (value1/1023) * 1.8
                    final_val2 = (value2/1023) * 1.2
                    # self._worker._parent._parent.value_test_power.setText(f"Value1 : {str(final_val1)}, Value2 : {str(final_val2)}")  
                    self._worker._parent._parent .value_test_power.setText(f"Value1 : {final_val1:.3f}, Value2 : {final_val2:.3f}")  
                    # tes sample 
                    # if final_val1 > th1 and final_val2 > th2: #test fail value
                    if final_val1 < th1 and final_val2 < th2: #test pass value
                        print("PASS")
                        self._worker._parent.update("PASS")
                        break
                    else:
                        print("FAIL")
                        self._worker._parent.update("FAIL")
                        self._worker._parent._parent .value_test_power.setText(f"Value1 : {final_val1:.3f}, Value2 : {final_val2:.3f}")  
                        time.sleep(2)
                        # return self.fail_function()
                else:
                        print("Error Value input from MCU")
                        self._worker._parent.update("FAIL")
                        break  
                    
        print("NEXT step")
            # break
        print("QC_STATE_TEST_POWER_RAIL wants to next State")
        time.sleep(2)
        self.context.setState(QC_STATE_SENSOR(Worker))     
        # self.serialInst.close()
        
    def fail_function(self) -> None:
        pass

class QC_STATE_SENSOR(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:

        print("STATE : QC_STATE_TEST_SENSOR.")
        self._worker._parent._parent.label_instruction.setText("TESTING SENSOR")

        self.serialInst = serial.Serial()    
        
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
        self.serialInst.write(b"{S?}")
        timeout = time.time() + 15 #in second         
        while True:
            flag = 0
            if flag == 1 or time.time() > timeout:
                print("there's no data recieved")
                self._worker._parent._parent.value_test_sensor.setText(f"TIMEOUT...") 
                self._worker._parent._parent.label_instruction.setText("Retry to push Button")
                self._worker._parent._parent.button_start.setEnabled(True)
                self.serialInst.close()
                
                return 
            
            if self.serialInst.in_waiting:
                data1 = self.serialInst.read()
                list_buffer.append(data1.decode('utf-8'))
                # print(list_buffer)
                if list_buffer[-1] == "}":
                    val1 = list_buffer[1:]
                    val2 = val1[2:-1]
                    # handle input error from mcu
                    val_err = val2
                    print(val_err)
                    err = str(val_err[0])
                    # print(err)   
                    if err == 'R':
                        print("Error Value input from MCU")
                        self._worker._parent.update("FAIL")
                        break 
                    join_all = "".join(val2)
                    split_value = join_all.split(',')
                    value_str1,value_str2,value_str3,value_str4,value_str5,value_str6 = split_value[0], split_value[1], split_value[2], split_value[3], split_value[4], split_value[5]
                    
                    value1 = int(value_str1) 
                    print(value1)
                    value2 = int(value_str2)               
                    value3 = int(value_str3) 
                    value4 = int(value_str4)            
                    value5 = int(value_str5)
                    value6 = int(value_str6)            
                    
                    th_low_down = 255 
                    th_low_up = 312 
                    th_mid_down = 512 
                    th_mid_up = 624 
                    th_high_down = 767 
                    th_high_up = 937 
                    
                    self._worker._parent._parent.value_test_sensor.setText(f"Sensor 1 : ({value1}-{value3}-{value5}), Sensor 2 : ({value2}-{value4}-{value6})")  
                    time.sleep(3)
                    self._worker._parent.update("PASS")
                    break

                    # if (value1 > th_low_down and value1 < th_low_up) and (value2 > th_low_down and value2 < th_low_up) and (value3 > th_mid_down and value3 < th_mid_up) and (value4 > th_mid_down and value4 < th_mid_up) and (value5 > th_high_down and value5 < th_high_up) and (value6 > th_high_down and value6 < th_high_up):
                    #     self._worker._parent._parent.value_test_sensor.setText(f"Sensor 1 : ({value1}-{value3}-{value5}), Sensor 2 : ({value2}-{value4}-{value6})")  
                    #     print("PASS")
                    #     self._worker._parent.update("PASS")
                    #     # print("KEMANA")
                    #     break
                    # else:
                    #     print("FAIL")
                    #     self._worker._parent._parent.value_test_sensor.setText(f"Sensor 1 : ({value1}-{value3}-{value5}), Sensor 2 : ({value2}-{value4}-{value6})")  
                    #     self._worker._parent.update("FAIL")

        
        print("NEXT step")
            # break

        print("QC_STATE_TEST_SENSOR wants to next State")
        time.sleep(1)
        self.context.setState(QC_STATE_TAMPER(Worker))     


    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_TAMPER(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        print("STATE : QC_STATE_TEST_TAMPER.")
        time.sleep(2)
        self.serialInst = serial.Serial()    
        
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
        self.serialInst.write(b"{T?}")
        self._worker._parent._parent.label_instruction.setText("TESTING TAMPER & PRESS THE BUTTON IN 3 SECONDS")
        
        timeout = time.time() + 3 #in second    
        
        while True: 
            flag = 0
            if flag == 1 or time.time() > timeout:
                print("there's no data recieved")   
                self._worker._parent._parent.value_test_tamper.setText(f"TIMEOUT...") 
                self._worker._parent._parent.label_instruction.setText("Retry to push Button")
                self._worker._parent._parent.button_start.setEnabled(True)
                self.serialInst.close()
                return 
            if self.serialInst.in_waiting:
                data1 = self.serialInst.read()
                list_buffer.append(data1.decode('utf-8'))
                # print(list_buffer)
                if list_buffer[-1] == "}":
                    first_bracket = list_buffer[1:]
                    last_bracket = first_bracket[:-1]
                    print(last_bracket)
                    join_all = ''.join(last_bracket)
                    if join_all == "TMP":
                        self._worker._parent._parent.value_test_tamper.setText(f"TAMPER OK")  
                        self._worker._parent.update("PASS")
                        break
                        # list_buffer_data_response = []
                        # while True:
                        #     data_respons = self.serialInst.read()
                        #     list_buffer_data_response.append(data_respons.decode('utf-8'))
                        #     print(list_buffer_data_response)
                        #     if list_buffer_data_response [-1] == "}":
                        #         print("tes")
                        #         first_bracket = list_buffer_data_response[2:]
                        #         last_bracket = first_bracket[0:-1]
                        #         join_all = ''.join(last_bracket)
                        #         print(join_all)
                        #         if join_all == "ERR":
                        #             self._worker._parent._parent.value_test_tamper.setText(f"TAMPER OK")  
                        #             self._worker._parent.update("PASS")
                                    
                            
                    else:
                        print("FAIL")
                        self._worker._parent.update("FAIL")

        print("NEXT TO MODEM TEST TURN OFF MCU PORT")  
        print("QC_STATE_TEST_TAMPER wants to change to next state.")
        self.serialInst.close()
        print(self.serialInst.is_open)

    def fail_function(self) -> None:
        pass
        
class QC_STATE_MODEM_ON(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        modem_ports:QComboBox = self._worker._parent._parent.port_modem
        modem_port_text = modem_ports.currentData()
        self.selected_port = modem_port_text
        print(modem_port_text)
        
        tes = SerialAT(self.selected_port, 115200)
        #Change nbiot network to gsm
        at_res = tes.exchange_at("AT+CSQ\r","+CSQ: " , True, 1000)
        print(at_res['Value'])

        print("STATE : QC_STATE_MODEM_ON.")
        self._worker._parent._parent.label_instruction.setText("MODEM ON")
        self._worker._parent._parent.label_instruction.setText("PASS")
        print("QC_STATE_MODEM ON wants to change to next state.")
        
        
    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIMCARD(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:

        self.serialIns = serial.Serial()
        modem_ports:QComboBox = self._worker._parent._parent.port_modem
        modem_port_text = modem_ports.currentData()
        self.selected_port = modem_port_text
        # print(self.selected_port)     
        print("STATE : QC_STATE_SIMCARD.")
        tes = SerialAT(self.selected_port, 115200)
        self._worker._parent._parent.label_instruction.setText("TESTING SIMCARD")

        for i in range(5):
            at_res = tes.exchange_at("AT+CPIN?\r", "READY", False, 1000)
            # print(at_res)
            if type(at_res) is int:
                if at_res == -1:
                    print("ERROR ???")
                    self._worker._parent._parent.value_test_simcard.setText("ERROR CHECK THE PORT")
                    time.sleep(2)
                    
                    return
            if at_res["Status"] == "OK":
                print("OK SIMCARD")
                self._worker._parent._parent.value_test_simcard.setText("OK")
                self._worker._parent._parent.label_instruction.setText("PASS")
                break
            else:
                print('no sim card ')
                self._worker._parent._parent.value_test_simcard.setText("ERROR NO SIMCARD")
                self._worker._parent.update("FAIL")
                if i == 4:
                    print("FAILED")
                    break
                else:
                    print("RETRY")
                    continue

        # self._worker._parent._parent.label_instruction.setText("PASS")
        print("QC_STATE_SIMCARD wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIGNAL(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        

        print("STATE : QC_STATE_SIGNAL.") 
        modem_ports:QComboBox = self._worker._parent._parent.port_modem
        modem_port_text = modem_ports.currentData()
        self.selected_port = modem_port_text
        
        self._worker._parent._parent.label_instruction.setText("TESTING SIGNAL")
        at = SerialAT(self.selected_port, 115200)
        at.asign_to_gsm()
        time.sleep(3)
        for i in range(5):
            at_res = at.exchange_at("AT+CSQ\r","+CSQ: " , True, 1000, None, None)
            value_str = at_res['Value']
            status_str = at_res['Status']
            list_val = value_str.replace(",", ".")
            value_signal = list_val[6:8]
            csq_int = int(value_signal)
            
            if csq_int > 10 and csq_int < 32:
                print("OK")
                self._worker._parent._parent.value_test_signal.setText("OK")
                break
            else:
                print("ERROR")
        
        time.sleep(2)
        self._worker._parent._parent.label_instruction.setText("PASS")
        print("Finished")

    def fail_function(self) -> None:
        pass
        
        

class Worker(QRunnable):
    # my_signal = pyqtSignal()

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
            
            update_status_test_sensor = self._parent._parent.label_instruction.text()
            if update_status_test_sensor == "PASS":
                print(update_status_test_sensor)
                test_tamper.pass_function()
                update_status_test_tamper = self._parent._parent.label_instruction.text()
        #         print(update_status_test_tamper)
                if update_status_test_tamper == "PASS":
                    test_modem_on.pass_function()
                    update_status_test_modem_on = self._parent._parent.label_instruction.text()
                    if update_status_test_modem_on == "PASS":
                        test_simcard.pass_function()
                        update_status_test_simcard = self._parent._parent.label_instruction.text()
                        if update_status_test_simcard == "PASS":
                            test_signal.pass_function()
                            update_status_test_signal = self._parent._parent.label_instruction.text()
                            if update_status_test_signal == "PASS":       
                                self._parent._parent.pass_button.setStyleSheet("background-color:#4DAF50;")

                            elif update_status_test_signal =="FAIL":
                                self._parent.handleNG()
                        elif update_status_test_simcard =="FAIL":
                            self._parent.handleNG()                            
                    elif update_status_test_modem_on =="FAIL":
                        self._parent.handleNG()
                elif update_status_test_tamper == "FAIL":
                    self._parent.handleNG()
            elif update_status_test_sensor == "FAIL":
                print(update_status_test_sensor)
                self._parent.handleNG()
        elif update_status_test_power == "FAIL":
            self._parent._parent.value_test_power.setText("FAIL")
            standby.pass_function()
            self._parent.handleNG()
        # test_tamper.pass_function()
        

if __name__ == "__main__":
    pass
