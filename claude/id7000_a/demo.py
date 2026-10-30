
from machine import Machine

rom_file='../../src/roms/ID7K0018/board5_eproms_0_to_6.bin'
m=Machine(rom_file, trace_io=True)
m.boot()

for line in [":STATUS", ":HP,ON", ":FOO", "HELLO", ":STATUS"]:
    m.type(line+"\r")
    m.run(400000)
    #print(f'{line!r:12} ->',m.take_tx().replace(b'\x00',b'').decode(errors='replace').replace('\r\n','|'))
    print(f'{line!r:12} ->',m.take_tx().replace(b'\x00',b'').decode(errors='replace'))

#print(m.bus.iolog)
