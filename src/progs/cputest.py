import devices.z80io_sps as io
### From


def hook(cpu, t):
    if cpu.m.pc == 5:
        if cpu.m.c == 2:
            chi = cpu.m.e
            if chi == 10:
                print(t)
                t = ""
            else:
                t += chr(cpu.m.e)
                #print(t)
        elif cpu.m.c == 9:
            print(cpu.mem[cpu.de:10])
        else:
            sys.exit()
    return t


cputest = {
    "descr": "CPUTEST",
    "start": 0x0100,
    "data": [
        ["file", "CPUTEST.COM",   0x0100],
        ["snippet", [0xc9],       0x0005]
        #["file", "8080PRE.COM", 0x0100]
        
    ],
    "io" : io,
    "hook" : hook,
    "funcs" : {
    },
    "pois" : {
       
    },
    "known_ranges" : [
      
    ]
}
