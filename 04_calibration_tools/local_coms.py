import zmq
import time

class LOCAL_COMS_MASTER():
    host_server = "tcp://*"
    port = 5555
    rx_timeout = 1000
    tx_timeout = 1000


    def __init__(self):
        self.context = zmq.Context()
        #self.socket = self.context.socket(zmq.PAIR)
        self.socket = self.context.socket(zmq.REQ)
        self.socket.bind(self.host_server+":"+str(self.port))
        self.socket.setsockopt(zmq.RCVTIMEO, self.rx_timeout)
        self.socket.setsockopt(zmq.SNDTIMEO, self.tx_timeout)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.AFFINITY, 1)

    def msg_text(self, text):
        reply_ok = False
        msg = None
        reply_time = 0

        try:
            t0 = time.time_ns()
            self.socket.send(bytes(text, 'utf-8'))
            msg = self.socket.recv().decode('utf8')
            t1 = time.time_ns()
            reply_ok = True
        except:
            t1 = time.time_ns()
            reply_ok = False

        return msg, reply_ok, (t1-t0)/1000000000


class LOCAL_COMS_NODE():    
    host_client = "tcp://localhost"
    port = 5555
    rx_timeout = 1000
    tx_timeout = 1000


    def __init__(self):
        self.context = zmq.Context()
        #self.socket = self.context.socket(zmq.PAIR)
        self.socket = self.context.socket(zmq.REP)
        self.socket.connect(self.host_client+":"+str(self.port))
        self.socket.setsockopt(zmq.RCVTIMEO, self.rx_timeout)
        self.socket.setsockopt(zmq.SNDTIMEO, self.tx_timeout)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.AFFINITY, 1)


    def get_text(self, block=False):
        msg = None
        rx_ok = False

        try:
            if block:
                msg = self.socket.recv().decode('utf8')
                rx_ok = True
            else:
                msg = self.socket.recv(flags=zmq.NOBLOCK).decode('utf8')
                rx_ok = True
        except Exception as e:
            rx_ok = False

        return msg, rx_ok


    def send_text(self, text):
        tx_ok = False
        
        try:
            self.socket.send(bytes(text, 'utf-8'))
            tx_ok = True
        except:
            tx_ok = False
        
        return tx_ok
