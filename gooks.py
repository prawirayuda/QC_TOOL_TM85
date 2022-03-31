# try:
#   print(x)
# except:
#   print("An exception occurred")
# x = -1

# if x < 0:
#   raise Exception("Sorry, no numbers below zero")

# try:
#   print(x)
# except:
#   print("Something went wrong")
# finally:
#   print("The 'try except' is finished")




l1 = ["eat","sleep","repeat"]
s1 = "geek"
 
# creating enumerate objects
obj1 = enumerate(l1)
obj2 = enumerate(s1)
 
print ("Return type:",type(obj1))
print (list(enumerate(l1,1)))
 
# changing start index to 2 from 0
print (list(enumerate(s1,1)))
