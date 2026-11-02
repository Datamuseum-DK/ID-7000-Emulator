"""Download examples/fib_plc.asm over the aux link and start it with aux command 20h 01 (no P command).

    python3 demo_fib_plc.py [seconds]          # emulated seconds to watch, default 12
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from machine import Machine, attach_analog
from aux import AuxHost
from asm8080 import assemble

HERE = os.path.dirname(os.path.abspath(__file__))
TICKS_PER_SEC = 500                       # must match TICKS_PER_SEC in fib_plc.asm
STEPS_PER_SEC = 400_000                   # the interactive front end's x1 speed

rom = '../../src/roms/sps_and_funk.bin'
def main(seconds=12):
    org, code, _, _ = assemble(open(os.path.join(HERE, 'examples', 'fib_plc.asm')).read())
    assert org == 0x807C
    name = b'FIB-PLC\0'
    image = name + bytes(0x7C - len(name)) + code          # 7Ch-byte header with the program name
    m = Machine(rom); attach_analog(m)
    m.TICK = STEPS_PER_SEC // TICKS_PER_SEC                # timer ticks per emulated second
    m.run(2_000_000); m.take()
    h = AuxHost(m); h.connect()                            # the first frame only starts the link
    blocks = [image[i:i + 32] for i in range(0, len(image), 32)]
    for n, b in enumerate(blocks):
        r = h.command(0x1E, n, 0 if n == len(blocks) - 1 else 1, *b)   # last block: more = 0
    print('download  ->', r, '| PLC_STATE =', m.bus.ram[0x4C02], '(1 = loaded)')
    r = h.command(0x20, 1)
    print('run 20h 1 ->', r, '| PLC_STATE =', m.bus.ram[0x4C02], '(3 = running)')
    last, prev = None, None
    for s in range(int(seconds * STEPS_PER_SEC / 1000)):
        m.run(1000)
        t = bytes(m.bus.ram[0x7100:0x7105])
        # the four digits are written one after another: accept a value only when it is stable (not mid-update)
        if t == prev and t != last and t[4] == 0 and all(chr(c) in '0123456789ABCDEF' for c in t[:4]):
            print('%5.1f s  7100h = %s' % (s * 1000 / STEPS_PER_SEC, t[:4].decode())); last = t
        prev = t

if __name__ == '__main__':
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 12)
