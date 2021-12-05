import serial
import time
import grbl_utils 


ser = serial.Serial()
ser.port = 'COM20'              # Controller com port
ser.baudrate = 115200           # Baud rate when connected over CDC USB is not important
ser.timeout = 10                # max timeout to wait for command response

ser.open()
ser.flushInput()
ser.flushOutput()




# Read controller version strings
ver = grbl_utils.send_command(ser, "$I", expecting_lines=3)
grbl_utils.parse_version(ver[0])
grbl_utils.parse_adc(ver[1])

# Switch to ABS positionig mode
grbl_utils.send_command(ser, "G90")


# Limit sensor LED ON
# In IR mode should be switched off because of beeding light to sensor
grbl_utils.send_command(ser, "M120 P1")


# IRIS open
grbl_utils.send_command(ser, "M114 P1")


# IR CUT filter 
grbl_utils.send_command(ser, "G90 G1 A0.3 F1")    # ON (Visible light)
#grbl_utils.send_command(ser, "G90 G1 A0.7 F1")  # OFF (Full spectrum)


# Move out of home position X axis, move in small steps. 
# 1.1f-SCE2.20211130 can't perform precision homing procedure unless motors 
# are moved out of home position. Later should be implemented in firmware
# and this step will not be needed
grbl_utils.unhome_motors(ser, "X")
grbl_utils.unhome_motors(ser, "Y")
grbl_utils.unhome_motors(ser, "Z")


# home motors
grbl_utils.send_command(ser, "$HX") 
grbl_utils.send_command(ser, "$HY") 
grbl_utils.send_command(ser, "$HZ") 



# Move wide and narrow angles
#grbl_utils.send_command(ser, "G90 G1 X-4 Y-1.3 Z1.1 F1000")
grbl_utils.send_command(ser, "G90 G1 X-8.2 Y-5.1 Z-2.6 F1000")
grbl_utils.wait_for_idle(ser, echo=False)
time.sleep(1)

grbl_utils.send_command(ser, "G90 G1 X-7.2 Y-5.9 Z-2.98 F1000")
grbl_utils.wait_for_idle(ser, echo=False)
time.sleep(1)

grbl_utils.send_command(ser, "G90 G1 X-0.5 Y-5.6 Z-0.7 F1000")
grbl_utils.wait_for_idle(ser, echo=False)
time.sleep(1)

grbl_utils.send_command(ser, "G90 G1 X2.3 Y-5.6 Z0.24 F1000")
grbl_utils.wait_for_idle(ser, echo=False)
time.sleep(1)

# Read GRBL status
status_txt = grbl_utils.read_status(ser)
status = grbl_utils.parse_status(status_txt, print_debug=True)
