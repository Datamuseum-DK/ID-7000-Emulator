import devices.z80io_sps as io
### From


spsa = {
    "descr": "SPS ROMS",
    "start": 0x0000,
    "data": [
        ["file", "roms/SPS/SPS_1_5_890505_ADR_255.bin", 0x0000],
        ["file", "roms/SPS/SPS_2_5_890505_ADR_255.bin", 0x0800],
        ["file", "roms/SPS/SPS_3_5_890505_ADR_255.bin", 0x1000],
        ["file", "roms/SPS/SPS_4_5_890505_ADR_255.bin", 0x1800],
        ["file", "roms/SPS/SPS_5_5_890505_ADR_255.bin", 0x2000],
        ["file", "roms/FUNK/FUNK_1_3_881229.bin",       0x2800],
        ["file", "roms/FUNK/FUNK_2_3_881229.bin",       0x3000],
        ["file", "roms/FUNK/FUNK_3_3_881229.bin",       0x3800]
        
    ],
    "io" : io,
    "funcs" : {
    },
    "pois" : {
        0x0001: "jump to start()",
       
    },
    "known_ranges" : [

        [0x0000, 0x0007, 'RST0 - boot vector, jp to start()'],
        [0x0008, 0x000f, 'RST1 - unused'],
        [0x0010, 0x0017, 'RST2 - jp to 0x005b (IOs 0xa0 & 0xa1)'],
        [0x0018, 0x001f, 'RST3 - jp to 0x0760 (IO 0xff)'],
        [0x0020, 0x0027, 'RST4 - jp to 0x020b (IOs 0xa0 & 0xa1)'],
        [0x0028, 0x002f, 'RST5 - unused'],
        [0x0030, 0x0037, 'RST6 - jp to 0x0800 (terminal IO?)'],
        [0x0038, 0x003f, 'RST7 - jp to start()'],
      
    ]
}
