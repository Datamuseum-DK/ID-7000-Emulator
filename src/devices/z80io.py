"""Module to provide IO hooks for the Q1 Lite"""

import sys
import utils.misc as misc
import utils.udptx as udp

# Serial Bus Module:    ID-7042 https://datamuseum.dk/bits/30005420
# Timer module:         ID-7015 https://datamuseum.dk/bits/30005410
# 4-port serial module  ID-7012: https://datamuseum.dk/bits/30005408


udptx = udp.UdpTx(port=5007, timestamp=True, nl=True)

class IO:
    def __init__(self, m):
        self.m = m
        self.incb = {}
        self.outcb = {}

        self.keyin = 0

        self.uartcount    = 12
        self.uartbase     = 0x60
        self.uartend      = self.uartbase + self.uartcount * 2
        self.uart_dummyin = 0x00 # NUL
        self.uart_status  = 0x01 # ready ?
        self.uartbuf      = [ '' for x in range(self.uartcount) ]

        self.register_out_cb(0x53, self.handle_53_out)

        self.register_out_cb(0xa1, self.handle_a1_out)
        self.register_out_cb(0xfe, self.handle_fe_out)
        self.register_in_cb( 0xff, self.handle_ff_in)



    ### Functions for registering and handling IO

    def register_out_cb(self, outaddr: int, outfunc):
        self.outcb[outaddr] = outfunc


    def register_in_cb(self, inaddr: int, infunc):
        self.incb[inaddr] = infunc

    #
    ###
    #
    def handle_io_in(self, value) -> int:
        #reg = value >> 8
        inaddr = value & 0xFF

        if self.uartbase <= inaddr < self.uartend:
            return self.handle_uart_in(inaddr)
        
        if inaddr in self.incb:
            return self.incb[inaddr]()

        msg = f'0x{inaddr:02x} - unregistered input address at pc {self.m.pc:04x}, exiting'
        print(msg)
        print()
        sys.exit()
        return 0

    #
    ###
    #
    def handle_io_out(self, outaddr, outval):
        outaddr = outaddr & 0xff

        if self.uartbase <= outaddr < self.uartend:
            self.handle_uart_out(outaddr, outval)
            return

        if outaddr in self.outcb:
            if outval != 0x07 and outaddr != 0x60:
                udptx.send(f'{outaddr:02x} out - {outval:02x} ({misc.ascii(outval)})')
            self.outcb[outaddr](outval)
        else:
            msg = f'0x{outaddr:02x} - unregistered output address, value (0x{outval:02x})'
            print(msg)
            sys.exit()

    ### UART IO
    def handle_uart_in(self, ioaddr):
        
        if ioaddr & 0x1: # odd ioaddrs = status
            #print(f'in(0x{ioaddr:02x}) - status')
            return self.uart_status
        else:            # even ioaddrs = data in
            self.uart_dummyin = self.keyin
            print(f'in(0x{ioaddr:02x}) - data in')
            return self.uart_dummyin


    def handle_uart_out(self, ioaddr, val):
        #print(f'0x{ioaddr:02x}, val')
        if ioaddr & 0x1:
            self.uart_control_out(ioaddr, val)
        else:
            self.uart_data_out(ioaddr, val)


    def uart_data_out(self, ioaddr, val):
        uart_index = (ioaddr - self.uartbase)//2

        if val == 0: # NUL is ignored
            return   
        if val == 7: # BELL is ignored - for now
            return
        
        if 31 < val < 127: # printable ascii
            self.uartbuf[uart_index] += chr(val)
        else:
            self.uartbuf[uart_index] += f'({val})'

        if val == 10: # NL
            print(f'UART out: 0x{ioaddr:02x}', self.uartbuf[uart_index])
            self.uartbuf[uart_index] = ''
            return
       

    def uart_control_out(self, ioaddr, val):
        pass


    ### Non UART IO Handling functions

    def handle_53_out(self, val):
        print(f'out 0x53: {val:3} {misc.ascii(val)}')
        pass


    def handle_a1_out(self, val):
        print(f'out 0xa1: {val:3} {misc.ascii(val)}')
        pass


    def handle_fe_out(self, val):
        print(f'out 0xfe: {val:3} {misc.ascii(val)}')
        pass

    #
    def handle_ff_in(self):
        val = 0xda
        print(f'in  0xff: {val:3} {misc.ascii(val)}')
        return val
