"""Program the PLC runtime over the aux link, then drive digital and analog I/O."""
from machine import Machine, attach_analog
from aux import AuxHost
m=Machine(); adc=attach_analog(m)
for i,a in enumerate(adc): a.values=[(i*8+c)*13+5 for c in range(8)]
m.run(2_000_000); m.take()
h=AuxHost(m)
print('connect          ->',h.connect())
print('version (60h)    ->',h.command(0x60))
print('I/O config (6Dh) ->',h.command(0x6D))
# compiled program (relocatable form): output point 0 := input point 0
prog=bytes([0x21,0x00,0x20,   # LXI H,<segment 2 = input image, offset 0>
            0x7E,             # MOV A,M
            0x21,0x00,0x10,   # LXI H,<segment 1 = output image, offset 0>
            0x77,             # MOV M,A
            0xC9])            # RET
image=bytes(0x7C)+prog        # 8000h-807Bh header, code at 807Ch (USER_ENTRY)
blocks=[image[i:i+32] for i in range(0,len(image),32)]
for n,b in enumerate(blocks):
    r=h.command(0x1E,n,0 if n==len(blocks)-1 else 1,*b)
print('download         -> last block reply',r,'| PLC_STATE =',m.bus.ram[0x4C02])
print('run (20h,1)      ->',h.command(0x20,1),'| PLC_STATE =',m.bus.ram[0x4C02])
print('relocated code   ->',m.bus.ram[0x807C:0x807C+len(prog)].hex(' '),' (LXI operands now point into the images)')
for on in (False,True,False):
    m.set_din(0,on); m.run(300000)
    print('input 0 %-8s -> output 0 = %s   (port 20h=%02X, port 10h=%02X)'%('active' if on else 'inactive',m.dout(0),m.bus.inputs[0x20],m.bus.outputs[0x10]))
r=m.bus.ram
print('analog table @77F0h (module 0, channels 0-7, word = high byte x 128):',[r[0x77F0+4*c+1]|r[0x77F0+4*c+2]<<8 for c in range(8)])
