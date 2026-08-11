from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSvg

import serial
import time
import queue
import threading
import serial.tools.list_ports

import logging
LOGGER = logging.getLogger(__name__)
LOGGER.info('start')


IDLE_TIMEOUT = 0.02

class SerialComm(QObject):
    strStatus = pyqtSignal(str)
    strVersion = pyqtSignal(str)
    serFeedback = pyqtSignal(str)
    serReceive = pyqtSignal(list)
    strError = pyqtSignal(str)
    current_line_feedback = pyqtSignal(str)

    log_tx = pyqtSignal(str)
    log_rx = pyqtSignal(str)
    
    port = None
    ser = None
    abort_flag = threading.Event()
    commands = queue.Queue()
    commands_buffered = queue.Queue()
    action_connect = queue.Queue()
    action_disconnect = queue.Queue()
    action_recipe = queue.Queue()


    def get_compot_list(self):
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append((p.device, p.description))
        return ports

    def connect(self, port, baudrate, seek_timeout):
        self.port = port
        self.baudrate = baudrate
        self.action_connect.put(True)
        self.seek_timeout = seek_timeout

    def disconnect(self):
        self.action_disconnect.put(True)

    def send(self, data):
        self.commands.put(data)

    def send_buffered(self, data):
        self.commands_buffered.put(data)

    def abort(self):
        """Immediately stop all motion: drop queued commands and soft-reset GRBL.

        The GRBL real-time soft-reset byte (0x18) is the only command that
        stops a running homing cycle (feed hold is ignored while homing).
        It is written directly to the port from the caller's thread because
        the worker thread may be blocked waiting for the homing 'ok'.
        The abort_flag makes the worker's wait loops bail out; the controller
        is left in ALARM state and must be unlocked with $X afterwards.
        """
        self.abort_flag.set()

        for q in (self.commands, self.commands_buffered):
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break

        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.write(b'\x18')
                LOGGER.warning(">>> 0x18 (soft reset / abort)")
                self.log_tx.emit("0x18 (soft reset)")
        except Exception as e:
            LOGGER.error("abort: failed to send soft reset: " + str(e))

    def __ser_send(self, ser, data, monitor=True):
        ser.reset_input_buffer()
        ser.write(bytes(data, 'utf8'))
        self.current_line_feedback.emit(data.strip())
        LOGGER.info(">>> " + data.strip())
        if monitor:
            self.log_tx.emit(data.strip())

    def __ser_read(self, ser, monitor=True):
        data = ser.readline().decode("utf-8", errors="replace").strip()
        LOGGER.info("<<< " + str(data))
        if monitor:
            self.log_rx.emit(data)

        return data

    @pyqtSlot()
    def serial_worker(self):

        while True:
            try:
                stay_connected = True
                needs_feedback = False
                feedback_ts = 0

                self.action_connect.get()  # in general - wait until connect button is pressed

                self.strStatus.emit("Connecting...")
                ser = serial.Serial()
                ser.port = str(self.port)
                ser.baudrate = int(self.baudrate)
                ser.timeout = 1

                ser.open()
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                self.ser = ser
                self.abort_flag.clear()

                self.strStatus.emit("Connected")

                while stay_connected:
                    # abort() already drained the queues and reset the
                    # controller; resume normal operation
                    if self.abort_flag.is_set():
                        self.abort_flag.clear()

                    if not self.action_disconnect.empty():
                        self.action_disconnect.get()
                        #self.action_disconnect.clear()
                        stay_connected = False

                    # read bare command
                    if not self.commands.empty():
                        f = self.commands.get()

                        self.__ser_send(ser, f)
                        # TODO: check command and adjust timeout accordingly
                        ser.timeout = 10
                        r = self.__ser_read(ser)
                        self.serReceive.emit([f.strip(), r.strip()])

                        # this part waits for command to be completed
                        LOGGER.debug("wait buffer")
                        while(True):
                            if self.abort_flag.is_set():
                                break

                            retry_cnt = 0
                            ret = ""
                            cmd = "?"
                            backup_timeout = ser.timeout
                            ser.timeout = 0.01
                            r1 = ""

                            while True:
                                if self.abort_flag.is_set():
                                    break

                                self.__ser_send(ser, cmd, monitor=False)
                                status = self.__ser_read(ser, monitor=False)
                                if len(status) > 10:
                                    if (status[0] == "<") and (status[-1] == ">"):
                                        r1 = status
                                        #print(r1)
                                        break

                                if retry_cnt > 0:
                                    LOGGER.info("* Retry count:"+str(retry_cnt))
                                    #if retry_cnt > 100:
                                    #    LOGGER.info("Forced break - reset controller")
                                    #    self.__ser_send(ser, '\x18', monitor=False)
                                    #    break

                                retry_cnt += 1                                

                            ser.timeout = backup_timeout

                            if self.abort_flag.is_set():
                                break

                            try:
                                if r1[0] == "<":
                                        # <Idle|MPos:0.000,0.000,0.000,0.000|Bf:35,254|FS:0,0|Pn:X>
                                        text = r1[1:-1]
                                        feedback_split = text.split("|")
                                        positions = feedback_split[2].split(":")
                                        positions = positions[1]
                                        positions = positions.split(",")
                                        buffers = int(positions[0])
                                        status = feedback_split[0]
                                        self.serFeedback.emit(r1)

                                        # GRBL command buffer = 0
                                        if buffers >= 35:
                                            if status == "Idle":
                                                break
                            except Exception as e:
                                print("Parse error", e)

                    if not self.commands_buffered.empty():
                        f = self.commands_buffered.get()

                        cmd = "?"
                        backup_timeout = ser.timeout
                        ser.timeout = 0.01
                        r1 = ""

                        while(1):
                            if self.abort_flag.is_set():
                                break

                            self.__ser_send(ser, cmd, monitor=False)
                            status = self.__ser_read(ser, monitor=False)
                            if len(status) > 10:
                                if (status[0] == "<") and (status[-1] == ">"):
                                    r1 = status
                                    #print(r1)
                                    #break

                            try:
                                if r1[0] == "<":
                                        # <Idle|MPos:0.000,0.000,0.000,0.000|Bf:35,254|FS:0,0|Pn:X>
                                        text = r1[1:-1]
                                        feedback_split = text.split("|")
                                        positions = feedback_split[2].split(":")
                                        positions = positions[1]
                                        positions = positions.split(",")
                                        buffers = int(positions[0])
                                        status = feedback_split[0]
                                        self.serFeedback.emit(r1)

                                        # GRBL command buffer = 0
                                        if buffers >= 2:
                                            break
                            except Exception as e:
                                print("Parse error", e)

                        ser.timeout = backup_timeout
                        if not self.abort_flag.is_set():
                            self.__ser_send(ser, f)



                    # some commands require certain sequence and testing, these are put into recipes
                    # process these recipes only when main buffer is consumed
                    if not self.action_recipe.empty():
                        rec = self.action_recipe.get()

                        if rec == "version":
                            LOGGER.debug("version")
                            ser.timeout = 2
                            cmd = "$I"
                            self.__ser_send(ser, cmd+'\n')
                            r1 = self.__ser_read(ser)                   # [VER:1.1f-SCE2.20200405:]
                            r2 = self.__ser_read(ser, monitor=False)    # [OPT:VMZHL,35,254]
                            r3 = self.__ser_read(ser, monitor=False)    # [VTEMP]
                            r3 = self.__ser_read(ser, monitor=False)    # ok
                            self.strVersion.emit(r1)

                        if rec == "status1":
                            LOGGER.debug("status")
                            retry_cnt = 0
                            ret = ""
                            cmd = "?"
                            backup_timeout = ser.timeout
                            ser.timeout = 0.5

                            while True:
                                self.__ser_send(ser, cmd, monitor=False)
                                status = self.__ser_read(ser, monitor=False)
                                if len(status) > 10:
                                    if (status[0] == "<") and (status[-1] == ">"):
                                        ret = status
                                        self.serFeedback.emit(ret)
                                        break

                                if retry_cnt > 0:
                                    LOGGER.info("Retry count " + str(retry_cnt))

                                retry_cnt += 1

                            ser.timeout = backup_timeout

                        if rec == "get_param_list":
                            LOGGER.debug("get param list")
                            temp = ser.timeout
                            ser.timeout = 0.5
                            cmd = "$$"
                            self.__ser_send(ser, cmd + '\n')
                            while True:
                                p = self.__ser_read(ser)
                                if (len(p) >= 2) and (p.find("ok") == 0):
                                    break
                            ser.timeout = temp
                            # TODO: return parameters to host

                self.ser = None
                ser.close()
                self.strStatus.emit("Disconnected")

            except Exception as e:
                self.ser = None
                self.strError.emit("Error:"+str(e))
                time.sleep(1)

            self.strStatus.emit("Disconnected")
