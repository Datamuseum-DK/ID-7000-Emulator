from machine import Machine

m=Machine(trace_io=True)
m.boot()


while True:
    text = input()
    m.type(text + "\r")
    m.run(400000)
    print(m.take_tx().replace(b'\x00',b'').decode(errors='replace'))