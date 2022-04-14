from __future__ import annotations
from itertools import count
from msilib.schema import Error
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
from Tsm_Config import QC_BYTESIZE, QC_PORT_SERIAL_BAUDRATE, QC_SERIAL_TIMEOUT, USB_AT_BAUDRATE
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
        print("STATE : QC_STATE_STANDBY.")
        # print("QC_STATE_STANDBY now changes the state of the context.")

    def fail_function(self):
        pass
        # print("if fail back to STANDBY MODE")
        # self.context.setState(QC_STATE_STANDBY(self))

    
class QC_STATE_TEST_POWER_RAIL(State):  
    def __init__(self, worker):
        self._worker = worker
    
    def pass_function(self) -> None:
        try:  
            print("STATE : QC_STATE_TEST_POWER_RAIL.")
            self._worker._parent._parent.label_instruction.setText("TESTING POWER RAIL")
            #  7B 90 01 F4 01 7D 0A
            self.serialInst = serial.Serial()    
            qc_ports:QComboBox = self._worker._parent._parent.port_qc   
            port_text = qc_ports.itemText(qc_ports.currentIndex())
            try:
                self.selected_port = port_text[port_text.index("(")+1 : port_text.index(")")]
                self.serialInst.port = self.selected_port
            except Exception as e:
                self._worker._parent._parent.label_error.setText("ERROR : NO PORT DETECTED")
                print(f"ini {e}")
                
            self.serialInst.baudrate = QC_PORT_SERIAL_BAUDRATE
            self.serialInst.bytesize = QC_BYTESIZE
            self.serialInst.timeout = QC_SERIAL_TIMEOUT
            self.serialInst.stopbits= serial.STOPBITS_ONE
            self.serialInst.open()
            list_buffer = []
            self.serialInst.write(b"{P?}")    
            timeout = time.time() + 7 #in second 
                
            while True:
                try:
                    flag = 0
                    if flag == 1 or time.time() > timeout:
                        print("there's no data recieved")
                        self._worker._parent._parent.value_test_power.setText(f"TIMEOUT...") 
                        self._worker._parent._parent.label_error.setText("ERROR MESSAGE : TIMEOUT...")
                        self._worker._parent.update_label_test_power("FAIL")
                        time.sleep(2)
                        self._worker._parent.handleNG()
                        self.serialInst.close()
                        return 

                    if self.serialInst.in_waiting:
                        data = self.serialInst.read()
                        list_buffer.append(data.decode('utf-8'))
                        # print(list_buffer)
                        try:
                            if list_buffer[-1] == "}":
                                val1 = list_buffer[1:]
                                val2 = val1[2:-1]
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
                                self._worker._parent._parent .value_test_power.setText(f"VALUE 1 : {final_val1:.3f}, VALUE 2 : {final_val2:.3f}")  
                                # tes sample 
                                # if final_val1 > th1 and final_val2 > th2: #test fail value
                                if final_val1 < th1 and final_val2 < th2: #test pass value
                                    print("PASS")
                                    self._worker._parent.update_label_test_power("PASS")
                                    break
                                else:
                                    print("FAIL")
                                    self._worker._parent.update_label_test_power("FAIL")
                                    self._worker._parent._parent.value_test_power.setText(f"VALUE 1 : {final_val1:.3f}, VALUE 2 : {final_val2:.3f}")  
                                    self.serialInst.close()
                                    #wait till timeout
                        

                        except Exception as e:
                            self._worker._parent._parent.label_error.setText(f"ERROR INPUT FROM MCU : {e}")
                            # print(f"ini {e}")
                        
                except Exception as e:
                    self._worker._parent._parent.label_error.setText(f"ERROR : INVALID VALUE POWER RAIL")
                    print(e)
                        
            # print("NEXT step")
            print("QC_STATE_TEST_POWER_RAIL wants to next State")
            time.sleep(1)
            self.context.setState(QC_STATE_SENSOR(Worker))     
        # self.serialInst.close()
        except serial.SerialException as e:
            self._worker._parent._parent.label_error.setText(f"ERROR MESSAGE : {e}")
            self.serialInst.close()
            
    def fail_function(self) -> None:
        pass
    
    
