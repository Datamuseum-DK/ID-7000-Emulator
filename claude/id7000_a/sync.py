"""8251 in sync mode at A0/A1 + a stub Cyber host."""
class Sync8251:
    def __init__(self):
        self.state='cmd'; self.mode=None; self.sync=None
        self.rx=[]; self.tx=bytearray(); self.txen=False; self.rxen=False
        self.log=[]
    def ctrl_w(self,v):
        self.log.append(('ctl',v))
        if self.state=='mode': self.mode=v; self.state='sync' if (v&3)==0 else 'cmd'; return
        if self.state=='sync': self.sync=v; self.state='cmd'; return
        if v&0x40: self.state='mode'; self.txen=self.rxen=False; return   # internal reset
        self.txen=bool(v&1); self.rxen=bool(v&4)
    def status(self): return (1 if self.txen else 0)|(2 if self.rx else 0)|(4 if self.txen else 0)
    def data_r(self): return self.rx.pop(0) if self.rx else 0
    def data_w(self,v): self.tx.append(v)

SOH,STX,ETX,ENQ,SYN=1,2,3,5,0x16
def frame(addr,dev,ctl,data=b''):
    body=bytes([addr,dev,ctl])+data+bytes([ETX])
    l=0xFE
    for b in body: l^=b
    return bytes([SYN,SYN,SYN,SOH])+body+bytes([l&0x7F])

def attach(m,s):
    """Wire the sync 8251 into machine m and make Machine.run raise RST 4 while TxEN."""
    b=m.bus
    b.in_handlers[0xA0]=lambda p:s.data_r(); b.in_handlers[0xA1]=lambda p:s.status()
    b.out_handlers[0xA0]=lambda p,v:s.data_w(v); b.out_handlers[0xA1]=lambda p,v:s.ctrl_w(v)
    def run(n):
        c=m.cpu
        for _ in range(n):
            c.step(); m.steps+=1
            if m.steps%m.TICK==0: c.interrupt(3)
            elif s.txen and m.steps%64==0 and c.pending_irq is None: c.interrupt(4)
    m.run=run

class CyberHost:
    """Stub host: sends frames to the terminal and decodes its replies."""
    def __init__(self,m,s): self.m=m; self.s=s
    def _send(self,f,steps=3000):
        for byte in f:
            self.s.rx.append(byte); self.m.cpu.interrupt(2); self.m.run(steps)
        self.m.run(300000)
    def exchange(self,addr,dev,ctl,data=b''):
        self.s.tx.clear(); self._send(frame(addr,dev,ctl,data))
        return self.parse(bytes(self.s.tx))
    @staticmethod
    def parse(tx):
        i=tx.find(b'\x01')
        if i<0: return None
        body=tx[i+1:]; e=body.find(b'\x03')
        if e<0: return None
        return dict(addr=body[0],dev=body[1],ctl=body[2],data=body[3:e],lrc=body[e+1])
    def poll(self,channel=0,dev=0x60): return self.exchange(0x70+channel,dev,ENQ)
    def say(self,channel,text,ctl=0x11,end=b'\x1bB',dev=0x60):
        return self.exchange(0x70+channel,dev,ctl,text+end)
