from time import *
import threading

from numpy import byte, true_divide

def countdown():
    global my_time
    global flag_timer
    my_time = 10
    flag_timer = 0
    
    
    for x in range(10):
        my_time -= 1
        print(my_time)
        if my_time == 0:
            flag_timer = 1    
            print("timeout")
        sleep(1) 
        

countdown_thread = threading.Thread(target= countdown)
countdown_thread.start()
byte_rcvd = '}'



while True :
    if flag_timer == 1:
        #stop timer
        print("abc")
        break
    if byte_rcvd == '}' :
        #stop timer 
        print(byte_rcvd)
        
        break
    
print("a")
        # print("run")
        # sleep(14)
        # print("testing power rail need 3 seconds")
        # sleep(10)
        # # if my_time == 0:
        # #     break
        # # if flag_timer == 1 :
        # #     break
        # ############
        # print("run")
        # sleep(10)
        # print("Testing sensor")
        # sleep(2)
        # # if my_time == 0:
        # #     break
        
        # ############
        # print("run")
        # sleep(10)
        # print("Testing tamper")
        # sleep(2)
        # # if my_time == 0:
        # #     break
    
    
    
    
# print("time up , goes to timeout")