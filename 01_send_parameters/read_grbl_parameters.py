import time
import os
import serial
import argparse

parser = argparse.ArgumentParser(description='Read parameters from the SCE2 controller', usage='%(prog)s -p COM20 -l L086.txt')
parser.add_argument('-p', '--port', help='COM port', required=True, type=str)
parser.add_argument('-l', '--lens', help='Parameter file for particular lens', required=True, type=str)
parser.add_argument('-d', '--delay', help='Delay to sleep between each sent parameter line', default=0.001, type=float)
args = parser.parse_args()

ser = serial.Serial()
ser.port = args.port
ser.baudrate = 115200
ser.timeout = 1
ser.open()
ser.flushInput()
ser.flushOutput()


ser.write(bytes("$$\r", 'utf8'))
time.sleep(args.delay)
data1 = ""
print("Reading motion parameters...")
while(1):
	packet = ser.read(10).decode("utf-8")
	if len(packet)==0:
		break
	data1 += packet
print(data1)


ser.write(bytes("$N\r", 'utf8'))
time.sleep(args.delay)
data2 = ""
print("Reading init parameters...")
while(1):
	packet = ser.read(10).decode("utf-8")
	if len(packet)==0:
		break
	data2 += packet
print(data2)


ser.write(bytes("$I\r", 'utf8'))
time.sleep(args.delay)
data3 = ""
print("Reading SN parameters...")
while(1):
	packet = ser.read(10).decode("utf-8")
	if len(packet)==0:
		break
	data3 += packet
print(data3)





data_out = []

for line in data1.split("\n"):
	if line.strip() not in ["ok", ""]:
		data_out.append(line)

for line in data2.split("\n"):
	if line.strip() not in ["ok", ""]:
		data_out.append(line)

for line in data3.split("\n"):
	if "VER" in line:
		temp1 = line.replace("[","").replace("]","").split(":")[-1]
		data_out.append("$I="+temp1)




f = open(args.lens, "w")
for i in data_out:
	f.write(i)
