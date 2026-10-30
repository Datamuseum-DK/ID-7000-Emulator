from machine import Machine

rom_file='../../src/roms/ID7K0018/board5_eproms_0_to_6.bin'
m=Machine(rom_file, trace_io=True)
m.boot()


while True:
    text = input('> ')
    m.type(text + "\r")
    m.run(400000)
    print(m.take_tx().replace(b'\x00',b'').decode(errors='replace'))