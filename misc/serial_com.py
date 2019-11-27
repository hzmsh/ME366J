import time
import serial
import serial.tools.list_ports


ser = serial.Serial('COM7', 2000000, timeout=1)
# ser = serial.Serial(serial.tools.list_ports[0])
print("Serial connection made @ port: " + ser.name)
time.sleep(1)
ser.read()
ser.write('<1:1>'.encode())
# msg_list = ['<1:0:0:500>', '<1:1:0:500>', '<0:1:0:500>', '<0:1:1:500>', '<0:0:1:500>', '<1:0:1:500>']
msg_list = ['<1:0:0:5000>', '<0:0:1:5000>']
counter = 0;
while True:
	while ser.in_waiting:
		ser.readline()
	# data = ser.readline()[:-2].decode("utf-8") #the last bit gets rid of the new-line chars
	# print(data)
	ser.write('<1:1>'.encode())
	# if data == "send_msg":
	# 	ser.write(msg_list[counter].encode())
	# 	counter += 1;

	# if counter == len(msg_list):
	# 	counter = 0;

ser.close()