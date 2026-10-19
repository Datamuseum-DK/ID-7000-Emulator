
Annotated disassembly
=====================

From **disassembly.py -a** on 2025 10 15

.. code-block:: text


    loading program: ID-7000 from punch tape
    loaded 7168 bytes from roms/ID7K0018/board5_eproms_0_to_6.bin at address 0000h

    ;RST0 - boot vector, jp to start()
    0000 f3           ; di                   | 
    0001 c3 a0 0d     ; jp 0xda0             | jump to start()
    0004 76           ; halt                 | 
    0005 76           ; halt                 | 
    0006 76           ; halt                 | 
    0007 76           ; halt                 | 

    ;RST1 - unused
    0008 fb           ; ei                   | 
    0009 c9           ; ret                  | 
    000a 76           ; halt                 | 
    000b 76           ; halt                 | 
    000c 76           ; halt                 | 
    000d 76           ; halt                 | 
    000e 76           ; halt                 | 
    000f 76           ; halt                 | 

    ;RST2 - jp to 0x005b (IOs 0xa0 & 0xa1)
    0010 c3 5b 00     ; jp 0x5b              | 
    0013 76           ; halt                 | 
    0014 76           ; halt                 | 
    0015 76           ; halt                 | 
    0016 76           ; halt                 | 
    0017 76           ; halt                 | 

    ;RST3 - jp to 0x0760 (IO 0xff)
    0018 c3 60 07     ; jp 0x760             | 
    001b 76           ; halt                 | 
    001c 76           ; halt                 | 
    001d 76           ; halt                 | 
    001e 76           ; halt                 | 
    001f 76           ; halt                 | 

    ;RST4 - jp to 0x020b (IOs 0xa0 & 0xa1)
    0020 c3 0b 02     ; jp 0x20b             | 
    0023 76           ; halt                 | 
    0024 76           ; halt                 | 
    0025 76           ; halt                 | 
    0026 76           ; halt                 | 
    0027 76           ; halt                 | 

    ;RST5 - unused
    0028 fb           ; ei                   | 
    0029 c9           ; ret                  | 
    002a 76           ; halt                 | 
    002b 76           ; halt                 | 
    002c 76           ; halt                 | 
    002d 76           ; halt                 | 
    002e 76           ; halt                 | 
    002f 76           ; halt                 | 

    ;RST6 - jp to 0x0800 (terminal IO?)
    0030 c3 80 08     ; jp 0x880             | 
    0033 76           ; halt                 | 
    0034 76           ; halt                 | 
    0035 76           ; halt                 | 
    0036 76           ; halt                 | 
    0037 76           ; halt                 | 

    ;RST7 - jp to start()
    0038 c3 a0 0d     ; jp 0xda0             | 
    003b 76           ; halt                 | 
    003c 76           ; halt                 | 
    003d 76           ; halt                 | 
    003e 76           ; halt                 | 
    003f 76           ; halt                 | 

    ;unknown subroutine
    0040 f5           ; push af              | 
    0041 e5           ; push hl              | 
    0042 21 f2 a2     ; ld hl, 0xa2f2        | 
    0045 36 ff        ; ld (hl), 0xff        | 
    0047 db a1        ; in a, (0xa1)         | 
    0049 e6 38        ; and 0x38             | 
    004b ca 52 00     ; jp z, 0x52           | 
    004e 3e 96        ; ld a, 0x96           | 
    0050 d3 a1        ; out (0xa1), a        | 
    0052 db fe        ; in a, (0xfe)         | 
    0054 f6 04        ; or 0x4               | set INTR 2?
    0056 d3 fe        ; out (0xfe), a        | 
    0058 e1           ; pop hl               | 
    0059 f1           ; pop af               | 
    005a c9           ; ret                  | 

    ;RST2()
    005b f5           ; push af              | 
    005c db a1        ; in a, (0xa1)         | 
    005e 0f           ; rrca                 | 
    005f 0f           ; rrca                 | 
    0060 d2 97 00     ; jp nc, 0x97          | 
    0063 e5           ; push hl              | 
    0064 d5           ; push de              | 
    0065 c5           ; push bc              | 
    0066 db a0        ; in a, (0xa0)         | 
    0068 47           ; ld b, a              | 
    0069 db a1        ; in a, (0xa1)         | 
    006b e6 38        ; and 0x38             | 
    006d c2 87 00     ; jp nz, 0x87          | 
    0070 21 f2 a2     ; ld hl, 0xa2f2        | 
    0073 7e           ; ld a, (hl)           | 
    0074 fe 07        ; cp 0x7               | 
    0076 ca 7e 00     ; jp z, 0x7e           | 
    0079 fe 05        ; cp 0x5               | 
    007b f2 9a 00     ; jp p, 0x9a           | 
    007e 78           ; ld a, b              | 
    007f fe 16        ; cp 0x16              | 
    0081 c2 9a 00     ; jp nz, 0x9a          | 
    0084 c3 94 00     ; jp 0x94              | 
    0087 cd 40 00     ; call 0x40            | 
    008a 2a f7 a2     ; ld hl, (0xa2f7)      | 
    008d 7d           ; ld a, l              | 
    008e b4           ; or h                 | 
    008f ca 94 00     ; jp z, 0x94           | 
    0092 36 ff        ; ld (hl), 0xff        | 
    0094 c1           ; pop bc               | 
    0095 d1           ; pop de               | 
    0096 e1           ; pop hl               | 
    0097 f1           ; pop af               | 
    0098 fb           ; ei                   | 
    0099 c9           ; ret                  | 

    ;unexplored
    009a b6           ; or (hl)              | 
    009b fa c4 00     ; jp m, 0xc4           | 
    009e 23           ; inc hl               | 
    009f 78           ; ld a, b              | 
    00a0 4e           ; ld c, (hl)           | 
    00a1 a9           ; xor c                | 
    00a2 77           ; ld (hl), a           | 
    00a3 2b           ; dec hl               | 
    00a4 7e           ; ld a, (hl)           | 
    00a5 a7           ; and a                | 
    00a6 ca f6 00     ; jp z, 0xf6           | case?: a == 0
    00a9 3d           ; dec a                | 
    00aa ca 0d 01     ; jp z, 0x10d          | case?: a == 1
    00ad 3d           ; dec a                | 
    00ae ca 26 01     ; jp z, 0x126          | case?: a == 2
    00b1 3d           ; dec a                | 
    00b2 ca 69 01     ; jp z, 0x169          | case?: a == 3
    00b5 3d           ; dec a                | 
    00b6 ca 75 01     ; jp z, 0x175          | case?: a == 4
    00b9 3d           ; dec a                | 
    00ba ca 99 01     ; jp z, 0x199          | case?: a == 5
    00bd 3d           ; dec a                | 
    00be ca ad 01     ; jp z, 0x1ad          | case?: a == 6
    00c1 c3 87 00     ; jp 0x87              | default?:
    00c4 78           ; ld a, b              | 
    00c5 d6 01        ; sub 0x1              | 
    00c7 c2 94 00     ; jp nz, 0x94          | 
    00ca 77           ; ld (hl), a           | 
    00cb 23           ; inc hl               | 
    00cc 36 fe        ; ld (hl), 0xfe        | 
    00ce 97           ; sub a                | 
    00cf 32 9b 42     ; ld (0x429b), a       | 
    00d2 32 9c 42     ; ld (0x429c), a       | 
    00d5 3a 9d 42     ; ld a, (0x429d)       | 
    00d8 a7           ; and a                | 
    00d9 ca 94 00     ; jp z, 0x94           | 
    00dc 97           ; sub a                | 
    00dd 32 9d 42     ; ld (0x429d), a       | 
    00e0 0e 00        ; ld c, 0x0            | 
    00e2 21 0d 18     ; ld hl, 0x180d        | hl = A[CYBER LINK ESTABLISHED]
    00e5 97           ; sub a                | 
    00e6 cd ec 15     ; call 0x15ec          | 
    00e9 79           ; ld a, c              | 
    00ea fe 0b        ; cp 0xb               | 
    00ec ca f3 00     ; jp z, 0xf3           | 
    00ef 0c           ; inc c                | 
    00f0 c3 e2 00     ; jp 0xe2              | 
    00f3 c3 94 00     ; jp 0x94              | 
    00f6 78           ; ld a, b              | 
    00f7 fe 70        ; cp 0x70              | 
    00f9 fa 87 00     ; jp m, 0x87           | 
    00fc fe 7f        ; cp 0x7f              | 
    00fe f2 87 00     ; jp p, 0x87           | 
    0101 34           ; inc (hl)             | 
    0102 c3 07 01     ; jp 0x107             | 
    0105 23           ; inc hl               | 
    0106 23           ; inc hl               | 
    0107 23           ; inc hl               | 
    0108 23           ; inc hl               | 
    0109 77           ; ld (hl), a           | 
    010a c3 94 00     ; jp 0x94              | 
    010d 78           ; ld a, b              | 
    010e fe 61        ; cp 0x61              | 
    0110 ca 22 01     ; jp z, 0x122          | 
    0113 fe 71        ; cp 0x71              | 
    0115 ca 22 01     ; jp z, 0x122          | 
    0118 fe 60        ; cp 0x60              | 
    011a ca 22 01     ; jp z, 0x122          | 
    011d fe 70        ; cp 0x70              | 
    011f c2 87 00     ; jp nz, 0x87          | 
    0122 34           ; inc (hl)             | 
    0123 c3 06 01     ; jp 0x106             | 
    0126 34           ; inc (hl)             | 
    0127 78           ; ld a, b              | 
    0128 fe 05        ; cp 0x5               | 
    012a ca 05 01     ; jp z, 0x105          | 
    012d fe 12        ; cp 0x12              | 
    012f ca 3c 01     ; jp z, 0x13c          | 
    0132 fe 11        ; cp 0x11              | 
    0134 ca 3c 01     ; jp z, 0x13c          | 
    0137 fe 0c        ; cp 0xc               | 
    0139 c2 87 00     ; jp nz, 0x87          | 
    013c 34           ; inc (hl)             | 
    013d 32 f6 a2     ; ld (0xa2f6), a       | 
    0140 06 ff        ; ld b, 0xff           | 
    0142 cd 71 06     ; call 0x671           | 
    0145 da 87 00     ; jp c, 0x87           | 
    0148 36 03        ; ld (hl), 0x3         | 
    014a 22 f7 a2     ; ld (0xa2f7), hl      | 
    014d 23           ; inc hl               | 
    014e 5e           ; ld e, (hl)           | 
    014f 23           ; inc hl               | 
    0150 56           ; ld d, (hl)           | 
    0151 e5           ; push hl              | 
    0152 21 f4 a2     ; ld hl, 0xa2f4        | 
    0155 0e fd        ; ld c, 0xfd           | 
    0157 7e           ; ld a, (hl)           | 
    0158 12           ; ld (de), a           | 
    0159 13           ; inc de               | 
    015a 23           ; inc hl               | 
    015b 0c           ; inc c                | 
    015c fa 57 01     ; jp m, 0x157          | 
    015f e1           ; pop hl               | 
    0160 23           ; inc hl               | 
    0161 23           ; inc hl               | 
    0162 23           ; inc hl               | 
    0163 73           ; ld (hl), e           | 
    0164 23           ; inc hl               | 
    0165 72           ; ld (hl), d           | 
    0166 c3 94 00     ; jp 0x94              | 
    0169 78           ; ld a, b              | 
    016a fe 03        ; cp 0x3               | 
    016c c2 87 00     ; jp nz, 0x87          | 
    016f 34           ; inc (hl)             | 
    0170 34           ; inc (hl)             | 
    0171 34           ; inc (hl)             | 
    0172 c3 94 00     ; jp 0x94              | 
    0175 78           ; ld a, b              | 
    0176 fe 03        ; cp 0x3               | 
    0178 ca 71 01     ; jp z, 0x171          | 
    017b 2a f7 a2     ; ld hl, (0xa2f7)      | 
    017e 11 06 00     ; ld de, 0x6           | 
    0181 19           ; add hl, de           | 
    0182 56           ; ld d, (hl)           | 
    0183 2b           ; dec hl               | 
    0184 5e           ; ld e, (hl)           | 
    0185 2b           ; dec hl               | 
    0186 2b           ; dec hl               | 
    0187 7e           ; ld a, (hl)           | 
    0188 93           ; sub e                | 
    0189 23           ; inc hl               | 
    018a 7e           ; ld a, (hl)           | 
    018b 9a           ; sbc a, d             | 
    018c da 87 00     ; jp c, 0x87           | 
    018f 78           ; ld a, b              | 
    0190 12           ; ld (de), a           | 
    0191 13           ; inc de               | 
    0192 23           ; inc hl               | 
    0193 73           ; ld (hl), e           | 
    0194 23           ; inc hl               | 
    0195 72           ; ld (hl), d           | 
    0196 c3 94 00     ; jp 0x94              | 
    0199 36 ff        ; ld (hl), 0xff        | 
    019b 23           ; inc hl               | 
    019c 79           ; ld a, c              | 
    019d e6 7f        ; and 0x7f             | 
    019f 90           ; sub b                | 
    01a0 c2 87 00     ; jp nz, 0x87          | 
    01a3 2a f7 a2     ; ld hl, (0xa2f7)      | 
    01a6 36 04        ; ld (hl), 0x4         | 
    01a8 3e 00        ; ld a, 0x0            | 
    01aa c3 bd 01     ; jp 0x1bd             | 
    01ad 36 ff        ; ld (hl), 0xff        | 
    01af 23           ; inc hl               | 
    01b0 79           ; ld a, c              | 
    01b1 e6 7f        ; and 0x7f             | 
    01b3 90           ; sub b                | 
    01b4 c2 87 00     ; jp nz, 0x87          | 
    01b7 3a f5 a2     ; ld a, (0xa2f5)       | 
    01ba 47           ; ld b, a              | 
    01bb 23           ; inc hl               | 
    01bc 7e           ; ld a, (hl)           | 
    01bd 32 d2 a2     ; ld (0xa2d2), a       | 
    01c0 3e 02        ; ld a, 0x2            | 
    01c2 d3 a1        ; out (0xa1), a        | 
    01c4 3e 01        ; ld a, 0x1            | 
    01c6 32 0b 40     ; ld (0x400b), a       | 
    01c9 c1           ; pop bc               | 
    01ca d1           ; pop de               | 
    01cb e1           ; pop hl               | 
    01cc f1           ; pop af               | 
    01cd e5           ; push hl              | 
    01ce d5           ; push de              | 
    01cf c5           ; push bc              | 
    01d0 f5           ; push af              | 
    01d1 3e 02        ; ld a, 0x2            | 
    01d3 c3 cd 07     ; jp 0x7cd             | 
    01d6 f3           ; di                   | 
    01d7 f5           ; push af              | 
    01d8 e5           ; push hl              | 
    01d9 d5           ; push de              | 
    01da c5           ; push bc              | 
    01db 36 03        ; ld (hl), 0x3         | 
    01dd 3e 01        ; ld a, 0x1            | 
    01df 32 19 a3     ; ld (0xa319), a       | 
    01e2 11 f9 a2     ; ld de, 0xa2f9        | 
    01e5 eb           ; ex de, hl            | 
    01e6 36 f5        ; ld (hl), 0xf5        | 
    01e8 23           ; inc hl               | 
    01e9 73           ; ld (hl), e           | 
    01ea 23           ; inc hl               | 
    01eb 72           ; ld (hl), d           | 
    01ec 23           ; inc hl               | 
    01ed 36 ff        ; ld (hl), 0xff        | 
    01ef eb           ; ex de, hl            | 
    01f0 23           ; inc hl               | 
    01f1 5e           ; ld e, (hl)           | 
    01f2 23           ; inc hl               | 
    01f3 56           ; ld d, (hl)           | 
    01f4 01 05 00     ; ld bc, 0x5           | 
    01f7 09           ; add hl, bc           | 
    01f8 73           ; ld (hl), e           | 
    01f9 23           ; inc hl               | 
    01fa 72           ; ld (hl), d           | 
    01fb 3e 33        ; ld a, 0x33           | 
    01fd d3 a1        ; out (0xa1), a        | 
    01ff db fe        ; in a, (0xfe)         | 
    0201 f6 10        ; or 0x10              | set INTR 4?
    0203 d3 fe        ; out (0xfe), a        | 
    0205 c1           ; pop bc               | 
    0206 d1           ; pop de               | 
    0207 e1           ; pop hl               | 
    0208 f1           ; pop af               | 
    0209 fb           ; ei                   | 
    020a c9           ; ret                  | 

    ;RST4() - in(0xa1), out(0xa0)
    020b f3           ; di                   | 
    020c f5           ; push af              | 
    020d db a1        ; in a, (0xa1)         | 
    020f 0f           ; rrca                 | 
    0210 d2 4b 02     ; jp nc, 0x24b         | 
    0213 e5           ; push hl              | 
    0214 d5           ; push de              | 
    0215 c5           ; push bc              | 
    0216 21 f9 a2     ; ld hl, 0xa2f9        | 
    0219 7e           ; ld a, (hl)           | 
    021a a7           ; and a                | 
    021b fa 5f 02     ; jp m, 0x25f          | 
    021e ca 67 02     ; jp z, 0x267          | 
    0221 e5           ; push hl              | 
    0222 23           ; inc hl               | 
    0223 5e           ; ld e, (hl)           | 
    0224 23           ; inc hl               | 
    0225 56           ; ld d, (hl)           | 
    0226 23           ; inc hl               | 
    0227 eb           ; ex de, hl            | 
    0228 01 08 00     ; ld bc, 0x8           | 
    022b 09           ; add hl, bc           | 
    022c 46           ; ld b, (hl)           | 
    022d 2b           ; dec hl               | 
    022e 4e           ; ld c, (hl)           | 
    022f 2b           ; dec hl               | 
    0230 7e           ; ld a, (hl)           | 
    0231 b8           ; cp b                 | 
    0232 2b           ; dec hl               | 
    0233 c2 3b 02     ; jp nz, 0x23b         | 
    0236 7e           ; ld a, (hl)           | 
    0237 b9           ; cp c                 | 
    0238 ca 70 02     ; jp z, 0x270          | 
    023b 0a           ; ld a, (bc)           | 
    023c 03           ; inc bc               | 
    023d 23           ; inc hl               | 
    023e 23           ; inc hl               | 
    023f 71           ; ld (hl), c           | 
    0240 23           ; inc hl               | 
    0241 70           ; ld (hl), b           | 
    0242 e1           ; pop hl               | 
    0243 d3 a0        ; out (0xa0), a        | 
    0245 eb           ; ex de, hl            | 
    0246 ae           ; xor (hl)             | 
    0247 77           ; ld (hl), a           | 
    0248 c1           ; pop bc               | 
    0249 d1           ; pop de               | 
    024a e1           ; pop hl               | 
    024b f1           ; pop af               | 
    024c fb           ; ei                   | 
    024d c9           ; ret                  | 

    ;unexplored
    024e 3a 19 a3     ; ld a, (0xa319)       | 
    0251 3d           ; dec a                | 
    0252 ca 5f 02     ; jp z, 0x25f          | 
    0255 32 19 a3     ; ld (0xa319), a       | 
    0258 3e 16        ; ld a, 0x16           | 
    025a d3 a0        ; out (0xa0), a        | 
    025c c3 48 02     ; jp 0x248             | 
    025f 3e 16        ; ld a, 0x16           | 
    0261 34           ; inc (hl)             | 
    0262 d3 a0        ; out (0xa0), a        | 
    0264 c3 48 02     ; jp 0x248             | 
    0267 3e 01        ; ld a, 0x1            | 
    0269 34           ; inc (hl)             | 
    026a 11 fc a2     ; ld de, 0xa2fc        | 
    026d c3 43 02     ; jp 0x243             | 
    0270 e1           ; pop hl               | 
    0271 7e           ; ld a, (hl)           | 
    0272 3d           ; dec a                | 
    0273 ca 9a 02     ; jp z, 0x29a          | 
    0276 3d           ; dec a                | 
    0277 ca a0 02     ; jp z, 0x2a0          | 
    027a 3d           ; dec a                | 
    027b ca 4e 02     ; jp z, 0x24e          | 
    027e 3e 96        ; ld a, 0x96           | 
    0280 d3 a1        ; out (0xa1), a        | 
    0282 2a fa a2     ; ld hl, (0xa2fa)      | 
    0285 36 07        ; ld (hl), 0x7         | 
    0287 2b           ; dec hl               | 
    0288 7e           ; ld a, (hl)           | 
    0289 fe ff        ; cp 0xff              | 
    028b c2 48 02     ; jp nz, 0x248         | 
    028e 23           ; inc hl               | 
    028f 36 ff        ; ld (hl), 0xff        | 
    0291 21 00 00     ; ld hl, 0x0           | 
    0294 22 fa a2     ; ld (0xa2fa), hl      | 
    0297 c3 48 02     ; jp 0x248             | 
    029a 3e 03        ; ld a, 0x3            | 
    029c 34           ; inc (hl)             | 
    029d c3 43 02     ; jp 0x243             | 
    02a0 34           ; inc (hl)             | 
    02a1 23           ; inc hl               | 
    02a2 23           ; inc hl               | 
    02a3 23           ; inc hl               | 
    02a4 7e           ; ld a, (hl)           | 
    02a5 c3 43 02     ; jp 0x243             | 
    02a8 76           ; halt                 | 
    02a9 76           ; halt                 | 
    02aa 76           ; halt                 | 
    02ab 76           ; halt                 | 
    02ac 76           ; halt                 | 
    02ad 76           ; halt                 | 
    02ae 76           ; halt                 | 
    02af 76           ; halt                 | 
    02b0 76           ; halt                 | 
    02b1 76           ; halt                 | 
    02b2 76           ; halt                 | 
    02b3 76           ; halt                 | 
    02b4 76           ; halt                 | 
    02b5 76           ; halt                 | 
    02b6 76           ; halt                 | 
    02b7 76           ; halt                 | 
    02b8 76           ; halt                 | 
    02b9 76           ; halt                 | 
    02ba 76           ; halt                 | 
    02bb 76           ; halt                 | 
    02bc 76           ; halt                 | 
    02bd 76           ; halt                 | 
    02be 76           ; halt                 | 
    02bf 76           ; halt                 | 
    02c0 76           ; halt                 | 
    02c1 76           ; halt                 | 
    02c2 76           ; halt                 | 
    02c3 76           ; halt                 | 
    02c4 76           ; halt                 | 
    02c5 76           ; halt                 | 
    02c6 76           ; halt                 | 
    02c7 76           ; halt                 | 
    02c8 76           ; halt                 | 
    02c9 76           ; halt                 | 
    02ca 76           ; halt                 | 
    02cb 76           ; halt                 | 
    02cc 76           ; halt                 | 
    02cd 76           ; halt                 | 
    02ce 76           ; halt                 | 
    02cf 76           ; halt                 | 
    02d0 76           ; halt                 | 
    02d1 76           ; halt                 | 
    02d2 76           ; halt                 | 
    02d3 76           ; halt                 | 
    02d4 76           ; halt                 | 
    02d5 76           ; halt                 | 
    02d6 76           ; halt                 | 
    02d7 76           ; halt                 | 
    02d8 76           ; halt                 | 
    02d9 76           ; halt                 | 
    02da 76           ; halt                 | 
    02db 76           ; halt                 | 
    02dc 76           ; halt                 | 
    02dd 76           ; halt                 | 
    02de 76           ; halt                 | 
    02df 76           ; halt                 | 
    02e0 21 d2 a2     ; ld hl, 0xa2d2        | 
    02e3 7e           ; ld a, (hl)           | 
    02e4 a7           ; and a                | 
    02e5 ca a5 03     ; jp z, 0x3a5          | 
    02e8 d6 70        ; sub 0x70             | 
    02ea 32 fd a2     ; ld (0xa2fd), a       | 
    02ed 4f           ; ld c, a              | 
    02ee 36 00        ; ld (hl), 0x0         | 
    02f0 21 8b 42     ; ld hl, 0x428b        | 
    02f3 3e 01        ; ld a, 0x1            | 
    02f5 cd 30 15     ; call 0x1530          | 
    02f8 21 fd a2     ; ld hl, 0xa2fd        | 
    02fb 7e           ; ld a, (hl)           | 
    02fc a7           ; and a                | 
    02fd 23           ; inc hl               | 
    02fe c2 92 03     ; jp nz, 0x392         | 
    0301 b6           ; or (hl)              | 
    0302 ca 92 03     ; jp z, 0x392          | 
    0305 06 00        ; ld b, 0x0            | 
    0307 e5           ; push hl              | 
    0308 cd 21 06     ; call 0x621           | 
    030b e1           ; pop hl               | 
    030c fe 00        ; cp 0x0               | 
    030e c2 92 03     ; jp nz, 0x392         | 
    0311 7e           ; ld a, (hl)           | 
    0312 1f           ; rra                  | 
    0313 da 4d 03     ; jp c, 0x34d          | 
    0316 46           ; ld b, (hl)           | 
    0317 f3           ; di                   | 
    0318 cd 4b 06     ; call 0x64b           | 
    031b fe 02        ; cp 0x2               | 
    031d ca 88 03     ; jp z, 0x388          | 
    0320 fe 07        ; cp 0x7               | 
    0322 ca 88 03     ; jp z, 0x388          | 
    0325 78           ; ld a, b              | 
    0326 fe 02        ; cp 0x2               | 
    0328 c2 3c 03     ; jp nz, 0x33c         | 
    032b 3a 04 40     ; ld a, (0x4004)       | 
    032e fe 01        ; cp 0x1               | 
    0330 fb           ; ei                   | 
    0331 c2 f1 04     ; jp nz, 0x4f1         | 
    0334 3e 20        ; ld a, 0x20           | 
    0336 32 0a 40     ; ld (0x400a), a       | 
    0339 c3 25 05     ; jp 0x525             | 
    033c 3a 07 40     ; ld a, (0x4007)       | 
    033f fe 01        ; cp 0x1               | 
    0341 fb           ; ei                   | 
    0342 c2 f1 04     ; jp nz, 0x4f1         | 
    0345 3e 20        ; ld a, 0x20           | 
    0347 32 0a 40     ; ld (0x400a), a       | 
    034a c3 25 05     ; jp 0x525             | 
    034d 46           ; ld b, (hl)           | 
    034e f3           ; di                   | 
    034f 78           ; ld a, b              | 
    0350 fe 01        ; cp 0x1               | 
    0352 c2 76 03     ; jp nz, 0x376         | 
    0355 db 51        ; in a, (0x51)         | 
    0357 e6 10        ; and 0x10             | 
    0359 fb           ; ei                   | 
    035a c3 65 03     ; jp 0x365             | 
    035d 3e 20        ; ld a, 0x20           | 
    035f 32 0a 40     ; ld (0x400a), a       | 
    0362 c3 25 05     ; jp 0x525             | 
    0365 cd 4b 06     ; call 0x64b           | 
    0368 fe 05        ; cp 0x5               | 
    036a c2 f1 04     ; jp nz, 0x4f1         | 
    036d fb           ; ei                   | 
    036e 3e 21        ; ld a, 0x21           | 
    0370 32 0a 40     ; ld (0x400a), a       | 
    0373 c3 25 05     ; jp 0x525             | 
    0376 db 0d        ; in a, (0xd)          | 
    0378 e6 0c        ; and 0xc              | 
    037a fe 08        ; cp 0x8               | 
    037c fb           ; ei                   | 
    037d ca 65 03     ; jp z, 0x365          | 
    0380 3e 20        ; ld a, 0x20           | 
    0382 32 0a 40     ; ld (0x400a), a       | 
    0385 c3 25 05     ; jp 0x525             | 
    0388 fb           ; ei                   | 
    0389 cd 04 06     ; call 0x604           | 
    038c 22 02 a3     ; ld (0xa302), hl      | 
    038f c3 a4 03     ; jp 0x3a4             | 
    0392 06 00        ; ld b, 0x0            | 
    0394 cd 21 06     ; call 0x621           | 
    0397 fe 02        ; cp 0x2               | 
    0399 ca a1 03     ; jp z, 0x3a1          | 
    039c fe 07        ; cp 0x7               | 
    039e c2 5b 05     ; jp nz, 0x55b         | 
    03a1 cd 04 06     ; call 0x604           | 
    03a4 00           ; nop                  | 
    03a5 2a fa a2     ; ld hl, (0xa2fa)      | 
    03a8 7c           ; ld a, h              | 
    03a9 b5           ; or l                 | 
    03aa ca b7 03     ; jp z, 0x3b7          | 
    03ad 2b           ; dec hl               | 
    03ae 7e           ; ld a, (hl)           | 
    03af fe ff        ; cp 0xff              | 
    03b1 c2 b7 03     ; jp nz, 0x3b7         | 
    03b4 23           ; inc hl               | 
    03b5 36 ff        ; ld (hl), 0xff        | 
    03b7 2a f7 a2     ; ld hl, (0xa2f7)      | 
    03ba 7c           ; ld a, h              | 
    03bb b5           ; or l                 | 
    03bc ca 28 04     ; jp z, 0x428          | 
    03bf e5           ; push hl              | 
    03c0 21 00 00     ; ld hl, 0x0           | 
    03c3 22 f7 a2     ; ld (0xa2f7), hl      | 
    03c6 e1           ; pop hl               | 
    03c7 23           ; inc hl               | 
    03c8 5e           ; ld e, (hl)           | 
    03c9 23           ; inc hl               | 
    03ca 56           ; ld d, (hl)           | 
    03cb 23           ; inc hl               | 
    03cc 23           ; inc hl               | 
    03cd 23           ; inc hl               | 
    03ce 4e           ; ld c, (hl)           | 
    03cf 23           ; inc hl               | 
    03d0 e5           ; push hl              | 
    03d1 46           ; ld b, (hl)           | 
    03d2 0b           ; dec bc               | 
    03d3 0b           ; dec bc               | 
    03d4 0a           ; ld a, (bc)           | 
    03d5 fe 1b        ; cp 0x1b              | 
    03d7 c2 1b 05     ; jp nz, 0x51b         | 
    03da 03           ; inc bc               | 
    03db 13           ; inc de               | 
    03dc 1a           ; ld a, (de)           | 
    03dd 32 ff a2     ; ld (0xa2ff), a       | 
    03e0 1b           ; dec de               | 
    03e1 0a           ; ld a, (bc)           | 
    03e2 fe 20        ; cp 0x20              | 
    03e4 ca 2d 04     ; jp z, 0x42d          | 
    03e7 fe 21        ; cp 0x21              | 
    03e9 ca 4b 04     ; jp z, 0x44b          | 
    03ec fe 22        ; cp 0x22              | 
    03ee ca f6 03     ; jp z, 0x3f6          | 
    03f1 fe 42        ; cp 0x42              | 
    03f3 c2 1b 05     ; jp nz, 0x51b         | 
    03f6 1a           ; ld a, (de)           | 
    03f7 d6 70        ; sub 0x70             | 
    03f9 4f           ; ld c, a              | 
    03fa c2 00 04     ; jp nz, 0x400         | 
    03fd 32 fe a2     ; ld (0xa2fe), a       | 
    0400 cd 5b 06     ; call 0x65b           | 
    0403 06 00        ; ld b, 0x0            | 
    0405 cd 21 06     ; call 0x621           | 
    0408 fe 07        ; cp 0x7               | 
    040a cd 25 07     ; call 0x725           | 
    040d c3 10 04     ; jp 0x410             | 
    0410 04           ; inc b                | 
    0411 cd 21 06     ; call 0x621           | 
    0414 fe 05        ; cp 0x5               | 
    0416 c2 fc 04     ; jp nz, 0x4fc         | 
    0419 05           ; dec b                | 
    041a 79           ; ld a, c              | 
    041b 32 d0 42     ; ld (0x42d0), a       | 
    041e cd 8c 05     ; call 0x58c           | 
    0421 3a d0 42     ; ld a, (0x42d0)       | 
    0424 4f           ; ld c, a              | 
    0425 cd 78 04     ; call 0x478           | 
    0428 3e 01        ; ld a, 0x1            | 
    042a cd c8 07     ; call 0x7c8           | 
    042d 06 01        ; ld b, 0x1            | 
    042f c3 34 04     ; jp 0x434             | 
    0432 06 03        ; ld b, 0x3            | 
    0434 cd 5b 06     ; call 0x65b           | 
    0437 cd 4b 06     ; call 0x64b           | 
    043a fe 05        ; cp 0x5               | 
    043c 0e 00        ; ld c, 0x0            | 
    043e cd 8c 05     ; call 0x58c           | 
    0441 cd 06 1a     ; call 0x1a06          | 
    0444 78           ; ld a, b              | 
    0445 32 fe a2     ; ld (0xa2fe), a       | 
    0448 c3 28 04     ; jp 0x428             | 
    044b 06 02        ; ld b, 0x2            | 
    044d c3 52 04     ; jp 0x452             | 
    0450 06 04        ; ld b, 0x4            | 
    0452 cd 5b 06     ; call 0x65b           | 
    0455 e1           ; pop hl               | 
    0456 eb           ; ex de, hl            | 
    0457 0e 00        ; ld c, 0x0            | 
    0459 23           ; inc hl               | 
    045a 7e           ; ld a, (hl)           | 
    045b e5           ; push hl              | 
    045c c5           ; push bc              | 
    045d 21 09 a3     ; ld hl, 0xa309        | 
    0460 06 00        ; ld b, 0x0            | 
    0462 09           ; add hl, bc           | 
    0463 77           ; ld (hl), a           | 
    0464 c1           ; pop bc               | 
    0465 e1           ; pop hl               | 
    0466 23           ; inc hl               | 
    0467 36 06        ; ld (hl), 0x6         | 
    0469 23           ; inc hl               | 
    046a eb           ; ex de, hl            | 
    046b 72           ; ld (hl), d           | 
    046c 2b           ; dec hl               | 
    046d 73           ; ld (hl), e           | 
    046e 11 fb ff     ; ld de, 0xfffb        | 
    0471 19           ; add hl, de           | 
    0472 cd d6 01     ; call 0x1d6           | 
    0475 c3 44 04     ; jp 0x444             | 
    0478 e5           ; push hl              | 
    0479 d5           ; push de              | 
    047a 11 05 00     ; ld de, 0x5           | 
    047d 19           ; add hl, de           | 
    047e 5e           ; ld e, (hl)           | 
    047f 23           ; inc hl               | 
    0480 56           ; ld d, (hl)           | 
    0481 1b           ; dec de               | 
    0482 1b           ; dec de               | 
    0483 eb           ; ex de, hl            | 
    0484 3e 20        ; ld a, 0x20           | 
    0486 2b           ; dec hl               | 
    0487 be           ; cp (hl)              | 
    0488 ca 86 04     ; jp z, 0x486          | 
    048b e5           ; push hl              | 
    048c d5           ; push de              | 
    048d 2b           ; dec hl               | 
    048e 2b           ; dec hl               | 
    048f eb           ; ex de, hl            | 
    0490 23           ; inc hl               | 
    0491 23           ; inc hl               | 
    0492 7e           ; ld a, (hl)           | 
    0493 ba           ; cp d                 | 
    0494 c2 a5 04     ; jp nz, 0x4a5         | 
    0497 2b           ; dec hl               | 
    0498 7e           ; ld a, (hl)           | 
    0499 bb           ; cp e                 | 
    049a c2 a5 04     ; jp nz, 0x4a5         | 
    049d d1           ; pop de               | 
    049e e1           ; pop hl               | 
    049f 23           ; inc hl               | 
    04a0 36 00        ; ld (hl), 0x0         | 
    04a2 c3 a7 04     ; jp 0x4a7             | 
    04a5 d1           ; pop de               | 
    04a6 e1           ; pop hl               | 
    04a7 23           ; inc hl               | 
    04a8 36 1b        ; ld (hl), 0x1b        | 
    04aa 23           ; inc hl               | 
    04ab 36 41        ; ld (hl), 0x41        | 
    04ad e5           ; push hl              | 
    04ae 21 7b 42     ; ld hl, 0x427b        | 
    04b1 cd 29 15     ; call 0x1529          | 
    04b4 a7           ; and a                | 
    04b5 ca bf 04     ; jp z, 0x4bf          | 
    04b8 e1           ; pop hl               | 
    04b9 23           ; inc hl               | 
    04ba 36 11        ; ld (hl), 0x11        | 
    04bc c3 ca 04     ; jp 0x4ca             | 
    04bf 21 6b 42     ; ld hl, 0x426b        | 
    04c2 cd 29 15     ; call 0x1529          | 
    04c5 a7           ; and a                | 
    04c6 c2 b8 04     ; jp nz, 0x4b8         | 
    04c9 e1           ; pop hl               | 
    04ca eb           ; ex de, hl            | 
    04cb 13           ; inc de               | 
    04cc 72           ; ld (hl), d           | 
    04cd 2b           ; dec hl               | 
    04ce 73           ; ld (hl), e           | 
    04cf 23           ; inc hl               | 
    04d0 23           ; inc hl               | 
    04d1 5e           ; ld e, (hl)           | 
    04d2 23           ; inc hl               | 
    04d3 56           ; ld d, (hl)           | 
    04d4 13           ; inc de               | 
    04d5 13           ; inc de               | 
    04d6 1a           ; ld a, (de)           | 
    04d7 fe 11        ; cp 0x11              | 
    04d9 3e 00        ; ld a, 0x0            | 
    04db ca e4 04     ; jp z, 0x4e4          | 
    04de 3e 1f        ; ld a, 0x1f           | 
    04e0 12           ; ld (de), a           | 
    04e1 c3 e9 04     ; jp 0x4e9             | 
    04e4 12           ; ld (de), a           | 
    04e5 1b           ; dec de               | 
    04e6 3e 00        ; ld a, 0x0            | 
    04e8 12           ; ld (de), a           | 
    04e9 72           ; ld (hl), d           | 
    04ea 2b           ; dec hl               | 
    04eb 73           ; ld (hl), e           | 
    04ec d1           ; pop de               | 
    04ed e1           ; pop hl               | 
    04ee 36 06        ; ld (hl), 0x6         | 
    04f0 c9           ; ret                  | 
    04f1 06 ff        ; ld b, 0xff           | 
    04f3 cd 71 06     ; call 0x671           | 
    04f6 d2 63 05     ; jp nc, 0x563         | 
    04f9 c3 58 05     ; jp 0x558             | 
    04fc e1           ; pop hl               | 
    04fd eb           ; ex de, hl            | 
    04fe 7e           ; ld a, (hl)           | 
    04ff d6 70        ; sub 0x70             | 
    0501 4f           ; ld c, a              | 
    0502 cd 80 05     ; call 0x580           | 
    0505 23           ; inc hl               | 
    0506 e6 fe        ; and 0xfe             | 
    0508 77           ; ld (hl), a           | 
    0509 23           ; inc hl               | 
    050a 36 18        ; ld (hl), 0x18        | 
    050c 23           ; inc hl               | 
    050d eb           ; ex de, hl            | 
    050e 72           ; ld (hl), d           | 
    050f 2b           ; dec hl               | 
    0510 73           ; ld (hl), e           | 
    0511 11 fb ff     ; ld de, 0xfffb        | 
    0514 19           ; add hl, de           | 
    0515 cd d6 01     ; call 0x1d6           | 
    0518 c3 28 04     ; jp 0x428             | 
    051b e1           ; pop hl               | 
    051c 11 fa ff     ; ld de, 0xfffa        | 
    051f 19           ; add hl, de           | 
    0520 36 ff        ; ld (hl), 0xff        | 
    0522 c3 28 04     ; jp 0x428             | 
    0525 06 ff        ; ld b, 0xff           | 
    0527 cd 71 06     ; call 0x671           | 
    052a da 58 05     ; jp c, 0x558          | 
    052d 23           ; inc hl               | 
    052e 5e           ; ld e, (hl)           | 
    052f 23           ; inc hl               | 
    0530 56           ; ld d, (hl)           | 
    0531 eb           ; ex de, hl            | 
    0532 36 70        ; ld (hl), 0x70        | 
    0534 23           ; inc hl               | 
    0535 0e 00        ; ld c, 0x0            | 
    0537 cd 80 05     ; call 0x580           | 
    053a 77           ; ld (hl), a           | 
    053b 23           ; inc hl               | 
    053c 36 13        ; ld (hl), 0x13        | 
    053e 23           ; inc hl               | 
    053f 36 1b        ; ld (hl), 0x1b        | 
    0541 23           ; inc hl               | 
    0542 3a 0a 40     ; ld a, (0x400a)       | 
    0545 77           ; ld (hl), a           | 
    0546 23           ; inc hl               | 
    0547 eb           ; ex de, hl            | 
    0548 e5           ; push hl              | 
    0549 23           ; inc hl               | 
    054a 23           ; inc hl               | 
    054b 23           ; inc hl               | 
    054c 73           ; ld (hl), e           | 
    054d 23           ; inc hl               | 
    054e 72           ; ld (hl), d           | 
    054f e1           ; pop hl               | 
    0550 2b           ; dec hl               | 
    0551 2b           ; dec hl               | 
    0552 cd d6 01     ; call 0x1d6           | 
    0555 c3 a4 03     ; jp 0x3a4             | 
    0558 c3 a4 03     ; jp 0x3a4             | 
    055b 06 ff        ; ld b, 0xff           | 
    055d cd b2 06     ; call 0x6b2           | 
    0560 da 58 05     ; jp c, 0x558          | 
    0563 23           ; inc hl               | 
    0564 5e           ; ld e, (hl)           | 
    0565 23           ; inc hl               | 
    0566 56           ; ld d, (hl)           | 
    0567 eb           ; ex de, hl            | 
    0568 3a fd a2     ; ld a, (0xa2fd)       | 
    056b c6 70        ; add a, 0x70          | 
    056d 77           ; ld (hl), a           | 
    056e 23           ; inc hl               | 
    056f 3a fd a2     ; ld a, (0xa2fd)       | 
    0572 4f           ; ld c, a              | 
    0573 cd 80 05     ; call 0x580           | 
    0576 e6 fe        ; and 0xfe             | 
    0578 77           ; ld (hl), a           | 
    0579 23           ; inc hl               | 
    057a 36 18        ; ld (hl), 0x18        | 
    057c 23           ; inc hl               | 
    057d c3 47 05     ; jp 0x547             | 
    0580 e5           ; push hl              | 
    0581 c5           ; push bc              | 
    0582 21 09 a3     ; ld hl, 0xa309        | 
    0585 06 00        ; ld b, 0x0            | 
    0587 09           ; add hl, bc           | 
    0588 7e           ; ld a, (hl)           | 
    0589 c1           ; pop bc               | 
    058a e1           ; pop hl               | 
    058b c9           ; ret                  | 
    058c 22 06 a3     ; ld (0xa306), hl      | 
    058f 3a ff a2     ; ld a, (0xa2ff)       | 
    0592 e5           ; push hl              | 
    0593 c5           ; push bc              | 
    0594 21 09 a3     ; ld hl, 0xa309        | 
    0597 06 00        ; ld b, 0x0            | 
    0599 09           ; add hl, bc           | 
    059a 77           ; ld (hl), a           | 
    059b c1           ; pop bc               | 
    059c e1           ; pop hl               | 
    059d 78           ; ld a, b              | 
    059e 32 08 a3     ; ld (0xa308), a       | 
    05a1 a7           ; and a                | 
    05a2 c2 b1 05     ; jp nz, 0x5b1         | 
    05a5 21 ae a2     ; ld hl, 0xa2ae        | 
    05a8 81           ; add a, c             | 
    05a9 32 08 a3     ; ld (0xa308), a       | 
    05ac 81           ; add a, c             | 
    05ad 4f           ; ld c, a              | 
    05ae c3 c5 05     ; jp 0x5c5             | 
    05b1 21 cd a2     ; ld hl, 0xa2cd        | 
    05b4 48           ; ld c, b              | 
    05b5 06 00        ; ld b, 0x0            | 
    05b7 09           ; add hl, bc           | 
    05b8 eb           ; ex de, hl            | 
    05b9 e1           ; pop hl               | 
    05ba e3           ; ex (sp), hl          | 
    05bb 01 fa ff     ; ld bc, 0xfffa        | 
    05be 09           ; add hl, bc           | 
    05bf 7d           ; ld a, l              | 
    05c0 de 8b        ; sbc a, 0x8b          | 
    05c2 c3 d0 05     ; jp 0x5d0             | 
    05c5 09           ; add hl, bc           | 
    05c6 eb           ; ex de, hl            | 
    05c7 e1           ; pop hl               | 
    05c8 e3           ; ex (sp), hl          | 
    05c9 01 fa ff     ; ld bc, 0xfffa        | 
    05cc 09           ; add hl, bc           | 
    05cd 7d           ; ld a, l              | 
    05ce de 8b        ; sbc a, 0x8b          | 
    05d0 3c           ; inc a                | 
    05d1 12           ; ld (de), a           | 
    05d2 22 04 a3     ; ld (0xa304), hl      | 
    05d5 2b           ; dec hl               | 
    05d6 3a 08 a3     ; ld a, (0xa308)       | 
    05d9 77           ; ld (hl), a           | 
    05da 2a 06 a3     ; ld hl, (0xa306)      | 
    05dd 2b           ; dec hl               | 
    05de 36 ff        ; ld (hl), 0xff        | 
    05e0 23           ; inc hl               | 
    05e1 23           ; inc hl               | 
    05e2 5e           ; ld e, (hl)           | 
    05e3 23           ; inc hl               | 
    05e4 56           ; ld d, (hl)           | 
    05e5 eb           ; ex de, hl            | 
    05e6 23           ; inc hl               | 
    05e7 3a ff a2     ; ld a, (0xa2ff)       | 
    05ea 77           ; ld (hl), a           | 
    05eb 23           ; inc hl               | 
    05ec 36 06        ; ld (hl), 0x6         | 
    05ee 23           ; inc hl               | 
    05ef 13           ; inc de               | 
    05f0 13           ; inc de               | 
    05f1 13           ; inc de               | 
    05f2 eb           ; ex de, hl            | 
    05f3 73           ; ld (hl), e           | 
    05f4 23           ; inc hl               | 
    05f5 72           ; ld (hl), d           | 
    05f6 2a 06 a3     ; ld hl, (0xa306)      | 
    05f9 cd d6 01     ; call 0x1d6           | 
    05fc 2a 04 a3     ; ld hl, (0xa304)      | 
    05ff 3a 08 a3     ; ld a, (0xa308)       | 
    0602 47           ; ld b, a              | 
    0603 c9           ; ret                  | 
    0604 e5           ; push hl              | 
    0605 d5           ; push de              | 
    0606 23           ; inc hl               | 
    0607 5e           ; ld e, (hl)           | 
    0608 23           ; inc hl               | 
    0609 56           ; ld d, (hl)           | 
    060a 21 fd a2     ; ld hl, 0xa2fd        | 
    060d 7e           ; ld a, (hl)           | 
    060e 4f           ; ld c, a              | 
    060f c6 70        ; add a, 0x70          | 
    0611 12           ; ld (de), a           | 
    0612 13           ; inc de               | 
    0613 cd 80 05     ; call 0x580           | 
    0616 12           ; ld (de), a           | 
    0617 3e 13        ; ld a, 0x13           | 
    0619 13           ; inc de               | 
    061a 12           ; ld (de), a           | 
    061b d1           ; pop de               | 
    061c e1           ; pop hl               | 
    061d cd d6 01     ; call 0x1d6           | 
    0620 c9           ; ret                  | 
    0621 c5           ; push bc              | 
    0622 78           ; ld a, b              | 
    0623 a7           ; and a                | 
    0624 ca 39 06     ; jp z, 0x639          | 
    0627 79           ; ld a, c              | 
    0628 81           ; add a, c             | 
    0629 80           ; add a, b             | 
    062a 06 00        ; ld b, 0x0            | 
    062c 4f           ; ld c, a              | 
    062d 21 ad a2     ; ld hl, 0xa2ad        | 
    0630 09           ; add hl, bc           | 
    0631 4e           ; ld c, (hl)           | 
    0632 21 8b a1     ; ld hl, 0xa18b        | 
    0635 09           ; add hl, bc           | 
    0636 7e           ; ld a, (hl)           | 
    0637 c1           ; pop bc               | 
    0638 c9           ; ret                  | 
    0639 79           ; ld a, c              | 
    063a 81           ; add a, c             | 
    063b 80           ; add a, b             | 
    063c 06 00        ; ld b, 0x0            | 
    063e 4f           ; ld c, a              | 
    063f 21 ad a2     ; ld hl, 0xa2ad        | 
    0642 09           ; add hl, bc           | 
    0643 4e           ; ld c, (hl)           | 
    0644 21 35 a2     ; ld hl, 0xa235        | 
    0647 09           ; add hl, bc           | 
    0648 7e           ; ld a, (hl)           | 
    0649 c1           ; pop bc               | 
    064a c9           ; ret                  | 
    064b c5           ; push bc              | 
    064c 48           ; ld c, b              | 
    064d 06 00        ; ld b, 0x0            | 
    064f 21 cd a2     ; ld hl, 0xa2cd        | 
    0652 09           ; add hl, bc           | 
    0653 4e           ; ld c, (hl)           | 
    0654 21 8b a1     ; ld hl, 0xa18b        | 
    0657 09           ; add hl, bc           | 
    0658 7e           ; ld a, (hl)           | 
    0659 c1           ; pop bc               | 
    065a c9           ; ret                  | 
    065b 2a 02 a3     ; ld hl, (0xa302)      | 
    065e 7d           ; ld a, l              | 
    065f b4           ; or h                 | 
    0660 c8           ; ret z                | 
    0661 7e           ; ld a, (hl)           | 
    0662 d6 07        ; sub 0x7              | 
    0664 c0           ; ret nz               | 
    0665 e5           ; push hl              | 
    0666 21 00 00     ; ld hl, 0x0           | 
    0669 22 02 a3     ; ld (0xa302), hl      | 
    066c e1           ; pop hl               | 
    066d cd 25 07     ; call 0x725           | 
    0670 c9           ; ret                  | 
    0671 d5           ; push de              | 
    0672 21 8b a1     ; ld hl, 0xa18b        | 
    0675 7e           ; ld a, (hl)           | 
    0676 a7           ; and a                | 
    0677 fa 8b 06     ; jp m, 0x68b          | 
    067a 11 0a 00     ; ld de, 0xa           | 
    067d 19           ; add hl, de           | 
    067e 11 35 a2     ; ld de, 0xa235        | 
    0681 7b           ; ld a, e              | 
    0682 95           ; sub l                | 
    0683 7a           ; ld a, d              | 
    0684 9c           ; sbc a, h             | 
    0685 da b0 06     ; jp c, 0x6b0          | 
    0688 c3 75 06     ; jp 0x675             | 
    068b 78           ; ld a, b              | 
    068c cd 22 07     ; call 0x722           | 
    068f a7           ; and a                | 
    0690 fa b0 06     ; jp m, 0x6b0          | 
    0693 11 cd a2     ; ld de, 0xa2cd        | 
    0696 ca 9e 06     ; jp z, 0x69e          | 
    0699 13           ; inc de               | 
    069a 3d           ; dec a                | 
    069b c2 99 06     ; jp nz, 0x699         | 
    069e d5           ; push de              | 
    069f 11 8b a1     ; ld de, 0xa18b        | 
    06a2 7a           ; ld a, d              | 
    06a3 2f           ; cpl                  | 
    06a4 57           ; ld d, a              | 
    06a5 7b           ; ld a, e              | 
    06a6 2f           ; cpl                  | 
    06a7 5f           ; ld e, a              | 
    06a8 13           ; inc de               | 
    06a9 eb           ; ex de, hl            | 
    06aa 19           ; add hl, de           | 
    06ab 7d           ; ld a, l              | 
    06ac eb           ; ex de, hl            | 
    06ad d1           ; pop de               | 
    06ae 12           ; ld (de), a           | 
    06af a7           ; and a                | 
    06b0 d1           ; pop de               | 
    06b1 c9           ; ret                  | 
    06b2 d5           ; push de              | 
    06b3 78           ; ld a, b              | 
    06b4 a7           ; and a                | 
    06b5 ca ed 06     ; jp z, 0x6ed          | 
    06b8 21 8b a1     ; ld hl, 0xa18b        | 
    06bb 7e           ; ld a, (hl)           | 
    06bc a7           ; and a                | 
    06bd fa d1 06     ; jp m, 0x6d1          | 
    06c0 11 0a 00     ; ld de, 0xa           | 
    06c3 19           ; add hl, de           | 
    06c4 11 35 a2     ; ld de, 0xa235        | 
    06c7 7b           ; ld a, e              | 
    06c8 95           ; sub l                | 
    06c9 7a           ; ld a, d              | 
    06ca 9c           ; sbc a, h             | 
    06cb da b0 06     ; jp c, 0x6b0          | 
    06ce c3 bb 06     ; jp 0x6bb             | 
    06d1 78           ; ld a, b              | 
    06d2 cd 22 07     ; call 0x722           | 
    06d5 a7           ; and a                | 
    06d6 fa b0 06     ; jp m, 0x6b0          | 
    06d9 81           ; add a, c             | 
    06da 81           ; add a, c             | 
    06db 11 ad a2     ; ld de, 0xa2ad        | 
    06de ca e6 06     ; jp z, 0x6e6          | 
    06e1 13           ; inc de               | 
    06e2 3d           ; dec a                | 
    06e3 c2 e1 06     ; jp nz, 0x6e1         | 
    06e6 d5           ; push de              | 
    06e7 11 8b a1     ; ld de, 0xa18b        | 
    06ea c3 a2 06     ; jp 0x6a2             | 
    06ed 21 35 a2     ; ld hl, 0xa235        | 
    06f0 7e           ; ld a, (hl)           | 
    06f1 a7           ; and a                | 
    06f2 fa 06 07     ; jp m, 0x706          | 
    06f5 11 0a 00     ; ld de, 0xa           | 
    06f8 19           ; add hl, de           | 
    06f9 11 ac a2     ; ld de, 0xa2ac        | 
    06fc 7b           ; ld a, e              | 
    06fd 95           ; sub l                | 
    06fe 7a           ; ld a, d              | 
    06ff 9c           ; sbc a, h             | 
    0700 da b0 06     ; jp c, 0x6b0          | 
    0703 c3 f0 06     ; jp 0x6f0             | 
    0706 78           ; ld a, b              | 
    0707 cd 22 07     ; call 0x722           | 
    070a a7           ; and a                | 
    070b fa b0 06     ; jp m, 0x6b0          | 
    070e 81           ; add a, c             | 
    070f 81           ; add a, c             | 
    0710 11 ad a2     ; ld de, 0xa2ad        | 
    0713 ca 1b 07     ; jp z, 0x71b          | 
    0716 13           ; inc de               | 
    0717 3d           ; dec a                | 
    0718 c2 16 07     ; jp nz, 0x716         | 
    071b d5           ; push de              | 
    071c 11 35 a2     ; ld de, 0xa235        | 
    071f c3 a2 06     ; jp 0x6a2             | 
    0722 2b           ; dec hl               | 
    0723 77           ; ld (hl), a           | 
    0724 23           ; inc hl               | 
    0725 e5           ; push hl              | 
    0726 d5           ; push de              | 
    0727 23           ; inc hl               | 
    0728 5e           ; ld e, (hl)           | 
    0729 23           ; inc hl               | 
    072a 56           ; ld d, (hl)           | 
    072b d5           ; push de              | 
    072c 13           ; inc de               | 
    072d 13           ; inc de               | 
    072e 13           ; inc de               | 
    072f 23           ; inc hl               | 
    0730 23           ; inc hl               | 
    0731 23           ; inc hl               | 
    0732 73           ; ld (hl), e           | 
    0733 23           ; inc hl               | 
    0734 72           ; ld (hl), d           | 
    0735 23           ; inc hl               | 
    0736 d1           ; pop de               | 
    0737 73           ; ld (hl), e           | 
    0738 23           ; inc hl               | 
    0739 72           ; ld (hl), d           | 
    073a d1           ; pop de               | 
    073b e1           ; pop hl               | 
    073c 36 00        ; ld (hl), 0x0         | 
    073e c9           ; ret                  | 
    073f 76           ; halt                 | 
    0740 76           ; halt                 | 
    0741 76           ; halt                 | 
    0742 76           ; halt                 | 
    0743 76           ; halt                 | 
    0744 76           ; halt                 | 
    0745 76           ; halt                 | 
    0746 76           ; halt                 | 
    0747 76           ; halt                 | 
    0748 76           ; halt                 | 
    0749 76           ; halt                 | 
    074a 76           ; halt                 | 
    074b 3c           ; inc a                | 
    074c 53           ; ld d, e              | 
    074d 3e 76        ; ld a, 0x76           | 
    074f 76           ; halt                 | 
    0750 76           ; halt                 | 
    0751 76           ; halt                 | 
    0752 76           ; halt                 | 
    0753 76           ; halt                 | 
    0754 76           ; halt                 | 
    0755 76           ; halt                 | 
    0756 76           ; halt                 | 
    0757 76           ; halt                 | 
    0758 76           ; halt                 | 
    0759 76           ; halt                 | 
    075a 76           ; halt                 | 
    075b 76           ; halt                 | 
    075c 76           ; halt                 | 
    075d 76           ; halt                 | 
    075e 76           ; halt                 | 
    075f 76           ; halt                 | 

    ;RST3() - in (0xff)
    0760 e5           ; push hl              | 
    0761 f5           ; push af              | 
    0762 db ff        ; in a, (0xff)         | 
    0764 21 9b 42     ; ld hl, 0x429b        | 
    0767 35           ; dec (hl)             | 
    0768 c2 70 07     ; jp nz, 0x770         | 
    076b 23           ; inc hl               | 
    076c 35           ; dec (hl)             | 
    076d ca 84 07     ; jp z, 0x784          | 
    0770 21 00 40     ; ld hl, 0x4000        | 
    0773 35           ; dec (hl)             | 
    0774 c2 80 07     ; jp nz, 0x780         | 
    0777 f1           ; pop af               | 
    0778 d5           ; push de              | 
    0779 c5           ; push bc              | 
    077a f5           ; push af              | 
    077b 3e 02        ; ld a, 0x2            | 
    077d c3 cd 07     ; jp 0x7cd             | 
    0780 f1           ; pop af               | 
    0781 e1           ; pop hl               | 
    0782 fb           ; ei                   | 
    0783 c9           ; ret                  | 

    ;unexplored
    0784 3a 9d 42     ; ld a, (0x429d)       | 
    0787 a7           ; and a                | 
    0788 c2 70 07     ; jp nz, 0x770         | 
    078b 3c           ; inc a                | 
    078c 32 9d 42     ; ld (0x429d), a       | 
    078f f1           ; pop af               | 
    0790 d5           ; push de              | 
    0791 c5           ; push bc              | 
    0792 f5           ; push af              | 
    0793 0e 00        ; ld c, 0x0            | 
    0795 21 f7 17     ; ld hl, 0x17f7        | 
    0798 97           ; sub a                | 
    0799 cd ec 15     ; call 0x15ec          | 
    079c 06 00        ; ld b, 0x0            | 
    079e cd 21 06     ; call 0x621           | 
    07a1 36 00        ; ld (hl), 0x0         | 
    07a3 23           ; inc hl               | 
    07a4 5e           ; ld e, (hl)           | 
    07a5 23           ; inc hl               | 
    07a6 56           ; ld d, (hl)           | 
    07a7 13           ; inc de               | 
    07a8 13           ; inc de               | 
    07a9 13           ; inc de               | 
    07aa 23           ; inc hl               | 
    07ab 23           ; inc hl               | 
    07ac 23           ; inc hl               | 
    07ad 73           ; ld (hl), e           | 
    07ae 23           ; inc hl               | 
    07af 72           ; ld (hl), d           | 
    07b0 97           ; sub a                | 
    07b1 21 8b 42     ; ld hl, 0x428b        | 
    07b4 cd 30 15     ; call 0x1530          | 
    07b7 79           ; ld a, c              | 
    07b8 fe 0b        ; cp 0xb               | 
    07ba ca c1 07     ; jp z, 0x7c1          | 
    07bd 0c           ; inc c                | 
    07be c3 95 07     ; jp 0x795             | 
    07c1 f1           ; pop af               | 
    07c2 c1           ; pop bc               | 
    07c3 d1           ; pop de               | 
    07c4 f5           ; push af              | 
    07c5 c3 70 07     ; jp 0x770             | 
    07c8 f3           ; di                   | 
    07c9 e5           ; push hl              | 
    07ca d5           ; push de              | 
    07cb c5           ; push bc              | 
    07cc f5           ; push af              | 
    07cd f3           ; di                   | 
    07ce 2a 02 40     ; ld hl, (0x4002)      | 
    07d1 11 04 00     ; ld de, 0x4           | 
    07d4 19           ; add hl, de           | 
    07d5 77           ; ld (hl), a           | 
    07d6 23           ; inc hl               | 
    07d7 23           ; inc hl               | 
    07d8 eb           ; ex de, hl            | 
    07d9 21 00 00     ; ld hl, 0x0           | 
    07dc 39           ; add hl, sp           | 
    07dd eb           ; ex de, hl            | 
    07de 73           ; ld (hl), e           | 
    07df 23           ; inc hl               | 
    07e0 72           ; ld (hl), d           | 
    07e1 23           ; inc hl               | 
    07e2 23           ; inc hl               | 
    07e3 23           ; inc hl               | 
    07e4 23           ; inc hl               | 
    07e5 23           ; inc hl               | 
    07e6 3a 0b 40     ; ld a, (0x400b)       | 
    07e9 3d           ; dec a                | 
    07ea fa f8 07     ; jp m, 0x7f8          | 
    07ed ca 4f 08     ; jp z, 0x84f          | 
    07f0 2a 0c 40     ; ld hl, (0x400c)      | 
    07f3 3e 00        ; ld a, 0x0            | 
    07f5 32 0b 40     ; ld (0x400b), a       | 
    07f8 06 03        ; ld b, 0x3            | 
    07fa 05           ; dec b                | 
    07fb ca 5c 08     ; jp z, 0x85c          | 
    07fe 23           ; inc hl               | 
    07ff 7e           ; ld a, (hl)           | 
    0800 fe ff        ; cp 0xff              | 
    0802 2b           ; dec hl               | 
    0803 c2 0d 08     ; jp nz, 0x80d         | 
    0806 21 05 42     ; ld hl, 0x4205        | 
    0809 05           ; dec b                | 
    080a ca 5c 08     ; jp z, 0x85c          | 
    080d 22 02 40     ; ld (0x4002), hl      | 
    0810 11 04 00     ; ld de, 0x4           | 
    0813 19           ; add hl, de           | 
    0814 7e           ; ld a, (hl)           | 
    0815 fe 02        ; cp 0x2               | 
    0817 ca 3c 08     ; jp z, 0x83c          | 
    081a fe 01        ; cp 0x1               | 
    081c ca 26 08     ; jp z, 0x826          | 
    081f 11 08 00     ; ld de, 0x8           | 
    0822 19           ; add hl, de           | 
    0823 c3 fa 07     ; jp 0x7fa             | 
    0826 36 03        ; ld (hl), 0x3         | 
    0828 23           ; inc hl               | 
    0829 7e           ; ld a, (hl)           | 
    082a 32 00 40     ; ld (0x4000), a       | 
    082d 2b           ; dec hl               | 
    082e 2b           ; dec hl               | 
    082f 56           ; ld d, (hl)           | 
    0830 2b           ; dec hl               | 
    0831 5e           ; ld e, (hl)           | 
    0832 eb           ; ex de, hl            | 
    0833 f9           ; ld sp, hl            | 
    0834 eb           ; ex de, hl            | 
    0835 2b           ; dec hl               | 
    0836 56           ; ld d, (hl)           | 
    0837 2b           ; dec hl               | 
    0838 5e           ; ld e, (hl)           | 
    0839 eb           ; ex de, hl            | 
    083a fb           ; ei                   | 
    083b e9           ; jp (hl)              | 
    083c 36 03        ; ld (hl), 0x3         | 
    083e 23           ; inc hl               | 
    083f 7e           ; ld a, (hl)           | 
    0840 32 00 40     ; ld (0x4000), a       | 
    0843 23           ; inc hl               | 
    0844 5e           ; ld e, (hl)           | 
    0845 23           ; inc hl               | 
    0846 56           ; ld d, (hl)           | 
    0847 eb           ; ex de, hl            | 
    0848 f9           ; ld sp, hl            | 
    0849 f1           ; pop af               | 
    084a c1           ; pop bc               | 
    084b d1           ; pop de               | 
    084c e1           ; pop hl               | 
    084d fb           ; ei                   | 
    084e c9           ; ret                  | 
    084f 22 0c 40     ; ld (0x400c), hl      | 
    0852 21 0b 40     ; ld hl, 0x400b        | 
    0855 34           ; inc (hl)             | 
    0856 21 1f 42     ; ld hl, 0x421f        | 
    0859 c3 0d 08     ; jp 0x80d             | 
    085c 21 f9 41     ; ld hl, 0x41f9        | 
    085f 22 02 40     ; ld (0x4002), hl      | 
    0862 11 04 00     ; ld de, 0x4           | 
    0865 19           ; add hl, de           | 
    0866 c3 26 08     ; jp 0x826             | 
    0869 76           ; halt                 | 
    086a c3 69 08     ; jp 0x869             | 
    086d 76           ; halt                 | 
    086e 76           ; halt                 | 
    086f 76           ; halt                 | 
    0870 76           ; halt                 | 
    0871 76           ; halt                 | 
    0872 76           ; halt                 | 
    0873 76           ; halt                 | 
    0874 76           ; halt                 | 
    0875 76           ; halt                 | 
    0876 76           ; halt                 | 
    0877 76           ; halt                 | 
    0878 76           ; halt                 | 
    0879 76           ; halt                 | 
    087a 76           ; halt                 | 
    087b 76           ; halt                 | 
    087c 76           ; halt                 | 
    087d 76           ; halt                 | 
    087e 76           ; halt                 | 
    087f 76           ; halt                 | 

    ;RST6() - terminal io?
    0880 e5           ; push hl              | 
    0881 d5           ; push de              | 
    0882 c5           ; push bc              | 
    0883 f5           ; push af              | 
    0884 06 02        ; ld b, 0x2            | 
    0886 cd c0 0c     ; call 0xcc0           | get terminal input?
    0889 06 00        ; ld b, 0x0            | 
    088b cd 21 06     ; call 0x621           | 
    088e fe 00        ; cp 0x0               | 
    0890 ca b9 08     ; jp z, 0x8b9          | 
    0893 fe 01        ; cp 0x1               | 
    0895 ca b9 08     ; jp z, 0x8b9          | 
    0898 21 04 0c     ; ld hl, 0xc04         | 
    089b cd 45 0d     ; call 0xd45           | 
    089e c3 b3 08     ; jp 0x8b3             | 
    08a1 21 04 0c     ; ld hl, 0xc04         | 
    08a4 cd 45 0d     ; call 0xd45           | 
    08a7 fe 7f        ; cp 0x7f              | 
    08a9 c2 b3 08     ; jp nz, 0x8b3         | 
    08ac 06 00        ; ld b, 0x0            | 
    08ae cd 21 06     ; call 0x621           | 
    08b1 36 01        ; ld (hl), 0x1         | 
    08b3 f1           ; pop af               | 
    08b4 c1           ; pop bc               | 
    08b5 d1           ; pop de               | 
    08b6 e1           ; pop hl               | 
    08b7 fb           ; ei                   | 
    08b8 c9           ; ret                  | 

    ;unexplored
    08b9 06 01        ; ld b, 0x1            | 
    08bb cd 21 06     ; call 0x621           | 
    08be fe 06        ; cp 0x6               | 
    08c0 ca a1 08     ; jp z, 0x8a1          | 
    08c3 fe 01        ; cp 0x1               | 
    08c5 ca a1 08     ; jp z, 0x8a1          | 
    08c8 21 04 0c     ; ld hl, 0xc04         | 
    08cb cd 45 0d     ; call 0xd45           | 
    08ce f5           ; push af              | 
    08cf 06 00        ; ld b, 0x0            | 
    08d1 cd 21 06     ; call 0x621           | 
    08d4 36 01        ; ld (hl), 0x1         | 
    08d6 23           ; inc hl               | 
    08d7 23           ; inc hl               | 
    08d8 23           ; inc hl               | 
    08d9 23           ; inc hl               | 
    08da 23           ; inc hl               | 
    08db 5e           ; ld e, (hl)           | 
    08dc 23           ; inc hl               | 
    08dd 56           ; ld d, (hl)           | 
    08de f1           ; pop af               | 
    08df fe 0d        ; cp 0xd               | 
    08e1 ca fc 08     ; jp z, 0x8fc          | 
    08e4 fe 13        ; cp 0x13              | 
    08e6 c2 2f 09     ; jp nz, 0x92f         | 
    08e9 f5           ; push af              | 
    08ea e5           ; push hl              | 
    08eb 21 7b 42     ; ld hl, 0x427b        | 
    08ee cd 29 15     ; call 0x1529          | 
    08f1 a7           ; and a                | 
    08f2 ca 25 09     ; jp z, 0x925          | 
    08f5 e1           ; pop hl               | 
    08f6 f1           ; pop af               | 
    08f7 1b           ; dec de               | 
    08f8 1b           ; dec de               | 
    08f9 c3 34 09     ; jp 0x934             | 
    08fc f5           ; push af              | 
    08fd e5           ; push hl              | 
    08fe 21 7b 42     ; ld hl, 0x427b        | 
    0901 cd 29 15     ; call 0x1529          | 
    0904 a7           ; and a                | 
    0905 ca 2a 09     ; jp z, 0x92a          | 
    0908 e1           ; pop hl               | 
    0909 f1           ; pop af               | 
    090a d5           ; push de              | 
    090b e5           ; push hl              | 
    090c c5           ; push bc              | 
    090d 2b           ; dec hl               | 
    090e 2b           ; dec hl               | 
    090f 2b           ; dec hl               | 
    0910 2b           ; dec hl               | 
    0911 56           ; ld d, (hl)           | 
    0912 2b           ; dec hl               | 
    0913 5e           ; ld e, (hl)           | 
    0914 13           ; inc de               | 
    0915 13           ; inc de               | 
    0916 13           ; inc de               | 
    0917 1a           ; ld a, (de)           | 
    0918 fe 3a        ; cp 0x3a              | 
    091a ca 47 09     ; jp z, 0x947          | 
    091d c1           ; pop bc               | 
    091e e1           ; pop hl               | 
    091f d1           ; pop de               | 
    0920 3e 0d        ; ld a, 0xd            | 
    0922 c3 35 0a     ; jp 0xa35             | 
    0925 e1           ; pop hl               | 
    0926 f1           ; pop af               | 
    0927 c3 db 09     ; jp 0x9db             | 
    092a e1           ; pop hl               | 
    092b f1           ; pop af               | 
    092c c3 34 09     ; jp 0x934             | 
    092f fe 03        ; cp 0x3               | 
    0931 c2 db 09     ; jp nz, 0x9db         | 
    0934 d5           ; push de              | 
    0935 e5           ; push hl              | 
    0936 c5           ; push bc              | 
    0937 2b           ; dec hl               | 
    0938 2b           ; dec hl               | 
    0939 2b           ; dec hl               | 
    093a 2b           ; dec hl               | 
    093b 56           ; ld d, (hl)           | 
    093c 2b           ; dec hl               | 
    093d 5e           ; ld e, (hl)           | 
    093e 13           ; inc de               | 
    093f 13           ; inc de               | 
    0940 13           ; inc de               | 
    0941 1a           ; ld a, (de)           | 
    0942 fe 3a        ; cp 0x3a              | 
    0944 c2 7a 09     ; jp nz, 0x97a         | 
    0947 d5           ; push de              | 
    0948 eb           ; ex de, hl            | 
    0949 23           ; inc hl               | 
    094a 11 9e 16     ; ld de, 0x169e        | de = ASC128,ON
    094d cd 00 15     ; call 0x1500          | 
    0950 cd 37 15     ; call 0x1537          | 
    0953 cd ec 15     ; call 0x15ec          | 
    0956 d1           ; pop de               | 
    0957 3e 20        ; ld a, 0x20           | 
    0959 12           ; ld (de), a           | 
    095a c1           ; pop bc               | 
    095b e1           ; pop hl               | 
    095c 72           ; ld (hl), d           | 
    095d 2b           ; dec hl               | 
    095e 73           ; ld (hl), e           | 
    095f 13           ; inc de               | 
    0960 12           ; ld (de), a           | 
    0961 13           ; inc de               | 
    0962 12           ; ld (de), a           | 
    0963 13           ; inc de               | 
    0964 12           ; ld (de), a           | 
    0965 13           ; inc de               | 
    0966 12           ; ld (de), a           | 
    0967 2b           ; dec hl               | 
    0968 2b           ; dec hl               | 
    0969 2b           ; dec hl               | 
    096a 2b           ; dec hl               | 
    096b 2b           ; dec hl               | 
    096c 2b           ; dec hl               | 
    096d 7e           ; ld a, (hl)           | 
    096e fe ff        ; cp 0xff              | 
    0970 c2 76 09     ; jp nz, 0x976         | 
    0973 23           ; inc hl               | 
    0974 36 ff        ; ld (hl), 0xff        | 
    0976 d1           ; pop de               | 
    0977 c3 b3 08     ; jp 0x8b3             | 
    097a 3a 9d 42     ; ld a, (0x429d)       | 
    097d a7           ; and a                | 
    097e ca 8b 09     ; jp z, 0x98b          | 
    0981 d5           ; push de              | 
    0982 21 2a 18     ; ld hl, 0x182a        | hl = A[CYBER LINK DOWN]
    0985 cd ec 15     ; call 0x15ec          | 
    0988 c3 56 09     ; jp 0x956             | 
    098b 21 8b 42     ; ld hl, 0x428b        | 
    098e cd 29 15     ; call 0x1529          | 
    0991 a7           ; and a                | 
    0992 c2 c0 09     ; jp nz, 0x9c0         | 
    0995 d5           ; push de              | 
    0996 79           ; ld a, c              | 
    0997 fe 08        ; cp 0x8               | 
    0999 f2 aa 09     ; jp p, 0x9aa          | 
    099c 3e 36        ; ld a, 0x36           | 
    099e 32 bc 42     ; ld (0x42bc), a       | 
    09a1 3e 30        ; ld a, 0x30           | 
    09a3 81           ; add a, c             | 
    09a4 32 bd 42     ; ld (0x42bd), a       | 
    09a7 c3 b7 09     ; jp 0x9b7             | 
    09aa 3e 37        ; ld a, 0x37           | 
    09ac 32 bc 42     ; ld (0x42bc), a       | 
    09af 79           ; ld a, c              | 
    09b0 d6 08        ; sub 0x8              | 
    09b2 c6 30        ; add a, 0x30          | 
    09b4 32 bd 42     ; ld (0x42bd), a       | 
    09b7 21 9e 42     ; ld hl, 0x429e        | 
    09ba cd ec 15     ; call 0x15ec          | 
    09bd c3 56 09     ; jp 0x956             | 
    09c0 c1           ; pop bc               | 
    09c1 e1           ; pop hl               | 
    09c2 d1           ; pop de               | 
    09c3 c3 c6 09     ; jp 0x9c6             | 
    09c6 3e 1b        ; ld a, 0x1b           | 
    09c8 12           ; ld (de), a           | 
    09c9 13           ; inc de               | 
    09ca 3e 42        ; ld a, 0x42           | 
    09cc 12           ; ld (de), a           | 
    09cd 13           ; inc de               | 
    09ce 72           ; ld (hl), d           | 
    09cf 2b           ; dec hl               | 
    09d0 73           ; ld (hl), e           | 
    09d1 2b           ; dec hl               | 
    09d2 2b           ; dec hl               | 
    09d3 2b           ; dec hl               | 
    09d4 2b           ; dec hl               | 
    09d5 2b           ; dec hl               | 
    09d6 36 02        ; ld (hl), 0x2         | 
    09d8 c3 b3 08     ; jp 0x8b3             | 
    09db fe 01        ; cp 0x1               | 
    09dd c2 e5 09     ; jp nz, 0x9e5         | 
    09e0 06 51        ; ld b, 0x51           | 
    09e2 c3 30 0a     ; jp 0xa30             | 
    09e5 fe 16        ; cp 0x16              | 
    09e7 c2 ef 09     ; jp nz, 0x9ef         | 
    09ea 06 52        ; ld b, 0x52           | 
    09ec c3 30 0a     ; jp 0xa30             | 
    09ef fe 1b        ; cp 0x1b              | 
    09f1 c2 f9 09     ; jp nz, 0x9f9         | 
    09f4 3e 54        ; ld a, 0x54           | 
    09f6 c3 30 0a     ; jp 0xa30             | 
    09f9 fe 08        ; cp 0x8               | 
    09fb c2 35 0a     ; jp nz, 0xa35         | 
    09fe 1b           ; dec de               | 
    09ff e5           ; push hl              | 
    0a00 d5           ; push de              | 
    0a01 2b           ; dec hl               | 
    0a02 2b           ; dec hl               | 
    0a03 2b           ; dec hl               | 
    0a04 2b           ; dec hl               | 
    0a05 56           ; ld d, (hl)           | 
    0a06 2b           ; dec hl               | 
    0a07 5e           ; ld e, (hl)           | 
    0a08 13           ; inc de               | 
    0a09 13           ; inc de               | 
    0a0a e1           ; pop hl               | 
    0a0b e5           ; push hl              | 
    0a0c 7b           ; ld a, e              | 
    0a0d 95           ; sub l                | 
    0a0e 7a           ; ld a, d              | 
    0a0f 9c           ; sbc a, h             | 
    0a10 da 20 0a     ; jp c, 0xa20          | 
    0a13 d1           ; pop de               | 
    0a14 e1           ; pop hl               | 
    0a15 3e 0c        ; ld a, 0xc            | 
    0a17 21 33 0c     ; ld hl, 0xc33         | 
    0a1a cd 45 0d     ; call 0xd45           | 
    0a1d c3 b3 08     ; jp 0x8b3             | 
    0a20 d1           ; pop de               | 
    0a21 e1           ; pop hl               | 
    0a22 1b           ; dec de               | 
    0a23 1a           ; ld a, (de)           | 
    0a24 fe 1b        ; cp 0x1b              | 
    0a26 13           ; inc de               | 
    0a27 ca 15 0a     ; jp z, 0xa15          | 
    0a2a 72           ; ld (hl), d           | 
    0a2b 2b           ; dec hl               | 
    0a2c 73           ; ld (hl), e           | 
    0a2d c3 b3 08     ; jp 0x8b3             | 
    0a30 3e 1b        ; ld a, 0x1b           | 
    0a32 12           ; ld (de), a           | 
    0a33 13           ; inc de               | 
    0a34 78           ; ld a, b              | 
    0a35 12           ; ld (de), a           | 
    0a36 13           ; inc de               | 
    0a37 d5           ; push de              | 
    0a38 e5           ; push hl              | 
    0a39 2b           ; dec hl               | 
    0a3a 2b           ; dec hl               | 
    0a3b 13           ; inc de               | 
    0a3c 13           ; inc de               | 
    0a3d 13           ; inc de               | 
    0a3e 2b           ; dec hl               | 
    0a3f 7b           ; ld a, e              | 
    0a40 96           ; sub (hl)             | 
    0a41 7a           ; ld a, d              | 
    0a42 23           ; inc hl               | 
    0a43 9e           ; sbc a, (hl)          | 
    0a44 da 54 0a     ; jp c, 0xa54          | 
    0a47 3e 0d        ; ld a, 0xd            | 
    0a49 21 33 0c     ; ld hl, 0xc33         | 
    0a4c cd 45 0d     ; call 0xd45           | 
    0a4f e1           ; pop hl               | 
    0a50 d1           ; pop de               | 
    0a51 c3 34 09     ; jp 0x934             | 
    0a54 e1           ; pop hl               | 
    0a55 d1           ; pop de               | 
    0a56 72           ; ld (hl), d           | 
    0a57 2b           ; dec hl               | 
    0a58 73           ; ld (hl), e           | 
    0a59 c3 b3 08     ; jp 0x8b3             | 
    0a5c 06 01        ; ld b, 0x1            | 
    0a5e cd 21 06     ; call 0x621           | 
    0a61 fe 06        ; cp 0x6               | 
    0a63 ca 7a 0a     ; jp z, 0xa7a          | 
    0a66 fe 01        ; cp 0x1               | 
    0a68 ca a0 0a     ; jp z, 0xaa0          | 
    0a6b 79           ; ld a, c              | 
    0a6c fe 0b        ; cp 0xb               | 
    0a6e f2 75 0a     ; jp p, 0xa75          | 
    0a71 0c           ; inc c                | 
    0a72 c3 5c 0a     ; jp 0xa5c             | 
    0a75 0e 00        ; ld c, 0x0            | 
    0a77 c3 5c 0a     ; jp 0xa5c             | 
    0a7a e5           ; push hl              | 
    0a7b d5           ; push de              | 
    0a7c 23           ; inc hl               | 
    0a7d 23           ; inc hl               | 
    0a7e 23           ; inc hl               | 
    0a7f 23           ; inc hl               | 
    0a80 23           ; inc hl               | 
    0a81 5e           ; ld e, (hl)           | 
    0a82 23           ; inc hl               | 
    0a83 56           ; ld d, (hl)           | 
    0a84 23           ; inc hl               | 
    0a85 7e           ; ld a, (hl)           | 
    0a86 23           ; inc hl               | 
    0a87 bb           ; cp e                 | 
    0a88 c2 97 0a     ; jp nz, 0xa97         | 
    0a8b 7e           ; ld a, (hl)           | 
    0a8c ba           ; cp d                 | 
    0a8d c2 97 0a     ; jp nz, 0xa97         | 
    0a90 d1           ; pop de               | 
    0a91 e1           ; pop hl               | 
    0a92 36 05        ; ld (hl), 0x5         | 
    0a94 c3 6b 0a     ; jp 0xa6b             | 
    0a97 cd 65 0d     ; call 0xd65           | 
    0a9a 36 fe        ; ld (hl), 0xfe        | 
    0a9c d1           ; pop de               | 
    0a9d e1           ; pop hl               | 
    0a9e 36 01        ; ld (hl), 0x1         | 
    0aa0 e5           ; push hl              | 
    0aa1 21 62 0c     ; ld hl, 0xc62         | 
    0aa4 cd 45 0d     ; call 0xd45           | 
    0aa7 e1           ; pop hl               | 
    0aa8 e6 01        ; and 0x1              | 
    0aaa ca 6b 0a     ; jp z, 0xa6b          | 
    0aad 23           ; inc hl               | 
    0aae 23           ; inc hl               | 
    0aaf 23           ; inc hl               | 
    0ab0 23           ; inc hl               | 
    0ab1 23           ; inc hl               | 
    0ab2 23           ; inc hl               | 
    0ab3 23           ; inc hl               | 
    0ab4 5e           ; ld e, (hl)           | 
    0ab5 23           ; inc hl               | 
    0ab6 56           ; ld d, (hl)           | 
    0ab7 1a           ; ld a, (de)           | 
    0ab8 fe 1b        ; cp 0x1b              | 
    0aba ca 52 0b     ; jp z, 0xb52          | 
    0abd e5           ; push hl              | 
    0abe f5           ; push af              | 
    0abf cd 65 0d     ; call 0xd65           | 
    0ac2 34           ; inc (hl)             | 
    0ac3 3e 50        ; ld a, 0x50           | 
    0ac5 be           ; cp (hl)              | 
    0ac6 c2 e2 0a     ; jp nz, 0xae2         | 
    0ac9 36 00        ; ld (hl), 0x0         | 
    0acb cd 6f 0d     ; call 0xd6f           | 
    0ace a7           ; and a                | 
    0acf ca e2 0a     ; jp z, 0xae2          | 
    0ad2 13           ; inc de               | 
    0ad3 1a           ; ld a, (de)           | 
    0ad4 fe 1b        ; cp 0x1b              | 
    0ad6 1b           ; dec de               | 
    0ad7 ca e2 0a     ; jp z, 0xae2          | 
    0ada 3e 41        ; ld a, 0x41           | 
    0adc 12           ; ld (de), a           | 
    0add 1b           ; dec de               | 
    0ade 3e 1b        ; ld a, 0x1b           | 
    0ae0 12           ; ld (de), a           | 
    0ae1 1b           ; dec de               | 
    0ae2 cd 5b 0d     ; call 0xd5b           | 
    0ae5 a7           ; and a                | 
    0ae6 ca 2d 0b     ; jp z, 0xb2d          | 
    0ae9 f1           ; pop af               | 
    0aea f5           ; push af              | 
    0aeb fe 7e        ; cp 0x7e              | 
    0aed c2 17 0b     ; jp nz, 0xb17         | 
    0af0 cd 65 0d     ; call 0xd65           | 
    0af3 fe 00        ; cp 0x0               | 
    0af5 ca 02 0b     ; jp z, 0xb02          | 
    0af8 cd 51 0d     ; call 0xd51           | 
    0afb 36 01        ; ld (hl), 0x1         | 
    0afd f1           ; pop af               | 
    0afe e1           ; pop hl               | 
    0aff c3 31 0b     ; jp 0xb31             | 
    0b02 36 00        ; ld (hl), 0x0         | 
    0b04 cd 51 0d     ; call 0xd51           | 
    0b07 e5           ; push hl              | 
    0b08 cd 6f 0d     ; call 0xd6f           | 
    0b0b a7           ; and a                | 
    0b0c e1           ; pop hl               | 
    0b0d 36 01        ; ld (hl), 0x1         | 
    0b0f c2 fd 0a     ; jp nz, 0xafd         | 
    0b12 36 00        ; ld (hl), 0x0         | 
    0b14 c3 fd 0a     ; jp 0xafd             | 
    0b17 cd 51 0d     ; call 0xd51           | 
    0b1a a7           ; and a                | 
    0b1b ca 2d 0b     ; jp z, 0xb2d          | 
    0b1e 36 00        ; ld (hl), 0x0         | 
    0b20 f1           ; pop af               | 
    0b21 ee 40        ; xor 0x40             | 
    0b23 21 33 0c     ; ld hl, 0xc33         | 
    0b26 cd 45 0d     ; call 0xd45           | 
    0b29 e1           ; pop hl               | 
    0b2a c3 31 0b     ; jp 0xb31             | 
    0b2d f1           ; pop af               | 
    0b2e c3 23 0b     ; jp 0xb23             | 
    0b31 e5           ; push hl              | 
    0b32 13           ; inc de               | 
    0b33 2b           ; dec hl               | 
    0b34 2b           ; dec hl               | 
    0b35 7e           ; ld a, (hl)           | 
    0b36 2b           ; dec hl               | 
    0b37 ba           ; cp d                 | 
    0b38 c2 4b 0b     ; jp nz, 0xb4b         | 
    0b3b 7e           ; ld a, (hl)           | 
    0b3c bb           ; cp e                 | 
    0b3d c2 4b 0b     ; jp nz, 0xb4b         | 
    0b40 2b           ; dec hl               | 
    0b41 2b           ; dec hl               | 
    0b42 2b           ; dec hl               | 
    0b43 2b           ; dec hl               | 
    0b44 2b           ; dec hl               | 
    0b45 36 05        ; ld (hl), 0x5         | 
    0b47 e1           ; pop hl               | 
    0b48 c3 6b 0a     ; jp 0xa6b             | 
    0b4b e1           ; pop hl               | 
    0b4c 72           ; ld (hl), d           | 
    0b4d 2b           ; dec hl               | 
    0b4e 73           ; ld (hl), e           | 
    0b4f c3 6b 0a     ; jp 0xa6b             | 
    0b52 13           ; inc de               | 
    0b53 1a           ; ld a, (de)           | 
    0b54 fe 51        ; cp 0x51              | 
    0b56 f2 61 0b     ; jp p, 0xb61          | 
    0b59 fe 41        ; cp 0x41              | 
    0b5b f2 89 0b     ; jp p, 0xb89          | 
    0b5e c3 31 0b     ; jp 0xb31             | 
    0b61 fe 51        ; cp 0x51              | 
    0b63 c2 6b 0b     ; jp nz, 0xb6b         | 
    0b66 3e 01        ; ld a, 0x1            | 
    0b68 c3 bd 0a     ; jp 0xabd             | 
    0b6b fe 52        ; cp 0x52              | 
    0b6d c2 75 0b     ; jp nz, 0xb75         | 
    0b70 3e 16        ; ld a, 0x16           | 
    0b72 c3 bd 0a     ; jp 0xabd             | 
    0b75 fe 53        ; cp 0x53              | 
    0b77 c2 7f 0b     ; jp nz, 0xb7f         | 
    0b7a 3e 03        ; ld a, 0x3            | 
    0b7c c3 bd 0a     ; jp 0xabd             | 
    0b7f fe 54        ; cp 0x54              | 
    0b81 c2 31 0b     ; jp nz, 0xb31         | 
    0b84 3e 1b        ; ld a, 0x1b           | 
    0b86 c3 bd 0a     ; jp 0xabd             | 
    0b89 fe 42        ; cp 0x42              | 
    0b8b f2 e5 0b     ; jp p, 0xbe5          | 
    0b8e e5           ; push hl              | 
    0b8f cd 5b 0d     ; call 0xd5b           | 
    0b92 a7           ; and a                | 
    0b93 ca b0 0b     ; jp z, 0xbb0          | 
    0b96 cd 51 0d     ; call 0xd51           | 
    0b99 a7           ; and a                | 
    0b9a ca b0 0b     ; jp z, 0xbb0          | 
    0b9d cd 65 0d     ; call 0xd65           | 
    0ba0 fe 00        ; cp 0x0               | 
    0ba2 da c6 0b     ; jp c, 0xbc6          | 
    0ba5 36 00        ; ld (hl), 0x0         | 
    0ba7 cd 51 0d     ; call 0xd51           | 
    0baa 36 00        ; ld (hl), 0x0         | 
    0bac e1           ; pop hl               | 
    0bad c3 31 0b     ; jp 0xb31             | 
    0bb0 cd 65 0d     ; call 0xd65           | 
    0bb3 fe 01        ; cp 0x1               | 
    0bb5 d2 c6 0b     ; jp nc, 0xbc6         | 
    0bb8 cd 6f 0d     ; call 0xd6f           | 
    0bbb a7           ; and a                | 
    0bbc ca df 0b     ; jp z, 0xbdf          | 
    0bbf cd 51 0d     ; call 0xd51           | 
    0bc2 a7           ; and a                | 
    0bc3 c2 df 0b     ; jp nz, 0xbdf         | 
    0bc6 cd 51 0d     ; call 0xd51           | 
    0bc9 36 00        ; ld (hl), 0x0         | 
    0bcb cd 65 0d     ; call 0xd65           | 
    0bce 36 00        ; ld (hl), 0x0         | 
    0bd0 3e 0d        ; ld a, 0xd            | 
    0bd2 21 33 0c     ; ld hl, 0xc33         | 
    0bd5 cd 45 0d     ; call 0xd45           | 
    0bd8 3e 42        ; ld a, 0x42           | 
    0bda 12           ; ld (de), a           | 
    0bdb e1           ; pop hl               | 
    0bdc c3 6b 0a     ; jp 0xa6b             | 
    0bdf cd 65 0d     ; call 0xd65           | 
    0be2 c3 a5 0b     ; jp 0xba5             | 
    0be5 fe 46        ; cp 0x46              | 
    0be7 c2 f7 0b     ; jp nz, 0xbf7         | 
    0bea 3e 0a        ; ld a, 0xa            | 
    0bec e5           ; push hl              | 
    0bed 21 33 0c     ; ld hl, 0xc33         | 
    0bf0 cd 45 0d     ; call 0xd45           | 
    0bf3 e1           ; pop hl               | 
    0bf4 c3 31 0b     ; jp 0xb31             | 
    0bf7 3c           ; inc a                | 
    0bf8 12           ; ld (de), a           | 
    0bf9 3e 00        ; ld a, 0x0            | 
    0bfb 21 33 0c     ; ld hl, 0xc33         | 
    0bfe cd 45 0d     ; call 0xd45           | 
    0c01 c3 6b 0a     ; jp 0xa6b             | 
    0c04 db 60        ; in a, (0x60)         | read character from terminal  1
    0c06 c9           ; ret                  | 
    0c07 00           ; nop                  | 
    0c08 db 62        ; in a, (0x62)         | read character from terminal  2
    0c0a c9           ; ret                  | 
    0c0b 00           ; nop                  | 
    0c0c db 64        ; in a, (0x64)         | read character from terminal  3
    0c0e c9           ; ret                  | 
    0c0f 00           ; nop                  | 
    0c10 db 66        ; in a, (0x66)         | read character from terminal  4
    0c12 c9           ; ret                  | 
    0c13 00           ; nop                  | 
    0c14 db 68        ; in a, (0x68)         | read character from terminal  5
    0c16 c9           ; ret                  | 
    0c17 00           ; nop                  | 
    0c18 db 6a        ; in a, (0x6a)         | read character from terminal  6
    0c1a c9           ; ret                  | 
    0c1b 00           ; nop                  | 
    0c1c db 6c        ; in a, (0x6c)         | read character from terminal  7
    0c1e c9           ; ret                  | 
    0c1f 00           ; nop                  | 
    0c20 db 6e        ; in a, (0x6e)         | read character from terminal  8
    0c22 c9           ; ret                  | 
    0c23 00           ; nop                  | 
    0c24 db 70        ; in a, (0x70)         | read character from terminal  9
    0c26 c9           ; ret                  | 
    0c27 00           ; nop                  | 
    0c28 db 72        ; in a, (0x72)         | read character from terminal 10
    0c2a c9           ; ret                  | 
    0c2b 00           ; nop                  | 
    0c2c db 74        ; in a, (0x74)         | read character from terminal 11
    0c2e c9           ; ret                  | 
    0c2f 00           ; nop                  | 
    0c30 db 76        ; in a, (0x76)         | read character from terminal 12
    0c32 c9           ; ret                  | 
    0c33 d3 60        ; out (0x60), a        | write character to terminal  1
    0c35 c9           ; ret                  | 
    0c36 00           ; nop                  | 
    0c37 d3 62        ; out (0x62), a        | write character to terminal  2
    0c39 c9           ; ret                  | 
    0c3a 00           ; nop                  | 
    0c3b d3 64        ; out (0x64), a        | write character to terminal  3
    0c3d c9           ; ret                  | 
    0c3e 00           ; nop                  | 
    0c3f d3 66        ; out (0x66), a        | write character to terminal  4
    0c41 c9           ; ret                  | 
    0c42 00           ; nop                  | 
    0c43 d3 68        ; out (0x68), a        | write character to terminal  5
    0c45 c9           ; ret                  | 
    0c46 00           ; nop                  | 
    0c47 d3 6a        ; out (0x6a), a        | write character to terminal  6
    0c49 c9           ; ret                  | 
    0c4a 00           ; nop                  | 
    0c4b d3 6c        ; out (0x6c), a        | write character to terminal  7
    0c4d c9           ; ret                  | 
    0c4e 00           ; nop                  | 
    0c4f d3 6e        ; out (0x6e), a        | write character to terminal  8
    0c51 c9           ; ret                  | 
    0c52 00           ; nop                  | 
    0c53 d3 70        ; out (0x70), a        | write character to terminal  9
    0c55 c9           ; ret                  | 
    0c56 00           ; nop                  | 
    0c57 d3 72        ; out (0x72), a        | write character to terminal 10
    0c59 c9           ; ret                  | 
    0c5a 00           ; nop                  | 
    0c5b d3 74        ; out (0x74), a        | write character to terminal 11
    0c5d c9           ; ret                  | 
    0c5e 00           ; nop                  | 
    0c5f d3 76        ; out (0x76), a        | write character to terminal 12
    0c61 c9           ; ret                  | 
    0c62 db 61        ; in a, (0x61)         | 
    0c64 c9           ; ret                  | 
    0c65 00           ; nop                  | 
    0c66 db 63        ; in a, (0x63)         | 
    0c68 c9           ; ret                  | 
    0c69 00           ; nop                  | 
    0c6a db 65        ; in a, (0x65)         | 
    0c6c c9           ; ret                  | 
    0c6d 00           ; nop                  | 
    0c6e db 67        ; in a, (0x67)         | 
    0c70 c9           ; ret                  | 
    0c71 00           ; nop                  | 
    0c72 db 69        ; in a, (0x69)         | 
    0c74 c9           ; ret                  | 
    0c75 00           ; nop                  | 
    0c76 db 6b        ; in a, (0x6b)         | 
    0c78 c9           ; ret                  | 
    0c79 00           ; nop                  | 
    0c7a db 6d        ; in a, (0x6d)         | 
    0c7c c9           ; ret                  | 
    0c7d 00           ; nop                  | 
    0c7e db 6f        ; in a, (0x6f)         | 
    0c80 c9           ; ret                  | 
    0c81 00           ; nop                  | 
    0c82 db 71        ; in a, (0x71)         | 
    0c84 c9           ; ret                  | 
    0c85 00           ; nop                  | 
    0c86 db 73        ; in a, (0x73)         | 
    0c88 c9           ; ret                  | 
    0c89 00           ; nop                  | 
    0c8a db 75        ; in a, (0x75)         | 
    0c8c c9           ; ret                  | 
    0c8d 00           ; nop                  | 
    0c8e db 77        ; in a, (0x77)         | 
    0c90 c9           ; ret                  | 
    0c91 d3 61        ; out (0x61), a        | 
    0c93 c9           ; ret                  | 
    0c94 00           ; nop                  | 
    0c95 d3 63        ; out (0x63), a        | 
    0c97 c9           ; ret                  | 
    0c98 00           ; nop                  | 
    0c99 d3 65        ; out (0x65), a        | 
    0c9b c9           ; ret                  | 
    0c9c 00           ; nop                  | 
    0c9d d3 67        ; out (0x67), a        | 
    0c9f c9           ; ret                  | 
    0ca0 00           ; nop                  | 
    0ca1 d3 69        ; out (0x69), a        | 
    0ca3 c9           ; ret                  | 
    0ca4 00           ; nop                  | 
    0ca5 d3 6b        ; out (0x6b), a        | 
    0ca7 c9           ; ret                  | 
    0ca8 00           ; nop                  | 
    0ca9 d3 6d        ; out (0x6d), a        | 
    0cab c9           ; ret                  | 
    0cac 00           ; nop                  | 
    0cad d3 6f        ; out (0x6f), a        | 
    0caf c9           ; ret                  | 
    0cb0 00           ; nop                  | 
    0cb1 d3 71        ; out (0x71), a        | 
    0cb3 c9           ; ret                  | 
    0cb4 00           ; nop                  | 
    0cb5 d3 73        ; out (0x73), a        | 
    0cb7 c9           ; ret                  | 
    0cb8 00           ; nop                  | 
    0cb9 d3 75        ; out (0x75), a        | 
    0cbb c9           ; ret                  | 
    0cbc 00           ; nop                  | 
    0cbd d3 77        ; out (0x77), a        | 
    0cbf c9           ; ret                  | 
    0cc0 0e 0b        ; ld c, 0xb            | (b = 2) c = 11
    0cc2 0c           ; inc c                | c = 12
    0cc3 db 61        ; in a, (0x61)         | get terminal 1 status
    0cc5 a0           ; and b                | check if bit 2 is set (has data?)
    0cc6 c2 3b 0d     ; jp nz, 0xd3b         | 
    0cc9 0d           ; dec c                | 
    0cca ca 41 0d     ; jp z, 0xd41          | 
    0ccd db 63        ; in a, (0x63)         | 
    0ccf a0           ; and b                | 
    0cd0 c2 3b 0d     ; jp nz, 0xd3b         | 
    0cd3 0d           ; dec c                | 
    0cd4 ca 41 0d     ; jp z, 0xd41          | 
    0cd7 db 65        ; in a, (0x65)         | 
    0cd9 a0           ; and b                | 
    0cda c2 3b 0d     ; jp nz, 0xd3b         | 
    0cdd 0d           ; dec c                | 
    0cde ca 41 0d     ; jp z, 0xd41          | 
    0ce1 db 67        ; in a, (0x67)         | 
    0ce3 a0           ; and b                | 
    0ce4 c2 3b 0d     ; jp nz, 0xd3b         | 
    0ce7 0d           ; dec c                | 
    0ce8 ca 41 0d     ; jp z, 0xd41          | 
    0ceb db 69        ; in a, (0x69)         | 
    0ced a0           ; and b                | 
    0cee c2 3b 0d     ; jp nz, 0xd3b         | 
    0cf1 0d           ; dec c                | 
    0cf2 ca 41 0d     ; jp z, 0xd41          | 
    0cf5 db 6b        ; in a, (0x6b)         | 
    0cf7 a0           ; and b                | 
    0cf8 c2 3b 0d     ; jp nz, 0xd3b         | 
    0cfb 0d           ; dec c                | 
    0cfc ca 41 0d     ; jp z, 0xd41          | 
    0cff db 6d        ; in a, (0x6d)         | 
    0d01 a0           ; and b                | 
    0d02 c2 3b 0d     ; jp nz, 0xd3b         | 
    0d05 0d           ; dec c                | 
    0d06 ca 41 0d     ; jp z, 0xd41          | 
    0d09 db 6f        ; in a, (0x6f)         | 
    0d0b a0           ; and b                | 
    0d0c c2 3b 0d     ; jp nz, 0xd3b         | 
    0d0f 0d           ; dec c                | 
    0d10 ca 41 0d     ; jp z, 0xd41          | 
    0d13 db 71        ; in a, (0x71)         | 
    0d15 a0           ; and b                | 
    0d16 c2 3b 0d     ; jp nz, 0xd3b         | 
    0d19 0d           ; dec c                | 
    0d1a ca 41 0d     ; jp z, 0xd41          | 
    0d1d db 73        ; in a, (0x73)         | 
    0d1f a0           ; and b                | 
    0d20 c2 3b 0d     ; jp nz, 0xd3b         | 
    0d23 0d           ; dec c                | 
    0d24 ca 41 0d     ; jp z, 0xd41          | 
    0d27 db 75        ; in a, (0x75)         | 
    0d29 a0           ; and b                | 
    0d2a c2 3b 0d     ; jp nz, 0xd3b         | 
    0d2d 0d           ; dec c                | 
    0d2e ca 41 0d     ; jp z, 0xd41          | 
    0d31 db 77        ; in a, (0x77)         | 
    0d33 a0           ; and b                | 
    0d34 c2 3b 0d     ; jp nz, 0xd3b         | 
    0d37 0d           ; dec c                | 
    0d38 ca 41 0d     ; jp z, 0xd41          | 
    0d3b 3e 0b        ; ld a, 0xb            | 
    0d3d 3c           ; inc a                | 
    0d3e 91           ; sub c                | 
    0d3f 4f           ; ld c, a              | 
    0d40 c9           ; ret                  | 
    0d41 e1           ; pop hl               | 
    0d42 c3 b3 08     ; jp 0x8b3             | 
    0d45 47           ; ld b, a              | 
    0d46 79           ; ld a, c              | 
    0d47 07           ; rlca                 | 
    0d48 07           ; rlca                 | 
    0d49 d5           ; push de              | 
    0d4a 5f           ; ld e, a              | 
    0d4b 16 00        ; ld d, 0x0            | 
    0d4d 19           ; add hl, de           | 
    0d4e d1           ; pop de               | 
    0d4f 78           ; ld a, b              | 
    0d50 e9           ; jp (hl)              | 
    0d51 c5           ; push bc              | 
    0d52 06 00        ; ld b, 0x0            | 
    0d54 21 2b 42     ; ld hl, 0x422b        | 
    0d57 09           ; add hl, bc           | 
    0d58 7e           ; ld a, (hl)           | 
    0d59 c1           ; pop bc               | 
    0d5a c9           ; ret                  | 
    0d5b c5           ; push bc              | 
    0d5c 06 00        ; ld b, 0x0            | 
    0d5e 21 3b 42     ; ld hl, 0x423b        | 
    0d61 09           ; add hl, bc           | 
    0d62 7e           ; ld a, (hl)           | 
    0d63 c1           ; pop bc               | 
    0d64 c9           ; ret                  | 
    0d65 c5           ; push bc              | 
    0d66 06 00        ; ld b, 0x0            | 
    0d68 21 4b 42     ; ld hl, 0x424b        | 
    0d6b 09           ; add hl, bc           | 
    0d6c 7e           ; ld a, (hl)           | 
    0d6d c1           ; pop bc               | 
    0d6e c9           ; ret                  | 
    0d6f c5           ; push bc              | 
    0d70 06 00        ; ld b, 0x0            | 
    0d72 21 5b 42     ; ld hl, 0x425b        | 
    0d75 09           ; add hl, bc           | 
    0d76 7e           ; ld a, (hl)           | 
    0d77 c1           ; pop bc               | 
    0d78 c9           ; ret                  | 
    0d79 76           ; halt                 | 
    0d7a 76           ; halt                 | 
    0d7b 76           ; halt                 | 
    0d7c 76           ; halt                 | 
    0d7d 76           ; halt                 | 
    0d7e 76           ; halt                 | 
    0d7f 76           ; halt                 | 
    0d80 76           ; halt                 | 
    0d81 76           ; halt                 | 
    0d82 76           ; halt                 | 
    0d83 76           ; halt                 | 
    0d84 76           ; halt                 | 
    0d85 76           ; halt                 | 
    0d86 76           ; halt                 | 
    0d87 76           ; halt                 | 
    0d88 76           ; halt                 | 
    0d89 76           ; halt                 | 
    0d8a 76           ; halt                 | 
    0d8b 76           ; halt                 | 
    0d8c 76           ; halt                 | 
    0d8d 76           ; halt                 | 
    0d8e 76           ; halt                 | 
    0d8f 76           ; halt                 | 
    0d90 76           ; halt                 | 
    0d91 76           ; halt                 | 
    0d92 76           ; halt                 | 
    0d93 76           ; halt                 | 
    0d94 76           ; halt                 | 
    0d95 76           ; halt                 | 
    0d96 76           ; halt                 | 
    0d97 76           ; halt                 | 
    0d98 76           ; halt                 | 
    0d99 76           ; halt                 | 
    0d9a 76           ; halt                 | 
    0d9b 76           ; halt                 | 
    0d9c 76           ; halt                 | 
    0d9d 76           ; halt                 | 
    0d9e 76           ; halt                 | 
    0d9f 76           ; halt                 | 
    0da0 f3           ; di                   | start()
    0da1 3e 00        ; ld a, 0x0            | 
    0da3 d3 fe        ; out (0xfe), a        | clear all interrupts?
    0da5 3e 03        ; ld a, 0x3            | 
    0da7 d3 61        ; out (0x61), a        | 
    0da9 3e 53        ; ld a, 0x53           | 
    0dab d3 61        ; out (0x61), a        | 
    0dad 3e fa        ; ld a, 0xfa           | 
    0daf d3 61        ; out (0x61), a        | 
    0db1 3e 25        ; ld a, 0x25           | 
    0db3 d3 61        ; out (0x61), a        | 
    0db5 db 60        ; in a, (0x60)         | 
    0db7 11 30 1a     ; ld de, 0x1a30        | de = end of ROM
    0dba 21 00 00     ; ld hl, 0x0           | 
    0dbd 0e 00        ; ld c, 0x0            | 
    0dbf 79           ; ld a, c              | LOOP1: (ROM check)
    0dc0 86           ; add a, (hl)          | 
    0dc1 4f           ; ld c, a              | 
    0dc2 23           ; inc hl               | 
    0dc3 7c           ; ld a, h              | 
    0dc4 ba           ; cp d                 | 
    0dc5 c2 bf 0d     ; jp nz, 0xdbf         |   goto LOOP1
    0dc8 7d           ; ld a, l              | 
    0dc9 bb           ; cp e                 | 
    0dca c2 bf 0d     ; jp nz, 0xdbf         |   goto LOOP1
    0dcd 79           ; ld a, c              | LOOP1 end:
    0dce 77           ; ld (hl), a           | 
    0dcf be           ; cp (hl)              | 
    0dd0 ca d9 0d     ; jp z, 0xdd9          | ROM cksum good -> RAM
    0dd3 21 c5 0e     ; ld hl, 0xec5         | hl = ** ERROR IN PROM MEMORY DETECTED **
    0dd6 c3 95 0e     ; jp 0xe95             | 
    0dd9 11 00 00     ; ld de, 0x0           | ROM passed, fill RAM 4000 - C000 with pattern
    0ddc 21 00 40     ; ld hl, 0x4000        | hl = start of RAM?
    0ddf 73           ; ld (hl), e           | LOOP2: (RAM check)
    0de0 23           ; inc hl               | 
    0de1 72           ; ld (hl), d           | 
    0de2 23           ; inc hl               | 
    0de3 13           ; inc de               | 
    0de4 7c           ; ld a, h              | 
    0de5 fe c0        ; cp 0xc0              |   check if end of RAM
    0de7 c2 df 0d     ; jp nz, 0xddf         | goto LOOP2
    0dea 11 00 00     ; ld de, 0x0           | 
    0ded 21 00 40     ; ld hl, 0x4000        | 
    0df0 7e           ; ld a, (hl)           | 
    0df1 bb           ; cp e                 | 
    0df2 c2 36 0e     ; jp nz, 0xe36         | 
    0df5 23           ; inc hl               | 
    0df6 7e           ; ld a, (hl)           | 
    0df7 ba           ; cp d                 | 
    0df8 c2 36 0e     ; jp nz, 0xe36         | 
    0dfb 23           ; inc hl               | 
    0dfc 13           ; inc de               | 
    0dfd 7c           ; ld a, h              | 
    0dfe fe c0        ; cp 0xc0              | 
    0e00 c2 f0 0d     ; jp nz, 0xdf0         | 
    0e03 11 00 00     ; ld de, 0x0           | 
    0e06 21 00 40     ; ld hl, 0x4000        | 
    0e09 7b           ; ld a, e              | 
    0e0a 2f           ; cpl                  | 
    0e0b 77           ; ld (hl), a           | 
    0e0c 23           ; inc hl               | 
    0e0d 7a           ; ld a, d              | 
    0e0e 2f           ; cpl                  | 
    0e0f 77           ; ld (hl), a           | 
    0e10 23           ; inc hl               | 
    0e11 13           ; inc de               | 
    0e12 7c           ; ld a, h              | 
    0e13 fe c0        ; cp 0xc0              | 
    0e15 c2 09 0e     ; jp nz, 0xe09         | 
    0e18 11 00 00     ; ld de, 0x0           | 
    0e1b 21 00 40     ; ld hl, 0x4000        | 
    0e1e 7e           ; ld a, (hl)           | 
    0e1f 2f           ; cpl                  | 
    0e20 bb           ; cp e                 | 
    0e21 c2 36 0e     ; jp nz, 0xe36         | 
    0e24 23           ; inc hl               | 
    0e25 7e           ; ld a, (hl)           | 
    0e26 2f           ; cpl                  | 
    0e27 ba           ; cp d                 | 
    0e28 c2 36 0e     ; jp nz, 0xe36         | 
    0e2b 23           ; inc hl               | 
    0e2c 13           ; inc de               | 
    0e2d 7c           ; ld a, h              | 
    0e2e fe c0        ; cp 0xc0              | 
    0e30 c2 1e 0e     ; jp nz, 0xe1e         | 
    0e33 c3 6c 0f     ; jp 0xf6c             | 
    0e36 7c           ; ld a, h              | RAM CHECK()

    ;RAM check report? + ...
    0e37 fe 30        ; cp 0x30              | 
    0e39 fa 65 0e     ; jp m, 0xe65          | 
    0e3c fe 40        ; cp 0x40              | 
    0e3e fa 6b 0e     ; jp m, 0xe6b          | 
    0e41 fe 50        ; cp 0x50              | 
    0e43 fa 71 0e     ; jp m, 0xe71          | 
    0e46 fe 60        ; cp 0x60              | 
    0e48 fa 77 0e     ; jp m, 0xe77          | 
    0e4b fe 70        ; cp 0x70              | 
    0e4d fa 7d 0e     ; jp m, 0xe7d          | 
    0e50 fe 80        ; cp 0x80              | 
    0e52 fa 83 0e     ; jp m, 0xe83          | 
    0e55 fe 90        ; cp 0x90              | 
    0e57 fa 89 0e     ; jp m, 0xe89          | 
    0e5a fe a0        ; cp 0xa0              | 
    0e5c fa 8f 0e     ; jp m, 0xe8f          | 
    0e5f 21 66 0f     ; ld hl, 0xf66         | 
    0e62 c3 95 0e     ; jp 0xe95             | 
    0e65 21 16 0f     ; ld hl, 0xf16         | hl = $2000-3000
    0e68 c3 95 0e     ; jp 0xe95             | 
    0e6b 21 20 0f     ; ld hl, 0xf20         | hl = $3000-4000
    0e6e c3 95 0e     ; jp 0xe95             | 
    0e71 21 2a 0f     ; ld hl, 0xf2a         | hl = $4000-5000
    0e74 c3 95 0e     ; jp 0xe95             | 
    0e77 21 34 0f     ; ld hl, 0xf34         | hl = $5000-6000
    0e7a c3 95 0e     ; jp 0xe95             | 
    0e7d 21 3e 0f     ; ld hl, 0xf3e         | hl = $6000-7000
    0e80 c3 95 0e     ; jp 0xe95             | 
    0e83 21 48 0f     ; ld hl, 0xf48         | hl = $7000-8000
    0e86 c3 95 0e     ; jp 0xe95             | 
    0e89 21 52 0f     ; ld hl, 0xf52         | hl = $8000-9000
    0e8c c3 95 0e     ; jp 0xe95             | 
    0e8f 21 5c 0f     ; ld hl, 0xf5c         | hl = $9000-A000
    0e92 c3 95 0e     ; jp 0xe95             | 

    ;print RAM check error
    0e95 eb           ; ex de, hl            | save RAM area for error message
    0e96 21 e9 0e     ; ld hl, 0xee9         | hl = ** ERROR IN RAM MEMORY DETECTED ...
    0e99 7e           ; ld a, (hl)           | LOOP zzz - print characters
    0e9a 4f           ; ld c, a              | 
    0e9b fe 24        ; cp 0x24              |   done printing ** ERROR ... ?
    0e9d ca b3 0e     ; jp z, 0xeb3          | 
    0ea0 fe 00        ; cp 0x0               |   finished with whole error message
    0ea2 ca b7 0e     ; jp z, 0xeb7          | 
    0ea5 db 61        ; in a, (0x61)         |   LOOP xxx wait for IO 0x61 ready
    0ea7 e6 01        ; and 0x1              |     wait for bit 0 to be set
    0ea9 ca a5 0e     ; jp z, 0xea5          |   goto xxx
    0eac 79           ; ld a, c              | 
    0ead d3 60        ; out (0x60), a        | 
    0eaf 23           ; inc hl               | 
    0eb0 c3 99 0e     ; jp 0xe99             | 
    0eb3 eb           ; ex de, hl            |   hl = $xxxx-yyyy
    0eb4 c3 99 0e     ; jp 0xe99             |   goto zzz print address range
    0eb7 db 61        ; in a, (0x61)         | LOOP yyy keep beeping
    0eb9 e6 01        ; and 0x1              | 
    0ebb ca b7 0e     ; jp z, 0xeb7          | 
    0ebe 3e 07        ; ld a, 0x7            | 
    0ec0 d3 60        ; out (0x60), a        |   beep!
    0ec2 c3 b7 0e     ; jp 0xeb7             | goto yyy

    ;ASCII TEXT prom and ram errors
    0ec5 2a 2a 20     ; ld hl, (0x202a)      | text: ** ERROR IN PROM MEMORY DETECTED **
    0ec8 45           ; ld b, l              | 
    0ec9 52           ; ld d, d              | 
    0eca 52           ; ld d, d              | 
    0ecb 4f           ; ld c, a              | 
    0ecc 52           ; ld d, d              | 
    0ecd 20 49        ; jr nz, 0xf18         | 
    0ecf 4e           ; ld c, (hl)           | 
    0ed0 20 50        ; jr nz, 0xf22         | 
    0ed2 52           ; ld d, d              | 
    0ed3 4f           ; ld c, a              | 
    0ed4 4d           ; ld c, l              | 
    0ed5 20 4d        ; jr nz, 0xf24         | 
    0ed7 45           ; ld b, l              | 
    0ed8 4d           ; ld c, l              | 
    0ed9 4f           ; ld c, a              | 
    0eda 52           ; ld d, d              | 
    0edb 59           ; ld e, c              | 
    0edc 20 44        ; jr nz, 0xf22         | 
    0ede 45           ; ld b, l              | 
    0edf 54           ; ld d, h              | 
    0ee0 45           ; ld b, l              | 
    0ee1 43           ; ld b, e              | 
    0ee2 54           ; ld d, h              | 
    0ee3 45           ; ld b, l              | 
    0ee4 44           ; ld b, h              | 
    0ee5 20 2a        ; jr nz, 0xf11         | 
    0ee7 2a 00 2a     ; ld hl, (0x2a00)      | 
    0eea 2a 20 45     ; ld hl, (0x4520)      | 
    0eed 52           ; ld d, d              | 
    0eee 52           ; ld d, d              | 
    0eef 4f           ; ld c, a              | 
    0ef0 52           ; ld d, d              | 
    0ef1 20 49        ; jr nz, 0xf3c         | 
    0ef3 4e           ; ld c, (hl)           | 
    0ef4 20 52        ; jr nz, 0xf48         | 
    0ef6 41           ; ld b, c              | 
    0ef7 4d           ; ld c, l              | 
    0ef8 20 4d        ; jr nz, 0xf47         | 
    0efa 45           ; ld b, l              | 
    0efb 4d           ; ld c, l              | 
    0efc 4f           ; ld c, a              | 
    0efd 52           ; ld d, d              | 
    0efe 59           ; ld e, c              | 
    0eff 20 44        ; jr nz, 0xf45         | 
    0f01 45           ; ld b, l              | 
    0f02 54           ; ld d, h              | 
    0f03 45           ; ld b, l              | 
    0f04 43           ; ld b, e              | 
    0f05 54           ; ld d, h              | 
    0f06 45           ; ld b, l              | 
    0f07 44           ; ld b, h              | 
    0f08 20 49        ; jr nz, 0xf53         | 
    0f0a 4e           ; ld c, (hl)           | 
    0f0b 20 48        ; jr nz, 0xf55         | 
    0f0d 45           ; ld b, l              | 
    0f0e 58           ; ld e, b              | 
    0f0f 20 41        ; jr nz, 0xf52         | 
    0f11 52           ; ld d, d              | 
    0f12 45           ; ld b, l              | 
    0f13 41           ; ld b, c              | 
    0f14 20 24        ; jr nz, 0xf3a         | 
    0f16 32 30 30     ; ld (0x3030), a       | text: $2000-3000
    0f19 30 2d        ; jr nc, 0xf48         | 
    0f1b 33           ; inc sp               | 
    0f1c 30 30        ; jr nc, 0xf4e         | 
    0f1e 30 00        ; jr nc, 0xf20         | 
    0f20 33           ; inc sp               | text: $3000-4000
    0f21 30 30        ; jr nc, 0xf53         | 
    0f23 30 2d        ; jr nc, 0xf52         | 
    0f25 34           ; inc (hl)             | 
    0f26 30 30        ; jr nc, 0xf58         | 
    0f28 30 00        ; jr nc, 0xf2a         | 
    0f2a 34           ; inc (hl)             | text: $4000-5000
    0f2b 30 30        ; jr nc, 0xf5d         | 
    0f2d 30 2d        ; jr nc, 0xf5c         | 
    0f2f 35           ; dec (hl)             | 
    0f30 30 30        ; jr nc, 0xf62         | 
    0f32 30 00        ; jr nc, 0xf34         | 
    0f34 35           ; dec (hl)             | text: $5000-6000
    0f35 30 30        ; jr nc, 0xf67         | 
    0f37 30 2d        ; jr nc, 0xf66         | 
    0f39 36 30        ; ld (hl), 0x30        | 
    0f3b 30 30        ; jr nc, 0xf6d         | 
    0f3d 00           ; nop                  | 
    0f3e 36 30        ; ld (hl), 0x30        | text: $6000-7000
    0f40 30 30        ; jr nc, 0xf72         | 
    0f42 2d           ; dec l                | 
    0f43 37           ; scf                  | 
    0f44 30 30        ; jr nc, 0xf76         | 
    0f46 30 00        ; jr nc, 0xf48         | 
    0f48 37           ; scf                  | text: $7000-8000
    0f49 30 30        ; jr nc, 0xf7b         | 
    0f4b 30 2d        ; jr nc, 0xf7a         | 
    0f4d 38 30        ; jr c, 0xf7f          | 
    0f4f 30 30        ; jr nc, 0xf81         | 
    0f51 00           ; nop                  | 
    0f52 38 30        ; jr c, 0xf84          | text: $8000-9000
    0f54 30 30        ; jr nc, 0xf86         | 
    0f56 2d           ; dec l                | 
    0f57 39           ; add hl, sp           | 
    0f58 30 30        ; jr nc, 0xf8a         | 
    0f5a 30 00        ; jr nc, 0xf5c         | 
    0f5c 39           ; add hl, sp           | text: $9000-A000
    0f5d 30 30        ; jr nc, 0xf8f         | 
    0f5f 30 2d        ; jr nc, 0xf8e         | 
    0f61 41           ; ld b, c              | 
    0f62 30 30        ; jr nc, 0xf94         | 
    0f64 30 00        ; jr nc, 0xf66         | 
    0f66 3e 41        ; ld a, 0x41           | 
    0f68 30 30        ; jr nc, 0xf9a         | 
    0f6a 30 00        ; jr nc, 0xf6c         | 

    ;OS start? SP=4053
    0f6c 31 54 40     ; ld sp, 0x4054        | SP = 0x4054

    ;copy ROM @ 0x1138 to RAM @ 0xa18a
    0f6f 01 21 01     ; ld bc, 0x121         | bc = # bytes to copy: 0x121(289)
    0f72 21 8b a1     ; ld hl, 0xa18b        | dest addr 0xa18b
    0f75 2b           ; dec hl               | 
    0f76 11 39 11     ; ld de, 0x1139        | 
    0f79 1b           ; dec de               | 
    0f7a 1a           ; ld a, (de)           | copy_to_0xa18a:
    0f7b 77           ; ld (hl), a           | copy data to RAM
    0f7c 23           ; inc hl               | 
    0f7d 13           ; inc de               | 
    0f7e 0b           ; dec bc               | 
    0f7f 78           ; ld a, b              | 
    0f80 b1           ; or c                 | 
    0f81 c2 7a 0f     ; jp nz, 0xf7a         | if not done goto copy_to_0xa18a

    ;clear RAM at 0x422a
    0f84 21 2b 42     ; ld hl, 0x422b        | 
    0f87 06 73        ; ld b, 0x73           | 
    0f89 36 00        ; ld (hl), 0x0         | clear_ram:
    0f8b 23           ; inc hl               | 
    0f8c 05           ; dec b                | 
    0f8d c2 89 0f     ; jp nz, 0xf89         | goto clear_ram

    ;unexplored
    0f90 3e 01        ; ld a, 0x1            | 
    0f92 32 9d 42     ; ld (0x429d), a       | 
    0f95 21 9e 42     ; ld hl, 0x429e        | 
    0f98 11 40 18     ; ld de, 0x1840        | de = A[CYBER LINK: SITE ADDRESS NOT ACTIVE]
    0f9b 1a           ; ld a, (de)           | 
    0f9c 47           ; ld b, a              | 
    0f9d cd 94 16     ; call 0x1694          | 
    0fa0 21 8b a1     ; ld hl, 0xa18b        | 
    0fa3 3e ff        ; ld a, 0xff           | 
    0fa5 cd 22 07     ; call 0x722           | 
    0fa8 35           ; dec (hl)             | 
    0fa9 11 0a 00     ; ld de, 0xa           | 
    0fac 19           ; add hl, de           | 
    0fad 11 ac a2     ; ld de, 0xa2ac        | 
    0fb0 7b           ; ld a, e              | 
    0fb1 95           ; sub l                | 
    0fb2 7a           ; ld a, d              | 
    0fb3 9c           ; sbc a, h             | 
    0fb4 d2 a3 0f     ; jp nc, 0xfa3         | 
    0fb7 21 d2 a2     ; ld hl, 0xa2d2        | 
    0fba 97           ; sub a                | 
    0fbb 0e 0f        ; ld c, 0xf            | 
    0fbd 77           ; ld (hl), a           | 
    0fbe 23           ; inc hl               | 
    0fbf 0d           ; dec c                | 
    0fc0 f2 bd 0f     ; jp p, 0xfbd          | 
    0fc3 06 02        ; ld b, 0x2            | 
    0fc5 cd 71 06     ; call 0x671           | 
    0fc8 36 00        ; ld (hl), 0x0         | 
    0fca 05           ; dec b                | 
    0fcb cd 71 06     ; call 0x671           | 
    0fce 36 05        ; ld (hl), 0x5         | 
    0fd0 05           ; dec b                | 
    0fd1 c2 c5 0f     ; jp nz, 0xfc5         | 
    0fd4 cd 71 06     ; call 0x671           | 
    0fd7 06 00        ; ld b, 0x0            | 
    0fd9 36 05        ; ld (hl), 0x5         | 
    0fdb 0e 0b        ; ld c, 0xb            | 
    0fdd cd b2 06     ; call 0x6b2           | 
    0fe0 70           ; ld (hl), b           | 
    0fe1 04           ; inc b                | 
    0fe2 cd b2 06     ; call 0x6b2           | 
    0fe5 36 05        ; ld (hl), 0x5         | 
    0fe7 23           ; inc hl               | 
    0fe8 5e           ; ld e, (hl)           | 
    0fe9 23           ; inc hl               | 
    0fea 56           ; ld d, (hl)           | 
    0feb 3e 70        ; ld a, 0x70           | 
    0fed 81           ; add a, c             | 
    0fee 12           ; ld (de), a           | 
    0fef 13           ; inc de               | 
    0ff0 3e 71        ; ld a, 0x71           | 
    0ff2 12           ; ld (de), a           | 
    0ff3 05           ; dec b                | 
    0ff4 0d           ; dec c                | 
    0ff5 f2 dd 0f     ; jp p, 0xfdd          | 
    0ff8 21 00 00     ; ld hl, 0x0           | 
    0ffb 22 02 a3     ; ld (0xa302), hl      | 
    0ffe 3e 03        ; ld a, 0x3            | 
    1000 d3 a1        ; out (0xa1), a        | 
    1002 3e 53        ; ld a, 0x53           | 
    1004 d3 a1        ; out (0xa1), a        | 
    1006 3e 98        ; ld a, 0x98           | 
    1008 d3 a1        ; out (0xa1), a        | 
    100a 3e 16        ; ld a, 0x16           | 
    100c d3 a1        ; out (0xa1), a        | 
    100e 3e 96        ; ld a, 0x96           | 
    1010 d3 a1        ; out (0xa1), a        | 
    1012 3e 82        ; ld a, 0x82           | 
    1014 d3 53        ; out (0x53), a        | 
    1016 3e 08        ; ld a, 0x8            | 
    1018 d3 53        ; out (0x53), a        | 
    101a 3e 09        ; ld a, 0x9            | 
    101c d3 53        ; out (0x53), a        | 
    101e 3e 0f        ; ld a, 0xf            | 
    1020 d3 53        ; out (0x53), a        | 
    1022 0e 00        ; ld c, 0x0            | 
    1024 21 91 0c     ; ld hl, 0xc91         | 
    1027 3e 03        ; ld a, 0x3            | 
    1029 cd 45 0d     ; call 0xd45           | 
    102c 21 91 0c     ; ld hl, 0xc91         | 
    102f 3e 53        ; ld a, 0x53           | 
    1031 cd 45 0d     ; call 0xd45           | 
    1034 21 91 0c     ; ld hl, 0xc91         | 
    1037 3e fa        ; ld a, 0xfa           | 
    1039 cd 45 0d     ; call 0xd45           | 
    103c 21 91 0c     ; ld hl, 0xc91         | 
    103f 3e 25        ; ld a, 0x25           | 
    1041 cd 45 0d     ; call 0xd45           | 
    1044 21 04 0c     ; ld hl, 0xc04         | 
    1047 cd 45 0d     ; call 0xd45           | 
    104a 06 01        ; ld b, 0x1            | 
    104c cd 21 06     ; call 0x621           | 
    104f 36 06        ; ld (hl), 0x6         | 
    1051 23           ; inc hl               | 
    1052 5e           ; ld e, (hl)           | 
    1053 23           ; inc hl               | 
    1054 56           ; ld d, (hl)           | 
    1055 13           ; inc de               | 
    1056 13           ; inc de               | 
    1057 13           ; inc de               | 
    1058 23           ; inc hl               | 
    1059 23           ; inc hl               | 
    105a 23           ; inc hl               | 
    105b e5           ; push hl              | 
    105c 23           ; inc hl               | 
    105d 23           ; inc hl               | 
    105e 73           ; ld (hl), e           | 
    105f 23           ; inc hl               | 
    1060 72           ; ld (hl), d           | 

    ;copy AID-700 *READY* to (de)
    1061 21 d6 10     ; ld hl, 0x10d6        | hl = AID-7000 *READY*
    1064 06 30        ; ld b, 0x30           | 
    1066 7e           ; ld a, (hl)           | 
    1067 12           ; ld (de), a           | 
    1068 13           ; inc de               | 
    1069 23           ; inc hl               | 
    106a 05           ; dec b                | 
    106b c2 66 10     ; jp nz, 0x1066        | 

    ;unexplored
    106c 66           ; ld h, (hl)           | 
    106d 10 e1        ; djnz 0x1050          | 
    106f 73           ; ld (hl), e           | 
    1070 23           ; inc hl               | 
    1071 72           ; ld (hl), d           | 
    1072 79           ; ld a, c              | 
    1073 fe 0b        ; cp 0xb               | 
    1075 ca 7c 10     ; jp z, 0x107c         | 
    1078 0c           ; inc c                | 
    1079 c3 24 10     ; jp 0x1024            | 
    107c 3e 7e        ; ld a, 0x7e           | 
    107e d3 fe        ; out (0xfe), a        | set INTR 7 to 1
    1080 21 06 11     ; ld hl, 0x1106        | 
    1083 11 f9 41     ; ld de, 0x41f9        | 
    1086 06 2c        ; ld b, 0x2c           | 
    1088 7e           ; ld a, (hl)           | 
    1089 12           ; ld (de), a           | 
    108a 23           ; inc hl               | 
    108b 13           ; inc de               | 
    108c 05           ; dec b                | 
    108d c2 88 10     ; jp nz, 0x1088        | 
    1090 21 f9 41     ; ld hl, 0x41f9        | 
    1093 22 02 40     ; ld (0x4002), hl      | 
    1096 3e 30        ; ld a, 0x30           | 
    1098 32 01 40     ; ld (0x4001), a       | 
    109b 3e 03        ; ld a, 0x3            | 
    109d 32 00 40     ; ld (0x4000), a       | 
    10a0 3e 00        ; ld a, 0x0            | 
    10a2 32 04 40     ; ld (0x4004), a       | 
    10a5 3e 02        ; ld a, 0x2            | 
    10a7 32 07 40     ; ld (0x4007), a       | 
    10aa 3e 04        ; ld a, 0x4            | 
    10ac 32 f9 a2     ; ld (0xa2f9), a       | 
    10af 3e ff        ; ld a, 0xff           | 
    10b1 32 f2 a2     ; ld (0xa2f2), a       | 
    10b4 21 00 00     ; ld hl, 0x0           | 
    10b7 22 f7 a2     ; ld (0xa2f7), hl      | 
    10ba 22 fa a2     ; ld (0xa2fa), hl      | 
    10bd 3e 00        ; ld a, 0x0            | 
    10bf 32 fe a2     ; ld (0xa2fe), a       | 
    10c2 32 0b 40     ; ld (0x400b), a       | 
    10c5 21 09 a3     ; ld hl, 0xa309        | 
    10c8 06 0b        ; ld b, 0xb            | 
    10ca 3e 61        ; ld a, 0x61           | 
    10cc 77           ; ld (hl), a           | 
    10cd 23           ; inc hl               | 
    10ce 05           ; dec b                | 
    10cf f2 cc 10     ; jp p, 0x10cc         | 
    10d2 fb           ; ei                   | 
    10d3 c3 69 08     ; jp 0x869             | 
    10d6 1b           ; dec de               | text: AID-7000 *READY*
    10d7 41           ; ld b, c              | 
    10d8 49           ; ld c, c              | 
    10d9 44           ; ld b, h              | 
    10da 2d           ; dec l                | 
    10db 37           ; scf                  | 
    10dc 30 30        ; jr nc, 0x110e        | 
    10de 30 20        ; jr nc, 0x1100        | 
    10e0 2a 52 45     ; ld hl, (0x4552)      | 
    10e3 41           ; ld b, c              | 
    10e4 44           ; ld b, h              | 
    10e5 59           ; ld e, c              | 
    10e6 2a 20 28     ; ld hl, (0x2820)      | 
    10e9 32 30 30     ; ld (0x3030), a       | 
    10ec 55           ; ld d, l              | 
    10ed 54           ; ld d, h              | 
    10ee 2f           ; cpl                  | 
    10ef 53           ; ld d, e              | 
    10f0 49           ; ld c, c              | 
    10f1 4d           ; ld c, l              | 
    10f2 29           ; add hl, hl           | 
    10f3 20 56        ; jr nz, 0x114b        | 
    10f5 45           ; ld b, l              | 
    10f6 52           ; ld d, d              | 
    10f7 53           ; ld d, e              | 
    10f8 49           ; ld c, c              | 
    10f9 4f           ; ld c, a              | 
    10fa 4e           ; ld c, (hl)           | 
    10fb 20 30        ; jr nz, 0x112d        | 
    10fd 31 2e 30     ; ld sp, 0x302e        | 
    1100 32 2e 38     ; ld (0x382e), a       | 
    1103 33           ; inc sp               | 
    1104 1b           ; dec de               | 
    1105 41           ; ld b, c              | 
    1106 69           ; ld l, c              | 
    1107 08           ; ex af, af'           | 
    1108 54           ; ld d, h              | 
    1109 40           ; ld b, b              | 
    110a 03           ; inc bc               | 
    110b 03           ; inc bc               | 
    110c 76           ; halt                 | 
    110d 76           ; halt                 | 
    110e 00           ; nop                  | 
    110f 00           ; nop                  | 
    1110 00           ; nop                  | 
    1111 00           ; nop                  | 
    1112 05           ; dec b                | 
    1113 19           ; add hl, de           | 
    1114 9a           ; sbc a, d             | 
    1115 40           ; ld b, b              | 
    1116 01 01 76     ; ld bc, 0x7601        | 
    1119 76           ; halt                 | 
    111a 00           ; nop                  | 
    111b 00           ; nop                  | 
    111c 00           ; nop                  | 
    111d 00           ; nop                  | 
    111e 75           ; ld (hl), l           | 
    111f 0a           ; ld a, (bc)           | 
    1120 e0           ; ret po               | 
    1121 40           ; ld b, b              | 
    1122 01 03 76     ; ld bc, 0x7603        | 
    1125 76           ; halt                 | 
    1126 00           ; nop                  | 
    1127 00           ; nop                  | 
    1128 00           ; nop                  | 
    1129 00           ; nop                  | 
    112a ff           ; rst 0x38             | 
    112b ff           ; rst 0x38             | 
    112c e0           ; ret po               | 
    112d 02           ; ld (bc), a           | 
    112e f8           ; ret m                | 
    112f 41           ; ld b, c              | 
    1130 01 1e 76     ; ld bc, 0x761e        | 
    1133 76           ; halt                 | 
    1134 00           ; nop                  | 
    1135 00           ; nop                  | 
    1136 00           ; nop                  | 
    1137 00           ; nop                  | 
    1138 ff           ; rst 0x38             | 
    1139 ff           ; rst 0x38             | 
    113a d2 42 f5     ; jp nc, 0xf542        | 
    113d 46           ; ld b, (hl)           | 
    113e d2 42 d2     ; jp nc, 0xd242        | 
    1141 42           ; ld b, d              | 
    1142 ff           ; rst 0x38             | 
    1143 ff           ; rst 0x38             | 
    1144 f6 46        ; or 0x46              | 
    1146 19           ; add hl, de           | 
    1147 4b           ; ld c, e              | 
    1148 f6 46        ; or 0x46              | 
    114a f6 46        ; or 0x46              | 
    114c ff           ; rst 0x38             | 
    114d ff           ; rst 0x38             | 
    114e 1a           ; ld a, (de)           | 
    114f 4b           ; ld c, e              | 
    1150 3d           ; dec a                | 
    1151 4f           ; ld c, a              | 
    1152 1a           ; ld a, (de)           | 
    1153 4b           ; ld c, e              | 
    1154 1a           ; ld a, (de)           | 
    1155 4b           ; ld c, e              | 
    1156 ff           ; rst 0x38             | 
    1157 ff           ; rst 0x38             | 
    1158 3e 4f        ; ld a, 0x4f           | 
    115a 61           ; ld h, c              | 
    115b 53           ; ld d, e              | 
    115c 3e 4f        ; ld a, 0x4f           | 
    115e 3e 4f        ; ld a, 0x4f           | 
    1160 ff           ; rst 0x38             | 
    1161 ff           ; rst 0x38             | 
    1162 62           ; ld h, d              | 
    1163 53           ; ld d, e              | 
    1164 85           ; add a, l             | 
    1165 57           ; ld d, a              | 
    1166 62           ; ld h, d              | 
    1167 53           ; ld d, e              | 
    1168 62           ; ld h, d              | 
    1169 53           ; ld d, e              | 
    116a ff           ; rst 0x38             | 
    116b ff           ; rst 0x38             | 
    116c 86           ; add a, (hl)          | 
    116d 57           ; ld d, a              | 
    116e a9           ; xor c                | 
    116f 5b           ; ld e, e              | 
    1170 86           ; add a, (hl)          | 
    1171 57           ; ld d, a              | 
    1172 86           ; add a, (hl)          | 
    1173 57           ; ld d, a              | 
    1174 ff           ; rst 0x38             | 
    1175 ff           ; rst 0x38             | 
    1176 aa           ; xor d                | 
    1177 5b           ; ld e, e              | 
    1178 cd 5f aa     ; call 0xaa5f          | 
    117b 5b           ; ld e, e              | 
    117c aa           ; xor d                | 
    117d 5b           ; ld e, e              | 
    117e ff           ; rst 0x38             | 
    117f ff           ; rst 0x38             | 
    1180 ce 5f        ; adc a, 0x5f          | 
    1182 f1           ; pop af               | 
    1183 63           ; ld h, e              | 
    1184 ce 5f        ; adc a, 0x5f          | 
    1186 ce 5f        ; adc a, 0x5f          | 
    1188 ff           ; rst 0x38             | 
    1189 ff           ; rst 0x38             | 
    118a f2 63 15     ; jp p, 0x1563         | 
    118d 68           ; ld l, b              | 
    118e f2 63 f2     ; jp p, 0xf263         | 
    1191 63           ; ld h, e              | 
    1192 ff           ; rst 0x38             | 
    1193 ff           ; rst 0x38             | 
    1194 16 68        ; ld d, 0x68           | 
    1196 39           ; add hl, sp           | 
    1197 6c           ; ld l, h              | 
    1198 16 68        ; ld d, 0x68           | 
    119a 16 68        ; ld d, 0x68           | 
    119c ff           ; rst 0x38             | 
    119d ff           ; rst 0x38             | 
    119e 3a 6c 5d     ; ld a, (0x5d6c)       | 
    11a1 70           ; ld (hl), b           | 
    11a2 3a 6c 3a     ; ld a, (0x3a6c)       | 
    11a5 6c           ; ld l, h              | 
    11a6 ff           ; rst 0x38             | 
    11a7 ff           ; rst 0x38             | 
    11a8 5e           ; ld e, (hl)           | 
    11a9 70           ; ld (hl), b           | 
    11aa 81           ; add a, c             | 
    11ab 74           ; ld (hl), h           | 
    11ac 5e           ; ld e, (hl)           | 
    11ad 70           ; ld (hl), b           | 
    11ae 5e           ; ld e, (hl)           | 
    11af 70           ; ld (hl), b           | 
    11b0 ff           ; rst 0x38             | 
    11b1 ff           ; rst 0x38             | 
    11b2 82           ; add a, d             | 
    11b3 74           ; ld (hl), h           | 
    11b4 a5           ; and l                | 
    11b5 78           ; ld a, b              | 
    11b6 82           ; add a, d             | 
    11b7 74           ; ld (hl), h           | 
    11b8 82           ; add a, d             | 
    11b9 74           ; ld (hl), h           | 
    11ba ff           ; rst 0x38             | 
    11bb ff           ; rst 0x38             | 
    11bc a6           ; and (hl)             | 
    11bd 78           ; ld a, b              | 
    11be c9           ; ret                  | 
    11bf 7c           ; ld a, h              | 
    11c0 a6           ; and (hl)             | 
    11c1 78           ; ld a, b              | 
    11c2 a6           ; and (hl)             | 
    11c3 78           ; ld a, b              | 
    11c4 ff           ; rst 0x38             | 
    11c5 ff           ; rst 0x38             | 
    11c6 ca 7c ed     ; jp z, 0xed7c         | 
    11c9 80           ; add a, b             | 
    11ca ca 7c ca     ; jp z, 0xca7c         | 
    11cd 7c           ; ld a, h              | 
    11ce ff           ; rst 0x38             | 
    11cf ff           ; rst 0x38             | 
    11d0 ee 80        ; xor 0x80             | 
    11d2 11 85 ee     ; ld de, 0xee85        | 
    11d5 80           ; add a, b             | 
    11d6 ee 80        ; xor 0x80             | 
    11d8 ff           ; rst 0x38             | 
    11d9 ff           ; rst 0x38             | 
    11da 12           ; ld (de), a           | 
    11db 85           ; add a, l             | 
    11dc 35           ; dec (hl)             | 
    11dd 89           ; adc a, c             | 
    11de 12           ; ld (de), a           | 
    11df 85           ; add a, l             | 
    11e0 12           ; ld (de), a           | 
    11e1 85           ; add a, l             | 
    11e2 ff           ; rst 0x38             | 
    11e3 ff           ; rst 0x38             | 
    11e4 36 89        ; ld (hl), 0x89        | 
    11e6 3c           ; inc a                | 
    11e7 8b           ; adc a, e             | 
    11e8 36 89        ; ld (hl), 0x89        | 
    11ea 36 89        ; ld (hl), 0x89        | 
    11ec ff           ; rst 0x38             | 
    11ed ff           ; rst 0x38             | 
    11ee 3d           ; dec a                | 
    11ef 8b           ; adc a, e             | 
    11f0 43           ; ld b, e              | 
    11f1 8d           ; adc a, l             | 
    11f2 3d           ; dec a                | 
    11f3 8b           ; adc a, e             | 
    11f4 3d           ; dec a                | 
    11f5 8b           ; adc a, e             | 
    11f6 ff           ; rst 0x38             | 
    11f7 ff           ; rst 0x38             | 
    11f8 44           ; ld b, h              | 
    11f9 8d           ; adc a, l             | 
    11fa 4a           ; ld c, d              | 
    11fb 8f           ; adc a, a             | 
    11fc 44           ; ld b, h              | 
    11fd 8d           ; adc a, l             | 
    11fe 44           ; ld b, h              | 
    11ff 8d           ; adc a, l             | 
    1200 ff           ; rst 0x38             | 
    1201 ff           ; rst 0x38             | 
    1202 4b           ; ld c, e              | 
    1203 8f           ; adc a, a             | 
    1204 51           ; ld d, c              | 
    1205 91           ; sub c                | 
    1206 4b           ; ld c, e              | 
    1207 8f           ; adc a, a             | 
    1208 4b           ; ld c, e              | 
    1209 8f           ; adc a, a             | 
    120a ff           ; rst 0x38             | 
    120b ff           ; rst 0x38             | 
    120c 52           ; ld d, d              | 
    120d 91           ; sub c                | 
    120e 58           ; ld e, b              | 
    120f 93           ; sub e                | 
    1210 52           ; ld d, d              | 
    1211 91           ; sub c                | 
    1212 52           ; ld d, d              | 
    1213 91           ; sub c                | 
    1214 ff           ; rst 0x38             | 
    1215 ff           ; rst 0x38             | 
    1216 59           ; ld e, c              | 
    1217 93           ; sub e                | 
    1218 5f           ; ld e, a              | 
    1219 95           ; sub l                | 
    121a 59           ; ld e, c              | 
    121b 93           ; sub e                | 
    121c 59           ; ld e, c              | 
    121d 93           ; sub e                | 
    121e ff           ; rst 0x38             | 
    121f ff           ; rst 0x38             | 
    1220 60           ; ld h, b              | 
    1221 95           ; sub l                | 
    1222 66           ; ld h, (hl)           | 
    1223 97           ; sub a                | 
    1224 60           ; ld h, b              | 
    1225 95           ; sub l                | 
    1226 60           ; ld h, b              | 
    1227 95           ; sub l                | 
    1228 ff           ; rst 0x38             | 
    1229 ff           ; rst 0x38             | 
    122a 67           ; ld h, a              | 
    122b 97           ; sub a                | 
    122c 6d           ; ld l, l              | 
    122d 99           ; sbc a, c             | 
    122e 67           ; ld h, a              | 
    122f 97           ; sub a                | 
    1230 67           ; ld h, a              | 
    1231 97           ; sub a                | 
    1232 ff           ; rst 0x38             | 
    1233 ff           ; rst 0x38             | 
    1234 6e           ; ld l, (hl)           | 
    1235 99           ; sbc a, c             | 
    1236 74           ; ld (hl), h           | 
    1237 9b           ; sbc a, e             | 
    1238 6e           ; ld l, (hl)           | 
    1239 99           ; sbc a, c             | 
    123a 6e           ; ld l, (hl)           | 
    123b 99           ; sbc a, c             | 
    123c ff           ; rst 0x38             | 
    123d ff           ; rst 0x38             | 
    123e 75           ; ld (hl), l           | 
    123f 9b           ; sbc a, e             | 
    1240 7b           ; ld a, e              | 
    1241 9d           ; sbc a, l             | 
    1242 75           ; ld (hl), l           | 
    1243 9b           ; sbc a, e             | 
    1244 75           ; ld (hl), l           | 
    1245 9b           ; sbc a, e             | 
    1246 ff           ; rst 0x38             | 
    1247 ff           ; rst 0x38             | 
    1248 7c           ; ld a, h              | 
    1249 9d           ; sbc a, l             | 
    124a 82           ; add a, d             | 
    124b 9f           ; sbc a, a             | 
    124c 7c           ; ld a, h              | 
    124d 9d           ; sbc a, l             | 
    124e 7c           ; ld a, h              | 
    124f 9d           ; sbc a, l             | 
    1250 ff           ; rst 0x38             | 
    1251 ff           ; rst 0x38             | 
    1252 83           ; add a, e             | 
    1253 9f           ; sbc a, a             | 
    1254 89           ; adc a, c             | 
    1255 a1           ; and c                | 
    1256 83           ; add a, e             | 
    1257 9f           ; sbc a, a             | 
    1258 83           ; add a, e             | 
    1259 9f           ; sbc a, a             | 
    125a 76           ; halt                 | 
    125b cd 40 00     ; call 0x40            | 
    125e 01 70 95     ; ld bc, 0x9570        | 
    1261 11 1d 00     ; ld de, 0x1d          | 
    1264 2a d6 a7     ; ld hl, (0xa7d6)      | 
    1267 cd c0 6a     ; call 0x6ac0          | 
    126a cd 00 6b     ; call 0x6b00          | 
    126d c9           ; ret                  | 
    126e 21 8b 95     ; ld hl, 0x958b        | 
    1271 cd 40 00     ; call 0x40            | 
    1274 3e 02        ; ld a, 0x2            | 
    1276 01 70 95     ; ld bc, 0x9570        | 
    1279 11 1d 00     ; ld de, 0x1d          | 
    127c 2a d6 a7     ; ld hl, (0xa7d6)      | 
    127f cd 91 00     ; call 0x91            | 
    1282 c9           ; ret                  | 
    1283 d1           ; pop de               | 
    1284 21 a5 95     ; ld hl, 0x95a5        | 
    1287 cd 35 a8     ; call 0xa835          | 
    128a 3e 02        ; ld a, 0x2            | 
    128c 01 8d 95     ; ld bc, 0x958d        | 
    128f 11 1c 00     ; ld de, 0x1c          | 
    1292 2a d6 a7     ; ld hl, (0xa7d6)      | 
    1295 cd 91 00     ; call 0x91            | 
    1298 c3 9b 8f     ; jp 0x8f9b            | 
    129b cd a6 00     ; call 0xa6            | 
    129e e5           ; push hl              | 
    129f 22 28 99     ; ld (0x9928), hl      | 
    12a2 44           ; ld b, h              | 
    12a3 4d           ; ld c, l              | 
    12a4 1b           ; dec de               | 
    12a5 1b           ; dec de               | 
    12a6 1b           ; dec de               | 
    12a7 36 00        ; ld (hl), 0x0         | 
    12a9 23           ; inc hl               | 
    12aa 1b           ; dec de               | 
    12ab 7a           ; ld a, d              | 
    12ac b3           ; or e                 | 
    12ad c2 a7 8f     ; jp nz, 0x8fa7        | 
    12b0 36 ff        ; ld (hl), 0xff        | 
    12b2 23           ; inc hl               | 
    12b3 71           ; ld (hl), c           | 
    12b4 23           ; inc hl               | 
    12b5 70           ; ld (hl), b           | 
    12b6 e1           ; pop hl               | 
    12b7 cd ba 60     ; call 0x60ba          | 
    12ba c9           ; ret                  | 
    12bb 21 06 00     ; ld hl, 0x6           | 
    12be cd 9a 00     ; call 0x9a            | 
    12c1 7a           ; ld a, d              | 
    12c2 b3           ; or e                 | 
    12c3 cc 83 8f     ; call z, 0x8f83       | 
    12c6 22 98 94     ; ld (0x9498), hl      | 
    12c9 eb           ; ex de, hl            | 
    12ca 22 96 94     ; ld (0x9496), hl      | 
    12cd 1e 06        ; ld e, 0x6            | 
    12cf 36 00        ; ld (hl), 0x0         | 
    12d1 23           ; inc hl               | 
    12d2 1d           ; dec e                | 
    12d3 c2 cf 8f     ; jp nz, 0x8fcf        | 
    12d6 c9           ; ret                  | 
    12d7 2a 96 94     ; ld hl, (0x9496)      | 
    12da eb           ; ex de, hl            | 
    12db 2a 98 94     ; ld hl, (0x9498)      | 
    12de cd 9d 00     ; call 0x9d            | 
    12e1 c9           ; ret                  | 
    12e2 2a 96 94     ; ld hl, (0x9496)      | 
    12e5 7e           ; ld a, (hl)           | 
    12e6 0e 00        ; ld c, 0x0            | 
    12e8 a7           ; and a                | 
    12e9 c9           ; ret                  | 
    12ea 2a 96 94     ; ld hl, (0x9496)      | 
    12ed 44           ; ld b, h              | 
    12ee 4d           ; ld c, l              | 
    12ef cd b2 00     ; call 0xb2            | 
    12f2 2a 94 94     ; ld hl, (0x9494)      | 
    12f5 4e           ; ld c, (hl)           | 
    12f6 23           ; inc hl               | 
    12f7 7e           ; ld a, (hl)           | 
    12f8 3c           ; inc a                | 
    12f9 c2 01 90     ; jp nz, 0x9001        | 
    12fc 23           ; inc hl               | 
    12fd 7e           ; ld a, (hl)           | 
    12fe 23           ; inc hl               | 
    12ff 66           ; ld h, (hl)           | 
    1300 6f           ; ld l, a              | 
    1301 22 94 94     ; ld (0x9494), hl      | 
    1304 c9           ; ret                  | 
    1305 21 15 4f     ; ld hl, 0x4f15        | 
    1308 11 50 00     ; ld de, 0x50          | 
    130b e5           ; push hl              | 
    130c 22 94 94     ; ld (0x9494), hl      | 
    130f 44           ; ld b, h              | 
    1310 4d           ; ld c, l              | 
    1311 1d           ; dec e                | 
    1312 1d           ; dec e                | 
    1313 1d           ; dec e                | 
    1314 36 00        ; ld (hl), 0x0         | 
    1316 23           ; inc hl               | 
    1317 1d           ; dec e                | 
    1318 c2 14 90     ; jp nz, 0x9014        | 
    131b 36 ff        ; ld (hl), 0xff        | 
    131d 23           ; inc hl               | 
    131e 71           ; ld (hl), c           | 
    131f 23           ; inc hl               | 
    1320 70           ; ld (hl), b           | 
    1321 2a 96 94     ; ld hl, (0x9496)      | 
    1324 e5           ; push hl              | 
    1325 97           ; sub a                | 
    1326 32 2a 99     ; ld (0x992a), a       | 
    1329 cd 5e 00     ; call 0x5e            | 
    132c 36 09        ; ld (hl), 0x9         | 
    132e 23           ; inc hl               | 
    132f 23           ; inc hl               | 
    1330 c1           ; pop bc               | 
    1331 71           ; ld (hl), c           | 
    1332 23           ; inc hl               | 
    1333 70           ; ld (hl), b           | 
    1334 01 04 00     ; ld bc, 0x4           | 
    1337 09           ; add hl, bc           | 
    1338 c1           ; pop bc               | 
    1339 71           ; ld (hl), c           | 
    133a 23           ; inc hl               | 
    133b 70           ; ld (hl), b           | 
    133c 2a d6 a7     ; ld hl, (0xa7d6)      | 
    133f 44           ; ld b, h              | 
    1340 4d           ; ld c, l              | 
    1341 eb           ; ex de, hl            | 
    1342 cd ac 00     ; call 0xac            | 
    1345 c9           ; ret                  | 
    1346 cd 5e 00     ; call 0x5e            | 
    1349 d5           ; push de              | 
    134a 36 07        ; ld (hl), 0x7         | 
    134c 23           ; inc hl               | 
    134d 23           ; inc hl               | 
    134e 01 1f 04     ; ld bc, 0x41f         | 
    1351 71           ; ld (hl), c           | 
    1352 23           ; inc hl               | 
    1353 70           ; ld (hl), b           | 
    1354 01 04 00     ; ld bc, 0x4           | 
    1357 09           ; add hl, bc           | 
    1358 11 d0 a7     ; ld de, 0xa7d0        | 
    135b 06 02        ; ld b, 0x2            | 
    135d cd 73 00     ; call 0x73            | 
    1360 2a d6 a7     ; ld hl, (0xa7d6)      | 
    1363 44           ; ld b, h              | 
    1364 4d           ; ld c, l              | 
    1365 e1           ; pop hl               | 
    1366 cd ac 00     ; call 0xac            | 
    1369 c9           ; ret                  | 
    136a e5           ; push hl              | 
    136b d5           ; push de              | 
    136c c5           ; push bc              | 
    136d f5           ; push af              | 
    136e 32 9d 94     ; ld (0x949d), a       | 
    1371 3e 02        ; ld a, 0x2            | 
    1373 01 9a 94     ; ld bc, 0x949a        | 
    1376 11 04 00     ; ld de, 0x4           | 
    1379 2a d6 a7     ; ld hl, (0xa7d6)      | 
    137c cd 91 00     ; call 0x91            | 
    137f f1           ; pop af               | 
    1380 c1           ; pop bc               | 
    1381 d1           ; pop de               | 
    1382 e1           ; pop hl               | 
    1383 c9           ; ret                  | 
    1384 e5           ; push hl              | 
    1385 d5           ; push de              | 
    1386 c5           ; push bc              | 
    1387 3e 20        ; ld a, 0x20           | 
    1389 32 9d 94     ; ld (0x949d), a       | 
    138c 3e 02        ; ld a, 0x2            | 
    138e 01 9d 94     ; ld bc, 0x949d        | 
    1391 11 01 00     ; ld de, 0x1           | 
    1394 2a d6 a7     ; ld hl, (0xa7d6)      | 
    1397 cd 91 00     ; call 0x91            | 
    139a c1           ; pop bc               | 
    139b d1           ; pop de               | 
    139c e1           ; pop hl               | 
    139d c9           ; ret                  | 
    139e 3a 2a 99     ; ld a, (0x992a)       | 
    13a1 a7           ; and a                | 
    13a2 ca d8 90     ; jp z, 0x90d8         | 
    13a5 fe 02        ; cp 0x2               | 
    13a7 ca ec 90     ; jp z, 0x90ec         | 
    13aa c5           ; push bc              | 
    13ab cd ea 8f     ; call 0x8fea          | 
    13ae c1           ; pop bc               | 
    13af 97           ; sub a                | 
    13b0 32 2a 99     ; ld (0x992a), a       | 
    13b3 79           ; ld a, c              | 
    13b4 f5           ; push af              | 
    13b5 cd 41 99     ; call 0x9941          | 
    13b8 47           ; ld b, a              | 
    13b9 f1           ; pop af               | 
    13ba fe 43        ; cp 0x43              | 
    13bc ca c6 90     ; jp z, 0x90c6         | 
    13bf fe 44        ; cp 0x44              | 
    13c1 ca c6 90     ; jp z, 0x90c6         | 
    13c4 78           ; ld a, b              | 
    13c5 c9           ; ret                  | 
    13c6 2a 2f 99     ; ld hl, (0x992f)      | 
    13c9 11 74 98     ; ld de, 0x9874        | 
    13cc 7c           ; ld a, h              | 
    13cd ba           ; cp d                 | 
    13ce c2 6c 91     ; jp nz, 0x916c        | 
    13d1 7d           ; ld a, l              | 
    13d2 bb           ; cp e                 | 
    13d3 c2 6c 91     ; jp nz, 0x916c        | 
    13d6 78           ; ld a, b              | 
    13d7 c9           ; ret                  | 
    13d8 79           ; ld a, c              | 
    13d9 fe 01        ; cp 0x1               | 
    13db c2 e5 90     ; jp nz, 0x90e5        | 
    13de 3e 01        ; ld a, 0x1            | 
    13e0 32 2a 99     ; ld (0x992a), a       | 
    13e3 97           ; sub a                | 
    13e4 c9           ; ret                  | 
    13e5 3a 63 a3     ; ld a, (0xa363)       | 
    13e8 a7           ; and a                | 
    13e9 ca 0a 91     ; jp z, 0x910a         | 
    13ec 21 31 99     ; ld hl, 0x9931        | 
    13ef 71           ; ld (hl), c           | 
    13f0 c5           ; push bc              | 
    13f1 01 01 00     ; ld bc, 0x1           | 
    13f4 cd 3b 60     ; call 0x603b          | 
    13f7 c1           ; pop bc               | 
    13f8 cd bb 91     ; call 0x91bb          | 
    13fb 97           ; sub a                | 
    13fc 32 2a 99     ; ld (0x992a), a       | 
    13ff 3a 64 a3     ; ld a, (0xa364)       | 
    1402 a7           ; and a                | 
    1403 c8           ; ret z                | 
    1404 79           ; ld a, c              | 
    1405 cd 6a 90     ; call 0x906a          | 
    1408 97           ; sub a                | 
    1409 c9           ; ret                  | 
    140a 79           ; ld a, c              | 
    140b fe 20        ; cp 0x20              | 
    140d fa 47 91     ; jp m, 0x9147         | 
    1410 fe 7f        ; cp 0x7f              | 
    1412 ca ac 92     ; jp z, 0x92ac         | 
    1415 2a 2d 99     ; ld hl, (0x992d)      | 
    1418 eb           ; ex de, hl            | 
    1419 2a 2b 99     ; ld hl, (0x992b)      | 
    141c 7d           ; ld a, l              | 
    141d bb           ; cp e                 | 
    141e c2 2d 91     ; jp nz, 0x912d        | 
    1421 7c           ; ld a, h              | 
    1422 ba           ; cp d                 | 
    1423 c2 2d 91     ; jp nz, 0x912d        | 
    1426 3e 07        ; ld a, 0x7            | 
    1428 cd 6a 90     ; call 0x906a          | 
    142b 97           ; sub a                | 
    142c c9           ; ret                  | 
    142d 71           ; ld (hl), c           | 
    142e 23           ; inc hl               | 
    142f eb           ; ex de, hl            | 
    1430 2a 2f 99     ; ld hl, (0x992f)      | 
    1433 cd 6d 00     ; call 0x6d            | 
    1436 19           ; add hl, de           | 
    1437 eb           ; ex de, hl            | 
    1438 d2 3e 91     ; jp nc, 0x913e        | 
    143b 22 2f 99     ; ld (0x992f), hl      | 
    143e 22 2b 99     ; ld (0x992b), hl      | 
    1441 79           ; ld a, c              | 
    1442 cd 6a 90     ; call 0x906a          | 
    1445 97           ; sub a                | 
    1446 c9           ; ret                  | 
    1447 fe 0d        ; cp 0xd               | 
    1449 ca 6c 91     ; jp z, 0x916c         | 
    144c fe 08        ; cp 0x8               | 
    144e ca cc 91     ; jp z, 0x91cc         | 
    1451 fe 0c        ; cp 0xc               | 
    1453 ca ee 91     ; jp z, 0x91ee         | 
    1456 fe 0b        ; cp 0xb               | 
    1458 ca 1c 92     ; jp z, 0x921c         | 
    145b fe 0a        ; cp 0xa               | 
    145d ca 1c 92     ; jp z, 0x921c         | 
    1460 fe 0e        ; cp 0xe               | 
    1462 ca 1c 92     ; jp z, 0x921c         | 
    1465 3e 07        ; ld a, 0x7            | 
    1467 cd 6a 90     ; call 0x906a          | 
    146a 97           ; sub a                | 
    146b c9           ; ret                  | 
    146c 2a 2f 99     ; ld hl, (0x992f)      | 
    146f 36 0d        ; ld (hl), 0xd         | 
    1471 3a 66 a3     ; ld a, (0xa366)       | 
    1474 a7           ; and a                | 
    1475 c2 7b 91     ; jp nz, 0x917b        | 
    1478 23           ; inc hl               | 
    1479 36 0a        ; ld (hl), 0xa         | 
    147b eb           ; ex de, hl            | 
    147c 21 74 98     ; ld hl, 0x9874        | 
    147f cd 6d 00     ; call 0x6d            | 
    1482 19           ; add hl, de           | 
    1483 23           ; inc hl               | 
    1484 e5           ; push hl              | 
    1485 3a 66 a3     ; ld a, (0xa366)       | 
    1488 a7           ; and a                | 
    1489 c2 91 91     ; jp nz, 0x9191        | 
    148c 3e 0a        ; ld a, 0xa            | 
    148e cd 6a 90     ; call 0x906a          | 
    1491 3e 0d        ; ld a, 0xd            | 
    1493 cd 6a 90     ; call 0x906a          | 
    1496 3a 41 45     ; ld a, (0x4541)       | 
    1499 21 43 45     ; ld hl, 0x4543        | 
    149c b6           ; or (hl)              | 
    149d ca b4 91     ; jp z, 0x91b4         | 
    14a0 c1           ; pop bc               | 
    14a1 c5           ; push bc              | 
    14a2 21 74 98     ; ld hl, 0x9874        | 
    14a5 c5           ; push bc              | 
    14a6 4e           ; ld c, (hl)           | 
    14a7 e5           ; push hl              | 
    14a8 cd 1f 93     ; call 0x931f          | 
    14ab e1           ; pop hl               | 
    14ac c1           ; pop bc               | 
    14ad 23           ; inc hl               | 
    14ae 0b           ; dec bc               | 
    14af 78           ; ld a, b              | 
    14b0 b1           ; or c                 | 
    14b1 c2 a5 91     ; jp nz, 0x91a5        | 
    14b4 c1           ; pop bc               | 
    14b5 21 74 98     ; ld hl, 0x9874        | 
    14b8 cd 3b 60     ; call 0x603b          | 
    14bb 21 74 98     ; ld hl, 0x9874        | 
    14be 22 2b 99     ; ld (0x992b), hl      | 
    14c1 22 2f 99     ; ld (0x992f), hl      | 
    14c4 21 28 99     ; ld hl, 0x9928        | 
    14c7 22 2d 99     ; ld (0x992d), hl      | 
    14ca 97           ; sub a                | 
    14cb c9           ; ret                  | 
    14cc 2a 2b 99     ; ld hl, (0x992b)      | 
    14cf 11 74 98     ; ld de, 0x9874        | 
    14d2 7b           ; ld a, e              | 
    14d3 bd           ; cp l                 | 
    14d4 c2 e3 91     ; jp nz, 0x91e3        | 
    14d7 7a           ; ld a, d              | 
    14d8 bc           ; cp h                 | 
    14d9 c2 e3 91     ; jp nz, 0x91e3        | 
    14dc 3e 07        ; ld a, 0x7            | 
    14de cd 6a 90     ; call 0x906a          | 
    14e1 97           ; sub a                | 
    14e2 c9           ; ret                  | 
    14e3 2b           ; dec hl               | 
    14e4 22 2b 99     ; ld (0x992b), hl      | 
    14e7 3e 08        ; ld a, 0x8            | 
    14e9 cd 6a 90     ; call 0x906a          | 
    14ec 97           ; sub a                | 
    14ed c9           ; ret                  | 
    14ee 2a 2d 99     ; ld hl, (0x992d)      | 
    14f1 eb           ; ex de, hl            | 
    14f2 2a 2b 99     ; ld hl, (0x992b)      | 
    14f5 7d           ; ld a, l              | 
    14f6 bb           ; cp e                 | 
    14f7 c2 ff 91     ; jp nz, 0x91ff        | 
    14fa 7c           ; ld a, h              | 
    14fb ba           ; cp d                 | 
    14fc ca dc 91     ; jp z, 0x91dc         | 
    14ff 2a c5 11     ; ld hl, (0x11c5)      | 

    ;print?
    1500 c5           ; push bc              | 
    1501 11 9e 16     ; ld de, 0x169e        | 
    1504 06 00        ; ld b, 0x0            | 
    1506 e5           ; push hl              | 
    1507 1a           ; ld a, (de)           | 
    1508 a7           ; and a                | 
    1509 ca 19 15     ; jp z, 0x1519         | 
    150c 4f           ; ld c, a              | 
    150d 13           ; inc de               | 
    150e 1a           ; ld a, (de)           | 
    150f be           ; cp (hl)              | 
    1510 c2 1d 15     ; jp nz, 0x151d        | 
    1513 13           ; inc de               | 
    1514 23           ; inc hl               | 
    1515 0d           ; dec c                | 
    1516 c2 0e 15     ; jp nz, 0x150e        | 
    1519 78           ; ld a, b              | 
    151a e1           ; pop hl               | 
    151b c1           ; pop bc               | 
    151c c9           ; ret                  | 
    151d 78           ; ld a, b              | 
    151e 06 00        ; ld b, 0x0            | 
    1520 eb           ; ex de, hl            | 
    1521 09           ; add hl, bc           | 
    1522 eb           ; ex de, hl            | 
    1523 e1           ; pop hl               | 
    1524 47           ; ld b, a              | 
    1525 04           ; inc b                | 
    1526 c3 06 15     ; jp 0x1506            | 
    1529 c5           ; push bc              | 
    152a 06 00        ; ld b, 0x0            | 
    152c 09           ; add hl, bc           | 
    152d 7e           ; ld a, (hl)           | 
    152e c1           ; pop bc               | 
    152f c9           ; ret                  | 
    1530 c5           ; push bc              | 
    1531 06 00        ; ld b, 0x0            | 
    1533 09           ; add hl, bc           | 
    1534 77           ; ld (hl), a           | 
    1535 c1           ; pop bc               | 
    1536 c9           ; ret                  | 
    1537 f5           ; push af              | 
    1538 a7           ; and a                | 
    1539 ca 63 15     ; jp z, 0x1563         | 
    153c 3d           ; dec a                | 
    153d ca 70 15     ; jp z, 0x1570         | 
    1540 3d           ; dec a                | 
    1541 ca 7c 15     ; jp z, 0x157c         | 
    1544 3d           ; dec a                | 
    1545 ca 89 15     ; jp z, 0x1589         | 
    1548 3d           ; dec a                | 
    1549 ca 95 15     ; jp z, 0x1595         | 
    154c 3d           ; dec a                | 
    154d ca a2 15     ; jp z, 0x15a2         | 
    1550 3d           ; dec a                | 
    1551 ca ae 15     ; jp z, 0x15ae         | 
    1554 3d           ; dec a                | 
    1555 ca bb 15     ; jp z, 0x15bb         | 
    1558 3d           ; dec a                | 
    1559 ca c7 15     ; jp z, 0x15c7         | 
    155c 3d           ; dec a                | 
    155d ca c9 15     ; jp z, 0x15c9         | 
    1560 c3 e7 15     ; jp 0x15e7            | 
    1563 3e 01        ; ld a, 0x1            | 
    1565 21 3b 42     ; ld hl, 0x423b        | 
    1568 cd 30 15     ; call 0x1530          | 
    156b f1           ; pop af               | 
    156c 21 f6 16     ; ld hl, 0x16f6        | 
    156f c9           ; ret                  | 
    1570 97           ; sub a                | 
    1571 21 3b 42     ; ld hl, 0x423b        | 
    1574 cd 30 15     ; call 0x1530          | 
    1577 f1           ; pop af               | 
    1578 21 1d 17     ; ld hl, 0x171d        | 
    157b c9           ; ret                  | 
    157c 3e 01        ; ld a, 0x1            | 
    157e 21 5b 42     ; ld hl, 0x425b        | 
    1581 cd 30 15     ; call 0x1530          | 
    1584 f1           ; pop af               | 
    1585 21 41 17     ; ld hl, 0x1741        | 
    1588 c9           ; ret                  | 
    1589 97           ; sub a                | 
    158a 21 5b 42     ; ld hl, 0x425b        | 
    158d cd 30 15     ; call 0x1530          | 
    1590 f1           ; pop af               | 
    1591 21 69 17     ; ld hl, 0x1769        | 
    1594 c9           ; ret                  | 
    1595 3e 01        ; ld a, 0x1            | 
    1597 21 6b 42     ; ld hl, 0x426b        | 
    159a cd 30 15     ; call 0x1530          | 
    159d f1           ; pop af               | 
    159e 21 8f 17     ; ld hl, 0x178f        | 
    15a1 c9           ; ret                  | 
    15a2 97           ; sub a                | 
    15a3 21 6b 42     ; ld hl, 0x426b        | 
    15a6 cd 30 15     ; call 0x1530          | 
    15a9 f1           ; pop af               | 
    15aa 21 a9 17     ; ld hl, 0x17a9        | hl = A[HP-CASSETTE MODE OFF]
    15ad c9           ; ret                  | 
    15ae 3e 01        ; ld a, 0x1            | 
    15b0 21 7b 42     ; ld hl, 0x427b        | 
    15b3 cd 30 15     ; call 0x1530          | 
    15b6 f1           ; pop af               | 
    15b7 21 c4 17     ; ld hl, 0x17c4        | 
    15ba c9           ; ret                  | 
    15bb 97           ; sub a                | 
    15bc 21 7b 42     ; ld hl, 0x427b        | 
    15bf cd 30 15     ; call 0x1530          | 
    15c2 f1           ; pop af               | 
    15c3 21 dd 17     ; ld hl, 0x17dd        | 
    15c6 c9           ; ret                  | 
    15c7 f1           ; pop af               | 
    15c8 c9           ; ret                  | 
    15c9 97           ; sub a                | 
    15ca 21 3b 42     ; ld hl, 0x423b        | 
    15cd cd 30 15     ; call 0x1530          | 
    15d0 21 5b 42     ; ld hl, 0x425b        | 
    15d3 cd 30 15     ; call 0x1530          | 
    15d6 21 6b 42     ; ld hl, 0x426b        | 
    15d9 cd 30 15     ; call 0x1530          | 
    15dc 21 7b 42     ; ld hl, 0x427b        | 
    15df cd 30 15     ; call 0x1530          | 
    15e2 f1           ; pop af               | 
    15e3 21 6e 18     ; ld hl, 0x186e        | hl = A[USER PORT NORMAL MODE]
    15e6 c9           ; ret                  | 
    15e7 f1           ; pop af               | 
    15e8 21 8a 18     ; ld hl, 0x188a        | hl = A[ILLEGAL COMMAND]
    15eb c9           ; ret                  | 
    15ec c5           ; push bc              | PRINT TEXT(?)
    15ed f5           ; push af              | 
    15ee e5           ; push hl              | 
    15ef 06 01        ; ld b, 0x1            | 
    15f1 cd 21 06     ; call 0x621           | 
    15f4 36 06        ; ld (hl), 0x6         | 
    15f6 23           ; inc hl               | 
    15f7 5e           ; ld e, (hl)           | 
    15f8 23           ; inc hl               | 
    15f9 56           ; ld d, (hl)           | 
    15fa 13           ; inc de               | 
    15fb 13           ; inc de               | 
    15fc 13           ; inc de               | 
    15fd 23           ; inc hl               | 
    15fe 23           ; inc hl               | 
    15ff 23           ; inc hl               | 
    1600 c1           ; pop bc               | 
    1601 f1           ; pop af               | 
    1602 f5           ; push af              | 
    1603 e5           ; push hl              | 
    1604 23           ; inc hl               | 
    1605 23           ; inc hl               | 
    1606 73           ; ld (hl), e           | 
    1607 23           ; inc hl               | 
    1608 72           ; ld (hl), d           | 
    1609 fe 08        ; cp 0x8               | 
    160b ca 1f 16     ; jp z, 0x161f         | 
    160e 60           ; ld h, b              | 
    160f 69           ; ld l, c              | 
    1610 46           ; ld b, (hl)           | 
    1611 05           ; dec b                | 
    1612 23           ; inc hl               | 
    1613 eb           ; ex de, hl            | 
    1614 cd 94 16     ; call 0x1694          | 
    1617 eb           ; ex de, hl            | 
    1618 e1           ; pop hl               | 
    1619 73           ; ld (hl), e           | 
    161a 23           ; inc hl               | 
    161b 72           ; ld (hl), d           | 
    161c f1           ; pop af               | 
    161d c1           ; pop bc               | 
    161e c9           ; ret                  | 
    161f e1           ; pop hl               | 
    1620 f1           ; pop af               | 
    1621 c1           ; pop bc               | 
    1622 e5           ; push hl              | 
    1623 21 3b 42     ; ld hl, 0x423b        | 
    1626 cd 29 15     ; call 0x1529          | 
    1629 a7           ; and a                | 
    162a c2 33 16     ; jp nz, 0x1633        | 
    162d 21 1d 17     ; ld hl, 0x171d        | 
    1630 c3 36 16     ; jp 0x1636            | 
    1633 21 f6 16     ; ld hl, 0x16f6        | 
    1636 46           ; ld b, (hl)           | 
    1637 05           ; dec b                | 
    1638 23           ; inc hl               | 
    1639 eb           ; ex de, hl            | 
    163a cd 94 16     ; call 0x1694          | 
    163d eb           ; ex de, hl            | 
    163e 21 5b 42     ; ld hl, 0x425b        | 
    1641 cd 29 15     ; call 0x1529          | 
    1644 a7           ; and a                | 
    1645 c2 4e 16     ; jp nz, 0x164e        | 
    1648 21 69 17     ; ld hl, 0x1769        | 
    164b c3 51 16     ; jp 0x1651            | 
    164e 21 41 17     ; ld hl, 0x1741        | 
    1651 46           ; ld b, (hl)           | 
    1652 05           ; dec b                | 
    1653 23           ; inc hl               | 
    1654 eb           ; ex de, hl            | 
    1655 cd 94 16     ; call 0x1694          | 
    1658 eb           ; ex de, hl            | 
    1659 21 6b 42     ; ld hl, 0x426b        | 
    165c cd 29 15     ; call 0x1529          | 
    165f a7           ; and a                | 
    1660 c2 69 16     ; jp nz, 0x1669        | 
    1663 21 a9 17     ; ld hl, 0x17a9        | 
    1666 c3 6c 16     ; jp 0x166c            | 
    1669 21 8f 17     ; ld hl, 0x178f        | 
    166c 46           ; ld b, (hl)           | 
    166d 05           ; dec b                | 
    166e 23           ; inc hl               | 
    166f eb           ; ex de, hl            | 
    1670 cd 94 16     ; call 0x1694          | 
    1673 eb           ; ex de, hl            | 
    1674 21 7b 42     ; ld hl, 0x427b        | 
    1677 cd 29 15     ; call 0x1529          | 
    167a a7           ; and a                | 
    167b c2 84 16     ; jp nz, 0x1684        | 
    167e 21 dd 17     ; ld hl, 0x17dd        | 
    1681 c3 87 16     ; jp 0x1687            | 
    1684 21 c4 17     ; ld hl, 0x17c4        | 
    1687 46           ; ld b, (hl)           | 
    1688 05           ; dec b                | 
    1689 23           ; inc hl               | 
    168a eb           ; ex de, hl            | 
    168b cd 94 16     ; call 0x1694          | 
    168e eb           ; ex de, hl            | 
    168f e1           ; pop hl               | 
    1690 73           ; ld (hl), e           | 
    1691 23           ; inc hl               | 
    1692 72           ; ld (hl), d           | 
    1693 c9           ; ret                  | 
    1694 04           ; inc b                | 
    1695 05           ; dec b                | 
    1696 c8           ; ret z                | 
    1697 1a           ; ld a, (de)           | 
    1698 77           ; ld (hl), a           | 
    1699 23           ; inc hl               | 
    169a 13           ; inc de               | 
    169b c3 95 16     ; jp 0x1695            | 
    169e 09           ; add hl, bc           | text: ASC128,ON

    ;ASCII TEXT
    169f 41           ; ld b, c              | 
    16a0 53           ; ld d, e              | 
    16a1 43           ; ld b, e              | 
    16a2 31 32 38     ; ld sp, 0x3832        | 
    16a5 2c           ; inc l                | 
    16a6 4f           ; ld c, a              | 
    16a7 4e           ; ld c, (hl)           | 
    16a8 0a           ; ld a, (bc)           | text: ASC128,OFF
    16a9 41           ; ld b, c              | 
    16aa 53           ; ld d, e              | 
    16ab 43           ; ld b, e              | 
    16ac 31 32 38     ; ld sp, 0x3832        | 
    16af 2c           ; inc l                | 
    16b0 4f           ; ld c, a              | 
    16b1 46           ; ld b, (hl)           | 
    16b2 46           ; ld b, (hl)           | 
    16b3 09           ; add hl, bc           | text: AUTO80,ON
    16b4 41           ; ld b, c              | 
    16b5 55           ; ld d, l              | 
    16b6 54           ; ld d, h              | 
    16b7 4f           ; ld c, a              | 
    16b8 38 30        ; jr c, 0x16ea         | 
    16ba 2c           ; inc l                | 
    16bb 4f           ; ld c, a              | 
    16bc 4e           ; ld c, (hl)           | 
    16bd 0a           ; ld a, (bc)           | 
    16be 41           ; ld b, c              | 
    16bf 55           ; ld d, l              | 
    16c0 54           ; ld d, h              | 
    16c1 4f           ; ld c, a              | 
    16c2 38 30        ; jr c, 0x16f4         | 
    16c4 2c           ; inc l                | 
    16c5 4f           ; ld c, a              | 
    16c6 46           ; ld b, (hl)           | 
    16c7 46           ; ld b, (hl)           | 
    16c8 05           ; dec b                | 
    16c9 48           ; ld c, b              | 
    16ca 50           ; ld d, b              | 
    16cb 2c           ; inc l                | 
    16cc 4f           ; ld c, a              | 
    16cd 4e           ; ld c, (hl)           | 
    16ce 06 48        ; ld b, 0x48           | 
    16d0 50           ; ld d, b              | 
    16d1 2c           ; inc l                | 
    16d2 4f           ; ld c, a              | 
    16d3 46           ; ld b, (hl)           | 
    16d4 46           ; ld b, (hl)           | 
    16d5 08           ; ex af, af'           | 
    16d6 50           ; ld d, b              | 
    16d7 54           ; ld d, h              | 
    16d8 41           ; ld b, c              | 
    16d9 50           ; ld d, b              | 
    16da 45           ; ld b, l              | 
    16db 2c           ; inc l                | 
    16dc 4f           ; ld c, a              | 
    16dd 4e           ; ld c, (hl)           | 
    16de 09           ; add hl, bc           | 
    16df 50           ; ld d, b              | 
    16e0 54           ; ld d, h              | 
    16e1 41           ; ld b, c              | 
    16e2 50           ; ld d, b              | 
    16e3 45           ; ld b, l              | 
    16e4 2c           ; inc l                | 
    16e5 4f           ; ld c, a              | 
    16e6 46           ; ld b, (hl)           | 
    16e7 46           ; ld b, (hl)           | 
    16e8 06 53        ; ld b, 0x53           | 
    16ea 54           ; ld d, h              | 
    16eb 41           ; ld b, c              | 
    16ec 54           ; ld d, h              | 
    16ed 55           ; ld d, l              | 
    16ee 53           ; ld d, e              | 
    16ef 05           ; dec b                | 
    16f0 52           ; ld d, d              | 
    16f1 45           ; ld b, l              | 
    16f2 53           ; ld d, e              | 
    16f3 45           ; ld b, l              | 
    16f4 54           ; ld d, h              | 
    16f5 00           ; nop                  | 
    16f6 27           ; daa                  | text: 
    16f7 1b           ; dec de               | 
    16f8 41           ; ld b, c              | 
    16f9 5b           ; ld e, e              | 
    16fa 41           ; ld b, c              | 
    16fb 53           ; ld d, e              | 
    16fc 43           ; ld b, e              | 
    16fd 49           ; ld c, c              | 
    16fe 49           ; ld c, c              | 
    16ff 20 45        ; jr nz, 0x1746        | 
    1701 58           ; ld e, b              | 
    1702 54           ; ld d, h              | 
    1703 45           ; ld b, l              | 
    1704 4e           ; ld c, (hl)           | 
    1705 44           ; ld b, h              | 
    1706 45           ; ld b, l              | 
    1707 44           ; ld b, h              | 
    1708 20 4d        ; jr nz, 0x1757        | 
    170a 4f           ; ld c, a              | 
    170b 44           ; ld b, h              | 
    170c 45           ; ld b, l              | 
    170d 20 28        ; jr nz, 0x1737        | 
    170f 31 32 38     ; ld sp, 0x3832        | 
    1712 20 43        ; jr nz, 0x1757        | 
    1714 48           ; ld c, b              | 
    1715 2d           ; dec l                | 
    1716 53           ; ld d, e              | 
    1717 45           ; ld b, l              | 
    1718 54           ; ld d, h              | 
    1719 29           ; add hl, hl           | 
    171a 5d           ; ld e, l              | 
    171b 1b           ; dec de               | 
    171c 41           ; ld b, c              | 
    171d 24           ; inc h                | 
    171e 1b           ; dec de               | 
    171f 41           ; ld b, c              | 
    1720 5b           ; ld e, e              | 
    1721 41           ; ld b, c              | 
    1722 53           ; ld d, e              | 
    1723 43           ; ld b, e              | 
    1724 49           ; ld c, c              | 
    1725 49           ; ld c, c              | 
    1726 20 4e        ; jr nz, 0x1776        | 
    1728 4f           ; ld c, a              | 
    1729 52           ; ld d, d              | 
    172a 4d           ; ld c, l              | 
    172b 41           ; ld b, c              | 
    172c 4c           ; ld c, h              | 
    172d 20 4d        ; jr nz, 0x177c        | 
    172f 4f           ; ld c, a              | 
    1730 44           ; ld b, h              | 
    1731 45           ; ld b, l              | 
    1732 20 28        ; jr nz, 0x175c        | 
    1734 39           ; add hl, sp           | 
    1735 35           ; dec (hl)             | 
    1736 20 43        ; jr nz, 0x177b        | 
    1738 48           ; ld c, b              | 
    1739 2d           ; dec l                | 
    173a 53           ; ld d, e              | 
    173b 45           ; ld b, l              | 
    173c 54           ; ld d, h              | 
    173d 29           ; add hl, hl           | 
    173e 5d           ; ld e, l              | 
    173f 1b           ; dec de               | 
    1740 41           ; ld b, c              | 
    1741 28 1b        ; jr z, 0x175e         | 
    1743 41           ; ld b, c              | 
    1744 5b           ; ld e, e              | 
    1745 41           ; ld b, c              | 
    1746 55           ; ld d, l              | 
    1747 54           ; ld d, h              | 
    1748 4f           ; ld c, a              | 
    1749 20 43        ; jr nz, 0x178e        | 
    174b 52           ; ld d, d              | 
    174c 2f           ; cpl                  | 
    174d 4c           ; ld c, h              | 
    174e 46           ; ld b, (hl)           | 
    174f 20 41        ; jr nz, 0x1792        | 
    1751 54           ; ld d, h              | 
    1752 20 4c        ; jr nz, 0x17a0        | 
    1754 49           ; ld c, c              | 
    1755 4e           ; ld c, (hl)           | 
    1756 45           ; ld b, l              | 
    1757 53           ; ld d, e              | 
    1758 20 57        ; jr nz, 0x17b1        | 
    175a 49           ; ld c, c              | 
    175b 54           ; ld d, h              | 
    175c 48           ; ld c, b              | 
    175d 20 38        ; jr nz, 0x1797        | 
    175f 30 20        ; jr nc, 0x1781        | 
    1761 43           ; ld b, e              | 
    1762 48           ; ld c, b              | 
    1763 41           ; ld b, c              | 
    1764 52           ; ld d, d              | 
    1765 53           ; ld d, e              | 
    1766 5d           ; ld e, l              | 
    1767 1b           ; dec de               | 
    1768 41           ; ld b, c              | 
    1769 26 1b        ; ld h, 0x1b           | 
    176b 41           ; ld b, c              | 
    176c 5b           ; ld e, e              | 
    176d 4e           ; ld c, (hl)           | 
    176e 4f           ; ld c, a              | 
    176f 20 43        ; jr nz, 0x17b4        | 
    1771 52           ; ld d, d              | 
    1772 2f           ; cpl                  | 
    1773 4c           ; ld c, h              | 
    1774 46           ; ld b, (hl)           | 
    1775 20 41        ; jr nz, 0x17b8        | 
    1777 54           ; ld d, h              | 
    1778 20 4c        ; jr nz, 0x17c6        | 
    177a 49           ; ld c, c              | 
    177b 4e           ; ld c, (hl)           | 
    177c 45           ; ld b, l              | 
    177d 53           ; ld d, e              | 
    177e 20 57        ; jr nz, 0x17d7        | 
    1780 49           ; ld c, c              | 
    1781 54           ; ld d, h              | 
    1782 48           ; ld c, b              | 
    1783 20 38        ; jr nz, 0x17bd        | 
    1785 30 20        ; jr nc, 0x17a7        | 
    1787 43           ; ld b, e              | 
    1788 48           ; ld c, b              | 
    1789 41           ; ld b, c              | 
    178a 52           ; ld d, d              | 
    178b 53           ; ld d, e              | 
    178c 5d           ; ld e, l              | 
    178d 1b           ; dec de               | 
    178e 41           ; ld b, c              | 
    178f 1a           ; ld a, (de)           | 
    1790 1b           ; dec de               | 
    1791 41           ; ld b, c              | 
    1792 5b           ; ld e, e              | 
    1793 48           ; ld c, b              | 
    1794 50           ; ld d, b              | 
    1795 2d           ; dec l                | 
    1796 43           ; ld b, e              | 
    1797 41           ; ld b, c              | 
    1798 53           ; ld d, e              | 
    1799 53           ; ld d, e              | 
    179a 45           ; ld b, l              | 
    179b 54           ; ld d, h              | 
    179c 54           ; ld d, h              | 
    179d 45           ; ld b, l              | 
    179e 20 4d        ; jr nz, 0x17ed        | 
    17a0 4f           ; ld c, a              | 
    17a1 44           ; ld b, h              | 
    17a2 45           ; ld b, l              | 
    17a3 20 4f        ; jr nz, 0x17f4        | 
    17a5 4e           ; ld c, (hl)           | 
    17a6 5d           ; ld e, l              | 
    17a7 1b           ; dec de               | 
    17a8 41           ; ld b, c              | 
    17a9 1b           ; dec de               | text: A[HP-CASSETTE MODE OFF]
    17aa 1b           ; dec de               | 
    17ab 41           ; ld b, c              | 
    17ac 5b           ; ld e, e              | 
    17ad 48           ; ld c, b              | 
    17ae 50           ; ld d, b              | 
    17af 2d           ; dec l                | 
    17b0 43           ; ld b, e              | 
    17b1 41           ; ld b, c              | 
    17b2 53           ; ld d, e              | 
    17b3 53           ; ld d, e              | 
    17b4 45           ; ld b, l              | 
    17b5 54           ; ld d, h              | 
    17b6 54           ; ld d, h              | 
    17b7 45           ; ld b, l              | 
    17b8 20 4d        ; jr nz, 0x1807        | 
    17ba 4f           ; ld c, a              | 
    17bb 44           ; ld b, h              | 
    17bc 45           ; ld b, l              | 
    17bd 20 4f        ; jr nz, 0x180e        | 
    17bf 46           ; ld b, (hl)           | 
    17c0 46           ; ld b, (hl)           | 
    17c1 5d           ; ld e, l              | 
    17c2 1b           ; dec de               | 
    17c3 41           ; ld b, c              | 
    17c4 19           ; add hl, de           | text: A[PAPER TAPE MODE ON]
    17c5 1b           ; dec de               | 
    17c6 41           ; ld b, c              | 
    17c7 5b           ; ld e, e              | 
    17c8 50           ; ld d, b              | 
    17c9 41           ; ld b, c              | 
    17ca 50           ; ld d, b              | 
    17cb 45           ; ld b, l              | 
    17cc 52           ; ld d, d              | 
    17cd 20 54        ; jr nz, 0x1823        | 
    17cf 41           ; ld b, c              | 
    17d0 50           ; ld d, b              | 
    17d1 45           ; ld b, l              | 
    17d2 20 4d        ; jr nz, 0x1821        | 
    17d4 4f           ; ld c, a              | 
    17d5 44           ; ld b, h              | 
    17d6 45           ; ld b, l              | 
    17d7 20 4f        ; jr nz, 0x1828        | 
    17d9 4e           ; ld c, (hl)           | 
    17da 5d           ; ld e, l              | 
    17db 1b           ; dec de               | 
    17dc 41           ; ld b, c              | 
    17dd 1a           ; ld a, (de)           | 
    17de 1b           ; dec de               | 
    17df 41           ; ld b, c              | 
    17e0 5b           ; ld e, e              | 
    17e1 50           ; ld d, b              | 
    17e2 41           ; ld b, c              | 
    17e3 50           ; ld d, b              | 
    17e4 45           ; ld b, l              | 
    17e5 52           ; ld d, d              | 
    17e6 20 54        ; jr nz, 0x183c        | 
    17e8 41           ; ld b, c              | 
    17e9 50           ; ld d, b              | 
    17ea 45           ; ld b, l              | 
    17eb 20 4d        ; jr nz, 0x183a        | 
    17ed 4f           ; ld c, a              | 
    17ee 44           ; ld b, h              | 
    17ef 45           ; ld b, l              | 
    17f0 20 4f        ; jr nz, 0x1841        | 
    17f2 46           ; ld b, (hl)           | 
    17f3 46           ; ld b, (hl)           | 
    17f4 5d           ; ld e, l              | 
    17f5 1b           ; dec de               | 
    17f6 41           ; ld b, c              | 
    17f7 16 1b        ; ld d, 0x1b           | 
    17f9 41           ; ld b, c              | 
    17fa 5b           ; ld e, e              | 
    17fb 43           ; ld b, e              | 
    17fc 59           ; ld e, c              | 
    17fd 42           ; ld b, d              | 
    17fe 45           ; ld b, l              | 
    17ff 52           ; ld d, d              | 
    1800 20 4c        ; jr nz, 0x184e        | 
    1802 49           ; ld c, c              | 
    1803 4e           ; ld c, (hl)           | 
    1804 4b           ; ld c, e              | 
    1805 20 4c        ; jr nz, 0x1853        | 
    1807 4f           ; ld c, a              | 
    1808 53           ; ld d, e              | 
    1809 54           ; ld d, h              | 
    180a 5d           ; ld e, l              | 
    180b 1b           ; dec de               | 
    180c 41           ; ld b, c              | 
    180d 1d           ; dec e                | text: A[CYBER LINK ESTABLISHED]
    180e 1b           ; dec de               | 
    180f 41           ; ld b, c              | 
    1810 5b           ; ld e, e              | 
    1811 43           ; ld b, e              | 
    1812 59           ; ld e, c              | 
    1813 42           ; ld b, d              | 
    1814 45           ; ld b, l              | 
    1815 52           ; ld d, d              | 
    1816 20 4c        ; jr nz, 0x1864        | 
    1818 49           ; ld c, c              | 
    1819 4e           ; ld c, (hl)           | 
    181a 4b           ; ld c, e              | 
    181b 20 45        ; jr nz, 0x1862        | 
    181d 53           ; ld d, e              | 
    181e 54           ; ld d, h              | 
    181f 41           ; ld b, c              | 
    1820 42           ; ld b, d              | 
    1821 4c           ; ld c, h              | 
    1822 49           ; ld c, c              | 
    1823 53           ; ld d, e              | 
    1824 48           ; ld c, b              | 
    1825 45           ; ld b, l              | 
    1826 44           ; ld b, h              | 
    1827 5d           ; ld e, l              | 
    1828 1b           ; dec de               | 
    1829 41           ; ld b, c              | 
    182a 16 1b        ; ld d, 0x1b           | text: A[CYBER LINK DOWN]
    182c 41           ; ld b, c              | 
    182d 5b           ; ld e, e              | 
    182e 43           ; ld b, e              | 
    182f 59           ; ld e, c              | 
    1830 42           ; ld b, d              | 
    1831 45           ; ld b, l              | 
    1832 52           ; ld d, d              | 
    1833 20 4c        ; jr nz, 0x1881        | 
    1835 49           ; ld c, c              | 
    1836 4e           ; ld c, (hl)           | 
    1837 4b           ; ld c, e              | 
    1838 20 44        ; jr nz, 0x187e        | 
    183a 4f           ; ld c, a              | 
    183b 57           ; ld d, a              | 
    183c 4e           ; ld c, (hl)           | 
    183d 5d           ; ld e, l              | 
    183e 1b           ; dec de               | 
    183f 41           ; ld b, c              | 
    1840 2e 1b        ; ld l, 0x1b           | text: A[CYBER LINK: SITE ADDRESS NOT ACTIVE]
    1842 41           ; ld b, c              | 
    1843 5b           ; ld e, e              | 
    1844 43           ; ld b, e              | 
    1845 59           ; ld e, c              | 
    1846 42           ; ld b, d              | 
    1847 45           ; ld b, l              | 
    1848 52           ; ld d, d              | 
    1849 20 4c        ; jr nz, 0x1897        | 
    184b 49           ; ld c, c              | 
    184c 4e           ; ld c, (hl)           | 
    184d 4b           ; ld c, e              | 
    184e 3a 20 53     ; ld a, (0x5320)       | 
    1851 49           ; ld c, c              | 
    1852 54           ; ld d, h              | 
    1853 45           ; ld b, l              | 
    1854 20 41        ; jr nz, 0x1897        | 
    1856 44           ; ld b, h              | 
    1857 44           ; ld b, h              | 
    1858 52           ; ld d, d              | 
    1859 45           ; ld b, l              | 
    185a 53           ; ld d, e              | 
    185b 53           ; ld d, e              | 
    185c 20 31        ; jr nz, 0x188f        | 
    185e 20 20        ; jr nz, 0x1880        | 
    1860 20 4e        ; jr nz, 0x18b0        | 
    1862 4f           ; ld c, a              | 
    1863 54           ; ld d, h              | 
    1864 20 41        ; jr nz, 0x18a7        | 
    1866 43           ; ld b, e              | 
    1867 54           ; ld d, h              | 
    1868 49           ; ld c, c              | 
    1869 56           ; ld d, (hl)           | 
    186a 45           ; ld b, l              | 
    186b 5d           ; ld e, l              | 
    186c 1b           ; dec de               | 
    186d 41           ; ld b, c              | 
    186e 1c           ; inc e                | text: A[USER PORT NORMAL MODE]
    186f 1b           ; dec de               | 
    1870 41           ; ld b, c              | 
    1871 5b           ; ld e, e              | 
    1872 55           ; ld d, l              | 
    1873 53           ; ld d, e              | 
    1874 45           ; ld b, l              | 
    1875 52           ; ld d, d              | 
    1876 20 50        ; jr nz, 0x18c8        | 
    1878 4f           ; ld c, a              | 
    1879 52           ; ld d, d              | 
    187a 54           ; ld d, h              | 
    187b 20 4e        ; jr nz, 0x18cb        | 
    187d 4f           ; ld c, a              | 
    187e 52           ; ld d, d              | 
    187f 4d           ; ld c, l              | 
    1880 41           ; ld b, c              | 
    1881 4c           ; ld c, h              | 
    1882 20 4d        ; jr nz, 0x18d1        | 
    1884 4f           ; ld c, a              | 
    1885 44           ; ld b, h              | 
    1886 45           ; ld b, l              | 
    1887 5d           ; ld e, l              | 
    1888 1b           ; dec de               | 
    1889 41           ; ld b, c              | 
    188a 16 1b        ; ld d, 0x1b           | text: A[ILLEGAL COMMAND]
    188c 41           ; ld b, c              | 
    188d 5b           ; ld e, e              | 
    188e 49           ; ld c, c              | 
    188f 4c           ; ld c, h              | 
    1890 4c           ; ld c, h              | 
    1891 45           ; ld b, l              | 
    1892 47           ; ld b, a              | 
    1893 41           ; ld b, c              | 
    1894 4c           ; ld c, h              | 
    1895 20 43        ; jr nz, 0x18da        | 
    1897 4f           ; ld c, a              | 
    1898 4d           ; ld c, l              | 
    1899 4d           ; ld c, l              | 
    189a 41           ; ld b, c              | 
    189b 4e           ; ld c, (hl)           | 
    189c 44           ; ld b, h              | 
    189d 5d           ; ld e, l              | 
    189e 1b           ; dec de               | 
    189f 41           ; ld b, c              | 
    18a0 72           ; ld (hl), d           | 
    18a1 65           ; ld h, l              | 
    18a2 73           ; ld (hl), e           | 
    18a3 73           ; ld (hl), e           | 
    18a4 20 76        ; jr nz, 0x191c        | 
    18a6 76           ; halt                 | 
    18a7 76           ; halt                 | 
    18a8 76           ; halt                 | 
    18a9 6e           ; ld l, (hl)           | 
    18aa 65           ; ld h, l              | 
    18ab 77           ; ld (hl), a           | 
    18ac 6e           ; ld l, (hl)           | 
    18ad 6f           ; ld l, a              | 
    18ae 74           ; ld (hl), h           | 
    18af 20 72        ; jr nz, 0x1923        | 
    18b1 65           ; ld h, l              | 
    18b2 73           ; ld (hl), e           | 
    18b3 74           ; ld (hl), h           | 
    18b4 72           ; ld (hl), d           | 
    18b5 69           ; ld l, c              | 
    18b6 63           ; ld h, e              | 
    18b7 74           ; ld (hl), h           | 
    18b8 65           ; ld h, l              | 
    18b9 64           ; ld h, h              | 
    18ba 3c           ; inc a                | 
    18bb 53           ; ld d, e              | 
    18bc 3e 76        ; ld a, 0x76           | 
    18be 76           ; halt                 | 
    18bf 76           ; halt                 | 
    18c0 76           ; halt                 | 
    18c1 76           ; halt                 | 
    18c2 76           ; halt                 | 
    18c3 76           ; halt                 | 
    18c4 76           ; halt                 | 
    18c5 76           ; halt                 | 
    18c6 76           ; halt                 | 
    18c7 76           ; halt                 | 
    18c8 76           ; halt                 | 
    18c9 76           ; halt                 | 
    18ca 76           ; halt                 | 
    18cb 76           ; halt                 | 
    18cc 76           ; halt                 | 
    18cd 76           ; halt                 | 
    18ce 76           ; halt                 | 
    18cf 76           ; halt                 | 

    ;unexplored
    18cf 76           ; halt                 | 
    18d0 76           ; halt                 | 
    18d1 76           ; halt                 | 
    18d2 76           ; halt                 | 
    18d3 76           ; halt                 | 
    18d4 76           ; halt                 | 
    18d5 76           ; halt                 | 
    18d6 76           ; halt                 | 
    18d7 76           ; halt                 | 
    18d8 76           ; halt                 | 
    18d9 76           ; halt                 | 
    18da 76           ; halt                 | 
    18db 76           ; halt                 | 
    18dc 76           ; halt                 | 
    18dd 76           ; halt                 | 
    18de 76           ; halt                 | 
    18df 76           ; halt                 | 
    18e0 76           ; halt                 | 
    18e1 76           ; halt                 | 
    18e2 76           ; halt                 | 
    18e3 76           ; halt                 | 
    18e4 76           ; halt                 | 
    18e5 76           ; halt                 | 
    18e6 76           ; halt                 | 
    18e7 76           ; halt                 | 
    18e8 76           ; halt                 | 
    18e9 76           ; halt                 | 
    18ea 76           ; halt                 | 
    18eb 76           ; halt                 | 
    18ec 76           ; halt                 | 
    18ed 76           ; halt                 | 
    18ee 76           ; halt                 | 
    18ef 76           ; halt                 | 
    18f0 76           ; halt                 | 
    18f1 76           ; halt                 | 
    18f2 76           ; halt                 | 
    18f3 76           ; halt                 | 
    18f4 76           ; halt                 | 
    18f5 76           ; halt                 | 
    18f6 76           ; halt                 | 
    18f7 76           ; halt                 | 
    18f8 76           ; halt                 | 
    18f9 76           ; halt                 | 
    18fa 76           ; halt                 | 
    18fb 76           ; halt                 | 
    18fc 76           ; halt                 | 
    18fd 76           ; halt                 | 
    18fe 76           ; halt                 | 
    18ff 76           ; halt                 | 
    1900 3e 02        ; ld a, 0x2            | 
    1902 cd c8 07     ; call 0x7c8           | 
    1905 06 01        ; ld b, 0x1            | 
    1907 cd 4b 06     ; call 0x64b           | 
    190a fe 06        ; cp 0x6               | 
    190c c2 00 19     ; jp nz, 0x1900        | 
    190f f3           ; di                   | 
    1910 21 cd a2     ; ld hl, 0xa2cd        | 
    1913 46           ; ld b, (hl)           | 
    1914 23           ; inc hl               | 
    1915 7e           ; ld a, (hl)           | 
    1916 70           ; ld (hl), b           | 
    1917 2b           ; dec hl               | 
    1918 77           ; ld (hl), a           | 
    1919 fb           ; ei                   | 
    191a 06 00        ; ld b, 0x0            | 
    191c cd 4b 06     ; call 0x64b           | 
    191f 36 01        ; ld (hl), 0x1         | 
    1921 23           ; inc hl               | 
    1922 23           ; inc hl               | 
    1923 23           ; inc hl               | 
    1924 23           ; inc hl               | 
    1925 23           ; inc hl               | 
    1926 4e           ; ld c, (hl)           | 
    1927 23           ; inc hl               | 
    1928 46           ; ld b, (hl)           | 
    1929 0b           ; dec bc               | 
    192a 23           ; inc hl               | 
    192b 5e           ; ld e, (hl)           | 
    192c 23           ; inc hl               | 
    192d 56           ; ld d, (hl)           | 
    192e eb           ; ex de, hl            | 
    192f c3 b6 19     ; jp 0x19b6            | 
    1932 7e           ; ld a, (hl)           | 
    1933 fe 1b        ; cp 0x1b              | 
    1935 ca 53 19     ; jp z, 0x1953         | 
    1938 cd e1 19     ; call 0x19e1          | 
    193b 78           ; ld a, b              | 
    193c bc           ; cp h                 | 
    193d c2 4f 19     ; jp nz, 0x194f        | 
    1940 79           ; ld a, c              | 
    1941 bd           ; cp l                 | 
    1942 c2 4f 19     ; jp nz, 0x194f        | 
    1945 06 00        ; ld b, 0x0            | 
    1947 cd 4b 06     ; call 0x64b           | 
    194a 36 05        ; ld (hl), 0x5         | 
    194c c3 00 19     ; jp 0x1900            | 
    194f 23           ; inc hl               | 
    1950 c3 32 19     ; jp 0x1932            | 
    1953 23           ; inc hl               | 
    1954 7e           ; ld a, (hl)           | 
    1955 fe 23        ; cp 0x23              | 
    1957 fa 6f 19     ; jp m, 0x196f         | 
    195a fe 40        ; cp 0x40              | 
    195c f2 6f 19     ; jp p, 0x196f         | 
    195f 3e 20        ; ld a, 0x20           | 
    1961 cd e1 19     ; call 0x19e1          | 
    1964 7e           ; ld a, (hl)           | 
    1965 3d           ; dec a                | 
    1966 fe 20        ; cp 0x20              | 
    1968 ca 3b 19     ; jp z, 0x193b         | 
    196b 77           ; ld (hl), a           | 
    196c c3 5f 19     ; jp 0x195f            | 
    196f fe 40        ; cp 0x40              | 
    1971 ca 93 19     ; jp z, 0x1993         | 
    1974 fe 41        ; cp 0x41              | 
    1976 ca 93 19     ; jp z, 0x1993         | 
    1979 fe 43        ; cp 0x43              | 
    197b fa 3b 19     ; jp m, 0x193b         | 
    197e fe 50        ; cp 0x50              | 
    1980 f2 3b 19     ; jp p, 0x193b         | 
    1983 3e 30        ; ld a, 0x30           | 
    1985 cd e1 19     ; call 0x19e1          | 
    1988 7e           ; ld a, (hl)           | 
    1989 3d           ; dec a                | 
    198a fe 40        ; cp 0x40              | 
    198c ca 3b 19     ; jp z, 0x193b         | 
    198f 77           ; ld (hl), a           | 
    1990 c3 83 19     ; jp 0x1983            | 
    1993 3e 0d        ; ld a, 0xd            | 
    1995 cd e1 19     ; call 0x19e1          | 
    1998 78           ; ld a, b              | 
    1999 bc           ; cp h                 | 
    199a c2 b6 19     ; jp nz, 0x19b6        | 
    199d 79           ; ld a, c              | 
    199e bd           ; cp l                 | 
    199f c2 b6 19     ; jp nz, 0x19b6        | 
    19a2 06 00        ; ld b, 0x0            | 
    19a4 cd 4b 06     ; call 0x64b           | 
    19a7 36 05        ; ld (hl), 0x5         | 
    19a9 3e 0a        ; ld a, 0xa            | 
    19ab cd e1 19     ; call 0x19e1          | 
    19ae 3e 0d        ; ld a, 0xd            | 
    19b0 cd e1 19     ; call 0x19e1          | 
    19b3 c3 00 19     ; jp 0x1900            | 
    19b6 23           ; inc hl               | 
    19b7 7e           ; ld a, (hl)           | 
    19b8 fe 1b        ; cp 0x1b              | 
    19ba ca 53 19     ; jp z, 0x1953         | 
    19bd fe 41        ; cp 0x41              | 
    19bf c2 ca 19     ; jp nz, 0x19ca        | 
    19c2 3e 0c        ; ld a, 0xc            | 
    19c4 cd e1 19     ; call 0x19e1          | 
    19c7 c3 3b 19     ; jp 0x193b            | 
    19ca fe 4a        ; cp 0x4a              | 
    19cc c2 d4 19     ; jp nz, 0x19d4        | 
    19cf 3e 0a        ; ld a, 0xa            | 
    19d1 cd e1 19     ; call 0x19e1          | 
    19d4 3e 0a        ; ld a, 0xa            | 
    19d6 cd e1 19     ; call 0x19e1          | 
    19d9 3e 0d        ; ld a, 0xd            | 
    19db cd e1 19     ; call 0x19e1          | 
    19de c3 3b 19     ; jp 0x193b            | 
    19e1 57           ; ld d, a              | 
    19e2 f3           ; di                   | 
    19e3 db 51        ; in a, (0x51)         | 
    19e5 e6 20        ; and 0x20             | 
    19e7 c2 f7 19     ; jp nz, 0x19f7        | 
    19ea 7a           ; ld a, d              | 
    19eb d3 50        ; out (0x50), a        | 
    19ed 3e 0e        ; ld a, 0xe            | 
    19ef d3 53        ; out (0x53), a        | 
    19f1 3e 0f        ; ld a, 0xf            | 
    19f3 d3 53        ; out (0x53), a        | 
    19f5 fb           ; ei                   | 
    19f6 c9           ; ret                  | 
    19f7 3e 02        ; ld a, 0x2            | 
    19f9 cd c8 07     ; call 0x7c8           | 
    19fc db 51        ; in a, (0x51)         | 
    19fe e6 08        ; and 0x8              | 
    1a00 ca e2 19     ; jp z, 0x19e2         | 
    1a03 c3 f7 19     ; jp 0x19f7            | 

    ;unknown subroutine
    1a06 e5           ; push hl              | 
    1a07 d5           ; push de              | 
    1a08 11 05 00     ; ld de, 0x5           | 
    1a0b 19           ; add hl, de           | 
    1a0c 5e           ; ld e, (hl)           | 
    1a0d 23           ; inc hl               | 
    1a0e 56           ; ld d, (hl)           | 
    1a0f 1b           ; dec de               | 
    1a10 1b           ; dec de               | 
    1a11 72           ; ld (hl), d           | 
    1a12 2b           ; dec hl               | 
    1a13 73           ; ld (hl), e           | 
    1a14 23           ; inc hl               | 
    1a15 23           ; inc hl               | 
    1a16 5e           ; ld e, (hl)           | 
    1a17 23           ; inc hl               | 
    1a18 56           ; ld d, (hl)           | 
    1a19 13           ; inc de               | 
    1a1a 13           ; inc de               | 
    1a1b 1a           ; ld a, (de)           | 
    1a1c fe 12        ; cp 0x12              | 
    1a1e c2 27 1a     ; jp nz, 0x1a27        | 
    1a21 3e 41        ; ld a, 0x41           | 
    1a23 12           ; ld (de), a           | 
    1a24 c3 28 1a     ; jp 0x1a28            | 
    1a27 13           ; inc de               | 
    1a28 72           ; ld (hl), d           | 
    1a29 2b           ; dec hl               | 
    1a2a 73           ; ld (hl), e           | 
    1a2b d1           ; pop de               | 
    1a2c e1           ; pop hl               | 
    1a2d 36 06        ; ld (hl), 0x6         | 
    1a2f c9           ; ret                  | 
