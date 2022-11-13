import serial
import time

from threading import Thread
from threading import Event
import queue


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

    timestamp = float
    
    
class SCE2():

    def __init__(self, com_port):
        self.lens_name = None
        self.lens_detected = None

        self.com_port = com_port
        self.ser = serial.Serial()
        self.ser.port = self.com_port
        self.ser.baudrate = 115200
        self.ser.timeout = 5

        self.ser.open()
        self.ser.flushInput()
        self.ser.flushOutput()
      
        ver = self.send_command("$I", echo=False, expecting_lines=3)
        txt = ver[0].replace('[', '').replace(']', '')
        txt_list = txt.split(':')    
        id_strings = txt_list[2].split(',')
        for i in id_strings:
            self.lens_detected = False
            if i[0:3] == "EFJ":
                self.lens_name = "L117"
            if i[0:3] == "6ZG":
                self.lens_name = "L086"   
            if i[0:3] == "LS8":
                self.lens_name = "L085"
            if i[0:3] == "JWF":
                self.lens_name = "L084"


    def send_command(self, cmd, echo=True, expecting_lines=1, flush=True):    
        if flush:
            self.ser.flushInput()

        self.ser.write(bytes(cmd+"\n", 'utf8'))
        if echo:
            print("")
            print("> "+cmd)

        if expecting_lines == 1:
            data_in = self.ser.readline().decode('utf-8').strip()
            if echo:
                print("< "+data_in)
            return data_in


        if expecting_lines > 1:
            ret = []
            for i in range(expecting_lines):
                data_in = self.ser.readline().decode('utf-8').strip()
                if echo:
                    print("< "+data_in)
                ret.append(data_in)            
            return ret

    def move_buffered(self, cmd):
        buffers = 0

        backup_timeout = self.ser.timeout
        self.ser.timeout = 0.01
        while buffers < 2:
            retry_cnt = 0
            ret = ""
        
            while True:
                status = self.send_command("?", echo=False)
                if len(status) > 10:
                    if (status[0] == "<") and (status[-1] == ">"):
                        ret = status
                        if retry_cnt > 0:
                            break
                    retry_cnt+=1
            #print(ret)
            text = ret[1:-1]
            feedback_split = text.split("|")
            positions = feedback_split[2].split(":")
            positions = positions[1]
            positions = positions.split(",")
            buffers = int(positions[0])
            #print(buffers)
        self.ser.timeout = backup_timeout


        self.ser.write(bytes(cmd+"\n", 'utf8'))
        data_in = self.ser.readline().decode('utf-8').strip()




    def read_status(self, echo=True):
        retry_cnt = 0
        ret = ""
        backup_timeout = self.ser.timeout
        self.ser.timeout = 0.5
        if echo:
            print("")
            print("> ?")

        while True:
            status = self.send_command("?", echo=False)
            if len(status) > 10:
                if (status[0] == "<") and (status[-1] == ">"):
                    ret = status
                    if retry_cnt > 0:
                        if echo:
                            print("* Retry count", retry_cnt)            
                    break
                retry_cnt+=1

        self.ser.timeout = backup_timeout
        return ret


    def parse_status(self, txt, echo=True, print_debug=False):
        # Assume string is formed like this (some portions might be missing):
        # <Idle|MPos:0.000,0.000,0.000,0.000|Bf:35,254|F:0|Pn:XYZR|WCO:0.000,0.000,0.000,0.000|Ov:100,100,100|A:S>        
        s = Status()
        s.timestamp = time.time_ns()
        
        txt = txt.replace('<', '').replace('>', '')
        txt_list = txt.split("|")

        if echo:
            print(txt_list)


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

    def wait_for_idle(self, echo=True):
        positions = []
        while True:
            status = self.read_status(echo)
            ret = self.parse_status(status, echo)
            #print(ret.pos_y, ret.timestamp)
            positions.append((ret.pos_x, ret.pos_y, ret.pos_z, ret.limit_x, ret.limit_y, ret.limit_z, ret.timestamp, ret.status))
                        
            if ret.block_buffer_avail >= 35:
                if ret.status == "Idle":
                    break
        return positions


    def home_lens(self, echo=False):
        if self.lens_name == "L117":
            if echo:
                print("Homing L117 lens", end = '')
            # TODO: check which lens it is. Home each lens according
            # Workaround for L117. Sometimes if Z is in -4..-2 Y axis can't home
            if echo:
                print("...", end = '')
            self.send_command("G91 G0 Z2", echo=False)
            self.wait_for_idle(echo=False)
            if echo:
                print("A", end = '')
            self.send_command("$HA", echo=False)
            if echo:
                print("X", end = '')
            self.send_command("$HX", echo=False)
            if echo:
                print("Y", end = '')
            self.send_command("$HY", echo=False)
            if echo:
                print("Z", end = '')
            self.send_command("$HZ", echo=False)
            if echo:
                print(" Done")

        if self.lens_name == "L086":
            if echo:
                print("Homing L086 lens...", end = '')
            if echo:
                print("X", end = '')
            self.send_command("$HX", echo=False)
            if echo:
                print("Y", end = '')
            self.send_command("$HY", echo=False)
            if echo:
                print("Z", end = '')
            self.send_command("$HZ", echo=False)
            if echo:
                print(" Done")





class SCE2_HAL():
    thread = None
    event = Event()
    queue = queue.Queue()


    def task1(self):
        lens = SCE2("COM165")

        # Read controller version strings
        ver = lens.send_command("$I", echo=False, expecting_lines=3)
        #print(ver)



        # TODO: check which lens it is. Home each lens according

        print("Homing")
        # Workaround. Sometimes if Z is in -4..-2 Y axis can't home
        lens.send_command("G91 G0 Z2")
        lens.wait_for_idle(echo=False)
        lens.send_command("$HA")
        lens.send_command("$HX")
        lens.send_command("$HY")
        lens.send_command("$HZ")
        print("Done")


    def start_task(self):
        self.event.clear()
        self.thread = Thread(target=self.task1)
        self.thread.start()
