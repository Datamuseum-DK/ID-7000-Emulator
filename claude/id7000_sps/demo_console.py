"""Boot the IPC/1 image and use the operator dialog on the console."""
from machine import Machine
import sys

class Terminal:

    def __init__(self):
        self.rxbuf = []

    def feed(self, data):
        #print(data)
        self.rxbuf += data

    def render(self):
        out = ""
        i = 0
        while i < len(self.rxbuf):
            ch = self.rxbuf[i]
            if ch == 27:
                #print('rxbuf', self.rxbuf[i:i+10])
                ec = self.rxbuf[i + 1]
                if ec == 43:
                    print('ESC+ - clrscr() ?')
                    i += 1
                    pass
                elif ec == 61:
                    row = self.rxbuf[i+1] - 32
                    col = self.rxbuf[i+2] - 32
                    #print(f'ESC= - row/col {row}/{col}')
                    print(out)
                    out=""
                    i += 3
                elif ec == 84:
                    #print('ESCT - ?')
                    i += 1
                else:
                    #print(f'ESC{chr(ec)} ({ec}) ')
                    #print(self.rxbuf[i:i+4])
                    i += 1
                    sys.exit()
            elif 32<= ch <= 127:
                ach = chr(ch)
                if ach == '[':
                    out += 'Æ'
                elif ach == '\\':
                    out += 'Ø'
                else:
                    out += ach
            elif ch == 0:
                pass
            else:
                print(ch)
                #print(out)
                #out = ""
               
            i += 1
        self.rxbuf = []
        print(out)



def prog1():
    m=Machine()
    t=Terminal()
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





def prog2():
    m=Machine()
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



prog1()
#prog2()