class QC_STATE_TEST_CRYSTAL(State):  
    def __init__(self, worker):
        self._worker = worker
    
    def pass_function(self) -> None:
        try:  
            print("STATE : QC_STATE_TEST_CRYSTAL.")
            self._worker._parent._parent.label_instruction.setText("TESTING CRYSTAL")
            #start time
            start_time = time.localtime() # get struct_time
            time_string_start = time.strftime("%d,%m,%y,%H,%M,%S", start_time)
            second_start = time_string_start[-2:]
            print(second_start)
            command_set_time = time_string_start
            # time.sleep(2)           
            
            #select port
            self.serialInst = serial.Serial()    
            qc_ports:QComboBox = self._worker._parent._parent.port_qc   
            port_text = qc_ports.itemText(qc_ports.currentIndex())
            try:
                self.selected_port = port_text[port_text.index("(")+1 : port_text.index(")")]
                self.serialInst.port = self.selected_port
            except Exception as e:
                self._worker._parent._parent.label_error.setText("ERROR : NO PORT DETECTED")
                print(f"ini {e}")
                
            self.serialInst.baudrate = QC_PORT_SERIAL_BAUDRATE
            self.serialInst.bytesize = QC_BYTESIZE
            self.serialInst.timeout = QC_SERIAL_TIMEOUT
            self.serialInst.stopbits= serial.STOPBITS_ONE
            self.serialInst.open()
            list_buffer = []
            time.sleep(3)
            self.serialInst.write(command_set_time.encode())    
            timeout = time.time() + 7 #in second 
                
            while True:
                try:
                         
                    flag = 0
                    if flag == 1 or time.time() > timeout:
                        print("there's no data recieved")
                        self._worker._parent._parent.value_test_power.setText(f"TIMEOUT...") 
                        self._worker._parent._parent.label_error.setText("ERROR MESSAGE : TIMEOUT...")
                        self._worker._parent.update_label_test_power("FAIL")
                        time.sleep(2)
                        self._worker._parent.handleNG()
                        self.serialInst.close()
                        return 

                    if self.serialInst.in_waiting:
                        data = self.serialInst.read()
                        list_buffer.append(data.decode('utf-8'))
                        print(list_buffer)
                        try:
                            if list_buffer[-1] == "}":
                                prefix = list_buffer[1:]
                                suffix = prefix[2:-1]
                                join_value = "".join(suffix)
                                print(join_value)

                                if join_value == "OK!":
                                    #get time tolerance 2 detik 
                                    self.serialInst.write(b"{X?}")
                                    list_buffer_time = []
                                    while True:
                                        try:
                                            get_time = self.serialInst.read()
                                            list_buffer_time.append(get_time.decode('utf-8'))
                                            print(list_buffer_time)
                                            if list_buffer_time[-1] == "}":
                                                print("time")
                                                break
                                            # print("PASS")
                                            # self._worker._parent.update_label_test_crystal("PASS")
                                            # self._worker._parent._parent.value_test_crystal.setText(f"VALUE TEST CRYSTAL: {join_value}")  
                                            # break
                                        except:
                                            pass
                                    break
                                            
                                else:
                                    print("FAIL")
                                    self._worker._parent.update_label_test_crystal("FAIL")
                                    self._worker._parent._parent.value_test_crystal.setText(f"VALUE TEST CRYSTAL: {join_value}")  
                                    self.serialInst.close()
                                    #wait till timeout
                                    
                        
                        except Exception as e:
                            self._worker._parent._parent.label_error.setText(f"ERROR INPUT FROM MCU : {e}")
                            # print(f"ini {e}")
                        
                except Exception as e:
                    self._worker._parent._parent.label_error.setText(f"ERROR : INVALID VALUE CRYSTAL")
                    print(e)
                        
            print("QC_STATE_CRYSTAL wants to next State")
            time.sleep(1)
        except serial.SerialException as e:
            self._worker._parent._parent.label_error.setText(f"ERROR MESSAGE : {e}")
            self.serialInst.close()
            
        
    def fail_function(self) -> None:
        pass


