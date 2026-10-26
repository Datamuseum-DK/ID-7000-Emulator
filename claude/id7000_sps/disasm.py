"""Small 8080 disassembler used by the interactive debugger."""
R=['B','C','D','E','H','L','M','A']; RP=['B','D','H','SP']; RPP=['B','D','H','PSW']
CC=['NZ','Z','NC','C','PO','PE','P','M']
ALU=['ADD','ADC','SUB','SBB','ANA','XRA','ORA','CMP']
ALUI=['ADI','ACI','SUI','SBI','ANI','XRI','ORI','CPI']
def disasm(read,a):
    """read(addr)->byte. Returns (length, text)."""
    o=read(a); w1=lambda:read((a+1)&0xFFFF); w16=lambda:read((a+1)&0xFFFF)|read((a+2)&0xFFFF)<<8
    if o==0x76: return 1,'HLT'
    if 0x40<=o<0x80: return 1,'MOV %s,%s'%(R[(o>>3)&7],R[o&7])
    if 0x80<=o<0xC0: return 1,'%s %s'%(ALU[(o>>3)&7],R[o&7])
    x=o&7;y=(o>>3)&7
    if o<0x40:
        if o==0: return 1,'NOP'
        if o==0x20: return 1,'RIM'
        if o==0x30: return 1,'SIM'
        if x==1: return (1,'DAD %s'%RP[y>>1]) if y&1 else (3,'LXI %s,%04XH'%(RP[y>>1],w16()))
        if x==2:
            if y<4: return 1,['STAX B','LDAX B','STAX D','LDAX D'][y]
            return 3,['SHLD','LHLD','STA','LDA'][y-4]+' %04XH'%w16()
        if x==3: return 1,('DCX ' if y&1 else 'INX ')+RP[y>>1]
        if x==4: return 1,'INR '+R[y]
        if x==5: return 1,'DCR '+R[y]
        if x==6: return 2,'MVI %s,%02XH'%(R[y],w1())
        if x==7: return 1,['RLC','RRC','RAL','RAR','DAA','CMA','STC','CMC'][y]
        return 1,'DB %02XH'%o
    if x==0: return 1,'R'+CC[y]
    if x==1:
        if y&1: return 1,['RET','RET','PCHL','SPHL'][y>>1]
        return 1,'POP '+RPP[y>>1]
    if x==2: return 3,'J%s %04XH'%(CC[y],w16())
    if x==3:
        if y in(0,1): return 3,'JMP %04XH'%w16()
        if y==2: return 2,'OUT %02XH'%w1()
        if y==3: return 2,'IN %02XH'%w1()
        return 1,['','','','','XTHL','XCHG','DI','EI'][y]
    if x==4: return 3,'C%s %04XH'%(CC[y],w16())
    if x==5:
        if y&1: return (3,'CALL %04XH'%w16()) if y==1 else (1,'DB %02XH'%o)
        return 1,'PUSH '+RPP[y>>1]
    if x==6: return 2,'%s %02XH'%(ALUI[y],w1())
    return 1,'RST %d'%y
