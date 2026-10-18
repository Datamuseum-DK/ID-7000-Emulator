
from machine import Machine
from sync import Sync8251, CyberHost, attach

m=Machine()
s=Sync8251()
attach(m,s)
m.boot()
host=CyberHost(m,s)

#show=lambda b:b.replace(b'\x00',b'').decode(errors='replace').replace('\r\n','|')
show=lambda b:b.replace(b'\x00',b'').decode(errors='replace')

print('1 poll (idle)      ->',host.poll())
print('  console:',show(m.take_tx()))

m.type("HELLO\r")
m.run(500000)

print('2 user typed HELLO; console:', show(m.take_tx()))
print('3 poll             ->', host.poll())
print('4 host says text   ->', host.say(0,b'HI FROM CYBER\r\n'))
print('  console:', show(m.take_tx()))

m.type(":STATUS\r")
m.run(900000)
print('5 :STATUS ->', show(m.take_tx()))
