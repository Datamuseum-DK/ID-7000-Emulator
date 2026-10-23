"""ID-7000 board-5 machine: memory map, I/O devices, timer, console API.

Memory map (inferred from ROM tracing):
  0000-1BFF  ROM (EPROMs 0-6, 1 KB each; 1A30 holds the checksum byte)
  4000-BFFF  RAM (self-test exercises exactly this range)
I/O map (inferred):
  50-53  8255 PPI  (port A data out, port B status in, PC7 strobe) - printer?
  60-77  12 x 8251 USART, data on even port, control/status on odd port
  A0/A1  8251 in sync mode (SYN=16h) - Cyber link
  FE     system control latch (7Eh written at end of boot)
  FF     read in the RST 3 timer handler (tick acknowledge)
Interrupts: RST2=sync RX, RST3=timer tick, RST4=sync TX, RST6=async RX.
"""
from cpu8080 import CPU8080
ROM_FILE='../src/roms/ID7K0018/board5_eproms_0_to_6.bin'
#ROM_FILE='../src/roms/sps_and_funk.bin'

class USART:
    """Minimal 8251: status bit0 TxRDY, bit1 RxRDY, bit2 TxEMPTY."""
    def __init__(self): self.rx=[]; self.tx=bytearray()
    def read_data(self): return self.rx.pop(0) if self.rx else 0
    def status(self): return 0x05|(0x02 if self.rx else 0)
    def write_data(self,v): self.tx.append(v)

class Bus:
    def __init__(self,rom,trace_io=False):
        self.rom=rom; self.ram=bytearray(0x10000)
        self.trace_io=trace_io; self.iolog=[]
        self.in_handlers={}; self.out_handlers={}
    def read(self,a):
        return self.rom[a] if a<len(self.rom) else self.ram[a]
    def write(self,a,v):
        if a>=len(self.rom): self.ram[a]=v
    def inp(self,p):
        h=self.in_handlers.get(p); v=h(p) if h else 0
        if self.trace_io: self.iolog.append(('IN',p,v))
        return v
    def out(self,p,v):
        if self.trace_io: self.iolog.append(('OUT',p,v))
        h=self.out_handlers.get(p)
        if h: h(p,v)

class Machine:
    TICK=2500                      # CPU steps per RST 3 tick (guess)
    
    def __init__(self,trace_io=False):
        self.rom=open(ROM_FILE,'rb').read()
        self.bus=Bus(self.rom,trace_io); self.cpu=CPU8080(self.bus)
        self.ch=[USART() for _ in range(12)]; self.steps=0
        for n,u in enumerate(self.ch):
            d=0x60+2*n
            self.bus.in_handlers[d]=lambda p,u=u:u.read_data()
            self.bus.in_handlers[d+1]=lambda p,u=u:u.status()
            self.bus.out_handlers[d]=lambda p,v,u=u:u.write_data(v)
        self.bus.in_handlers[0xA1]=lambda p:0x05
        self.bus.in_handlers[0x51]=lambda p:0x00

    def run(self,n):
        c=self.cpu
        for _ in range(n):
            c.step(); self.steps+=1
            if self.steps%self.TICK==0: c.interrupt(3)

    def boot(self):
        self.run(900000); self.run(500000); self.take_tx()

    def type(self,text,ch=0,gap=40000):
        for s in text:
            self.ch[ch].rx.append(ord(s)); self.cpu.interrupt(6); self.run(gap)

    def take_tx(self,ch=0):
        b=bytes(self.ch[ch].tx); self.ch[ch].tx.clear(); return b
