"""ID-7000 IPC/1 + SPC/1 machine (SPS_1-5 + FUNK_1-3 image).

Memory: ROM 0000-3FFF (16 KB), everything above is RAM (the firmware uses 4000-81xx).
I/O (inferred): 60/61 console 8251, 08/09 aux 8251, 10-17 digital out, 20-33 digital in
(active low), 40-4B six analog modules, FF timer ack, FE system latch.
Interrupts: RST1 timer, RST2 aux UART, RST4 console UART."""
from cpu8080 import CPU8080
import os

ROM_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sps_funk_image.bin')

class USART:
    """Minimal 8251. Received bytes wait in a FIFO and enter the one-byte holding register at the
    serial character rate (Machine.CHAR_STEPS steps apart), so a fast burst of keys is not lost."""
    def __init__(self):
        self.rx=[]; self.tx=bytearray(); self.log=[]; self.state='cmd'; self.mode=None
        self.txen=False; self.rxen=False; self.hold=None; self.next_at=0; self.clock=lambda:0; self.gap=420
    def ctrl_w(self,v):
        self.log.append(v)
        if self.state=='mode': self.mode=v; self.state='cmd'; return
        if v&0x40: self.state='mode'; self.txen=self.rxen=False; return
        self.txen=bool(v&1); self.rxen=bool(v&4)
    def status(self): return 0x05|(0x02 if self.hold is not None else 0)
    def data_r(self):
        v=self.hold
        if v is None: return 0
        self.hold=None; self.next_at=self.clock()+self.gap; return v
    def data_w(self,v): self.tx.append(v)
    def pump(self):
        if self.hold is None and self.rx and self.clock()>=self.next_at: self.hold=self.rx.pop(0)
    @property
    def rdy(self): return self.hold is not None

class Bus:
    def __init__(self,rom,trace_io=False):
        self.rom=rom; self.ram=bytearray(0x10000)
        self.trace_io=trace_io; self.iolog=[]; self.in_handlers={}; self.out_handlers={}
        self.inputs=bytearray(256); self.outputs=bytearray(256)
    def read(self,a): return self.rom[a] if a<len(self.rom) else self.ram[a]
    def write(self,a,v):
        if a>=len(self.rom): self.ram[a]=v
    def inp(self,p):
        h=self.in_handlers.get(p); v=h(p) if h else self.inputs[p]
        if self.trace_io: self.iolog.append(('IN',p,v))
        return v
    def out(self,p,v):
        if self.trace_io: self.iolog.append(('OUT',p,v))
        self.outputs[p]=v
        h=self.out_handlers.get(p)
        if h: h(p,v)

class Machine:
    TICK=4000
    CHAR_STEPS=420            # about 1 ms per character at 9600 baud and 400k steps/s
    def __init__(self,rom_file, trace_io=False):
        self.rom=open(rom_file,'rb').read()
        self.bus=Bus(self.rom,trace_io); self.cpu=CPU8080(self.bus); self.steps=0; self.ticks=0; self.tick_due=False
        self.con=USART(); self.aux=USART()
        for u in (self.con,self.aux): u.clock=lambda:self.steps; u.gap=self.CHAR_STEPS
        b=self.bus
        b.in_handlers[0x60]=lambda p:self.con.data_r(); b.in_handlers[0x61]=lambda p:self.con.status()
        b.out_handlers[0x60]=lambda p,v:self.con.data_w(v); b.out_handlers[0x61]=lambda p,v:self.con.ctrl_w(v)
        b.in_handlers[0x08]=lambda p:self.aux.data_r(); b.in_handlers[0x09]=lambda p:self.aux.status()
        b.out_handlers[0x08]=lambda p,v:self.aux.data_w(v); b.out_handlers[0x09]=lambda p,v:self.aux.ctrl_w(v)
        b.in_handlers[0xFF]=lambda p:0
        for p in range(0x20,0x34): b.inputs[p]=0xFF        # all digital inputs inactive
    def run(self,n):
        c=self.cpu
        for _ in range(n):
            c.step(); self.steps+=1
            if self.steps%12==0: self.con.pump(); self.aux.pump()
            if self.steps%self.TICK==0: self.tick_due=True          # the tick is latched until it can be taken
            if c.pending_irq is None and c.ie:
                if self.tick_due: c.interrupt(1); self.ticks+=1; self.tick_due=False                  # timer tick
                elif self.steps%24==0 and (self.con.rdy and self.con.rxen or self.con.txen): c.interrupt(4)   # console
                elif self.steps%24==12 and (self.aux.rdy and self.aux.rxen or self.aux.txen): c.interrupt(2)  # aux line
    # ---- console helpers
    def type(self,text,gap=60000):
        for ch in text: self.con.rx.append(ord(ch)); self.run(gap)
    # ---- digital I/O helpers (points are numbered like the images: port bit = point % 8)
    def set_din(self,point,active=True):
        port=0x20+point//8; bit=1<<(point%8)
        v=self.bus.inputs[port]
        self.bus.inputs[port]=(v&~bit) if active else (v|bit)     # active low
    def dout(self,point): return bool(self.bus.outputs[0x10+point//8]>>(point%8)&1)
    def take(self):
        b=bytes(self.con.tx); self.con.tx.clear(); return b

class AdcModule:
    """One analog input module (ports base, base+1), 8 mux channels, 10-bit result (inferred from 2087h-20E8h)."""
    def __init__(self,base,bus):
        self.base=base; self.mux=0; self.ready=False; self.values=[0]*8; self.cur=0
        bus.out_handlers[base]=self.set_mux
        bus.out_handlers[base+1]=self.start
        bus.in_handlers[base]=lambda p:(self.cur>>2)&0xFF           # high 8 bits
        bus.in_handlers[base+1]=lambda p:((self.cur&3)<<6)|(0x10 if self.ready else 0)  # low 2 bits in 7:6, bit4 = data ready
    def set_mux(self,p,v): self.mux=v&7; self.ready=False
    def start(self,p,v): self.cur=self.values[self.mux]&0x3FF; self.ready=True

def attach_analog(m):
    """6 analog modules at 40h/41h .. 4Ah/4Bh"""
    m.adc=[AdcModule(0x40+2*i,m.bus) for i in range(6)]
    return m.adc
