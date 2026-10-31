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



def memdbg(m):
    res = "7300: "
    for i in range(0x7300,0x7304):
        res += f'{m.bus.ram[i]:02x} '
    print(res)
    #print(m.bus.ram[0x7217],m.bus.ram[0x7216],m.bus.ram[0x7215],m.bus.ram[0x7214])
    #print([c for c in m.bus.ram[0x7100:0x7110]])

def prog3(rom):
    m=Machine(rom)
    t=terminal.Terminal()
    memdbg(m)
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
    memdbg(m)

    # a RAM process at 7000h that counts at 7F00h once per 5 timer ticks: it waits on the tick
    # semaphore (4047h) through the OS API entry 00B8h, so the dialog process still gets the CPU.

    # first go at the 32 bit counter loop
    m.bus.ram[0x7200:0x721D]=bytes(
        [0x2a, 0x00, 0x73, 0x23, 0x22, 0x00, 0x73, 0x7c, 0xb5, 0xc2, 0x00, 0x72, 0x2a, 0x02, 0x73, 0x7d,
         0xc6, 0x01, 0x6f, 0x7c, 0xce, 0x00, 0x67, 0x22, 0x02, 0x73, 0xf2, 0x00, 0x72])

    m.type('7200\r',gap=40000)
    m.run(500000)
    memdbg(m)
    m.run(5000000)
    memdbg(m)

    t.feed(m.take())
    m.type('\x1b')
    m.run(500000)
    t.feed(m.take())
    print('=== after ESC (back to the menu) ===')
    t.render()
    memdbg(m)

    for i in range(200):
        m.run(5000)
        memdbg(m)


rom = '../../src/roms/sps_and_funk.bin'
#prog1(rom)
#prog2(rom)
prog3(rom)
