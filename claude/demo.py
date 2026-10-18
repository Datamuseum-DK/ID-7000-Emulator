
from machine import Machine

m=Machine(trace_io=True)
m.boot()

for line in [":STATUS", ":HP,ON", ":FOO", "HELLO", ":STATUS"]:
    m.type(line+"\r")
    m.run(400000)
    #print(f'{line!r:12} ->',m.take_tx().replace(b'\x00',b'').decode(errors='replace').replace('\r\n','|'))
    print(f'{line!r:12} ->',m.take_tx().replace(b'\x00',b'').decode(errors='replace'))

#print(m.bus.iolog)
