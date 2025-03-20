import socket
import time


class UdpTx:

    def __init__(self, ip='127.0.0.1', port=9901, timestamp=False, nl=False, term=False):
        self.addr = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ts = timestamp
        self.toffset = time.time()
        self.nl = nl
        self.term = term


    def send(self, message: str):
        msg = message
        if self.term:
            print(msg)
        if self.ts:
            msg = f'{time.time()-self.toffset:7.3f}: ' + msg
        if self.nl:
            msg += '\n'
        self.sock.sendto(msg.encode(), self.addr)
