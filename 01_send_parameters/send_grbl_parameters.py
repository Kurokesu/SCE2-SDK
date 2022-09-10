import time
import os
from tqdm import tqdm
import serial
import argparse

parser = argparse.ArgumentParser(description='Send parameters to SCE2 controller', usage='%(prog)s -p COM20 -l L086.txt')
parser.add_argument('-p', '--port', help='COM port', required=True, type=str)
parser.add_argument('-l', '--lens', help='Parameter file for particular lens', required=True, type=str)
parser.add_argument('-d', '--delay', help='Delay to sleep between each sent parameter line', default=0.001, type=float)
args = parser.parse_args()

ser = serial.Serial()
ser.port = args.port
ser.baudrate = 115200
ser.timeout = 2
ser.open()
ser.flushInput()
ser.flushOutput()

f = open(args.lens, "r")

content = f.read()
for i in tqdm(range(len(content))):
	ser.write(bytes(content[i], 'utf8'))
	time.sleep(args.delay)
