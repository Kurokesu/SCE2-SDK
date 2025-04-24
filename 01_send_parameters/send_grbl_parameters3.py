import time
import os
from tqdm import tqdm
import serial
import argparse
import serial.tools.list_ports

parser = argparse.ArgumentParser(description='Send parameters to SCE2 controller', usage='%(prog)s -p COM20 -l L086.txt')
parser.add_argument('-p', '--port', help='COM port', type=str)
parser.add_argument('-l', '--lens', help='Parameter file for particular lens', required=True, type=str)
parser.add_argument('-d', '--delay', help='Delay to sleep between each sent parameter line', default=0.001, type=float)
parser.add_argument('-s', '--sn', help='Provide serial number', default=0.001, type=str)
args = parser.parse_args()

if args.port == None:
	port_list = serial.tools.list_ports.comports()

	for port, desc, hwid in port_list:
		#print('-', port, desc)
		args.port = port

	print(args.port)


ser = serial.Serial()
ser.port = args.port
ser.baudrate = 115200
ser.timeout = 1
ser.open()
ser.flushInput()
ser.flushOutput()

f = open(args.lens, "r")

content = f.readlines()
for i in tqdm(content):
	#time.sleep(args.delay)
	#print(i.strip())
	ser.flushInput()
	ser.flushOutput()
	ser.write(bytes(i.strip()+"\r", 'utf8'))
	packet = ser.read(2).decode("utf-8")

if args.sn:
	ser.flushInput()
	ser.flushOutput()
	ser.write(bytes("$I="+args.sn.strip()+"\r", 'utf8'))
	packet = ser.read(2).decode("utf-8")
