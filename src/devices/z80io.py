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
        self.status = 0x00
        self.keyin = 0

        self.buf60=''

        self.register_out_cb(0x53, self.handle_53_out)

        self.register_in_cb( 0x60, self.handle_60_in)
        self.register_out_cb(0x60, self.handle_60_out)
        self.register_in_cb( 0x61, self.handle_61_in)
        self.register_out_cb(0x61, self.handle_61_out)
        self.register_in_cb( 0x62, self.handle_62_in)
        self.register_out_cb(0x63, self.handle_63_out)
        self.register_in_cb( 0x63, self.handle_63_in)

        self.register_in_cb( 0x64, self.handle_64_in)
        self.register_in_cb( 0x65, self.handle_65_in)
        self.register_out_cb(0x65, self.handle_65_out)
        self.register_in_cb( 0x66, self.handle_66_in)
        self.register_in_cb( 0x67, self.handle_67_in)
        self.register_out_cb(0x67, self.handle_67_out)

        self.register_in_cb( 0x68, self.handle_68_in)
        self.register_in_cb( 0x69, self.handle_69_in)
        self.register_out_cb(0x69, self.handle_69_out)
        self.register_in_cb( 0x6a, self.handle_6a_in)
        self.register_in_cb( 0x6b, self.handle_6b_in)
        self.register_out_cb(0x6b, self.handle_6b_out)

        self.register_in_cb( 0x6c, self.handle_6c_in)
        self.register_in_cb( 0x6d, self.handle_6d_in)
        self.register_out_cb(0x6d, self.handle_6d_out)
        self.register_in_cb( 0x6e, self.handle_6e_in)
        self.register_in_cb( 0x6f, self.handle_6f_in)
        self.register_out_cb(0x6f, self.handle_6f_out)

        self.register_in_cb( 0x70, self.handle_70_in)
        self.register_in_cb( 0x71, self.handle_71_in)
        self.register_out_cb(0x71, self.handle_71_out)
        self.register_in_cb( 0x72, self.handle_72_in)
        self.register_in_cb( 0x73, self.handle_73_in)
        self.register_out_cb(0x73, self.handle_73_out)

        self.register_in_cb( 0x74, self.handle_74_in)
        self.register_in_cb( 0x75, self.handle_75_in)
        self.register_out_cb(0x75, self.handle_75_out)
        self.register_in_cb( 0x76, self.handle_76_in)
        self.register_in_cb( 0x77, self.handle_77_in)
        self.register_out_cb(0x77, self.handle_77_out)

        self.register_out_cb(0xa1, self.handle_a1_out)
        self.register_out_cb(0xfe, self.handle_fe_out)



    ### Functions for registering and handling IO

    def register_out_cb(self, outaddr: int, outfunc):
        self.outcb[outaddr] = outfunc

    def register_in_cb(self, inaddr: int, infunc):
        self.incb[inaddr] = infunc

    def handle_io_in(self, value) -> int:
        #reg = value >> 8
        inaddr = value & 0xFF
        if inaddr in self.incb:
            return self.incb[inaddr]()

        msg = f'0x{inaddr:02x} - unregistered input address at pc {self.m.pc:04x}, exiting'
        print(msg)
        print()
        sys.exit()
        return 0


    def handle_io_out(self, outaddr, outval):
        outaddr = outaddr & 0xff
        if outaddr in self.outcb:
            if outval != 0x07:
                udptx.send(f'{outaddr:02x} out - {outval:02x} ({misc.ascii(outval)})')
            self.outcb[outaddr](outval)
        else:
            msg = f'0x{outaddr:02x} - unregistered output address, value (0x{outval:02x})'
            print(msg)
            sys.exit()


    ### IO Handling functions

    def handle_53_out(self, val):
        print(f'out 0x53: {val:3} {misc.ascii(val)}')
        pass


    def handle_60_in(self):
        val = self.keyin
        print(f'in  0x60: {val:3} {misc.ascii(val)}')
        return val


    def handle_60_out(self, val):
        if misc.isprintable(val):
            self.buf60 += chr(val)
        else:
            if len(self.buf60):
                udptx.send(self.buf60)
                self.buf60 = ''
        print(f'out 0x60: {val:3} {misc.ascii(val)}')


    def handle_61_in(self):
        val = 0x2 # ready ?
        #print(f'in  0x61: {val:3} {misc.ascii(val)}')
        return val

    def handle_61_out(self, val):
        print(f'out 0x61: {val:3} {misc.ascii(val)}')
        pass


    def handle_62_in(self):
        val = self.status
        print(f'in  0x62: {val:3} {misc.ascii(val)}')
        return val


    def handle_63_in(self):
        val = self.status
        print(f'in  0x63: {val:3} {misc.ascii(val)}')
        return val

    def handle_63_out(self, val):
        print(f'out 0x63: {val:3} {misc.ascii(val)}')
        pass


    def handle_64_in(self):
        val = self.status
        print(f'in  0x64: {val:3} {misc.ascii(val)}')
        return val


    def handle_65_in(self):
        val = self.status
        print(f'in  0x65: {val:3} {misc.ascii(val)}')
        return val


    def handle_65_out(self, val):
        print(f'out 0x65: {val:3} {misc.ascii(val)}')
        pass


    def handle_66_in(self):
        val = self.status
        print(f'in  0x66: {val:3} {misc.ascii(val)}')
        return val


    def handle_67_out(self, val):
        print(f'out 0x67: {val:3} {misc.ascii(val)}')
        pass


    def handle_67_in(self):
        val = self.status
        print(f'in  0x67: {val:3} {misc.ascii(val)}')
        return val


    def handle_68_in(self):
        val = self.status
        print(f'in  0x68: {val:3} {misc.ascii(val)}')
        return val

    def handle_69_in(self):
        val = self.status
        print(f'in  0x69: {val:3} {misc.ascii(val)}')
        return val


    def handle_69_out(self, val):
        print(f'out 0x69: {val:3} {misc.ascii(val)}')
        pass


    def handle_6a_in(self):
        val = self.status
        print(f'in  0x6a: {val:3} {misc.ascii(val)}')
        return val


    def handle_6b_in(self):
        val = self.status
        print(f'in  0x6b: {val:3} {misc.ascii(val)}')
        return val


    def handle_6b_out(self, val):
        print(f'out 0x6b: {val:3} {misc.ascii(val)}')
        pass


    def handle_6c_in(self):
        val = self.status
        print(f'in  0x6c: {val:3} {misc.ascii(val)}')
        return val

    def handle_6d_in(self):
        val = self.status
        print(f'in  0x6d: {val:3} {misc.ascii(val)}')
        return val


    def handle_6d_out(self, val):
        print(f'out 0x6d: {val:3} {misc.ascii(val)}')
        pass


    def handle_6e_in(self):
        val = self.status
        print(f'in  0x6e: {val:3} {misc.ascii(val)}')
        return val

    def handle_6f_in(self):
        val = self.status
        print(f'in  0x6f: {val:3} {misc.ascii(val)}')
        return val

    def handle_6f_out(self, val):
        print(f'out 0x6f: {val:3} {misc.ascii(val)}')
        pass


    def handle_70_in(self):
        val = self.status
        print(f'in  0x70: {val:3} {misc.ascii(val)}')
        return val

    def handle_71_in(self):
        val = self.status
        print(f'in  0x71: {val:3} {misc.ascii(val)}')
        return val

    def handle_71_out(self, val):
        print(f'out 0x71: {val:3} {misc.ascii(val)}')
        pass


    def handle_72_in(self):
        val = self.status
        print(f'in  0x72: {val:3} {misc.ascii(val)}')
        return val

    def handle_73_in(self):
        val = self.status
        print(f'in  0x73: {val:3} {misc.ascii(val)}')
        return val

    def handle_73_out(self, val):
        print(f'out 0x73: {val:3} {misc.ascii(val)}')
        pass


    def handle_74_in(self):
        val = self.status
        print(f'in  0x74: {val:3} {misc.ascii(val)}')
        return val

    def handle_75_in(self):
        val = self.status
        print(f'in  0x75: {val:3} {misc.ascii(val)}')
        return val

    def handle_75_out(self, val):
        #print(f'out 0x75: {val:3} {misc.ascii(val)}')
        pass


    def handle_76_in(self):
        val = self.status
        print(f'in  0x76: {val:3} {misc.ascii(val)}')
        return val

    def handle_77_in(self):
        val = self.status
        print(f'in  0x77: {val:3} {misc.ascii(val)}')
        return val


    def handle_77_out(self, val):
        print(f'out 0x77: {val:3} {misc.ascii(val)}')
        pass


    def handle_a1_out(self, val):
        print(f'out 0xa1: {val:3} {misc.ascii(val)}')
        pass


    def handle_fe_out(self, val):
        print(f'out 0xfe: {val:3} {misc.ascii(val)}')
        pass
