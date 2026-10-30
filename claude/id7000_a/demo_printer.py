from machine import Machine
from sync import Sync8251, CyberHost, attach
from printer import Printer, attach_printer, print_via_host, tab, zeros, CR_OVERPRINT

rom_file='../../src/roms/ID7K0018/board5_eproms_0_to_6.bin'

def fresh(**kw):
    m = Machine(rom_file); s = Sync8251(); attach(m, s)
    p = attach_printer(m, Printer(**kw)); m.boot()
    host = CyberHost(m, s); host.poll()      # bring the link up
    return m, host, p

m, host, p = fresh()
print('8255 mode word seen by printer:', hex(p.mode), '| PC after init:', bin(p.pc))

def check(name, got, want):
    print(('PASS' if got == want else 'FAIL'), name, got if got != want else '')

def run(host, p, m, *a, **k):
    p.raw.clear(); print_via_host(host, *a, **k); m.run(400000); return bytes(p.raw)

check('single space',      run(host,p,m,'HELLO'),            b'\n\rHELLO\r\n')
check('A = form feed',     run(host,p,m,'LINE',cc='A'),      b'\x0cLINE\r\n')
check('J = skip a line',   run(host,p,m,'LINE',cc='J'),      b'\n\n\rLINE\r\n')
check('ESC # = 3 spaces',  run(host,p,m,b'X'+tab(3)+b'Y'),   b'\n\rX   Y\r\n')
check('ESC J = 10 zeros',  run(host,p,m,b'X'+zeros(10)+b'Y'),b'\n\rX0000000000Y\r\n')

# rendered report
p.raw.clear()
for line,cc in [('ID-7000 PRINTER TEST',' '),('PAGE ONE',' '),('NEW PAGE','A'),('AMOUNT: '+'',' ')]:
    print_via_host(host, line, cc=cc); m.run(400000)
print_via_host(host, b'TOTAL'+tab(5)+b'|'+zeros(6), cc='J'); m.run(400000)
print('\nrendered output (pages separated by ----):')
print('\n----\n'.join('\n'.join(pg) for pg in p.pages()))

# busy / hold handshake
m2, host2, p2 = fresh(busy_reads=4)
print('\nbusy_reads=4 :', run(host2,p2,m2,'SLOW'))
m3, host3, p3 = fresh()
p3.force_busy = True; p3.hold = True
p3.raw.clear(); r = print_via_host(host3, 'HELD'); m3.run(300000)
print('busy+hold    : printed', bytes(p3.raw), '| host ACK ctl =', hex(r['ctl']))
p3.force_busy = False; m3.run(300000); print('busy cleared, hold still on:', bytes(p3.raw))
p3.hold = False; m3.run(300000); print('hold cleared :', bytes(p3.raw))
