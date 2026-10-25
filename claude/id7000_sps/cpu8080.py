"""Intel 8080 core (documented opcodes) for the ID-7000 emulator."""
PARITY=[bin(i).count('1')%2==0 for i in range(256)]

class CPU8080:
    def __init__(self, bus):
        self.bus = bus
        self.a = self.b = self.c = self.d = self.e = self.h = self.l = 0
        self.sp = 0; self.pc = 0
        self.s = self.z = self.ac = self.p =self.cy = False
        self.ie = False
        self.halted=False
        self.cycles=0
        self.pending_irq=None   # RST vector number 0-7

    # --- register pairs
    @property
    def bc(self): return self.b << 8 | self.c
    @bc.setter
    def bc(self,v):
        self.b = v >> 8 & 255
        self.c = v & 255
    @property
    def de(self): return self.d << 8 | self.e
    @de.setter
    def de(self,v):
        self.d = v >> 8 & 255
        self.e = v & 255
    @property
    def hl(self): return self.h << 8 | self.l
    @hl.setter
    def hl(self,v):
        self.h = v >> 8 & 255
        self.l=v&255
    @property
    def f(self):
        return (self.s<<7|self.z<<6|self.ac<<4|self.p<<2|2|self.cy)
    @f.setter
    def f(self,v):
        self.s=bool(v&128)
        self.z=bool(v&64)
        self.ac=bool(v&16)
        self.p=bool(v&4)
        self.cy=bool(v&1)

    def rd(self,a): return self.bus.read(a & 0xFFFF)
    def wr(self,a,v): self.bus.write(a & 0xFFFF, v & 255)
    def fetch(self):
        v = self.rd(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return v
    def fetch16(self):
        lo = self.fetch()
        return lo | self.fetch() << 8
    def push(self,v):
        self.sp=(self.sp-2)&0xFFFF; self.wr(self.sp,v); self.wr(self.sp+1,v>>8)
    def pop(self):
        v=self.rd(self.sp)|self.rd(self.sp+1)<<8; self.sp=(self.sp+2)&0xFFFF; return v

    def getr(self,i):
        return [self.b,self.c,self.d,self.e,self.h,self.l,None,self.a][i] if i!=6 else self.rd(self.hl)
    def setr(self,i,v):
        v&=255
        if i==0:self.b=v
        elif i==1:self.c=v
        elif i==2:self.d=v
        elif i==3:self.e=v
        elif i==4:self.h=v
        elif i==5:self.l=v
        elif i==6:self.wr(self.hl,v)
        else:self.a=v
    def getrp(self,i):
        return [self.bc,self.de,self.hl,self.sp][i]
    def setrp(self,i,v):
        v&=0xFFFF
        if i==0:self.bc=v
        elif i==1:self.de=v
        elif i==2:self.hl=v
        else:self.sp=v

    def szp(self,v):
        v&=255; self.s=bool(v&128); self.z=v==0; self.p=PARITY[v]; return v
    def alu(self,op,v):
        a=self.a
        if op in(1,3) and self.cy: c=1
        else: c=0
        if op in(0,1):
            r=a+v+c; self.ac=((a&15)+(v&15)+c)>15
            self.cy=r>255; self.a=self.szp(r)
        elif op in(2,3,7):
            r=a-v-c; self.ac=not (((a&15)-(v&15)-c)<0)
            self.cy=r<0; r=self.szp(r)
            if op!=7: self.a=r
        elif op==4:
            self.ac=bool((a|v)&8); self.a=self.szp(a&v); self.cy=False
        elif op==5:
            self.a=self.szp(a^v); self.cy=False; self.ac=False
        elif op==6:
            self.a=self.szp(a|v); self.cy=False; self.ac=False
    def cond(self,i):
        return [not self.z,self.z,not self.cy,self.cy,not self.p,self.p,not self.s,self.s][i]

    def interrupt(self,n):
        self.pending_irq=n

    def step(self):
        if self.pending_irq is not None and self.ie:
            n = self.pending_irq
            self.pending_irq = None
            self.ie = False
            self.halted = False
            self.push(self.pc)
            self.pc = n * 8
            self.cycles += 11
            return
        
        if self.halted:
            self.cycles+=4
            return
        
        op = self.fetch()
        self.cycles += 4
        if op==0x76: self.halted=True; return

        if 0x40<=op<0x80:
            self.setr(op>>3&7,self.getr(op&7)); return
        
        if 0x80<=op<0xC0:
            self.alu(op>>3&7,self.getr(op&7)); return
        
        x=op&7; y=op>>3&7
        if op<0x40:
            if x==0: return          # NOP (and undocumented nops)
            if x==1:
                if y&1:
                    r=self.hl+self.getrp(y>>1); self.cy=r>0xFFFF; self.hl=r
                else: self.setrp(y>>1,self.fetch16())
                return
            if x==2:
                if y==0: self.wr(self.bc,self.a)
                elif y==1: self.a=self.rd(self.bc)
                elif y==2: self.wr(self.de,self.a)
                elif y==3: self.a=self.rd(self.de)
                elif y==4:
                    ad=self.fetch16(); self.wr(ad,self.l); self.wr(ad+1,self.h)
                elif y==5:
                    ad=self.fetch16(); self.l=self.rd(ad); self.h=self.rd(ad+1)
                elif y==6: self.wr(self.fetch16(),self.a)
                else: self.a=self.rd(self.fetch16())
                return
            if x==3:
                self.setrp(y>>1,self.getrp(y>>1)+(-1 if y&1 else 1)); return
            if x==4:
                v=self.getr(y)+1; self.ac=(v&15)==0; self.setr(y,self.szp(v)); return
            if x==5:
                v=self.getr(y)-1; self.ac=(v&15)!=15; self.setr(y,self.szp(v)); return
            if x==6: self.setr(y,self.fetch()); return
            if x==7:
                a=self.a
                if y==0: self.cy=bool(a&128); self.a=(a<<1|a>>7)&255
                elif y==1: self.cy=bool(a&1); self.a=(a>>1|a<<7)&255
                elif y==2: c=self.cy; self.cy=bool(a&128); self.a=(a<<1|c)&255
                elif y==3: c=self.cy; self.cy=bool(a&1); self.a=(a>>1|c<<7)&255
                elif y==4:
                    adj=0; cy=self.cy
                    if self.ac or (a&15)>9: adj|=6
                    if cy or a>0x99: adj|=0x60; cy=True
                    self.ac=((a&15)+(adj&15))>15
                    self.a=self.szp(a+adj); self.cy=cy
                elif y==5: self.a=a^255
                elif y==6: self.cy=True
                else: self.cy=not self.cy
                return
        if x==0:
            self.cycles+=1
            if self.cond(y): self.pc=self.pop()
            return
        if x==1:
            if y&1:
                if y==1: self.pc=self.pop()
                elif y==3: self.pc=self.pop()   # undocumented RET
                elif y==5: self.pc=self.hl
                else: self.sp=self.hl
            else:
                v=self.pop(); r=y>>1
                if r==3: self.a=v>>8; self.f=v&255
                else: self.setrp(r,v)
            return
        if x==2:
            ad=self.fetch16()
            if self.cond(y): self.pc=ad
            return
        if x==3:
            if y in(0,1):
                self.pc=self.fetch16()
            elif y==2: self.bus.out(self.fetch(),self.a)
            elif y==3: self.a=self.bus.inp(self.fetch())&255
            elif y==4:
                v=self.rd(self.sp)|self.rd(self.sp+1)<<8
                self.wr(self.sp,self.l); self.wr(self.sp+1,self.h); self.hl=v
            elif y==5: t=self.hl; self.hl=self.de; self.de=t
            elif y==6: self.ie=False
            else: self.ie=True
            return
        if x==4:
            ad=self.fetch16()
            if self.cond(y): self.push(self.pc); self.pc=ad
            return
        if x==5:
            if y&1:
                ad=self.fetch16(); self.push(self.pc); self.pc=ad
            else:
                r=y>>1
                self.push(self.a<<8|self.f if r==3 else self.getrp(r))
            return
        if x==6: self.alu(y,self.fetch()); return
        if x==7: self.push(self.pc); self.pc=y*8; return
