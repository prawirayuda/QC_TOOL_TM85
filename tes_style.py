import time

start_time = time.localtime() # get struct_time
time_string_start = time.strftime("%d,%m,%y,%H,%M,%S", start_time)
print(time_string_start.encode())
second_start = time_string_start[-2:]
print(second_start)
time.sleep(2)
get_time = 12


end_time = time.localtime() # get struct_time
time_string_end = time.strftime("%d,%m,%y,%H,%M,%S", end_time)
second_end = time_string_end[-2:]
print(second_end)




# end_time = int(b)+2
