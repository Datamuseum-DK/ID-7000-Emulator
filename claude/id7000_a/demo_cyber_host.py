"""Interactive ID-7000 + simulated Cyber: type lines, the terminal sends them
to the host on the next poll, the host answers on the terminal display."""
from machine import Machine
from sync import Sync8251, attach
from cyber import CyberHost

rom_file = '../../src/roms/ID7K0018/board5_eproms_0_to_6.bin'
show = lambda b: b.replace(b'\x00', b'').decode(errors='replace')

m = Machine(rom_file); s = Sync8251(); attach(m, s); m.boot()
#host = CyberHost(m, s, log=lambda *a: print('  [link]', *a))
host = CyberHost(m, s)
host.service(); print(show(m.take_tx()))       # bring the link up

while True:
    try: line = input('> ')
    except EOFError: break
    m.type(line + '\r'); m.run(500000)
    print(show(m.take_tx()), end='')
    host.service()
    print(show(m.take_tx()))
