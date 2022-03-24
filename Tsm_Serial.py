from serial import Serial
import serial.tools.list_ports 
from queue import Queue
import time
from threading import Thread    


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
    def __init__(self, com_port, baudrate, expect = None):
        self.queue = Queue()
        self._com_port = com_port
        self._baudrate = baudrate
        self._serial = None
        
    
    def async_listen(self, com_port, expect, timeout, q, get_value):
        start_time = time.time() * 1000
        data_str = ""
        while True:
            if timeout:
                if time.time()* 1000 - start_time > timeout:
                    q.put({"status": "Error", "Value": None})
                    break
            if com_port.in_waiting > 0:
                ##
                data_str = com_port.readline().encode("utf-8", "ignore")
                print("got_data:", data_str)
                if expect in data_str:
                    
                    if (get_value):
                        q.put({"Status": "OK", "Value": data_str[data_str.index(":") + 2: data_str.index("\r")]})
                        break
                    else:
                        q.put({"Status": "OK", "Value": None})
                        break
                
    
    def exchange_at(self, command, expect, get_value, timeout):
        try:
            for i in range(5):
                self._serial = Serial(self._com_port, self._baudrate, timeout = 1)
                if self._serial.is_open: break
        except Exception as e:
            print("Error", e)
            return -1
        if not self._serial.is_open: return -1
        self._exit_flag = 0
        self._listeningThread = Thread(target = self.async_listen, args = (self._serial, expect, timeout, self._queue, get_value))
        self._listeningThread.start()
        
        if command:
            self._serial.write(command.encode())
            
        while True:
            try:
                data_str = self.queue.get(timeout=0.1)
                self._serial.close()
                return data_str
            
            except Exception as e:
                pass
            
        
    
    
    
if __name__ =="__main__":

    print(SerialUtil.get_serial_ports())
