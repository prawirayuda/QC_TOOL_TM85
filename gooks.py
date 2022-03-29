import serial
import struct
import serial.tools.list_ports

# serialPort = serial.Serial(port = "COM20", baudrate=9600,
#                     bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE)
# data = serialPort.readline()
serialInst = serial.Serial()
ports = serial.tools.list_ports.comports()
portList = []

for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))
    
val = input("SELECT PORT : ")

for x in range(0, len(portList)):
    if portList[x].startswith("COM" + str(val)):
        portVar = "COM" + str(val)
        print(f" selected port is {portList[x]}")
        
serialInst.baudrate = 9600
serialInst.port = portVar
serialInst.bytesize = 8
serialInst.timeout = 10
serialInst.stopbits=serial.STOPBITS_ONE
serialInst.open()

list_byte = bytearray()
list_buffer = []
while True:
    if serialInst.in_waiting:
        data1 = serialInst.read()
        list_buffer.append(data1)
        # print(list_buffer)
        if list_buffer[-1] == b"}":
            print("out of loop")
            
            val1 = list_buffer[1:3]
            val2 = list_buffer[3:5]
            byte1, byte2 = val1 
            byte3, byte4 = val2 
            # print(byte1)
            # print(byte2)
            data_int1 = int.from_bytes(byte1+byte2, 'little')
            data_int2 = int.from_bytes(byte3+byte4, 'little')
            print(data_int1)
            print(data_int2)
            

            break
        
        
