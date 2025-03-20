#!/usr/bin/env python3

import sys
import argparse
import devices.cpu as c
import devices.kbd as kbd
import match
import devices.z80io as z80io
import progs.programs as prg
import utils.misc as misc
import utils.udptx as udp
from timeit import default_timer as timer

'''
    Q1 Emulator
'''

udptx = udp.UdpTx(port=5009, timestamp=True, nl=True)

class Emulator:

    def on_write(self, address, value):
        assert value < 256
        assert address < 65536
        if address < 0x1C00: #
            #print(f"write to ROM (0x{address:04x})")
            #print(f"write to ROM (0x{address:04x}) error, exiting ...")
            print(f"write to ROM (0x{address:04x}), val {value} pc {self.cpu.m.pc:04x} warning, no effect ...")
            #self.cpu.exit()
            #self.cpu.m.memory[address] = 0xAA
            return

        if 0x7000 < address < 0x7004:
            print('FAKE INVALID WRITE TO RAM')
            newval = (value + 1) & 0xff
            self.cpu.m.memory[address] = newval
            return

        self.cpu.m.memory[address] = value


    def __del__(self):
        pass


    def __init__(self, args):
        self.args = args
        self.prgobj = prg.proglist[args.program]
        self.funcs = self.prgobj["funcs"]

        self.cpu = c.Cpu(self.prgobj)
        self.defaultsteps = 1
        self.steps = self.defaultsteps

        self.io = z80io.IO(self.cpu.m)

        self.key = kbd.Key()
        self.kc = kbd.KeyboardCodes()

        self.cpu.reset()
        self.cpu.m.set_write_callback(self.on_write)
        self.cpu.m.set_input_callback(self.io.handle_io_in)
        self.cpu.m.set_output_callback(self.io.handle_io_out)

        self.stoppc = 0x1ffff
        if "stop" in self.prgobj:
            self.stoppc = self.prgobj["stop"]

        self.icount = 0
        if self.args.hexdump:
            self.cpu.mem.hexdump(0x2000, 0xFFFF - 0x2000) # dump RAM part of memory

    ints = {0: 0x0000, 2: 0x0010, 3:0x0018, 4:0x0020, 6:0x0030, 7:0x0038 }

    # to be improved - for now assume serial in on 0x60
    def interrupt(self, intnum, data):
        self.io.keyin = data
        oldpc = self.cpu.m.pc
        self.cpu.m.sp -= 2
        self.cpu.mem.writeu16(self.cpu.m.sp, oldpc)
        self.cpu.m.pc = self.ints[intnum]
        assert self.cpu.m.halted
        self.cpu.m.halted = False


    def kbd_input(self):
        kc = self.kc
        if self.key.kbhit():
            ch = ord(self.key.getch())
            if misc.isprintable(ch):
                print(f'{chr(ch)}')
            else:
                print(f'{ch}')

            if ch == 0x222b:       # opt-b -> hexdump
                self.cpu.mem.hexdump(0x4200, 0x0400)
            elif ch == 8224: # opt-t
                args.decode = not args.decode
                if args.decode:
                    self.steps = 1
                else:
                    self.steps = self.defaultsteps
            else:
                pass
                #self.interrupt(6, ch)



    # Fake a keyboard interrupt, seems to work, but the Q1 interrupt model
    # is currently not well understood
    def int38(self, ch):
        self.io.keyin = 0x02
        oldpc = self.cpu.m.pc
        self.cpu.m.sp -= 2
        self.cpu.mem.writeu16(self.cpu.m.sp, oldpc)
        self.cpu.m.pc = 0x38


    # Main emulator loop
    def run(self):
        args = self.args
        io = self.io
        cpu = self.cpu
        kc = self.kc
        n = self.steps

        tstart = timer()
        while True:
            # First take care of timer 'interrupt'
            tend = timer()
            if (tend - tstart) > 1.0:
                tstart = timer()
                io.timeout = True

            # Prepare for next instruction(s)
            pc = cpu.m.pc
            self.icount += 1

            # Check for halt condition (number of instructions or invalid
            # address )
            if self.icount >= args.stopafter or pc > 65530:
                print(f'exiting ... {self.icount}')
                for l in cpu.bt:
                    print(l)
                sys.exit()

            # Print info about known functions
            if pc in self.funcs and args.decode:
                print(f'; {self.funcs[pc]}')


            if pc == args.poi and args.decode: # PC of interest
                print('\n<<<<< pc of interest >>>>>\n')

            # Decode the instruction.
            inst_str, _, bytes_str = cpu.getinst()
            inst_str2 = cpu.decodestr(inst_str, bytes_str)
            annot = ""
            if cpu.m.pc in self.prgobj["pois"]:
                annot = f'{self.prgobj["pois"][cpu.m.pc]}'
            if args.decode:
                print(inst_str2, annot)


            if self.icount % args.dumpfreq == 0 and args.hexdump:
                cpu.mem.hexdump(0x2000, 0x10000 - 0x2000) # dump RAM part of memory

            # Debugging PL/1 programs (experimental)
            # if cpu.m.pc > 0x1880:
            #     self.pl1_debug()

            # main cpu emulation step
            cpu.step(self.steps) # actual emulation of the next n instruction(s)

            # Handle breakpoints
            if pc in (args.breakpoint, self.stoppc):
                print(f'\n<<<< BREAKPOINT at 0x{pc:04x} >>>>\n')
                #cpu.e(False, True, False)
                cpu.exit()

            # Handle trigger conditions
            if args.trigger == pc:
                print(f'\n<<<< TRIGGER at 0x{pc:04x} >>>>\n')
                args.decode = True
                io.verbose = True
                cpu.info()

            # Handle (JDC) program halt
            if pc ==0x4cb and args.program == 'jdc':
                print("<STOP>")

            # Handle occasional keyboard input
            if (self.icount % 1000) == 0: # int_disabled check?
                self.kbd_input()



if __name__ == "__main__":

    def auto_int(x):
        return int(x, 0)

    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--breakpoint", help = "stop on BP, hexdump and backtrace",
        type = auto_int, default = 0x1FFFF)
    parser.add_argument("-t", "--trigger", help = "start decode at trigger address",
        type = auto_int, default = 0x1FFFF)
    parser.add_argument("-s", "--stopafter", help = "stop after N instructions",
        type = int, default = -1)
    parser.add_argument("-p", "--poi", help = "Point of interest (PC)",
                        type = auto_int, default = 0x1ffff)
    parser.add_argument("--dumpfreq", help = "Hexdump every N instruction",
                        type = int, default = 256)
    parser.add_argument("-x", "--hexdump", help = "Toggle hexdump", action='store_true')
    parser.add_argument("-d", "--decode", help = "Decode instructions", action='store_true')
    parser.add_argument("-l", "--list", help = "show available programs",
        action='store_true')
    parser.add_argument("--program", help = "name of program to load, see programs.py",
                        type = str, default = "id7ka")


    args = parser.parse_args()
    if args.stopafter == -1:
        args.stopafter = 1000000000

    if args.list:
        for p in prg.proglist:
            print(p)
        sys.exit()

    emulator = Emulator(args)
    emulator.run()
