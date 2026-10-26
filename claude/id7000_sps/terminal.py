from enum import Enum

ESC=0x1B
ROWCOL=0x3D
CLEAR=0x2B
CLRENDL=0x54

class Terminal:
    def __init__(self,rows=24,cols=80):
        self.rows = rows
        self.cols = cols
        self.clear()
        self.state = None
        self.buf = []

    def clear(self):
        self.g = [[' ']*self.cols for _ in range(self.rows)]
        self.r = self.c = 0

    def feed(self,data):
        for b in data:
            if self.state=='esc':
                self.state=None
                if b == CLEAR: self.clear()
                elif b == ROWCOL: self.state='row'
                elif b == CLRENDL:
                    for i in range(self.c,self.cols): self.g[self.r][i]=' '
                continue
            if self.state=='row': self.r=min(max(b-0x20,0),self.rows-1); self.state='col'; continue
            if self.state=='col': self.c=min(max(b-0x20,0),self.cols-1); self.state=None; continue
            if b == ESC: self.state='esc'
            elif b==0x0D: self.c=0
            elif b==0x0A: self.r=min(self.r+1,self.rows-1)
            elif b==0x08: self.c=max(self.c-1,0)
            elif 32<=b<127:
                self.g[self.r][self.c]=chr(b); self.c=min(self.c+1,self.cols-1)

    def render(self,national=True):
        rows=[''.join(r).rstrip() for r in self.g]
        while rows and not rows[-1]: rows.pop()
        txt='\n'.join(rows)
        if national: txt=txt.translate(str.maketrans('[\\]{|}','ÆØÅæøå'))     # Danish 7-bit set
        print(txt)
        return txt