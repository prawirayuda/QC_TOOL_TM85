from serial import Serial
import serial.tools.list_ports 
from queue import Queue
import time
from threading import Thread    
from typing import Callable
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)
serialInst = serial.Serial()    

class SerialUtil:
    port = []
    def __init__(self):
        self.ports = serial.tools.list_ports.comports()
        
    @classmethod
    def get_serial_ports(cls):
        return list({"port": x,"port_name": y,"hwid": z} for x,y,z in sorted(cls().ports))
    
    @classmethod
    def get_port_number_by_path(cls, path):
        for port, _, hwid in sorted(cls().ports):
            if "LOCATION" in hwid:
                if list(map(lambda x: int(x), hwid[hwid.index("LOCATION") + 9:].replace("-", ".").replace(":x","").split(".")))[:len(path)]==path:
                    return port
        return None
    
    def set_at_ret(self, str):
        self._atr_ret = str
        





class SerialAT:
    def __init__(self, com_port, baudrate, expect=None):
        self._queue = Queue()
        self._com_port = com_port
        self._baudrate = baudrate
        self._serial = None

    def check_exit_flag(self):
        return self._exit_flag

    def exchange_at(self, command, expect, get_value: bool, timeout= 1000, pos_cb:Callable[[str],None] = None, neg_cb:Callable[[str],None]= None):
        try:
            for i in range(5):
                self._serial = Serial(self._com_port, self._baudrate, timeout = 1)
                if self._serial.is_open: break
            # self._serial.open()
        except Exception as e:
            print("Error:", e)
            return -1
        if not self._serial.is_open: return -1
        self._exit_flag = 0
        self._listeningThread = Thread(target = self.async_listen, args=(self._serial, expect, timeout, self._queue, get_value))
        # self._listeningThread.daemon = True
        self._listeningThread.start()

        if command:
            self._serial.write(command.encode())

        while True:
            try:
                data_str = self._queue.get(timeout=0.1)
                self._serial.close()
                return data_str
                # print(data_str)
                # if (data_str['Status'] == "OK"):
                #     print("Return OK")
                # break
            except Exception as e:
                pass
                # self._exit_flag = 1
                # print("Error")
        if (self._serial.is_open):
            self._serial.close()

    def async_listen(self, com_port, expect, timeout, q, get_value):
        start_time = time.time() * 1000
        data_str = ""
        while True:
            if timeout:
                if time.time() * 1000 - start_time > timeout:
                    q.put({"Status": "Error", "Value": None})
                    break
            if com_port.in_waiting > 0:
                #### Warning: This code remove non ASCII, Dont reuse code in another program #### 
                data_str = com_port.readline().decode("utf-8", "ignore")
                # print("got data:", data_str)
                data_ls = list(data_str.split(','))
                # print(data_ls)
                value_signal = str(data_ls[-1])
                # print(value_signal)
                if expect in data_str:
                    # print("Expected")

                    if (get_value):
                        q.put({"Status": "OK", "Value": data_str})
                        break
                    else:
                        q.put({"Status": "OK", "Value": None})
                        break



        
    def tes_simcard(self):        
        # print("tes")
        tes = SerialAT("COM33", 115200)
        for i in range(5):
            at_res = tes.exchange_at("AT+CPIN?\r", "READY", False, 1000)
            # print(at_res)
            if type(at_res) is int:
                if at_res == -1:
                    print("ERROR")
                    return
            if at_res["Status"] == "OK":
                print("OK SIMCARD")
                break
            else:
                print('no sim card ')
                if i == 4:
                    print("FAILED")
                    return
                else:
                    
                    print("RETRY")
                    continue
                
    
    
    def set_at_ret(self, str):
        self.at_ret = str
    
    def tes_signal(self):        
        # print("tes")
       tes = SerialAT("COM33", 115200)  
       for i in range(5):
        at_res = tes.exchange_at("AT+CSQ\r","+CSQ: " , True, 1000, self.set_at_ret, None)
        # print(type(at_res['Status']))
        # print(at_res['Status'])
        value_str = at_res['Value']
        status_str = at_res['Status']
        # print(type(value_str))
        list_val = value_str.replace(",", ".")
        # print(list_val[6:])
        value_signal = list_val[6:8]
        csq_int = int(value_signal)
        
        if csq_int > 10 and csq_int < 31:
            print("OK")
            break
        else:
            print("ERROR")
            
    def asign_to_gsm(self):
        pass
        
        # tes = SerialAT(self.selected_port, 115200)
        # at_res = tes.exchange_at("AT+CSQ\r","+CSQ: " , True, 1000, self.set_at_ret, None)
        # # print(at_res['Value'])

        
if __name__ =="__main__":
    pass
    # print(SerialUtil.get_serial_ports())
    # gas = SerialAT('COM33',115200)
    # gas.tes_simcard()
    # gas.tes_signal()
    # gas.asign_to_gsm()