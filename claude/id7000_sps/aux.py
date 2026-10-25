"""Host side of the aux serial link (08h/09h): frame builder + ROM-exact CRC."""
FLAG,ESCB=0x7E,0x40
ESCSET={0x40:(0xF0,0xB0),0x7E:(0xF0,0x8E),0x06:(0xFF,0xF9),0x15:(0xFF,0xEA),0x1B:(0xFF,0xE4)}
def make_tables():
    """Replica of 2556h: reflected CRC-CCITT (8408h) tables, high bytes (49A8) and low bytes (4AA8)."""
    t1=[];t2=[]                      # 49A8h gets the LOW bytes, 4AA8h the HIGH bytes
    for i in range(256):
        v=i
        for _ in range(8): v=(v>>1)^0x8408 if v&1 else v>>1
        t1.append(v&255); t2.append(v>>8)
    return t1,t2
HI,LO=make_tables()
def crc_update(crc,b):
    """Replica of 253Dh: D=crc hi, E=crc lo; idx=b^D; new hi=T1[idx]^E, new lo=T2[idx]."""
    D,E=crc>>8,crc&255; idx=b^D
    return ((HI[idx]^E)<<8)|LO[idx]
def crc(data,init=0):
    c=init
    for b in data: c=crc_update(c,b)
    return c
def stuff(b): return bytes(ESCSET[b]) and bytes([ESCB])+bytes(ESCSET[b]) if b in ESCSET else bytes([b])
def frame(payload,order='hl'):
    body=bytes([len(payload)+1])+bytes(payload)   # LEN counts itself
    c=crc(body)
    tail=bytes([c>>8,c&255]) if order=='hl' else bytes([c&255,c>>8])
    out=bytes([FLAG])
    for b in body+tail: out+=stuff(b)
    return out+bytes([FLAG])

def unframe(b):
    """Split bytes sent by the terminal into frames (undo 40h-stuffing, drop flags)."""
    frames=[];cur=None;i=0
    while i<len(b):
        x=b[i]
        if x==FLAG:
            if cur: frames.append(bytes(cur))
            cur=[]; i+=1; continue
        if cur is None: i+=1; continue
        if x==ESCB and i+2<len(b): cur.append(b[i+1]^b[i+2]); i+=3; continue
        cur.append(x); i+=1
    return frames

class AuxHost:
    """Programming-device side of the aux link. Frame payload = ADDR, N, sub-message*N,
    sub-message = [len][code][args...] (len counts itself)."""
    ADDR=0xFF           # station address = ROM byte 27FFh
    def __init__(self,m,gap=1500): self.m=m; self.gap=gap
    def raw(self,payload):
        f=frame(payload); self.m.aux.tx.clear()
        for b in f: self.m.aux.rx.append(b); self.m.run(self.gap)
        self.m.run(300000)
        fr=unframe(bytes(self.m.aux.tx)); self.m.aux.tx.clear(); return fr
    def connect(self):                    # first frame only triggers the start-up announcement
        return self.raw([self.ADDR,0])
    def command(self,code,*args):
        sub=bytes([2+len(args),code,*args])
        fr=self.raw([self.ADDR,1]+list(sub))
        return self.parse(fr[0]) if fr else None
    @staticmethod
    def parse(f):
        """reply = [LEN][ADDR][02] sub-message* 00 ; returns list of (code, data)"""
        subs=[];i=3
        while i<len(f)-1 and f[i]:
            l=f[i]; subs.append((f[i+1],bytes(f[i+2:i+l]))); i+=l
        return subs
