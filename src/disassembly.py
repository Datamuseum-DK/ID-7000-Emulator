#!/usr/bin/env python3

"""Module providing Z80 disassembly functionality"""

import sys
import argparse
import devices.cpu as cpu
import progs.programs as prg


def hexdump(mem, start, end):
    while end - start > 16:
        a = ' '.join([f'{mem.getu8(x):02x}' for x in range(start, start+16)])
        b = ''.join([chr(mem.getu8(x)) if 31 < mem.getu8(x) < 127 else '.' for x in range(start, start+16)])
        print(f'{start:04x}', a, ' ', b)
        start += 16

    a = ' '.join([f'{mem.getu8(x):02x}' for x in range(start, end)])
    b = ''.join([chr(mem.getu8(x)) if 31 < mem.getu8(x) < 127 else '.' for x in range(start, end)])
    print(f'{start:04x}',a, ' ', b)


def disassemble(args, ranges):
    prgobj = prg.proglist[args.program]
    c = cpu.Cpu(prgobj)
    c.reset()

    for x in ranges:
        start = x[0]
        end = x[1]
        text = x[2]

        print(f'\n;{text}')
        c.m.pc = start
        if len(x) ==4:
            hexdump(c.mem, start, end)
            c.m.pc = end
            continue

        while True:
            # Decode the instruction.
            inst_str, ibytes, bytes_str = c.getinst()

            annot = ""

            if c.m.pc in prgobj["pois"]:
                annot = f'{prgobj["pois"][c.m.pc]}'

            print(f'{c.m.pc:04x} {bytes_str:12} ; {inst_str:20} | {annot}')

            c.m.pc += len(ibytes)

            if c.m.pc > end:
                #print('-------------------------------------')
                break




if __name__ == "__main__":

    def auto_int(x):
        return int(x, 0)

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auto", help = "disassemble known ranges", action='store_true')
    parser.add_argument("-l", "--list", help = "showavailable programs", action='store_true')
    parser.add_argument("-s", "--start", help = "start at specified address",
                        type = auto_int, default = 0)
    parser.add_argument("-e", "--end", help = "end at specified address",
                        type = auto_int, default = 0x0500)
    parser.add_argument("--program", help = "name of program to load, see programs.py",
                        type = str, default = "id7ka")

    args = parser.parse_args()

    if args.list:
        for p in prg.proglist:
            print(p)
        sys.exit()

    known_ranges = [[args.start, args.end, 'Custom']]
    if args.auto:
        try:
            known_ranges = prg.proglist[args.program]["known_ranges"]
        except KeyError:
            print(f'please specify known_ranges for {args.program}')
            sys.exit()

    disassemble(args, known_ranges)