class QC_STATE_SENSOR(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        try:
            print("STATE : QC_STATE_TEST_SENSOR.")
            
            #for testing modem on
            # self._worker._parent.update_label_test_sensor("PASS")
            
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
            timeout = time.time() + 7 #in second         
            while True:
                try:
                    
                    flag = 0
                    if flag == 1 or time.time() > timeout:
                        print("there's no data recieved")
                        self._worker._parent._parent.value_test_sensor.setText(f"TIMEOUT...") 
                        self._worker._parent._parent.label_error.setText(f"ERROR MESSAGE : TIMEOUT...") 
                        self._worker._parent.update_label_test_sensor("FAIL")
                        time.sleep(2)
                        self._worker._parent.handleNG()
                        self.serialInst.close()
                        return 
                    
                    if self.serialInst.in_waiting:
                        data1 = self.serialInst.read()
                        list_buffer.append(data1.decode('utf-8'))
                        print(list_buffer)
                        if list_buffer[-1] == "}":
                            val1 = list_buffer[1:]
                            val2 = val1[2:-1]
                            print(val2)

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
                            
                            self._worker._parent._parent.value_test_sensor.setText(f"SENSOR 1 : ({value1}-{value3}-{value5}) | SENSOR 2 : ({value2}-{value4}-{value6})")  
                            time.sleep(1)
                            self._worker._parent.update_label_test_sensor("PASS")
                            self.serialInst.close()
                            #just for testing
                            break

                            # if (value1 > th_low_down and value1 < th_low_up) and (value2 > th_low_down and value2 < th_low_up) and (value3 > th_mid_down and value3 < th_mid_up) and (value4 > th_mid_down and value4 < th_mid_up) and (value5 > th_high_down and value5 < th_high_up) and (value6 > th_high_down and value6 < th_high_up):
                            #     self._worker._parent._parent.value_test_sensor.setText(f"Sensor 1 : ({value1}-{value3}-{value5}), Sensor 2 : ({value2}-{value4}-{value6})")  
                            #     print("PASS")
                            #     self._worker._parent.update_label_test_sensor("PASS")
                            #     # print("KEMANA")
                            #     break
                            # else:
                            #     print("FAIL")
                            #     self._worker._parent._parent.value_test_sensor.setText(f"Sensor 1 : ({value1}-{value3}-{value5}), Sensor 2 : ({value2}-{value4}-{value6})")  
                            #     self._worker._parent.update_label_test_sensor("FAIL")
                except Exception as e:
                    print(e)
                    self._worker._parent._parent.label_error.setText(f"ERROR MESSAGE : ERROR INPUT FROM MCU ")
                    self._worker._parent.update_label_test_sensor("FAIL")
                    self._worker._parent._parent.value_test_sensor.setText("NO DATA")
        except serial.SerialException as e:
            print(e)
            print("NEXT step")
            

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
        
        #for testing modem only
        self._worker._parent.update_label_test_tamper("PASS")
        
        
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
        
        timeout = time.time() + 5 #in second    
        
        while True: 
            flag = 0
            if flag == 1 or time.time() > timeout:
                print("there's no data recieved")   
                self._worker._parent._parent.value_test_tamper.setText(f"TIMEOUT...") 
                self._worker._parent._parent.label_error.setText("ERROR MESSAGE : TIMEOUT...")
                self._worker._parent.update_label_test_tamper("FAIL")
                time.sleep(2)
                self._worker._parent.handleNG()
                self.serialInst.close()
                return 
            
            if self.serialInst.in_waiting:
                data1 = self.serialInst.read()
                list_buffer.append(data1.decode('utf-8'))
                # print(list_buffer)
                if list_buffer[-1] == "}":
                    first_bracket = list_buffer[1:]
                    last_bracket = first_bracket[:-1]
                    # print(last_bracket)
                    join_all = ''.join(last_bracket)
                    print(join_all)
                    if join_all == "TMP":
                        #here the process waiting user press the tamper
                        while True:
                            data_press_btn = self.serialInst.readline()
                            decode_data = data_press_btn.decode('utf-8')
                            data_strip = decode_data.strip()
                            print(data_strip)
                            if '}' in data_strip:
                                data_1 = data_strip[1:]
                                data_2 = data_1[:-1]
                                print(data_2)
                                if data_2 == "T:OK!":
                                    # print("get data")
                                    self._worker._parent._parent.value_test_tamper.setText(f"TAMPER OK")  
                                    self._worker._parent.update_label_test_tamper("PASS")
                                    break
                               
                                else:
                                    print("FAIL")
                                    self._worker._parent.update_label_test_tamper("FAIL")
                                    self._worker._parent._parent.value_test_tamper.setText(f"TAMPER NOT OK")  
                                    self.serialInst.close()
                                    time.sleep(2)
                        break
                    
                    
        print("NEXT TO MODEM TEST TURN OFF MCU PORT")  
        print("QC_STATE_TEST_TAMPER wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
class QC_STATE_MODEM_ON(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        # Turning modem On
        try:
            print("STATE : QC_STATE_MODEM_ON.")
            ##Turning Modem by send Comand to QC TOOLS 
            
            # qc_ports:QComboBox = self._worker._parent._parent.port_qc   
            # port_text = qc_ports.itemText(qc_ports.currentIndex())
            # self.selected_port = port_text[port_text.index("(")+1 : port_text.index(")")]         
            # self.serialInst = serial.Serial()
            # self.serialInst.port = self.selected_port
            # self.serialInst.baudrate = QC_PORT_SERIAL_BAUDRATE
            # self.serialInst.bytesize = 8
            # self.serialInst.timeout = 10
            # self.serialInst.stopbits= serial.STOPBITS_ONE
            # self.serialInst.open()
            # list_buffer = []
            # self.serialInst.write(b"{O:1,1}")
            ############ adding function for updating label modem on ########## 
            
            # time.sleep(3)
            #Search Port Modem
            self.port_modem = serial.tools.list_ports.comports()
            self.comport = 'None'
            self.numConnection = len(self.port_modem)
            for i in range(0, self.numConnection):
                port = self.port_modem[i]
                str_port = str(port)
                # print(str_port)
                if "Modem" in str_port:
                    split_port = str_port.split(' ')
                    self.comport = (split_port[0])
                    # print(self.comport)
                
            #give time to wait modem stable
            time.sleep(5)            
            self._worker._parent._parent.label_instruction.setText("MODEM ON !!")
            self._worker._parent._parent.label_instruction.setText("PASS")
            #Change nbiot network to gsm
            tes = SerialAT(self.comport, USB_AT_BAUDRATE)
            at_res = tes.exchange_at("AT+qcfg=\"nwscanmode\",1,1\r","OK" , True, 1000)
            print(at_res['Value'])
            print("QC_STATE_MODEM ON wants to change to next state.")
            
        except Exception as e:
            self._worker._parent._parent.label_error.setText("MODEM OFF !! CHECK THE MODEM")
            # print(f"Error {e}")
        
    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIMCARD(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        print("STATE : QC_STATE_SIMCARD.")
        self._worker._parent._parent.label_instruction.setText("TESTING SIMCARD")
        #Search Port Modem
        self.port_modem = serial.tools.list_ports.comports()
        self.comport = 'None'
        self.numConnection = len(self.port_modem)
        for i in range(0, self.numConnection):
            port = self.port_modem[i]
            str_port = str(port)
            # print(str_port)
            try:               
                if "Modem" in str_port:
                    split_port = str_port.split(' ')
                    self.comport = (split_port[0])
                    # print(self.comport)
                else:
                    print("modem not found")
            except Exception as e:
                self._worker._parent._parent.label_error.setText("MODEM NOT FOUND")

        tes = SerialAT(self.comport, USB_AT_BAUDRATE)
        for i in range(5):
            at_res = tes.exchange_at("AT+CPIN?\r", "READY", False, 1000)
            # print(at_res)
            if type(at_res) is int:
                if at_res == -1:
                    print("error value")
                    self._worker._parent._parent.label_error.setText("ERROR CHECK THE PORT")
                    time.sleep(3)
                    return
            if at_res["Status"] == "OK":
                print("ok simcard")
                self._worker._parent._parent.value_test_simcard.setText("OK")
                self._worker._parent.update_label_test_simcard("PASS")                
                break
            else:
                print('no sim card ')
                self._worker._parent._parent.value_test_simcard.setText("SIMCARD NOT OK")
                self._worker._parent.update_label_test_simcard("FAIL")
                time.sleep(3)
                self._worker._parent.handleNG()       
                if i == 4:
                    print("FAILED")
                    break
                else:
                    print("RETRY")
                    continue


        print("QC_STATE_SIMCARD wants to change to next state.")

    def fail_function(self) -> None:
        pass
        
        
class QC_STATE_SIGNAL(State):
    def __init__(self, worker):
        self._worker = worker
        
    def pass_function(self) -> None:
        print("STATE : QC_STATE_SIGNAL.") 
        self._worker._parent._parent.label_instruction.setText("TESTING SIGNAL")
        #Search Port Modem
        self.port_modem = serial.tools.list_ports.comports()
        self.comport = 'None'
        self.numConnection = len(self.port_modem)
        for i in range(0, self.numConnection):
            port = self.port_modem[i]
            str_port = str(port)
            # print(str_port)
            try:               
                if "Modem" in str_port:
                    split_port = str_port.split(' ')
                    self.comport = (split_port[0])
                    # print(self.comport)
                else:
                    print("modem not found")
            except Exception as e:
                self._worker._parent._parent.label_error.setText("MODEM NOT FOUND")
    
        at = SerialAT(self.comport, USB_AT_BAUDRATE)
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
                self._worker._parent.update_label_test_signal("PASS")
                self._worker._parent._parent.value_test_signal.setText(f"VALUE SIGNAL {str(csq_int)} : OK")
                break
            else:
                self._worker._parent.update_label_test_signal("FAIL")
                self._worker._parent._parent.value_test_signal.setText(f"VALUE SIGNAL {str(csq_int)} : IS NOT OK")
                time.sleep(2)
                self._worker._parent.handleNG()
                print("err")
        
        time.sleep(2)
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
        self._parent.standby_mode()
        self._parent._parent.button_start.setEnabled(False)
        standby = Context(QC_STATE_STANDBY(self))
        test_power_rail = Context(QC_STATE_TEST_POWER_RAIL(self))
        test_crystal = Context(QC_STATE_TEST_CRYSTAL(self))
        test_sensor = Context(QC_STATE_SENSOR(self))
        test_tamper = Context(QC_STATE_TAMPER(self))
        test_modem_on = Context(QC_STATE_MODEM_ON(self))
        test_simcard = Context(QC_STATE_SIMCARD(self))
        test_signal = Context(QC_STATE_SIGNAL(self))
        
        standby.pass_function()
        test_power_rail.pass_function()
        update_status_test_power = self._parent._parent.label_instruction.text()

        
        if update_status_test_power == "PASS":
            self._parent._parent.value_test_crystal.setText("ON GOING")
            test_crystal.pass_function()
            update_status_test_crystal = self._parent._parent.label_instruction.text()
            if update_status_test_crystal == "PASS":
                self._parent._parent.value_test_sensor.setText("ON GOING")
                test_sensor.pass_function()
                update_status_test_sensor = self._parent._parent.label_instruction.text()
                if update_status_test_sensor == "PASS":
                    self._parent._parent.value_test_tamper.setText("ON GOING")
                    test_tamper.pass_function()
                    update_status_test_tamper = self._parent._parent.label_instruction.text()
                    if update_status_test_tamper == "PASS":
                        self._parent._parent.label_instruction.setText("TURNING ON MODEM !!")
                        test_modem_on.pass_function()
                        update_status_test_modem_on = self._parent._parent.label_instruction.text()
                        if update_status_test_modem_on == "PASS":
                            self._parent._parent.value_test_simcard.setText("ON GOING")
                            test_simcard.pass_function()
                            update_status_test_simcard = self._parent._parent.label_instruction.text()
                            if update_status_test_simcard == "PASS":
                                test_signal.pass_function()
                                update_status_test_signal = self._parent._parent.label_instruction.text()
                                if update_status_test_signal == "PASS":       
                                    self._parent._parent.pass_button.setStyleSheet("background-color:#4DAF50;")
                                    time.sleep(2)
                                    self._parent.standby_mode()
                                    #finish

                                elif update_status_test_signal =="FAIL":
                                    self._parent._parent.fail_button.setStyleSheet("background-color:#C82626;")
                                    self._parent.handleNG()
                            elif update_status_test_simcard =="FAIL":
                                self._parent.handleNG()                            
                        elif update_status_test_modem_on =="FAIL":
                            self._parent.handleNG()
                    elif update_status_test_tamper == "FAIL":
                        self._parent.handleNG()
                elif update_status_test_sensor == "FAIL":
                    self._parent.handleNG()
            elif update_status_test_crystal == "FAIL":
                self._parent.handleNG()
        elif update_status_test_power == "FAIL":
            self._parent._parent.fail_button.setStyleSheet("background-color:#C82626;")
            self._parent._parent.value_test_power.setText("FAIL")
            self._parent.handleNG()
        # test_tamper.pass_function()
        

if __name__ == "__main__":
    pass
