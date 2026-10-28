"""Boot the IPC/1 image and use the operator dialog on the console."""
from machine import Machine
import terminal
import sys


def prog1(rom):
    m=Machine(rom)
    t=terminal.Terminal()
    m.run(2_000_000)
    t.feed(m.take())
    print('=== screen after boot ===')
    t.render()

    m.type('P\r')
    m.run(300000)
    m.type('3\r')
    m.run(300000)
    t.feed(m.take())
    print('=== after P and priority 3 ===')
    t.render()


    c1=m.bus.ram[0x7F00]
    m.run(5000000)
    c2=m.bus.ram[0x7F00]
    print('process started at 7000h, counter at 7F00h: %d -> %d (running: %s)'%(c1,c2,c1!=c2))

    # a RAM process at 7000h that counts at 7F00h once per 5 timer ticks: it waits on the tick
    # semaphore (4047h) through the OS API entry 00B8h, so the dialog process still gets the CPU.

    m.bus.ram[0x7000:0x700D]=bytes([0x21,0x00,0x7F,      # LXI H,7F00
                                    0x34,                # INR M
                                    0x01,0x47,0x40,      # LXI B,4047h  (SEM_TICK5)
                                    0xCD,0xB8,0x00,      # CALL 00B8h   (sem_wait)
                                    0xC3,0x03,0x70])     # JMP 7003h

    m.type('7000\r',gap=40000)
    m.run(500000)
    c1=m.bus.ram[0x7F00]
    m.run(5000000)
    c2=m.bus.ram[0x7F00]
    print('process started at 7000h, counter at 7F00h: %d -> %d (running: %s)'%(c1,c2,c1!=c2))
    t.feed(m.take())
    m.type('\x1b')
    m.run(500000)
    t.feed(m.take())
    print('=== after ESC (back to the menu) ===')
    t.render()

    m.run(500000)
    c1=m.bus.ram[0x7F00]
    m.run(5000000)
    c2=m.bus.ram[0x7F00]
    print('process counter at 7F00h: %d -> %d (running: %s)'%(c1,c2,c1!=c2))



def prog2(rom):
    m=Machine(rom)
    t=Terminal()
    m.run(2_000_000)
    t.feed(m.take())
    print('=== screen after boot ===')
    t.render()

    m.type('P\r')
    m.run(300000)
    t.feed(m.take())
    t.render()

    m.type('9\r')
    m.run(300000)
    t.feed(m.take())
    t.render()

    m.type('P\r')
    m.run(300000)
    t.feed(m.take())
    t.render()



def fibdbg(m):
    print([c for c in m.bus.ram[0x7100:0x7110]])

def prog3(rom):
    m=Machine(rom)
    t=terminal.Terminal()
    fibdbg(m)
    m.run(2_000_000)
    t.feed(m.take())
    print('=== screen after boot ===')
    t.render()

    m.type('P\r')
    m.run(300000)
    m.type('3\r')
    m.run(300000)
    t.feed(m.take())
    print('=== after P and priority 3 ===')
    t.render()



    m.run(5000000)
    fibdbg(m)

    # a RAM process at 7000h that counts at 7F00h once per 5 timer ticks: it waits on the tick
    # semaphore (4047h) through the OS API entry 00B8h, so the dialog process still gets the CPU.

    m.bus.ram[0x7000:0x7099]=bytes(
        [0x21, 0x00, 0x00, 0x22, 0x0e, 0x81, 0x23, 0x22, 0x10, 0x81, 0xaf, 0x32, 0x14, 0x81, 0x2a, 0x0e,
            0x81, 0xcd, 0xc7, 0x80, 0xcd, 0xe9, 0x80, 0xcd, 0x99, 0x80, 0xc3, 0x8a, 0x80, 0x3a, 0x14, 0x81,
            0xb7, 0xca, 0xaf, 0x80, 0xaf, 0x32, 0x14, 0x81, 0x21, 0x00, 0x00, 0x22, 0x0e, 0x81, 0x23, 0x22,
            0x10, 0x81, 0xc9, 0x2a, 0x0e, 0x81, 0xeb, 0x2a, 0x10, 0x81, 0x22, 0x0e, 0x81, 0x19, 0xd2, 0xc3,
            0x80, 0x3e, 0x01, 0x32, 0x14, 0x81, 0xc9, 0x22, 0x10, 0x81, 0xc9, 0x11, 0x00, 0x71, 0x7c, 0xcd,
            0xd5, 0x80, 0x7d, 0xcd, 0xd5, 0x80, 0xaf, 0x12, 0xc9, 0xf5, 0x0f, 0x0f, 0x0f, 0x0f, 0xcd, 0xde,
            0x80, 0xf1, 0xe6, 0x0f, 0xc6, 0x90, 0x27, 0xce, 0x40, 0x27, 0x12, 0x13, 0xc9, 0x2a, 0x00, 0x40,
            0x11, 0xfa, 0x00, 0x19, 0x22, 0x12, 0x81, 0x01, 0x47, 0x40, 0xcd, 0xb8, 0x00, 0x01, 0x47, 0x40,
            0xcd, 0xb2, 0x00, 0x2a, 0x00, 0x40, 0xeb, 0x2a, 0x12, 0x81, 0x7b, 0x95, 0x7a, 0x9c, 0xfa, 0xf3,
            0x80, 0xc9, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00])



    m.type('7000\r',gap=40000)
    m.run(500000)
    fibdbg(m)
    m.run(5000000)
    fibdbg(m)

    t.feed(m.take())
    m.type('\x1b')
    m.run(500000)
    t.feed(m.take())
    print('=== after ESC (back to the menu) ===')
    t.render()
    fibdbg(m)

    m.run(500000)
    fibdbg(m)
    m.run(5000000)
    fibdbg(m)




rom = '../../src/roms/sps_and_funk.bin'
prog1(rom)
#prog2(rom)
#prog3(rom)
