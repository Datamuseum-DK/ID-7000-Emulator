"""Download examples/fib.asm over the aux link, start it with the P command and watch 7100h."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from machine import Machine
from aux import AuxHost
from asm8080 import assemble

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS_PER_SEC = 400_000                    # the interactive front end's x1 speed

def load_and_start(m, defines=None, priority='3'):
    org, code, syms, _ = assemble(open(os.path.join(HERE, '', 'fib.asm')).read(), defines)
    h = AuxHost(m); h.connect()
    image = bytes(0x7C) + code                 # the download puts byte 0 of the image at 8000h
    assert org == 0x807C
    blocks = [image[i:i + 32] for i in range(0, len(image), 32)]
    for n, b in enumerate(blocks): h.command(0x1E, n, 0 if n == len(blocks) - 1 else 1, *b)
    m.type('P\r'); m.run(200000); m.type(priority + '\r'); m.run(200000); m.type('%04X\r' % org, gap=40000)
    return syms

def text7100(m): return bytes(m.bus.ram[0x7100:0x7105])

def watch(m, seconds, probe=2000):
    """Return [(emulated seconds, text)] each time the text at 7100h changes."""
    seen, last, t0 = [], None, m.steps
    while m.steps - t0 < seconds * STEPS_PER_SEC:
        m.run(probe); t = text7100(m)
        if t != last: seen.append(((m.steps - t0) / STEPS_PER_SEC, t)); last = t
    return seen

if __name__ == '__main__':
    rom = '../../src/roms/sps_and_funk.bin'
    m = Machine(rom); m.TICK = STEPS_PER_SEC // 500          # 500 timer ticks per second
    pulses = []; m.bus.out_handlers[0x0A] = lambda p, v: pulses.append(m.steps)   # clock process heartbeat
    m.run(2_000_000); m.take()
    base0 = len(pulses); m.run(STEPS_PER_SEC); rate_before = len(pulses) - base0
    load_and_start(m)
    m.run(300000); m.take()
    p0 = len(pulses); log = watch(m, 12); rate_after = (len(pulses) - p0) / 12
    print('value changes at 7100h (emulated seconds, text):')
    prev = None
    for t, txt in log:
        print('  %6.2f s   %r' % (t, txt.rstrip(b'\0').decode('latin1')), '' if prev is None else '(+%.2f s)' % (t - prev)); prev = t
    print('clock-process pulses (OUT 0Ah) per second: %d before, %.0f with the Fibonacci process running' % (rate_before, rate_after))
