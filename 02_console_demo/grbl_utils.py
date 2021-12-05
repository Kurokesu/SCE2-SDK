import serial
import time
import inspect


class Status():
    status = str

    limit_x = bool
    limit_y = bool
    limit_z = bool
    limit_a = bool

    pos_x = float
    pos_y = float
    pos_z = float
    pos_a = float

    block_buffer_avail = int
    rx_buffer_avail = int
    


def send_command(ser, cmd, echo=True, expecting_lines=1, flush=True):    
    if flush:
        ser.flushInput()

    ser.write(bytes(cmd+"\n", 'utf8'))
    if echo:
        print("")
        print("> "+cmd)

    if expecting_lines == 1:
        data_in = ser.readline().decode('utf-8').strip()
        if echo:
            print("< "+data_in)
        return data_in


    if expecting_lines > 1:
        ret = []
        for i in range(expecting_lines):
            data_in = ser.readline().decode('utf-8').strip()
            if echo:
                print("< "+data_in)
            ret.append(data_in)            
        return ret


def read_status(ser, echo=True):
    retry_cnt = 0
    ret = ""
    backup_timeout = ser.timeout
    ser.timeout = 0.5
    if echo:
        print("")
        print("> ?")

    while True:
        status = send_command(ser, "?", echo=False)
        if len(status) > 10:
            if (status[0] == "<") and (status[-1] == ">"):
                ret = status
                if retry_cnt > 0:
                    if echo:
                        print("* Retry count", retry_cnt)            
                break
            retry_cnt+1

    ser.timeout = backup_timeout
    return ret


def wait_for_idle(ser, echo=True):
    while True:
        status = read_status(ser, echo)
        ret = parse_status(status, echo)

        if ret.block_buffer_avail >= 35:
            if ret.status == "Idle":
                break


def parse_status(txt, echo=True, print_debug=False):
    # Assume string is formed like this (some portions might be missing):
    # <Idle|MPos:0.000,0.000,0.000,0.000|Bf:35,254|F:0|Pn:XYZR|WCO:0.000,0.000,0.000,0.000|Ov:100,100,100|A:S>
    txt = txt.replace('<', '').replace('>', '')
    txt_list = txt.split("|")

    if echo:
        print(txt_list)

    s = Status()
    s.status = txt_list[0] # allways first element

    for p in txt_list[1:]:
        #print("* ", p)

        if p[0:2] == "Bf":
           temp1 = p.split(":")[1]
           s.block_buffer_avail = int(temp1.split(",")[0])
           s.rx_buffer_avail = int(temp1.split(",")[1])

        if p[0:2] == "Pn":
            temp1 = p.split(":")[1]
            s.limit_x = "X" in temp1
            s.limit_y = "Y" in temp1
            s.limit_z = "Z" in temp1

        if p[0:4] == "MPos":
            temp1 = p.split(":")[1]
            s.pos_x = float(temp1.split(",")[0])
            s.pos_y = float(temp1.split(",")[1])
            s.pos_z = float(temp1.split(",")[2])
            s.pos_a = float(temp1.split(",")[3])

    # print all elements for debug
    if print_debug:
        for i in inspect.getmembers(s):
            if not i[0].startswith('_'):
                if not inspect.ismethod(i[1]): 
                    print(i)

    # TODO: print unparsed sub-strings
    return s



def parse_version(txt):
    # Assume string is formed like this:
    # [VER:1.1f-SCE2.20211130:L086,6ZG-BEG19]
    txt = txt.replace('[', '').replace(']', '')

    print()
    txt_list = txt.split(':')    
    print("* Firmware version:", txt_list[1])


    id_strings = txt_list[2].split(',')
    print("* ID strings:", id_strings)

    for i in id_strings:
        if i[0:3] == "6ZG":
            print(" o L086 lens detected, SN:", i[4:])
            
    for i in id_strings:
        if i[0:3] == "D2R":
            print(" o SCE2-L086 controller detected, SN:", i[4:])


def parse_adc(txt):
    # Assume string is formed like this:
    # [TLENS:1743]
    txt = txt.replace('[', '').replace(']', '')

    print()
    txt_list = txt.split(':')    
    adc = int(txt_list[1].strip())
    print("* 12 Bit ADC (Vref=3.3V):", adc, "/", round(adc/4096*3.3, 3), "V")



def unhome_motors(ser, axis, step=1, speed=1000):
    print("* Moving out of home position:", axis)
    while True:
        status_txt = read_status(ser, echo=False)
        status = parse_status(status_txt, echo=False)

        if axis.upper() == "X":
            axis_status = status.limit_x
        if axis.upper() == "Y":
            axis_status = status.limit_y
        if axis.upper() == "Z":
            axis_status = status.limit_z
        if axis.upper() == "A":
            axis_status = status.limit_a
                
        if axis_status:
            cmd = "G91 G"+str(step)+" "+axis+"1 F"+str(speed)
            send_command(ser, cmd, echo=False)
            wait_for_idle(ser, echo=False)
        else:
            break

