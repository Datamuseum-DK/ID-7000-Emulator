
Annotated disassembly
=====================

.. code-block:: text
  
        ; ===========================================================================
        ; ID-7000  IPC/1 + SPC/1  (SPS_1-5 + FUNK_1-3)  --  annotated 8080 disassembly
        ; Image  : SPS_1..5_5_890505_ADR_255 then FUNK_1..3_3_881229, 16384 bytes at 0000H
        ; CPU    : Intel 8080 (no RIM/SIM). Danish text uses the 7-bit national set:
        ;          [ = AE   \ = OE   ] = AA   (so V[LG = VAELG, F\LGENDE = FOELGENDE)
        ; What   : a small multitasking operating system (IPC/1) running a PLC runtime
        ;          (SPC/1): digital/analog I/O scan, a loader for compiled boolean
        ;          programs and a function library (FUNK), programmed over a serial link.
        ; ===========================================================================
        ;
        ; Legend (flag column after the address):
        ;    *   executed at least once in the emulator runs
        ;        statically reachable but not executed
        ;    ?   not reached: linear-sweep guess (may be data)
        ; Everything is INFERRED from the firmware and emulator behaviour.
        ;
        ; ----- memory map (inferred) ------------------------------------------------
        ;   0000-3FFF  ROM: 0000-27FF IPC/1 + SPC/1 (SPS), 2800-3FFF function library (FUNK)
        ;   27FF       station address on the aux link (0FFH = "ADR 255")
        ;   4000-4BB1  kernel and driver variables (zeroed at boot);  4BB2-4C0x SPC/1 variables
        ;   4C06-4D0C  aux message and command buffers;  4D8D-508D  aux transmit ring
        ;   52D5/5A55  digital output / input images (1920 bytes each, one byte per point)
        ;   77F0       analog value table (4-byte records);  7F5F-7FFF  function table copy
        ;   8000-807B  user program header (as downloaded);  807C  user program entry
        ;   F000       debugger ROM (not in these files)
        ;
        ; ----- I/O map (inferred) ---------------------------------------------------
        ;   08/09  8251 aux link (8N1 x64, receive init; framed protocol with CRC-16)
        ;   0A     written every 5 ticks by proc_clock (watchdog/heartbeat?)
        ;   10-17  digital outputs (64 points)       20-33  digital inputs (160 points, active low)
        ;   40-4B  six analog modules (even = mux select / high byte, odd = strobe / status / low bits)
        ;   60/61  8251 operator console (7E1 x16), ADM-style ESC sequences
        ;   FE     system latch      FF  timer tick acknowledge
        ;
        ; ----- interrupts -----------------------------------------------------------
        ;   RST1 timer   RST2 aux UART   RST4 console UART   (RST3/5/6/7: EI;RET)
        ; ----- equates ----------------------------------------------------------------
        AUX_DATA           EQU  08H
        AUX_CTL            EQU  09H
        WDOG_OUT           EQU  0AH
        CON_DATA           EQU  60H
        CON_CTL            EQU  61H
        SYSCTL             EQU  FEH
        TICK_ACK           EQU  FFH
        CUR_PCB            EQU  4012H
        READYQ             EQU  4014H
        SLICE_CNT          EQU  4046H
        SEM_TICK5          EQU  4047H
        MBOX_FREE          EQU  4053H
        SEM_TXRING_DATA    EQU  40B3H
        SEM_AUX_FRAME      EQU  40B9H
        MBOX_CMD           EQU  40BFH
        SEM_CMD_DONE       EQU  40C5H
        SEM_TXRING_SPACE   EQU  40CBH
        SEM_CMD_AVAIL      EQU  40D7H
        SEM_ATTN           EQU  4101H
        SEM_CON_OUT        EQU  48A9H
        SEM_CON_LINE       EQU  48AFH
        CON_ECHO_FLAG      EQU  48B5H
        AUX_STATUS         EQU  48C3H
        SEM_AUX_RX         EQU  48C5H
        SEM_AUX_TX         EQU  48D8H
        IN_STUB            EQU  48EEH
        IN_STUB_PORT       EQU  48EFH
        OUT_STUB           EQU  48F1H
        OUT_STUB_PORT      EQU  48F2H
        CON_OUT_BUF        EQU  4908H
        CON_LINE_BUF       EQU  4958H
        CRC_TAB_T1         EQU  49A8H
        CRC_TAB_T2         EQU  4AA8H
        AUX_CRC            EQU  4BB0H
        IMG_OUT_BASE       EQU  4BB4H
        IMG_IN_BASE        EQU  4BB6H
        IMG_MARK_BASE      EQU  4BB8H
        IO_CFG_PTR         EQU  4BC4H
        N_ADC              EQU  4BD2H
        FUNK_TAB_PTR       EQU  4BD3H
        USER_ENTRY         EQU  4BD5H
        STARTUP_PENDING    EQU  4BD7H
        STARTUP_MSG        EQU  4BE0H
        SUBMSG_COUNT       EQU  4BE8H
        MUX_CHAN           EQU  4BF2H
        DL_BLOCK_NO        EQU  4BFFH
        DL_PTR             EQU  4C00H
        PLC_STATE          EQU  4C02H
        AUX_MSG            EQU  4C06H
        AUX_RXBUF          EQU  4C08H
        CMD_BUF            EQU  4C8CH
        REPLY_BUF          EQU  4D0DH
        FUNK_RAM_TAB       EQU  7F5FH
        USER_PROG          EQU  8000H
        USER_CODE          EQU  807CH
        ESC                EQU  1BH
                ORG  0000H

        ;============================================================================
        ; 0000-003F  RESET AND INTERRUPT VECTORS
        ;============================================================================

        ;----------------------------------------------------------------------
        ; reset  (0000H)
        ;   Reset vector: DI, jump to boot (00CAh).
        ;----------------------------------------------------------------------
        reset:
        0000 * F3         DI
        0001 * C3 CA 00   JMP boot
        0004            DB   76H x 4  ; padding (HLT)

        ;----------------------------------------------------------------------
        ; rst1  (0008H)
        ;   RST 1 = timer tick: jump to timer_isr.
        ;----------------------------------------------------------------------
        rst1:
        0008 * C3 92 03   JMP timer_isr
        000B            DB   76H x 5  ; padding (HLT)

        ;----------------------------------------------------------------------
        ; rst2  (0010H)
        ;   RST 2 = aux UART (08h/09h) interrupt: jump to aux_isr.
        ;----------------------------------------------------------------------
        rst2:
        0010 * C3 31 0E   JMP aux_isr
        0013            DB   76H x 5  ; padding (HLT)

        ;----------------------------------------------------------------------
        ; rst3  (0018H)
        ;   RST 3: unused (EI; RET).
        ;----------------------------------------------------------------------
        rst3:
        0018   FB         EI
        0019   C9         RET
        001A            DB   76H x 6  ; padding (HLT)

        ;----------------------------------------------------------------------
        ; rst4  (0020H)
        ;   RST 4 = console UART (60h/61h) interrupt: jump to console_isr.
        ;----------------------------------------------------------------------
        rst4:
        0020 * C3 A2 07   JMP console_isr
        0023 ? 76         HLT

        ;----------------------------------------------------------------------
        ; trap  (0024H)
        ;   TRAP (8085 vector, unused on an 8080): jumps to F000h, where the
        ;   missing debugger ROM would be.
        ;----------------------------------------------------------------------
        trap:
        0024   C3 00 F0   JMP F000H
        0027 ? 76         HLT
        0028   FB         EI
        0029   C9         RET
        002A ? 76         HLT
        002B ? 76         HLT
        002C   76         HLT
        002D            DB   76H x 3  ; padding (HLT)
        0030   FB         EI
        0031   C9         RET
        0032 ? 76         HLT
        0033 ? 76         HLT
        0034   76         HLT
        0035            DB   76H x 3  ; padding (HLT)
        0038   FB         EI
        0039   C9         RET
        003A ? 76         HLT
        003B ? 76         HLT
        003C   76         HLT
        003D            DB   76H x 3  ; padding (HLT)

        ;============================================================================
        ; 0040-00C9  OPERATING SYSTEM API JUMP TABLE
        ;   Fixed-address entry points used by FUNK functions and user code.
        ;============================================================================
        api_0040:
        0040   C3 35 06   JMP  L0635
        api_0043:
        0043   C3 D2 06   JMP  L06D2
        api_0046:
        0046   C3 4C 06   JMP  L064C
        0049            DB   76H x 6  ; padding (HLT)
        api_div_helper:
        004F   C3 08 06   JMP  L0608
        api_sdiv16:
        0052   C3 B9 05   JMP  sdiv16
        api_0055:
        0055   C3 99 07   JMP  L0799
        api_mbox_get:
        0058   C3 A4 06   JMP  L06A4
        api_005B:
        005B   C3 5E 06   JMP  L065E
        api_005E:
        005E   C3 64 06   JMP  L0664
        0061            DB   76H x 6  ; padding (HLT)
        api_0067:
        0067   C3 8D 05   JMP  neg_bc
        api_006A:
        006A   C3 85 05   JMP  neg_de
        api_006D:
        006D   C3 7D 05   JMP  neg_hl
        api_0070:
        0070   C3 7E 06   JMP  L067E
        api_memcpy:
        0073   C3 72 07   JMP  memcpy_b
        api_0076:
        0076   C3 7E 07   JMP  L077E
        api_0079:
        0079   C3 88 07   JMP  L0788
        api_mul16:
        007C   C3 A0 05   JMP  mul16
        007F            DB   76H x 6  ; padding (HLT)
        api_test_hl:
        0085   C3 95 05   JMP  test_hl
        api_0088:
        0088   C3 90 06   JMP  L0690
        api_008B:
        008B   C3 96 06   JMP  L0696
        api_008E:
        008E   C3 F2 06   JMP  L06F2
        api_0091:
        0091   C3 B6 06   JMP  L06B6
        0094            DB   76H x 12  ; padding (HLT)
        api_00A0:
        00A0   C3 42 09   JMP  L0942
        00A3            DB   76H x 6  ; padding (HLT)
        api_00A9:
        00A9   C3 16 05   JMP  sem_wait_timeout
        api_mbox_put:
        00AC   C3 90 04   JMP  mbox_put_di
        api_00AF:
        00AF   C3 CC 04   JMP  mbox_get_core
        api_sem_signal:
        00B2   C3 AE 04   JMP  sem_signal_di
        api_00B5:
        00B5   C3 FE 04   JMP  sem_signal_core
        api_sem_wait:
        00B8   C3 4F 05   JMP  sem_wait
        api_con_read_line:
        00BB   C3 97 08   JMP  con_read_line
        api_con_put_block:
        00BE   C3 16 09   JMP  con_put_block
        api_aux_send_frame:
        00C1   C3 B1 11   JMP  aux_send_frame
        api_aux_receive_frame:
        00C4   C3 3D 10   JMP  aux_receive_frame
        api_00C7:
        00C7   C3 16 07   JMP  L0716

        ;============================================================================
        ; 00CA-01E5  BOOT
        ;   Zero RAM, set SP, patch the RAM I/O stubs, init devices, create the start-up processes.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; boot  (00CAH)
        ;   Boot: zero RAM 4000h-4BB1h, SP := 4908h, patch RAM I/O stubs, init
        ;   UARTs and SPC/1 tables, create the 8 start-up processes from the
        ;   table at 01F5h, start the scheduler.
        ;----------------------------------------------------------------------
        boot:
        00CA * 00         NOP
        00CB * 00         NOP
        00CC * 00         NOP
        00CD * 3E 00      MVI A,00H
        00CF * D3 FE      OUT SYSCTL
        00D1 * DB FF      IN TICK_ACK                ; IN FFh: dummy read acknowledges a pending tick
        00D3 * 31 08 49   LXI SP,CON_OUT_BUF
        00D6 * 21 00 40   LXI H,4000H
        00D9 * 11 B2 4B   LXI D,4BB2H
        L00DC:
        00DC * 36 00      MVI M,00H
        00DE * 23         INX H
        00DF * 7B         MOV A,E
        00E0 * BD         CMP L
        00E1 * C2 DC 00   JNZ L00DC
        00E4 * 7A         MOV A,D
        00E5 * BC         CMP H
        00E6 * C2 DC 00   JNZ L00DC
        00E9 * 3E 04      MVI A,04H
        00EB * 32 3F 48   STA 483FH
        00EE * 3E 19      MVI A,19H
        00F0 * 32 40 48   STA 4840H
        00F3 * 3E 02      MVI A,02H
        00F5 * 32 45 48   STA 4845H
        00F8 * 21 EE 48   LXI H,IN_STUB              ; RAM stub for IN: "IN p; RET" with the port patched at run time
        00FB * 36 DB      MVI M,DBH
        00FD * 23         INX H
        00FE * 36 00      MVI M,00H
        0100 * 23         INX H
        0101 * 36 C9      MVI M,C9H
        0103 * 21 F1 48   LXI H,OUT_STUB             ; RAM stub for OUT: "OUT p; RET"
        0106 * 36 D3      MVI M,D3H
        0108 * 23         INX H
        0109 * 36 00      MVI M,00H
        010B * 23         INX H
        010C * 36 C9      MVI M,C9H
        010E * CD B9 07   CALL L07B9
        0111 * CD 48 0E   CALL aux_init
        0114 * CD 19 12   CALL spc1_init
        0117 * 21 E6 01   LXI H,01E6H
        011A * E5         PUSH H
        L011B:
        011B * E1         POP H
        011C * 11 0F 00   LXI D,000FH
        011F * 19         DAD D
        0120 * 01 6D 02   LXI B,026DH
        0123 * 78         MOV A,B
        0124 * BC         CMP H
        0125 * C2 2D 01   JNZ L012D
        0128 * 79         MOV A,C
        0129 * BD         CMP L
        012A * CA 38 01   JZ L0138
        L012D:
        012D * E5         PUSH H
        012E * 5E         MOV E,M
        012F * 23         INX H
        0130 * 56         MOV D,M
        0131 * 23         INX H
        0132 * CD 68 01   CALL process_create
        0135 * C3 1B 01   JMP L011B
        L0138:
        0138 * 21 F7 41   LXI H,41F7H
        013B * 22 12 40   SHLD CUR_PCB
        013E * 3E 01      MVI A,01H
        0140 * 01 53 40   LXI B,MBOX_FREE
        0143 * 02         STAX B
        0144 * 03         INX B
        0145 * 11 07 41   LXI D,4107H
        0148 * 21 0F 00   LXI H,000FH
        L014B:
        014B * 3E 01      MVI A,01H
        014D * E5         PUSH H
        014E * C5         PUSH B
        014F * CD 03 04   CALL queue_insert
        0152 * C1         POP B
        0153 * E1         POP H
        0154 * 2B         DCX H
        0155 * CD 95 05   CALL test_hl
        0158 * CA 65 01   JZ L0165
        015B * E5         PUSH H
        015C * 21 10 00   LXI H,0010H
        015F * 19         DAD D
        0160 * EB         XCHG
        0161 * E1         POP H
        0162 * C3 4B 01   JMP L014B
        L0165:
        0165 * C3 68 04   JMP L0468

        ;----------------------------------------------------------------------
        ; process_create  (0168H)
        ;   Create/start a process from a descriptor at HL (used by boot and by
        ;   the P command).
        ;----------------------------------------------------------------------
        process_create:
        0168 * 7E         MOV A,M
        0169 * 23         INX H
        016A * E5         PUSH H
        016B * 21 04 00   LXI H,0004H
        016E * 19         DAD D
        016F * 77         MOV M,A
        0170 * 21 14 40   LXI H,READYQ
        0173 * 01 05 00   LXI B,0005H
        L0176:
        0176 * A7         ANA A
        0177 * CA 7F 01   JZ L017F
        017A * 09         DAD B
        017B * 3D         DCR A
        017C * C3 76 01   JMP L0176
        L017F:
        017F * 44         MOV B,H
        0180 * 4D         MOV C,L
        0181 * 3E 01      MVI A,01H
        0183 * CD 03 04   CALL queue_insert
        0186 * E1         POP H
        0187 * 01 0E 00   LXI B,000EH
        018A * CD E9 01   CALL L01E9
        018D * 01 10 00   LXI B,0010H
        0190 * CD E9 01   CALL L01E9
        0193 * 01 0C 00   LXI B,000CH
        0196 * CD E9 01   CALL L01E9
        0199 * 01 14 00   LXI B,0014H
        019C * CD E9 01   CALL L01E9
        019F * 01 12 00   LXI B,0012H
        01A2 * CD E9 01   CALL L01E9
        01A5 * 4E         MOV C,M
        01A6 * 23         INX H
        01A7 * 46         MOV B,M
        01A8 * C5         PUSH B
        01A9 * 21 22 00   LXI H,0022H
        01AC * 19         DAD D
        01AD * 44         MOV B,H
        01AE * 4D         MOV C,L
        01AF * 36 FF      MVI M,FFH
        01B1 * 21 0A 00   LXI H,000AH
        01B4 * 19         DAD D
        01B5 * 71         MOV M,C
        01B6 * 23         INX H
        01B7 * 70         MOV M,B
        01B8 * 21 14 00   LXI H,0014H
        01BB * 19         DAD D
        01BC * 7E         MOV A,M
        01BD * 21 5F 00   LXI H,005FH
        01C0 * FE 61      CPI 61H
        01C2 * DA C8 01   JC L01C8
        01C5   21 7B 00   LXI H,007BH
        L01C8:
        01C8 * 19         DAD D
        01C9 * 44         MOV B,H
        01CA * 4D         MOV C,L
        01CB * 36 FF      MVI M,FFH
        01CD * 21 08 00   LXI H,0008H
        01D0 * 19         DAD D
        01D1 * 71         MOV M,C
        01D2 * 23         INX H
        01D3 * 70         MOV M,B
        01D4 * 60         MOV H,B
        01D5 * 69         MOV L,C
        01D6 * 2B         DCX H
        01D7 * C1         POP B
        01D8 * 70         MOV M,B
        01D9 * 2B         DCX H
        01DA * 71         MOV M,C
        01DB * 01 F8 FF   LXI B,FFF8H
        01DE * 09         DAD B
        01DF * 44         MOV B,H
        01E0 * 4D         MOV C,L
        01E1 * 21 02 00   LXI H,0002H
        01E4 * 19         DAD D
        01E5 * 71         MOV M,C

        ;============================================================================
        ; 01E6-01F4  SMALL HELPER ROUTINES
        ;============================================================================
        01E6 * 23         INX H
        01E7 * 70         MOV M,B
        01E8 * C9         RET
        L01E9:
        01E9 * C5         PUSH B
        01EA * 4E         MOV C,M
        01EB * 23         INX H
        01EC * 46         MOV B,M
        01ED * 23         INX H
        01EE * E3         XTHL
        01EF * 19         DAD D
        01F0 * 71         MOV M,C
        01F1 * 23         INX H
        01F2 * 70         MOV M,B
        01F3 * E1         POP H
        01F4 * C9         RET

        ;============================================================================
        ; 01F5-026C  START-UP PROCESS TABLE (8 ENTRIES OF 15 BYTES)
        ;   Fields: PCB address, priority (0 = highest), two pointers, one word, 4 bytes (name/id), entry point.
        ;   Entries: 02C7h clock (prio 0), 09CFh dialog (3), 056Eh idle (8), 13D4h aux rx (3), 1E6Bh aux tx (3),
        ;   1456h aux message (3), 151Eh command (3), 1FB2h PLC cycle (4).  Order in the table follows the bytes below.
        ;============================================================================
        01F5            DW   41F7H           ; PCB address
        01F7            DB   00H             ; priority
        01F8            DW   0000H,0000H,0000H ; pointers / queue heads
        01FE            DB   41H,00H,00H,00H     ; id bytes
        0202            DW   02C7H           ; entry point -> proc_clock
        0204            DW   4257H           ; PCB address
        0206            DB   03H             ; priority
        0207            DW   4059H,405FH,0000H ; pointers / queue heads
        020D            DB   42H,00H,00H,00H     ; id bytes
        0211            DW   09CFH           ; entry point -> proc_dialog
        0213            DW   44F7H           ; PCB address
        0215            DB   08H             ; priority
        0216            DW   0000H,0000H,0000H ; pointers / queue heads
        021C            DB   57H,00H,00H,00H     ; id bytes
        0220            DW   056EH           ; entry point -> proc_idle
        0222            DW   42B7H           ; PCB address
        0224            DB   03H             ; priority
        0225            DW   0000H,0000H,0000H ; pointers / queue heads
        022B            DB   41H,00H,00H,00H     ; id bytes
        022F            DW   13D4H           ; entry point -> proc_aux_rx
        0231            DW   4317H           ; PCB address
        0233            DB   03H             ; priority
        0234            DW   0000H,40EFH,0000H ; pointers / queue heads
        023A            DB   42H,00H,00H,00H     ; id bytes
        023E            DW   1E6BH           ; entry point -> proc_aux_tx
        0240            DW   4377H           ; PCB address
        0242            DB   03H             ; priority
        0243            DW   0000H,0000H,0000H ; pointers / queue heads
        0249            DB   43H,00H,00H,00H     ; id bytes
        024D            DW   1456H           ; entry point -> proc_aux_msg
        024F            DW   43D7H           ; PCB address
        0251            DB   03H             ; priority
        0252            DW   0000H,0000H,0000H ; pointers / queue heads
        0258            DB   44H,00H,00H,00H     ; id bytes
        025C            DW   151EH           ; entry point -> proc_command
        025E            DW   4437H           ; PCB address
        0260            DB   04H             ; priority
        0261            DW   0000H,40F5H,0000H ; pointers / queue heads
        0267            DB   45H,00H,00H,00H     ; id bytes
        026B            DW   1FB2H           ; entry point -> proc_plc_cycle

        ;============================================================================
        ; 026D-02C6  DYNAMIC PROCESS TEMPLATES (6 x 15 BYTES, USED BY THE P COMMAND)
        ;============================================================================
        026D            DB   57H,45H,00H,65H,40H,6BH,40H,00H,00H,41H,00H,00H,00H,00H,00H
        027C            DB   D3H,45H,00H,71H,40H,77H,40H,00H,00H,42H,00H,00H,00H,00H,00H
        028B            DB   4FH,46H,00H,7DH,40H,83H,40H,00H,00H,43H,00H,00H,00H,00H,00H
        029A            DB   CBH,46H,00H,89H,40H,8FH,40H,00H,00H,44H,00H,00H,00H,00H,00H
        02A9            DB   47H,47H,00H,95H,40H,9BH,40H,00H,00H,45H,00H,00H,00H,00H,00H
        02B8            DB   C3H,47H,00H,A1H,40H,A7H,40H,00H,00H,43H,00H,00H,00H,00H,00H

        ;============================================================================
        ; 02C7-0391  PROCESS A: CLOCK / WATCHDOG
        ;============================================================================

        ;----------------------------------------------------------------------
        ; proc_clock  (02C7H)
        ;   Process "A" (prio 0): waits for SEM_TICK5 (every 5 ticks), pulses
        ;   port 0Ah (watchdog/heartbeat - inferred) and keeps the real-time
        ;   counters.
        ;----------------------------------------------------------------------
        proc_clock:
        02C7 * 3E 05      MVI A,05H
        02C9 * 32 46 40   STA SLICE_CNT
        02CC * F3         DI
        02CD * DB FE      IN SYSCTL
        02CF * F6 02      ORI 02H
        02D1 * D3 FE      OUT SYSCTL
        02D3 * FB         EI
        02D4 * 21 D4 02   LXI H,02D4H
        02D7 * E5         PUSH H
        02D8 * 01 47 40   LXI B,SEM_TICK5
        02DB * CD 4F 05   CALL sem_wait
        02DE * D3 0A      OUT WDOG_OUT
        02E0 * CD 5D 03   CALL L035D
        02E3 * 21 3F 48   LXI H,483FH
        02E6 * 35         DCR M
        02E7 * C2 F9 02   JNZ L02F9
        02EA * 36 04      MVI M,04H
        02EC * 23         INX H
        02ED * 97         SUB A
        02EE * 35         DCR M
        02EF * C2 F6 02   JNZ L02F6
        02F2 * 3E F8      MVI A,F8H
        02F4 * 36 19      MVI M,19H
        L02F6:
        02F6 * 32 41 48   STA 4841H
        L02F9:
        02F9 * 3A 4E 40   LDA 404EH
        02FC * A7         ANA A
        02FD * CA 5C 03   JZ L035C
        0300 * 2A 4F 40   LHLD 404FH
        0303 * 11 4F 40   LXI D,404FH
        L0306:
        0306 * F5         PUSH PSW
        0307 * 23         INX H
        0308 * 23         INX H
        0309 * 23         INX H
        030A * 23         INX H
        030B * F3         DI
        030C * 7E         MOV A,M
        030D * D6 05      SUI 05H
        030F * 77         MOV M,A
        0310 * 4F         MOV C,A
        0311 * 23         INX H
        0312 * 7E         MOV A,M
        0313 * DE 00      SBI 00H
        0315 * 77         MOV M,A
        0316 * FB         EI
        0317 * DA 1E 03   JC L031E
        031A * B1         ORA C
        031B * C2 4F 03   JNZ L034F
        L031E:
        031E * D5         PUSH D
        031F * 97         SUB A
        0320 * 77         MOV M,A
        0321 * 2B         DCX H
        0322 * 77         MOV M,A
        0323 * 2B         DCX H
        0324 * 46         MOV B,M
        0325 * 2B         DCX H
        0326 * 4E         MOV C,M
        0327 * 2B         DCX H
        0328 * 56         MOV D,M
        0329 * 2B         DCX H
        032A * 5E         MOV E,M
        032B * D5         PUSH D
        032C * F3         DI
        032D * CD CC 04   CALL mbox_get_core
        0330 * FB         EI
        0331 * 21 4E 40   LXI H,404EH
        0334 * 35         DCR M
        0335 * C2 3B 03   JNZ L033B
        0338 * 2B         DCX H
        0339 * 36 00      MVI M,00H
        L033B:
        033B * E1         POP H
        033C * D1         POP D
        033D * 7D         MOV A,L
        033E * 12         STAX D
        033F * 7C         MOV A,H
        0340 * 13         INX D
        0341 * 12         STAX D
        0342 * 1B         DCX D
        0343 * F1         POP PSW
        0344 * 3D         DCR A
        0345 * C2 06 03   JNZ L0306
        0348 * EB         XCHG
        0349 * 22 51 40   SHLD 4051H
        034C * C3 5C 03   JMP L035C
        L034F:
        034F   2B         DCX H
        0350   2B         DCX H
        0351   2B         DCX H
        0352   2B         DCX H
        0353   56         MOV D,M
        0354   2B         DCX H
        0355   5E         MOV E,M
        0356   EB         XCHG
        0357   F1         POP PSW
        0358   3D         DCR A
        0359   C2 06 03   JNZ L0306
        L035C:
        035C * C9         RET
        L035D:
        035D * 3A CD 48   LDA 48CDH
        0360 * 07         RLC
        0361 * D0         RNC
        0362 * 3A CE 48   LDA 48CEH
        0365 * 07         RLC
        0366 * D0         RNC
        0367 * 3A EA 48   LDA 48EAH
        036A * 3D         DCR A
        036B * 32 EA 48   STA 48EAH
        036E * C0         RNZ
        036F   3E 02      MVI A,02H
        0371   32 C3 48   STA AUX_STATUS
        0374   3E 00      MVI A,00H
        0376   32 CE 48   STA 48CEH
        0379   32 D1 48   STA 48D1H
        037C   32 CF 48   STA 48CFH
        037F   32 D0 48   STA 48D0H
        0382   32 D2 48   STA 48D2H
        0385   32 D3 48   STA 48D3H
        0388   32 CD 48   STA 48CDH
        038B   01 C5 48   LXI B,SEM_AUX_RX
        038E   CD B5 00   CALL api_00B5
        0391   C9         RET

        ;============================================================================
        ; 0392-0620  KERNEL: TIMER ISR, SCHEDULER, QUEUES, SEMAPHORES, IDLE PROCESS, ARITHMETIC HELPERS
        ;   Preemptive scheduler with 8 priority queues (READYQ + 5*priority), semaphores and mailboxes.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; timer_isr  (0392H)
        ;   Timer ISR (RST 1): reads TICK_ACK, counts ticks, signals SEM_TICK5
        ;   every 5th tick, decrements the time slice and preempts when it
        ;   expires.
        ;----------------------------------------------------------------------
        timer_isr:
        0392 * F5         PUSH PSW
        0393 * C5         PUSH B
        0394 * D5         PUSH D
        0395 * E5         PUSH H
        0396 * DB FF      IN TICK_ACK
        0398 * 3A 45 48   LDA 4845H
        039B * 3D         DCR A
        039C * C2 A8 03   JNZ L03A8
        039F * 2A 00 40   LHLD 4000H
        03A2 * 23         INX H
        03A3 * 22 00 40   SHLD 4000H
        03A6 * 3E 02      MVI A,02H
        L03A8:
        03A8 * 32 45 48   STA 4845H
        03AB * 3A 43 48   LDA 4843H
        03AE * FE 00      CPI 00H
        03B0 * CA B7 03   JZ L03B7
        03B3 * 3D         DCR A
        03B4 * 32 43 48   STA 4843H
        L03B7:
        03B7 * 21 46 40   LXI H,SLICE_CNT
        03BA * 35         DCR M
        03BB * CA C4 03   JZ L03C4
        03BE * E1         POP H
        03BF * D1         POP D
        03C0 * C1         POP B
        03C1 * F1         POP PSW
        03C2 * FB         EI
        03C3 * C9         RET
        L03C4:
        03C4 * 36 05      MVI M,05H
        03C6 * 01 47 40   LXI B,SEM_TICK5
        03C9 * CD FE 04   CALL sem_signal_core
        03CC * 2A 12 40   LHLD CUR_PCB
        03CF * 54         MOV D,H
        03D0 * 5D         MOV E,L
        03D1 * 01 07 00   LXI B,0007H
        03D4 * 09         DAD B
        03D5 * 97         SUB A
        03D6 * 35         DCR M
        03D7 * C2 DB 03   JNZ L03DB
        03DA * 3C         INR A
        L03DB:
        03DB * CD E1 03   CALL make_ready
        03DE * C3 5B 04   JMP L045B

        ;----------------------------------------------------------------------
        ; make_ready  (03E1H)
        ;   Mark a process ready and queue it on READYQ[priority].
        ;----------------------------------------------------------------------
        make_ready:
        03E1 * F5         PUSH PSW
        03E2 * A7         ANA A
        03E3 * CA EC 03   JZ L03EC
        03E6 * 21 07 00   LXI H,0007H
        03E9 * 19         DAD D
        03EA * 36 02      MVI M,02H
        L03EC:
        03EC * 21 04 00   LXI H,0004H
        03EF * 19         DAD D
        03F0 * 7E         MOV A,M
        03F1 * E6 0F      ANI 0FH
        03F3 * 67         MOV H,A
        03F4 * 87         ADD A
        03F5 * 87         ADD A
        03F6 * 84         ADD H
        03F7 * 01 14 40   LXI B,READYQ
        03FA * 81         ADD C
        03FB * 4F         MOV C,A
        03FC * 3E 00      MVI A,00H
        03FE * 88         ADC B
        03FF * 47         MOV B,A
        0400 * C3 04 04   JMP L0404

        ;----------------------------------------------------------------------
        ; queue_insert  (0403H)
        ;   Insert a node at the tail of a 5-byte queue head.
        ;----------------------------------------------------------------------
        queue_insert:
        0403 * F5         PUSH PSW
        L0404:
        0404 * 0A         LDAX B
        0405 * A7         ANA A
        0406 * CA 32 04   JZ L0432
        0409 * 3C         INR A
        040A * 02         STAX B
        040B * 03         INX B
        040C * F1         POP PSW
        040D * A7         ANA A
        040E * CA 21 04   JZ L0421
        0411 * 03         INX B
        0412 * 03         INX B
        0413 * 0A         LDAX B
        0414 * 6F         MOV L,A
        0415 * 03         INX B
        0416 * 0A         LDAX B
        0417 * 67         MOV H,A
        0418 * 73         MOV M,E
        0419 * 23         INX H
        041A * 72         MOV M,D
        041B * 7A         MOV A,D
        041C * 02         STAX B
        041D * 0B         DCX B
        041E * 7B         MOV A,E
        041F * 02         STAX B
        0420 * C9         RET
        L0421:
        0421 * 0A         LDAX B
        0422 * 6F         MOV L,A
        0423 * 03         INX B
        0424 * 0A         LDAX B
        0425 * 67         MOV H,A
        0426 * 7A         MOV A,D
        0427 * 02         STAX B
        0428 * 0B         DCX B
        0429 * 7B         MOV A,E
        042A * 02         STAX B
        042B * 7D         MOV A,L
        042C * 12         STAX D
        042D * 13         INX D
        042E * 7C         MOV A,H
        042F * 12         STAX D
        0430 * 1B         DCX D
        0431 * C9         RET
        L0432:
        0432 * 3C         INR A
        0433 * 02         STAX B
        0434 * 03         INX B
        0435 * 7B         MOV A,E
        0436 * 02         STAX B
        0437 * 03         INX B
        0438 * 7A         MOV A,D
        0439 * 02         STAX B
        043A * 03         INX B
        043B * 7B         MOV A,E
        043C * 02         STAX B
        043D * 03         INX B
        043E * 7A         MOV A,D
        043F * 02         STAX B
        0440 * F1         POP PSW
        0441 * C9         RET

        ;----------------------------------------------------------------------
        ; queue_remove  (0442H)
        ;   Remove the first node of a queue.
        ;----------------------------------------------------------------------
        queue_remove:
        0442 * 0A         LDAX B
        0443 * A7         ANA A
        0444 * CA 59 04   JZ L0459
        0447 * 3D         DCR A
        0448 * 02         STAX B
        0449 * 03         INX B
        044A * 0A         LDAX B
        044B * 5F         MOV E,A
        044C * 03         INX B
        044D * 0A         LDAX B
        044E * 57         MOV D,A
        044F * 0B         DCX B
        0450 * 1A         LDAX D
        0451 * 02         STAX B
        0452 * 03         INX B
        0453 * 13         INX D
        0454 * 1A         LDAX D
        0455 * 02         STAX B
        0456 * 1B         DCX D
        0457 * AF         XRA A
        0458 * C9         RET
        L0459:
        0459   3C         INR A
        045A   C9         RET
        L045B:
        045B * 21 00 00   LXI H,0000H
        045E * 39         DAD SP
        045F * EB         XCHG
        0460 * 2A 12 40   LHLD CUR_PCB
        0463 * 23         INX H
        0464 * 23         INX H
        0465 * 73         MOV M,E
        0466 * 23         INX H
        0467 * 72         MOV M,D
        L0468:
        0468 * 21 0F 40   LXI H,400FH
        046B * 97         SUB A
        046C * 11 05 00   LXI D,0005H
        L046F:
        046F * 19         DAD D
        0470 * 86         ADD M
        0471 * CA 6F 04   JZ L046F
        0474 * 35         DCR M
        0475 * 23         INX H
        0476 * 5E         MOV E,M
        0477 * 23         INX H
        0478 * 56         MOV D,M
        0479 * EB         XCHG
        047A * 22 12 40   SHLD CUR_PCB
        047D * 1B         DCX D
        047E * 7E         MOV A,M
        047F * 12         STAX D
        0480 * 23         INX H
        0481 * 13         INX D
        0482 * 7E         MOV A,M
        0483 * 12         STAX D
        0484 * 23         INX H
        0485 * 5E         MOV E,M
        0486 * 23         INX H
        0487 * 56         MOV D,M
        0488 * EB         XCHG
        0489 * F9         SPHL
        048A * E1         POP H
        048B * D1         POP D
        048C * C1         POP B
        048D * F1         POP PSW
        048E * FB         EI
        048F * C9         RET

        ;----------------------------------------------------------------------
        ; mbox_put_di  (0490H)
        ;   API 00ACh: send a node to a mailbox (interrupts disabled around the
        ;   core).
        ;----------------------------------------------------------------------
        mbox_put_di:
        0490 * F3         DI
        0491 * F5         PUSH PSW
        0492 * C5         PUSH B
        0493 * D5         PUSH D
        0494 * E5         PUSH H
        0495 * CD CC 04   CALL mbox_get_core
        0498 * A7         ANA A
        0499 * CA A8 04   JZ L04A8
        049C * 2A 12 40   LHLD CUR_PCB
        049F * EB         XCHG
        04A0 * 3E 00      MVI A,00H
        04A2 * CD E1 03   CALL make_ready
        04A5 * C3 5B 04   JMP L045B
        L04A8:
        04A8 * E1         POP H
        04A9 * D1         POP D
        04AA * C1         POP B
        04AB * F1         POP PSW
        04AC * FB         EI
        04AD * C9         RET

        ;----------------------------------------------------------------------
        ; sem_signal_di  (04AEH)
        ;   API 00B2h: signal semaphore BC (interrupts disabled around the
        ;   core).
        ;----------------------------------------------------------------------
        sem_signal_di:
        04AE * F3         DI
        04AF * F5         PUSH PSW
        04B0 * C5         PUSH B
        04B1 * D5         PUSH D
        04B2 * E5         PUSH H
        04B3 * CD FE 04   CALL sem_signal_core
        04B6 * A7         ANA A
        04B7 * CA C6 04   JZ L04C6
        04BA * 2A 12 40   LHLD CUR_PCB
        04BD * EB         XCHG
        04BE * 3E 00      MVI A,00H
        04C0 * CD E1 03   CALL make_ready
        04C3 * C3 5B 04   JMP L045B
        L04C6:
        04C6 * E1         POP H
        04C7 * D1         POP D
        04C8 * C1         POP B
        04C9 * F1         POP PSW
        04CA * FB         EI
        04CB * C9         RET

        ;----------------------------------------------------------------------
        ; mbox_get_core  (04CCH)
        ;   Core of API 00AFh.
        ;----------------------------------------------------------------------
        mbox_get_core:
        04CC * 0A         LDAX B
        04CD * 3C         INR A
        04CE * CA DE 04   JZ L04DE
        04D1 * 3E 01      MVI A,01H
        04D3 * 02         STAX B
        04D4 * 03         INX B
        04D5 * EB         XCHG
        04D6 * 3E 01      MVI A,01H
        04D8 * CD 03 04   CALL queue_insert
        04DB * 3E 00      MVI A,00H
        04DD * C9         RET
        L04DE:
        04DE * 03         INX B
        04DF * 0A         LDAX B
        04E0 * 3D         DCR A
        04E1 * C2 E7 04   JNZ L04E7
        04E4 * 0B         DCX B
        04E5 * 02         STAX B
        04E6 * 03         INX B
        L04E7:
        04E7 * CD 42 04   CALL queue_remove
        04EA * 42         MOV B,D
        04EB * 4B         MOV C,E
        04EC * 03         INX B
        04ED * 03         INX B
        04EE * 03         INX B
        04EF * 03         INX B
        04F0 * 03         INX B
        04F1 * 7D         MOV A,L
        04F2 * 02         STAX B
        04F3 * 03         INX B
        04F4 * 7C         MOV A,H
        04F5 * 02         STAX B
        04F6 * 3E 01      MVI A,01H
        04F8 * CD E1 03   CALL make_ready
        04FB * 3E 01      MVI A,01H
        04FD * C9         RET

        ;----------------------------------------------------------------------
        ; sem_signal_core  (04FEH)
        ;   Signal core: wake the first waiter or increment the count.
        ;----------------------------------------------------------------------
        sem_signal_core:
        04FE * 03         INX B
        04FF * 0A         LDAX B
        0500 * A7         ANA A
        0501 * C2 0B 05   JNZ L050B
        0504 * 0B         DCX B
        0505 * 0A         LDAX B
        0506 * 3C         INR A
        0507 * 02         STAX B
        0508 * 3E 00      MVI A,00H
        050A * C9         RET
        L050B:
        050B * CD 42 04   CALL queue_remove
        050E * 3E 01      MVI A,01H
        0510 * CD E1 03   CALL make_ready
        0513 * 3E 01      MVI A,01H
        0515 * C9         RET

        ;----------------------------------------------------------------------
        ; sem_wait_timeout  (0516H)
        ;   API 00A9h: wait on a semaphore with timeout (inferred).
        ;----------------------------------------------------------------------
        sem_wait_timeout:
        0516 * F3         DI
        0517 * F5         PUSH PSW
        0518 * C5         PUSH B
        0519 * D5         PUSH D
        051A * E5         PUSH H
        051B * 2A 12 40   LHLD CUR_PCB
        051E * E5         PUSH H
        051F * 23         INX H
        0520 * 23         INX H
        0521 * 23         INX H
        0522 * 0A         LDAX B
        0523 * 3D         DCR A
        0524 * F2 34 05   JP L0534
        0527 * 3E FF      MVI A,FFH
        0529 * 02         STAX B
        052A * 03         INX B
        052B * D1         POP D
        052C * 3E 01      MVI A,01H
        052E * CD 03 04   CALL queue_insert
        0531 * C3 5B 04   JMP L045B
        L0534:
        0534 * 03         INX B
        0535 * 0A         LDAX B
        0536 * 3D         DCR A
        0537 * 3E 01      MVI A,01H
        0539 * C2 3D 05   JNZ L053D
        053C   3D         DCR A
        L053D:
        053D * 0B         DCX B
        053E * 02         STAX B
        053F * 03         INX B
        0540 * CD 42 04   CALL queue_remove
        0543 * 23         INX H
        0544 * 23         INX H
        0545 * 73         MOV M,E
        0546 * 23         INX H
        0547 * 72         MOV M,D
        0548 * D1         POP D
        0549 * E1         POP H
        054A * D1         POP D
        054B * C1         POP B
        054C * F1         POP PSW
        054D * FB         EI
        054E * C9         RET

        ;----------------------------------------------------------------------
        ; sem_wait  (054FH)
        ;   API 00B8h: wait (P) on semaphore BC; blocks the calling process.
        ;----------------------------------------------------------------------
        sem_wait:
        054F * F3         DI
        0550 * F5         PUSH PSW
        0551 * C5         PUSH B
        0552 * D5         PUSH D
        0553 * E5         PUSH H
        0554 * 2A 12 40   LHLD CUR_PCB
        0557 * 0A         LDAX B
        0558 * A7         ANA A
        0559 * CA 64 05   JZ L0564
        055C * 3D         DCR A
        055D * 02         STAX B
        055E * E1         POP H
        055F * D1         POP D
        0560 * C1         POP B
        0561 * F1         POP PSW
        0562 * FB         EI
        0563 * C9         RET
        L0564:
        0564 * 03         INX B
        0565 * EB         XCHG
        0566 * 3E 01      MVI A,01H
        0568 * CD 03 04   CALL queue_insert
        056B * C3 5B 04   JMP L045B

        ;----------------------------------------------------------------------
        ; proc_idle  (056EH)
        ;   Process "W" (prio 8): idle loop.
        ;----------------------------------------------------------------------
        proc_idle:
        056E   1E 7F      MVI E,7FH
        L0570:
        0570   3E FF      MVI A,FFH
        L0572:
        0572   3D         DCR A
        0573   C2 72 05   JNZ L0572
        0576   1D         DCR E
        0577   C2 70 05   JNZ L0570
        057A   C3 6E 05   JMP proc_idle

        ;----------------------------------------------------------------------
        ; neg_hl  (057DH)
        ;   HL := -HL.
        ;----------------------------------------------------------------------
        neg_hl:
        057D * 7C         MOV A,H
        057E * 2F         CMA
        057F * 67         MOV H,A
        0580 * 7D         MOV A,L
        0581 * 2F         CMA
        0582 * 6F         MOV L,A
        0583 * 23         INX H
        0584 * C9         RET

        ;----------------------------------------------------------------------
        ; neg_de  (0585H)
        ;   DE := -DE.
        ;----------------------------------------------------------------------
        neg_de:
        0585 * 7A         MOV A,D
        0586 * 2F         CMA
        0587 * 57         MOV D,A
        0588 * 7B         MOV A,E
        0589 * 2F         CMA
        058A * 5F         MOV E,A
        058B * 13         INX D
        058C * C9         RET

        ;----------------------------------------------------------------------
        ; neg_bc  (058DH)
        ;   BC := -BC.
        ;----------------------------------------------------------------------
        neg_bc:
        058D   78         MOV A,B
        058E   2F         CMA
        058F   47         MOV B,A
        0590   79         MOV A,C
        0591   2F         CMA
        0592   4F         MOV C,A
        0593   03         INX B
        0594   C9         RET

        ;----------------------------------------------------------------------
        ; test_hl  (0595H)
        ;   Z set when HL = 0, sign in carry (API 0085h).
        ;----------------------------------------------------------------------
        test_hl:
        0595 * 97         SUB A
        0596 * B4         ORA H
        0597 * 07         RLC
        0598 * 3F         CMC
        0599 * C0         RNZ
        059A * B5         ORA L
        059B * C8         RZ
        059C * 97         SUB A
        059D * 3C         INR A
        059E * 37         STC
        059F * C9         RET

        ;----------------------------------------------------------------------
        ; mul16  (05A0H)
        ;   16-bit multiply helper (API 007Ch).
        ;----------------------------------------------------------------------
        mul16:
        05A0   11 00 00   LXI D,0000H
        05A3   79         MOV A,C
        L05A4:
        05A4   48         MOV C,B
        05A5   06 08      MVI B,08H
        L05A7:
        05A7   1F         RAR
        05A8   D2 AE 05   JNC L05AE
        05AB   EB         XCHG
        05AC   19         DAD D
        05AD   EB         XCHG
        L05AE:
        05AE   29         DAD H
        05AF   05         DCR B
        05B0   C2 A7 05   JNZ L05A7
        05B3   79         MOV A,C
        05B4   A7         ANA A
        05B5   C2 A4 05   JNZ L05A4
        05B8   C9         RET

        ;----------------------------------------------------------------------
        ; sdiv16  (05B9H)
        ;   Signed 16-bit divide helper (API 0052h).
        ;----------------------------------------------------------------------
        sdiv16:
        05B9   44         MOV B,H
        05BA   4D         MOV C,L
        05BB   97         SUB A
        05BC   BD         CMP L
        05BD   C2 C7 05   JNZ L05C7
        05C0   B4         ORA H
        05C1   37         STC
        05C2   C8         RZ
        05C3   FE 80      CPI 80H
        05C5   37         STC
        05C6   C8         RZ
        L05C7:
        05C7   7C         MOV A,H
        05C8   A7         ANA A
        05C9   FA E8 05   JM L05E8
        05CC   B2         ORA D
        05CD   FA D4 05   JM L05D4
        05D0   CD 08 06   CALL L0608
        05D3   C9         RET
        L05D4:
        05D4   CD 85 05   CALL neg_de
        05D7   CD 08 06   CALL L0608
        05DA   CD 85 05   CALL neg_de
        05DD   CD 85 00   CALL api_test_hl
        05E0   C8         RZ
        05E1   1B         DCX D
        05E2   CD 7D 05   CALL neg_hl
        05E5   09         DAD B
        05E6   A7         ANA A
        05E7   C9         RET
        L05E8:
        05E8   CD 7D 05   CALL neg_hl
        05EB   7A         MOV A,D
        05EC   A7         ANA A
        05ED   FA FE 05   JM L05FE
        05F0   CD 08 06   CALL L0608
        05F3   CD 85 05   CALL neg_de
        05F6   CD 85 00   CALL api_test_hl
        05F9   C8         RZ
        05FA   1B         DCX D
        05FB   09         DAD B
        05FC   A7         ANA A
        05FD   C9         RET
        L05FE:
        05FE   CD 85 05   CALL neg_de
        0601   CD 08 06   CALL L0608
        0604   CD 7D 05   CALL neg_hl
        0607   C9         RET
        L0608:
        0608 * C5         PUSH B
        0609 * 97         SUB A
        L060A:
        060A * 3C         INR A
        060B * 29         DAD H
        060C * D2 0A 06   JNC L060A
        060F * 4D         MOV C,L
        0610 * 44         MOV B,H
        0611 * 21 00 00   LXI H,0000H
        L0614:
        0614 * F5         PUSH PSW
        0615 * 78         MOV A,B
        0616 * 1F         RAR
        0617 * 47         MOV B,A
        0618 * 79         MOV A,C
        0619 * 1F         RAR
        061A * 4F         MOV C,A
        061B * 29         DAD H
        061C * 7B         MOV A,E
        061D * 91         SUB C
        061E * 5F         MOV E,A
        061F * 7A         MOV A,D
        0620 * 98         SBB B

        ;============================================================================
        ; 0621-07A1  KERNEL SUPPORT AND GENERAL ROUTINES
        ;============================================================================
        0621 * 57         MOV D,A
        0622 * D2 2B 06   JNC L062B
        0625 * EB         XCHG
        0626 * 09         DAD B
        0627 * EB         XCHG
        0628 * C3 2C 06   JMP L062C
        L062B:
        062B * 23         INX H
        L062C:
        062C * F1         POP PSW
        062D * D6 01      SUI 01H
        062F * C2 14 06   JNZ L0614
        0632 * C1         POP B
        0633 * EB         XCHG
        0634 * C9         RET
        L0635:
        0635   E5         PUSH H
        0636   5F         MOV E,A
        0637   16 00      MVI D,00H
        0639   21 0A 00   LXI H,000AH
        063C   CD 4F 00   CALL api_div_helper
        063F   E3         XTHL
        0640   16 30      MVI D,30H
        0642   7B         MOV A,E
        0643   82         ADD D
        0644   77         MOV M,A
        0645   23         INX H
        0646   C1         POP B
        0647   79         MOV A,C
        0648   82         ADD D
        0649   77         MOV M,A
        064A   23         INX H
        064B   C9         RET
        064C   E5         PUSH H
        064D   21 64 00   LXI H,0064H
        0650   CD 4F 00   CALL api_div_helper
        0653   E3         XTHL
        0654   7B         MOV A,E
        0655   CD 35 06   CALL L0635
        0658   D1         POP D
        0659   7B         MOV A,E
        065A   CD 35 06   CALL L0635
        065D   C9         RET
        L065E:
        065E * 01 10 00   LXI B,0010H
        0661 * C3 67 06   JMP L0667
        0664   01 0E 00   LXI B,000EH
        L0667:
        0667 * C5         PUSH B
        0668 * 01 53 40   LXI B,MBOX_FREE
        066B * CD A4 06   CALL L06A4
        066E * C1         POP B
        066F * E5         PUSH H
        0670 * 2A 12 40   LHLD CUR_PCB
        0673 * 09         DAD B
        0674 * 4E         MOV C,M
        0675 * 23         INX H
        0676 * 46         MOV B,M
        0677 * EB         XCHG
        0678 * 71         MOV M,C
        0679 * 23         INX H
        067A * 70         MOV M,B
        067B * 23         INX H
        067C * D1         POP D
        067D * C9         RET
        067E   E5         PUSH H
        067F   CD 8B 00   CALL api_008B
        0682   E3         XTHL
        0683   06 0E      MVI B,0EH
        0685   CD 72 07   CALL memcpy_b
        0688   01 53 40   LXI B,MBOX_FREE
        068B   E1         POP H
        068C   CD 90 04   CALL mbox_put_di
        068F   C9         RET
        L0690:
        0690 * 01 10 00   LXI B,0010H
        0693 * C3 99 06   JMP L0699
        L0696:
        0696   01 0E 00   LXI B,000EH
        L0699:
        0699 * 2A 12 40   LHLD CUR_PCB
        069C * 09         DAD B
        069D * 4E         MOV C,M
        069E * 23         INX H
        069F * 46         MOV B,M
        06A0 * CD A4 06   CALL L06A4
        06A3 * C9         RET
        L06A4:
        06A4 * CD 16 05   CALL sem_wait_timeout
        06A7 * 2A 12 40   LHLD CUR_PCB
        06AA * 11 05 00   LXI D,0005H
        06AD * 19         DAD D
        06AE * 5E         MOV E,M
        06AF * 23         INX H
        06B0 * 56         MOV D,M
        06B1 * 62         MOV H,D
        06B2 * 6B         MOV L,E
        06B3 * 13         INX D
        06B4 * 13         INX D
        06B5 * C9         RET
        06B6   CD D2 06   CALL L06D2
        06B9   CD 90 06   CALL L0690
        06BC   EB         XCHG
        06BD   21 0D 00   LXI H,000DH
        06C0   19         DAD D
        06C1   46         MOV B,M
        06C2   23         INX H
        06C3   4E         MOV C,M
        06C4   23         INX H
        06C5   66         MOV H,M
        06C6   C5         PUSH B
        06C7   E5         PUSH H
        06C8   EB         XCHG
        06C9   01 53 40   LXI B,MBOX_FREE
        06CC   CD 90 04   CALL mbox_put_di
        06CF   D1         POP D
        06D0   C1         POP B
        06D1   C9         RET
        L06D2:
        06D2   E5         PUSH H
        06D3   D5         PUSH D
        06D4   C5         PUSH B
        06D5   F5         PUSH PSW
        06D6   CD 5E 06   CALL L065E
        06D9   F1         POP PSW
        06DA   77         MOV M,A
        06DB   23         INX H
        06DC   97         SUB A
        06DD   77         MOV M,A
        06DE   23         INX H
        06DF   C1         POP B
        06E0   71         MOV M,C
        06E1   23         INX H
        06E2   70         MOV M,B
        06E3   23         INX H
        06E4   C1         POP B
        06E5   71         MOV M,C
        06E6   23         INX H
        06E7   70         MOV M,B
        06E8   23         INX H
        06E9   77         MOV M,A
        06EA   23         INX H
        06EB   77         MOV M,A
        06EC   EB         XCHG
        06ED   C1         POP B
        06EE   CD 90 04   CALL mbox_put_di
        06F1   C9         RET
        L06F2:
        06F2 * E5         PUSH H
        06F3 * CD 5E 06   CALL L065E
        06F6 * C1         POP B
        06F7 * 71         MOV M,C
        06F8 * 23         INX H
        06F9 * 70         MOV M,B
        06FA * E5         PUSH H
        06FB * 2A 12 40   LHLD CUR_PCB
        06FE * 4D         MOV C,L
        06FF * 44         MOV B,H
        0700 * E1         POP H
        0701 * 23         INX H
        0702 * 71         MOV M,C
        0703 * 23         INX H
        0704 * 70         MOV M,B
        0705 * EB         XCHG
        0706 * 01 4D 40   LXI B,404DH
        0709 * CD 90 04   CALL mbox_put_di
        070C * CD 90 06   CALL L0690
        070F * 01 53 40   LXI B,MBOX_FREE
        0712 * CD 90 04   CALL mbox_put_di
        0715 * C9         RET
        0716   F3         DI
        0717   F5         PUSH PSW
        0718   C5         PUSH B
        0719   D5         PUSH D
        071A   E5         PUSH H
        071B   3A 4E 40   LDA 404EH
        071E   FE 00      CPI 00H
        0720   CA 6D 07   JZ L076D
        0723   2A 4F 40   LHLD 404FH
        0726   11 4F 40   LXI D,404FH
        L0729:
        0729   F5         PUSH PSW
        072A   E5         PUSH H
        072B   D5         PUSH D
        072C   11 06 00   LXI D,0006H
        072F   19         DAD D
        0730   7E         MOV A,M
        0731   B9         CMP C
        0732   C2 61 07   JNZ L0761
        0735   23         INX H
        0736   7E         MOV A,M
        0737   B8         CMP B
        0738   C2 61 07   JNZ L0761
        073B   D1         POP D
        073C   E1         POP H
        073D   E5         PUSH H
        073E   4E         MOV C,M
        073F   23         INX H
        0740   46         MOV B,M
        0741   23         INX H
        0742   EB         XCHG
        0743   71         MOV M,C
        0744   23         INX H
        0745   70         MOV M,B
        0746   EB         XCHG
        0747   4E         MOV C,M
        0748   23         INX H
        0749   46         MOV B,M
        074A   E1         POP H
        074B   F1         POP PSW
        074C   3A 4E 40   LDA 404EH
        074F   3D         DCR A
        0750   32 4E 40   STA 404EH
        0753   C2 59 07   JNZ L0759
        0756   32 4D 40   STA 404DH
        L0759:
        0759   CD 90 04   CALL mbox_put_di
        075C   E1         POP H
        075D   D1         POP D
        075E   C1         POP B
        075F   F1         POP PSW
        0760   C9         RET
        L0761:
        0761   D1         POP D
        0762   E1         POP H
        0763   5E         MOV E,M
        0764   23         INX H
        0765   56         MOV D,M
        0766   2B         DCX H
        0767   EB         XCHG
        0768   F1         POP PSW
        0769   3D         DCR A
        076A   C2 29 07   JNZ L0729
        L076D:
        076D   E1         POP H
        076E   D1         POP D
        076F   C1         POP B
        0770   F1         POP PSW
        0771   C9         RET

        ;----------------------------------------------------------------------
        ; memcpy_b  (0772H)
        ;   Copy B bytes from (DE) to (HL) (API 0073h).
        ;----------------------------------------------------------------------
        memcpy_b:
        0772 * 04         INR B
        0773 * 05         DCR B
        0774 * C8         RZ
        L0775:
        0775 * 1A         LDAX D
        0776 * 77         MOV M,A
        0777 * 23         INX H
        0778 * 13         INX D
        0779 * 05         DCR B
        077A * C2 75 07   JNZ L0775
        077D * C9         RET
        077E   04         INR B
        L077F:
        077F   05         DCR B
        0780   C8         RZ
        0781   1A         LDAX D
        0782   77         MOV M,A
        0783   2B         DCX H
        0784   1B         DCX D
        0785   C3 7F 07   JMP L077F
        0788   78         MOV A,B
        0789   80         ADD B
        078A   41         MOV B,C
        078B   4F         MOV C,A
        078C   CD 72 07   CALL memcpy_b
        L078F:
        078F   0D         DCR C
        0790   F8         RM
        0791   06 80      MVI B,80H
        0793   CD 72 07   CALL memcpy_b
        0796   C3 8F 07   JMP L078F
        0799   3C         INR A
        L079A:
        079A   3D         DCR A
        079B   C8         RZ
        079C   36 20      MVI M,20H
        079E   23         INX H
        079F   C3 9A 07   JMP L079A

        ;============================================================================
        ; 07A2-09CE  CONSOLE DRIVER (8251 AT 60H/61H, INTERRUPT DRIVEN)
        ;   RST 4 fires for RxRDY and TxRDY. ESC aborts a line and signals SEM_ATTN. Echo, backspace, 80 chars.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; console_isr  (07A2H)
        ;   Console UART ISR (RST 4): status AND 03h: RxRDY -> console_rx, TxRDY
        ;   -> console_tx.
        ;----------------------------------------------------------------------
        console_isr:
        07A2 * F5         PUSH PSW
        07A3 * DB 61      IN CON_CTL
        07A5 * E6 03      ANI 03H
        07A7 * FE 02      CPI 02H
        07A9 * CA E5 07   JZ console_rx
        07AC * FE 01      CPI 01H
        07AE * CA B6 08   JZ console_tx
        07B1 * FE 03      CPI 03H
        07B3 * CA E5 07   JZ console_rx
        07B6   F1         POP PSW
        07B7   FB         EI
        07B8   C9         RET
        L07B9:
        07B9 * 21 AF 48   LXI H,SEM_CON_LINE
        07BC * 36 00      MVI M,00H
        07BE * 23         INX H
        07BF * 36 00      MVI M,00H
        07C1 * 21 A9 48   LXI H,SEM_CON_OUT
        07C4 * 36 01      MVI M,01H
        07C6 * 23         INX H
        07C7 * 36 00      MVI M,00H
        07C9 * 3E 03      MVI A,03H
        07CB * D3 61      OUT CON_CTL                ; 8251: dummy/flush
        07CD * 3E 53      MVI A,53H
        07CF * D3 61      OUT CON_CTL                ; 8251: RESET (IR=1)
        07D1 * 3E 7A      MVI A,7AH
        07D3 * D3 61      OUT CON_CTL                ; 8251: mode: 7 bits, even parity, 1 stop, x16
        07D5 * 3E 26      MVI A,26H
        07D7 * D3 61      OUT CON_CTL                ; 8251: command: RTS RxE DTR (transmitter off)
        07D9 * 32 C0 48   STA 48C0H
        07DC * DB 60      IN CON_DATA
        07DE * DB FE      IN SYSCTL
        07E0 * F6 10      ORI 10H
        07E2 * D3 FE      OUT SYSCTL
        07E4 * C9         RET

        ;----------------------------------------------------------------------
        ; console_rx  (07E5H)
        ;   Console receive: strip parity, ESC signals SEM_ATTN,
        ;   backspace/CR/line editing, echo request, 80-character line limit.
        ;----------------------------------------------------------------------
        console_rx:
        07E5 * C5         PUSH B
        07E6 * D5         PUSH D
        07E7 * E5         PUSH H
        07E8 * DB 60      IN CON_DATA
        07EA * E6 7F      ANI 7FH
        07EC * F5         PUSH PSW
        07ED * FE 1B      CPI 1BH
        07EF * C2 08 08   JNZ L0808
        07F2 * 01 01 41   LXI B,SEM_ATTN
        07F5 * 0A         LDAX B
        07F6 * FE 00      CPI 00H
        07F8 * C2 08 08   JNZ L0808
        07FB * 03         INX B
        07FC * 0A         LDAX B
        07FD * FE 01      CPI 01H
        07FF * C2 08 08   JNZ L0808
        0802   01 01 41   LXI B,SEM_ATTN
        0805   CD FE 04   CALL sem_signal_core
        L0808:
        0808 * 3A B5 48   LDA CON_ECHO_FLAG
        080B * 07         RLC
        080C * DA 7E 08   JC L087E
        080F * 3A BA 48   LDA 48BAH
        0812 * 07         RLC
        0813 * D2 7E 08   JNC L087E
        0816 * 3A B6 48   LDA 48B6H
        0819 * FE 50      CPI 50H
        081B * D2 85 08   JNC L0885
        081E * F1         POP PSW
        081F * 32 B7 48   STA 48B7H
        0822 * FE 08      CPI 08H
        0824 * C2 3F 08   JNZ L083F
        0827 * 3A B6 48   LDA 48B6H
        082A * FE 00      CPI 00H
        082C * CA 7F 08   JZ L087F
        082F * 3D         DCR A
        0830 * 32 B6 48   STA 48B6H
        0833 * 2A B8 48   LHLD 48B8H
        0836 * 36 00      MVI M,00H
        0838 * 2B         DCX H
        0839 * 22 B8 48   SHLD 48B8H
        083C * C3 6C 08   JMP L086C
        L083F:
        083F * FE 1B      CPI 1BH
        0841 * C2 4E 08   JNZ L084E
        0844 * 3E FF      MVI A,FFH
        0846 * 32 BB 48   STA 48BBH
        0849 * 3E 0D      MVI A,0DH
        084B * 32 B7 48   STA 48B7H
        L084E:
        084E * FE 0D      CPI 0DH
        0850 * C2 56 08   JNZ L0856
        0853 * C3 86 08   JMP L0886
        L0856:
        0856 * FE 20      CPI 20H
        0858 * FA 7F 08   JM L087F
        085B * FE 7F      CPI 7FH
        085D * CA 7F 08   JZ L087F
        0860 * 2A B8 48   LHLD 48B8H
        0863 * 77         MOV M,A
        0864 * 23         INX H
        0865 * 22 B8 48   SHLD 48B8H
        0868 * 21 B6 48   LXI H,48B6H
        086B * 34         INR M
        L086C:
        086C * 3E FF      MVI A,FFH
        086E * 32 B5 48   STA CON_ECHO_FLAG
        0871 * 3A C0 48   LDA 48C0H
        0874 * F6 01      ORI 01H
        0876 * 32 C0 48   STA 48C0H
        0879 * D3 61      OUT CON_CTL
        087B * C3 7F 08   JMP L087F
        L087E:
        087E   F1         POP PSW
        L087F:
        087F * E1         POP H
        0880 * D1         POP D
        0881 * C1         POP B
        0882 * F1         POP PSW
        0883 * FB         EI
        0884 * C9         RET
        L0885:
        0885   F1         POP PSW
        L0886:
        0886 * 3E 00      MVI A,00H
        0888 * 32 BA 48   STA 48BAH
        088B * 01 AF 48   LXI B,SEM_CON_LINE
        088E * CD FE 04   CALL sem_signal_core
        0891 * E1         POP H
        0892 * D1         POP D
        0893 * C1         POP B
        0894 * F1         POP PSW
        0895 * FB         EI
        0896 * C9         RET

        ;----------------------------------------------------------------------
        ; con_read_line  (0897H)
        ;   API 00BBh: read a line from the console into HL (blocks on
        ;   SEM_CON_LINE); returns the length.
        ;----------------------------------------------------------------------
        con_read_line:
        0897 * F3         DI
        0898 * 22 B8 48   SHLD 48B8H
        089B * AF         XRA A
        089C * 32 B6 48   STA 48B6H
        089F * 32 BB 48   STA 48BBH
        08A2 * 2F         CMA
        08A3 * 32 BA 48   STA 48BAH
        08A6 * 01 AF 48   LXI B,SEM_CON_LINE
        08A9 * CD B8 00   CALL api_sem_wait
        08AC * F3         DI
        08AD * 3A BB 48   LDA 48BBH
        08B0 * 07         RLC
        08B1 * 3A B6 48   LDA 48B6H
        08B4 * FB         EI
        08B5 * C9         RET

        ;----------------------------------------------------------------------
        ; console_tx  (08B6H)
        ;   Console transmit: echo character, or next byte of the output block;
        ;   when idle clears TxEN (OUT 61h).
        ;----------------------------------------------------------------------
        console_tx:
        08B6 * C5         PUSH B
        08B7 * D5         PUSH D
        08B8 * E5         PUSH H
        08B9 * 3A B5 48   LDA CON_ECHO_FLAG
        08BC * 07         RLC
        08BD * D2 DC 08   JNC L08DC
        08C0 * 3A B7 48   LDA 48B7H
        08C3 * D3 60      OUT CON_DATA
        08C5 * FE 0D      CPI 0DH
        08C7 * C2 D5 08   JNZ L08D5
        08CA   3E 0A      MVI A,0AH
        08CC   32 B7 48   STA 48B7H
        L08CF:
        08CF * E1         POP H
        08D0 * D1         POP D
        08D1 * C1         POP B
        08D2 * F1         POP PSW
        08D3 * FB         EI
        08D4 * C9         RET
        L08D5:
        08D5 * AF         XRA A
        08D6 * 32 B5 48   STA CON_ECHO_FLAG
        08D9 * C3 CF 08   JMP L08CF
        L08DC:
        08DC * 3A BD 48   LDA 48BDH
        08DF * 07         RLC
        08E0 * DA F4 08   JC L08F4
        08E3 * 3E 00      MVI A,00H
        08E5 * D3 60      OUT CON_DATA
        08E7 * 3A C0 48   LDA 48C0H
        08EA * E6 FE      ANI FEH
        08EC * 32 C0 48   STA 48C0H
        08EF * D3 61      OUT CON_CTL
        08F1 * C3 CF 08   JMP L08CF
        L08F4:
        08F4 * 2A BE 48   LHLD 48BEH
        08F7 * 7E         MOV A,M
        08F8 * D3 60      OUT CON_DATA
        08FA * 23         INX H
        08FB * 22 BE 48   SHLD 48BEH
        08FE * 3A BC 48   LDA 48BCH
        0901 * 3D         DCR A
        0902 * 32 BC 48   STA 48BCH
        0905 * C2 CF 08   JNZ L08CF
        0908 * 3E 00      MVI A,00H
        090A * 32 BD 48   STA 48BDH
        090D * 01 A9 48   LXI B,SEM_CON_OUT
        0910 * CD FE 04   CALL sem_signal_core
        0913 * C3 CF 08   JMP L08CF

        ;----------------------------------------------------------------------
        ; con_put_block  (0916H)
        ;   API 00BEh: send A bytes at HL to the console and wait until they are
        ;   out.
        ;----------------------------------------------------------------------
        con_put_block:
        0916 * F3         DI
        0917 * F5         PUSH PSW
        0918 * 01 A9 48   LXI B,SEM_CON_OUT
        091B * CD B8 00   CALL api_sem_wait
        091E * F3         DI
        091F * 3E FF      MVI A,FFH
        0921 * 32 BD 48   STA 48BDH
        0924 * 3A C0 48   LDA 48C0H
        0927 * F6 01      ORI 01H
        0929 * 32 C0 48   STA 48C0H
        092C * D3 61      OUT CON_CTL
        092E * F1         POP PSW
        092F * 32 BC 48   STA 48BCH
        0932 * 22 BE 48   SHLD 48BEH
        0935 * 01 A9 48   LXI B,SEM_CON_OUT
        0938 * CD B8 00   CALL api_sem_wait
        093B * 01 A9 48   LXI B,SEM_CON_OUT
        093E * CD FE 04   CALL sem_signal_core
        0941 * C9         RET
        0942   F5         PUSH PSW
        0943   E5         PUSH H
        0944   FE 00      CPI 00H
        0946   CA 66 09   JZ L0966
        0949   FE 09      CPI 09H
        094B   D2 66 09   JNC L0966
        094E   3A 46 48   LDA 4846H
        0951   FE 00      CPI 00H
        0953   CA 6A 09   JZ L096A
        0956   3A 47 48   LDA 4847H
        0959   FE 00      CPI 00H
        095B   CA 88 09   JZ L0988
        095E   3A 48 48   LDA 4848H
        0961   FE 00      CPI 00H
        0963   CA A6 09   JZ L09A6
        L0966:
        0966   E1         POP H
        0967   F1         POP PSW
        0968   37         STC
        0969   C9         RET
        L096A:
        096A   11 6D 02   LXI D,026DH
        096D   21 4C 48   LXI H,484CH
        0970   06 0F      MVI B,0FH
        0972   CD 73 00   CALL api_memcpy
        0975   E1         POP H
        0976   22 59 48   SHLD 4859H
        0979   F1         POP PSW
        097A   32 4E 48   STA 484EH
        097D   3E 01      MVI A,01H
        097F   32 46 48   STA 4846H
        0982   21 4C 48   LXI H,484CH
        0985   C3 C4 09   JMP L09C4
        L0988:
        0988   11 7C 02   LXI D,027CH
        098B   21 5B 48   LXI H,485BH
        098E   06 0F      MVI B,0FH
        0990   CD 73 00   CALL api_memcpy
        0993   E1         POP H
        0994   22 68 48   SHLD 4868H
        0997   F1         POP PSW
        0998   32 5D 48   STA 485DH
        099B   3E 01      MVI A,01H
        099D   32 47 48   STA 4847H
        09A0   21 5B 48   LXI H,485BH
        09A3   C3 C4 09   JMP L09C4
        L09A6:
        09A6   11 8B 02   LXI D,028BH
        09A9   21 6A 48   LXI H,486AH
        09AC   06 0F      MVI B,0FH
        09AE   CD 73 00   CALL api_memcpy
        09B1   E1         POP H
        09B2   22 77 48   SHLD 4877H
        09B5   F1         POP PSW
        09B6   32 6C 48   STA 486CH
        09B9   3E 01      MVI A,01H
        09BB   32 48 48   STA 4848H
        09BE   21 6A 48   LXI H,486AH
        09C1   C3 C4 09   JMP L09C4
        L09C4:
        09C4   5E         MOV E,M
        09C5   23         INX H
        09C6   56         MOV D,M
        09C7   23         INX H
        09C8   F3         DI
        09C9   CD 68 01   CALL process_create
        09CC   FB         EI
        09CD   AF         XRA A
        09CE   C9         RET

        ;============================================================================
        ; 09CF-0C9A  OPERATOR DIALOG PROCESS
        ;   Menu: C, D, P. P starts a process (priority 1-8, hex address). ESC returns to the menu.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; proc_dialog  (09CFH)
        ;   Process (prio 3): operator dialog. Menu: C = SPC/1 dialog (stub), D
        ;   = debugger (CALL F008h), P = start a process.
        ;----------------------------------------------------------------------
        proc_dialog:
        09CF * CD F6 0B   CALL con_clear_screen
        09D2 * 11 9D 0C   LXI D,0C9DH
        09D5 * 06 28      MVI B,28H
        09D7 * CD D9 0B   CALL con_build_text
        09DA * CD A8 0B   CALL con_flush_buf

        ;----------------------------------------------------------------------
        ; menu  (09DDH)
        ;   Redraw the menu and prompt for a command.
        ;----------------------------------------------------------------------
        menu:
        09DD * 11 C5 0C   LXI D,0CC5H
        09E0 * 06 46      MVI B,46H
        09E2 * CD D9 0B   CALL con_build_text
        09E5 * CD A8 0B   CALL con_flush_buf
        09E8 * 11 0B 0D   LXI D,0D0BH
        09EB * 06 53      MVI B,53H
        09ED * CD D9 0B   CALL con_build_text
        09F0 * CD A8 0B   CALL con_flush_buf
        L09F3:
        09F3 * CD AE 0B   CALL get_command
        09F6 * 3A 58 49   LDA CON_LINE_BUF
        09F9 * FE 50      CPI 50H
        09FB * CA 25 0A   JZ cmd_start_process
        09FE * FE 44      CPI 44H
        0A00 * CA 9B 0B   JZ cmd_debugger
        0A03 * FE 43      CPI 43H
        0A05 * CA A5 0B   JZ cmd_spc1_dialog
        0A08 * FE 70      CPI 70H
        0A0A * CA 25 0A   JZ cmd_start_process
        0A0D * FE 64      CPI 64H
        0A0F * CA 9B 0B   JZ cmd_debugger
        0A12 * FE 63      CPI 63H
        0A14 * CA A5 0B   JZ cmd_spc1_dialog
        0A17 * 11 5E 0D   LXI D,0D5EH
        0A1A * 06 1D      MVI B,1DH
        0A1C * CD D9 0B   CALL con_build_text
        0A1F * CD A8 0B   CALL con_flush_buf
        0A22 * C3 F3 09   JMP L09F3

        ;----------------------------------------------------------------------
        ; cmd_start_process  (0A25H)
        ;   P command: ask for a priority (1-8) and a hex start address, take a
        ;   free PCB template (026Dh+) and start it.
        ;----------------------------------------------------------------------
        cmd_start_process:
        0A25 * 11 AB 0D   LXI D,0DABH
        0A28 * 06 35      MVI B,35H
        0A2A * CD D9 0B   CALL con_build_text
        0A2D * CD A8 0B   CALL con_flush_buf
        0A30 * CD B4 0B   CALL L0BB4
        0A33 * DA 8D 0B   JC L0B8D
        0A36 * 06 01      MVI B,01H
        0A38 * CD 2E 0C   CALL L0C2E
        0A3B * DA 8D 0B   JC L0B8D
        0A3E * 7D         MOV A,L
        0A3F * FE 00      CPI 00H
        0A41 * CA 8D 0B   JZ L0B8D
        0A44 * FE 09      CPI 09H
        0A46 * D2 8D 0B   JNC L0B8D
        0A49   32 A6 48   STA 48A6H
        0A4C   11 E0 0D   LXI D,0DE0H
        0A4F   06 29      MVI B,29H
        0A51   CD D9 0B   CALL con_build_text
        0A54   CD A8 0B   CALL con_flush_buf
        0A57   CD AE 0B   CALL get_command
        0A5A   FE 04      CPI 04H
        0A5C   C2 8D 0B   JNZ L0B8D
        0A5F   CD 01 0C   CALL L0C01
        0A62   DA 8D 0B   JC L0B8D
        0A65   11 58 49   LXI D,CON_LINE_BUF
        0A68   CD DD 24   CALL parse_hex
        0A6B   22 A7 48   SHLD 48A7H
        0A6E   3A 46 48   LDA 4846H
        0A71   FE 00      CPI 00H
        0A73   CA AC 0A   JZ L0AAC
        0A76   3A 47 48   LDA 4847H
        0A79   FE 00      CPI 00H
        0A7B   CA CE 0A   JZ L0ACE
        0A7E   3A 48 48   LDA 4848H
        0A81   FE 00      CPI 00H
        0A83   CA F0 0A   JZ L0AF0
        0A86   3A 49 48   LDA 4849H
        0A89   FE 00      CPI 00H
        0A8B   CA 12 0B   JZ L0B12
        0A8E   3A 4A 48   LDA 484AH
        0A91   FE 00      CPI 00H
        0A93   CA 34 0B   JZ L0B34
        0A96   3A 4B 48   LDA 484BH
        0A99   FE 00      CPI 00H
        0A9B   CA 56 0B   JZ L0B56
        0A9E   11 09 0E   LXI D,0E09H
        0AA1   06 26      MVI B,26H
        0AA3   CD D9 0B   CALL con_build_text
        0AA6   CD A8 0B   CALL con_flush_buf
        0AA9   C3 81 0B   JMP L0B81
        L0AAC:
        0AAC   11 6D 02   LXI D,026DH
        0AAF   21 4C 48   LXI H,484CH
        0AB2   06 0F      MVI B,0FH
        0AB4   CD 73 00   CALL api_memcpy
        0AB7   3A A6 48   LDA 48A6H
        0ABA   32 4E 48   STA 484EH
        0ABD   2A A7 48   LHLD 48A7H
        0AC0   22 59 48   SHLD 4859H
        0AC3   3E 01      MVI A,01H
        0AC5   32 46 48   STA 4846H
        0AC8   21 4C 48   LXI H,484CH
        0ACB   C3 78 0B   JMP start_user_process
        L0ACE:
        0ACE   11 7C 02   LXI D,027CH
        0AD1   21 5B 48   LXI H,485BH
        0AD4   06 0F      MVI B,0FH
        0AD6   CD 73 00   CALL api_memcpy
        0AD9   3A A6 48   LDA 48A6H
        0ADC   32 5D 48   STA 485DH
        0ADF   2A A7 48   LHLD 48A7H
        0AE2   22 68 48   SHLD 4868H
        0AE5   3E 01      MVI A,01H
        0AE7   32 47 48   STA 4847H
        0AEA   21 5B 48   LXI H,485BH
        0AED   C3 78 0B   JMP start_user_process
        L0AF0:
        0AF0   11 8B 02   LXI D,028BH
        0AF3   21 6A 48   LXI H,486AH
        0AF6   06 0F      MVI B,0FH
        0AF8   CD 73 00   CALL api_memcpy
        0AFB   3A A6 48   LDA 48A6H
        0AFE   32 6C 48   STA 486CH
        0B01   2A A7 48   LHLD 48A7H
        0B04   22 77 48   SHLD 4877H
        0B07   3E 01      MVI A,01H
        0B09   32 48 48   STA 4848H
        0B0C   21 6A 48   LXI H,486AH
        0B0F   C3 78 0B   JMP start_user_process
        L0B12:
        0B12   11 9A 02   LXI D,029AH
        0B15   21 79 48   LXI H,4879H
        0B18   06 0F      MVI B,0FH
        0B1A   CD 73 00   CALL api_memcpy
        0B1D   3A A6 48   LDA 48A6H
        0B20   32 7B 48   STA 487BH
        0B23   2A A7 48   LHLD 48A7H
        0B26   22 86 48   SHLD 4886H
        0B29   3E 01      MVI A,01H
        0B2B   32 49 48   STA 4849H
        0B2E   21 79 48   LXI H,4879H
        0B31   C3 78 0B   JMP start_user_process
        L0B34:
        0B34   11 A9 02   LXI D,02A9H
        0B37   21 88 48   LXI H,4888H
        0B3A   06 0F      MVI B,0FH
        0B3C   CD 73 00   CALL api_memcpy
        0B3F   3A A6 48   LDA 48A6H
        0B42   32 8A 48   STA 488AH
        0B45   2A A7 48   LHLD 48A7H
        0B48   22 95 48   SHLD 4895H
        0B4B   3E 01      MVI A,01H
        0B4D   32 4A 48   STA 484AH
        0B50   21 88 48   LXI H,4888H
        0B53   C3 78 0B   JMP start_user_process
        L0B56:
        0B56   11 B8 02   LXI D,02B8H
        0B59   21 97 48   LXI H,4897H
        0B5C   06 0F      MVI B,0FH
        0B5E   CD 73 00   CALL api_memcpy
        0B61   3A A6 48   LDA 48A6H
        0B64   32 99 48   STA 4899H
        0B67   2A A7 48   LHLD 48A7H
        0B6A   22 A4 48   SHLD 48A4H
        0B6D   3E 01      MVI A,01H
        0B6F   32 4B 48   STA 484BH
        0B72   21 97 48   LXI H,4897H
        0B75   C3 78 0B   JMP start_user_process

        ;----------------------------------------------------------------------
        ; start_user_process  (0B78H)
        ;   Start the new process, wait for ESC (SEM_ATTN), then clear the
        ;   screen and return to the menu.
        ;----------------------------------------------------------------------
        start_user_process:
        0B78   5E         MOV E,M
        0B79   23         INX H
        0B7A   56         MOV D,M
        0B7B   23         INX H
        0B7C   F3         DI
        0B7D   CD 68 01   CALL process_create
        0B80   FB         EI
        L0B81:
        0B81   01 01 41   LXI B,SEM_ATTN
        0B84   CD B8 00   CALL api_sem_wait
        0B87   CD F6 0B   CALL con_clear_screen
        0B8A   C3 DD 09   JMP menu
        L0B8D:
        0B8D * 11 7B 0D   LXI D,0D7BH
        0B90 * 06 30      MVI B,30H
        0B92 * CD D9 0B   CALL con_build_text
        0B95 * CD A8 0B   CALL con_flush_buf
        0B98 * C3 F3 09   JMP L09F3

        ;----------------------------------------------------------------------
        ; cmd_debugger  (0B9BH)
        ;   D command: DI; CALL F008h (external debugger).
        ;----------------------------------------------------------------------
        cmd_debugger:
        0B9B   F3         DI
        0B9C   CD 08 F0   CALL F008H
        0B9F   CD F6 0B   CALL con_clear_screen
        0BA2   C3 DD 09   JMP menu

        ;----------------------------------------------------------------------
        ; cmd_spc1_dialog  (0BA5H)
        ;   C command: only redraws the menu in this image.
        ;----------------------------------------------------------------------
        cmd_spc1_dialog:
        0BA5 * C3 DD 09   JMP menu

        ;----------------------------------------------------------------------
        ; con_flush_buf  (0BA8H)
        ;   Send the text prepared at CON_OUT_BUF.
        ;----------------------------------------------------------------------
        con_flush_buf:
        0BA8 * 21 08 49   LXI H,CON_OUT_BUF
        0BAB * C3 BE 00   JMP api_con_put_block

        ;----------------------------------------------------------------------
        ; get_command  (0BAEH)
        ;   Read one line and leave the first character at CON_LINE_BUF.
        ;----------------------------------------------------------------------
        get_command:
        0BAE * 21 58 49   LXI H,CON_LINE_BUF
        0BB1 * C3 BB 00   JMP api_con_read_line
        L0BB4:
        0BB4 * 21 58 49   LXI H,CON_LINE_BUF
        0BB7 * CD BB 00   CALL api_con_read_line
        0BBA * 4F         MOV C,A
        0BBB * 47         MOV B,A
        0BBC * 21 58 49   LXI H,CON_LINE_BUF
        0BBF * 7E         MOV A,M
        L0BC0:
        0BC0 * FE 30      CPI 30H
        0BC2 * DA D6 0B   JC L0BD6
        0BC5 * FE 3A      CPI 3AH
        0BC7 * D2 D6 0B   JNC L0BD6
        0BCA * 0D         DCR C
        0BCB * C2 D1 0B   JNZ L0BD1
        0BCE * AF         XRA A
        0BCF * 78         MOV A,B
        0BD0 * C9         RET
        L0BD1:
        0BD1   23         INX H
        0BD2   7E         MOV A,M
        0BD3   C3 C0 0B   JMP L0BC0
        L0BD6:
        0BD6   37         STC
        0BD7   78         MOV A,B
        0BD8   C9         RET

        ;----------------------------------------------------------------------
        ; con_build_text  (0BD9H)
        ;   Copy B bytes from DE into CON_OUT_BUF; returns A = B.
        ;----------------------------------------------------------------------
        con_build_text:
        0BD9 * 21 08 49   LXI H,CON_OUT_BUF
        0BDC * C5         PUSH B
        0BDD * CD 73 00   CALL api_memcpy
        0BE0 * C1         POP B
        0BE1 * 78         MOV A,B
        0BE2 * C9         RET
        0BE3 ? 21 08 49   LXI H,CON_OUT_BUF
        0BE6 ? 3E 50      MVI A,50H
        0BE8 ? C3 55 00   JMP api_0055
        0BEB ? 11 7B 0D   LXI D,0D7BH
        0BEE ? 06 02      MVI B,02H
        0BF0 ? CD D9 0B   CALL con_build_text
        0BF3 ? C3 A8 0B   JMP con_flush_buf

        ;----------------------------------------------------------------------
        ; con_clear_screen  (0BF6H)
        ;   Send ESC + (clear screen) with padding NULs.
        ;----------------------------------------------------------------------
        con_clear_screen:
        0BF6 * 11 2F 0E   LXI D,0E2FH
        0BF9 * 06 02      MVI B,02H
        0BFB * CD D9 0B   CALL con_build_text
        0BFE * C3 A8 0B   JMP con_flush_buf
        L0C01:
        0C01   21 58 49   LXI H,CON_LINE_BUF
        0C04   06 04      MVI B,04H
        L0C06:
        0C06   7E         MOV A,M
        0C07   FE 30      CPI 30H
        0C09   DA 2C 0C   JC L0C2C
        0C0C   FE 3A      CPI 3AH
        0C0E   DA 25 0C   JC L0C25
        0C11   FE 41      CPI 41H
        0C13   DA 2C 0C   JC L0C2C
        0C16   FE 47      CPI 47H
        0C18   DA 25 0C   JC L0C25
        0C1B   FE 61      CPI 61H
        0C1D   DA 2C 0C   JC L0C2C
        0C20   FE 67      CPI 67H
        0C22   D2 2C 0C   JNC L0C2C
        L0C25:
        0C25   23         INX H
        0C26   05         DCR B
        0C27   C2 06 0C   JNZ L0C06
        0C2A   AF         XRA A
        0C2B   C9         RET
        L0C2C:
        0C2C   37         STC
        0C2D   C9         RET
        L0C2E:
        0C2E * 04         INR B
        0C2F * B8         CMP B
        0C30 * D2 73 0C   JNC L0C73
        0C33 * FE 00      CPI 00H
        0C35 * CA 73 0C   JZ L0C73
        0C38 * FE 01      CPI 01H
        0C3A * CA 4A 0C   JZ L0C4A
        0C3D   FE 02      CPI 02H
        0C3F   CA 54 0C   JZ L0C54
        0C42   FE 03      CPI 03H
        0C44   CA 63 0C   JZ L0C63
        0C47   C3 73 0C   JMP L0C73
        L0C4A:
        0C4A * 3A 58 49   LDA CON_LINE_BUF
        0C4D * D6 30      SUI 30H
        0C4F * 6F         MOV L,A
        0C50 * 26 00      MVI H,00H
        0C52 * AF         XRA A
        0C53 * C9         RET
        L0C54:
        0C54   3A 58 49   LDA CON_LINE_BUF
        0C57   47         MOV B,A
        0C58   3A 59 49   LDA 4959H
        0C5B   CD 75 0C   CALL L0C75
        0C5E   6F         MOV L,A
        0C5F   26 00      MVI H,00H
        0C61   AF         XRA A
        0C62   C9         RET
        L0C63:
        0C63   3A 58 49   LDA CON_LINE_BUF
        0C66   4F         MOV C,A
        0C67   3A 59 49   LDA 4959H
        0C6A   47         MOV B,A
        0C6B   3A 5A 49   LDA 495AH
        0C6E   CD 85 0C   CALL L0C85
        0C71   AF         XRA A
        0C72   C9         RET
        L0C73:
        0C73   37         STC
        0C74   C9         RET
        L0C75:
        0C75   D6 30      SUI 30H
        0C77   4F         MOV C,A
        0C78   78         MOV A,B
        0C79   D6 30      SUI 30H
        0C7B   47         MOV B,A
        0C7C   E6 1F      ANI 1FH
        0C7E   07         RLC
        0C7F   07         RLC
        0C80   07         RLC
        0C81   80         ADD B
        0C82   80         ADD B
        0C83   81         ADD C
        0C84   C9         RET
        L0C85:
        0C85   51         MOV D,C
        0C86   CD 75 0C   CALL L0C75
        0C89   F5         PUSH PSW
        0C8A   7A         MOV A,D
        0C8B   D6 30      SUI 30H
        0C8D   4F         MOV C,A
        0C8E   06 00      MVI B,00H
        0C90   21 64 00   LXI H,0064H
        0C93   CD 7C 00   CALL api_mul16
        0C96   EB         XCHG
        0C97   F1         POP PSW
        0C98   4F         MOV C,A
        0C99   06 00      MVI B,00H
        0C9B   09         DAD B
        0C9C   C9         RET

        ;============================================================================
        ; 0C9D-0E30  CONSOLE TEXT (TERMINAL ESCAPE SEQUENCES: ESC = row col, ESC T, ESC +)
        ;   ESC = r c positions the cursor at (r-20h, c-20h); ESC T clears to end of line; ESC + clears the screen.
        ;   Strings are not NUL terminated: the code passes address and length (see the LXI D / MVI B before CALL 0BD9h).
        ;============================================================================
        0C9D            DB   ESC,'=','%','5','VELKOMMEN TIL IPC/1 OPERATIVSYSTEMET'  ; cursor row 5, col 21
        0CC5            DB   ESC,'=','&','5',' V[LG IMELLEM  F\LGENDE KOMMANDOER:'  ; cursor row 6, col 21
        0CEC            DB   ESC,'=',27H,'5','     ''C''- DIALOG  MED SPC/1'  ; cursor row 7, col 21
        0D0B            DB   ESC,'=','(','5','     ''D''- HOP TIL  DEBUGGER'  ; cursor row 8, col 21
        0D2A            DB   ESC,'=',')','5','     ''P''- OPSTART AF PROCES'  ; cursor row 9, col 21
        0D49            DB   ESC,'=','7',' ',ESC,'T'  ; cursor row 23, col 0
        0D4F            DB   ESC,'=','7',' ','KOMMANDO : '  ; cursor row 23, col 0
        0D5E            DB   ESC,'=','5',' ',ESC,'T'  ; cursor row 21, col 0
        0D64            DB   ESC,'=','6',' ',ESC,'T'  ; cursor row 22, col 0
        0D6A            DB   ESC,'=','7',' ',ESC,'T','KOMMANDO : '  ; cursor row 23, col 0
        0D7B            DB   ESC,'=','5',' ',ESC,'T','INDTASTNINGSFEJL ! '  ; cursor row 21, col 0
        0D94            DB   ESC,'=','6',' ',ESC,'T'  ; cursor row 22, col 0
        0D9A            DB   ESC,'=','7',' ',ESC,'T','KOMMANDO : '  ; cursor row 23, col 0
        0DAB            DB   ESC,'=','5',' ',ESC,'T'  ; cursor row 21, col 0
        0DB1            DB   ESC,'=','6',' ',ESC,'T','INDTAST  PRIORITET  ( 1-8 )  : '  ; cursor row 22, col 0
        0DD6            DB   ESC,'=','7',' ',ESC,'T'  ; cursor row 23, col 0
        0DDC            DB   ESC,'=','6','?'  ; cursor row 22, col 31
        0DE0            DB   ESC,'=','7',' ',ESC,'T','INDTAST STARTADRESSE ( HEX ) : '  ; cursor row 23, col 0
        0E05            DB   ESC,'=','7','?'  ; cursor row 23, col 31
        0E09            DB   ESC,'=','6',' ',ESC,'T','INGEN PROCESKONTROLBLOKKE LEDIGE'  ; cursor row 22, col 0
        0E2F            DB   ESC,'+'  ; clear screen

        ;============================================================================
        ; 0E31-1200  AUX LINK DRIVER (8251 AT 08H/09H)
        ;   Frame: 7E, LEN (counts itself), ADDR, N, sub-messages..., CRC16 (hi, lo), 7E.
        ;   Bytes 40H,7EH,06H,15H,1BH are sent as 40H,K,C with K xor C = byte.  Single 06H/15H bytes are ACK/NAK.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; aux_isr  (0E31H)
        ;   Aux UART ISR (RST 2): status AND 03h: RxRDY -> aux_rx, TxRDY ->
        ;   aux_tx_isr.
        ;----------------------------------------------------------------------
        aux_isr:
        0E31 * F5         PUSH PSW
        0E32 * DB 09      IN AUX_CTL
        0E34 * E6 03      ANI 03H
        0E36 * FE 02      CPI 02H
        0E38 * CA AE 0E   JZ aux_rx
        0E3B * FE 01      CPI 01H
        0E3D * CA 5A 10   JZ aux_tx_isr
        0E40 * FE 03      CPI 03H
        0E42 * CA AE 0E   JZ aux_rx
        0E45   F1         POP PSW
        0E46   FB         EI
        0E47   C9         RET

        ;----------------------------------------------------------------------
        ; aux_init  (0E48H)
        ;   Initialise the aux UART (03h,53h,6Fh,16h) and the CRC tables
        ;   (2556h).
        ;----------------------------------------------------------------------
        aux_init:
        0E48 * 3A D9 48   LDA 48D9H
        0E4B * B7         ORA A
        0E4C * C0         RNZ
        0E4D * 21 C5 48   LXI H,SEM_AUX_RX
        0E50 * 36 00      MVI M,00H
        0E52 * 23         INX H
        0E53 * 36 00      MVI M,00H
        0E55 * 21 D8 48   LXI H,SEM_AUX_TX
        0E58 * 36 01      MVI M,01H
        0E5A * 23         INX H
        0E5B * 36 00      MVI M,00H
        0E5D * 3E 03      MVI A,03H
        0E5F * D3 09      OUT AUX_CTL                ; 8251: dummy/flush
        0E61 * 3E 53      MVI A,53H
        0E63 * D3 09      OUT AUX_CTL                ; 8251: RESET (IR=1)
        0E65 * 3E 6F      MVI A,6FH
        0E67 * D3 09      OUT AUX_CTL                ; 8251: mode: async 8 bits, no parity, 1 stop, x64
        0E69 * 3E 16      MVI A,16H
        0E6B * D3 09      OUT AUX_CTL                ; 8251: command: ER RxE DTR (receive only)
        0E6D * 32 E9 48   STA 48E9H
        0E70 * DB 08      IN AUX_DATA
        0E72 * CD 56 25   CALL crc_init
        0E75 * 3E 00      MVI A,00H
        0E77 * 32 CD 48   STA 48CDH
        0E7A * 32 CE 48   STA 48CEH
        0E7D * 32 D1 48   STA 48D1H
        0E80 * 32 CF 48   STA 48CFH
        0E83 * 32 D0 48   STA 48D0H
        0E86 * 32 D2 48   STA 48D2H
        0E89 * 32 D3 48   STA 48D3H
        0E8C * 32 E0 48   STA 48E0H
        0E8F * 32 E1 48   STA 48E1H
        0E92 * 32 E2 48   STA 48E2H
        0E95 * 32 E5 48   STA 48E5H
        0E98 * 32 E3 48   STA 48E3H
        0E9B * 32 E4 48   STA 48E4H
        0E9E * 32 E6 48   STA 48E6H
        0EA1 * 32 E7 48   STA 48E7H
        0EA4 * 32 E8 48   STA 48E8H
        0EA7 * DB FE      IN SYSCTL
        0EA9 * F6 04      ORI 04H
        0EAB * D3 FE      OUT SYSCTL
        0EAD * C9         RET

        ;----------------------------------------------------------------------
        ; aux_rx  (0EAEH)
        ;   Aux receive state machine: flag 7Eh delimits frames, 40h starts a
        ;   3-byte escape (40h K C -> K xor C), 06h/15h handshake bytes, CRC-16
        ;   accumulated in AUX_CRC.
        ;----------------------------------------------------------------------
        aux_rx:
        0EAE * C5         PUSH B
        0EAF * D5         PUSH D
        0EB0 * E5         PUSH H
        0EB1 * DB 08      IN AUX_DATA
        0EB3 * C3 F0 0E   JMP L0EF0
        0EB6 ? F5         PUSH PSW
        0EB7 ? 5F         MOV E,A
        0EB8 ? 21 B2 4B   LXI H,4BB2H
        0EBB ? CD 09 25   CALL print_hex_byte
        0EBE ? 3A C0 48   LDA 48C0H
        0EC1 ? F6 01      ORI 01H
        0EC3 ? D3 61      OUT CON_CTL
        0EC5 ? DB 61      IN CON_CTL
        0EC7 ? E6 01      ANI 01H
        0EC9 ? CA C5 0E   JZ L0EC5
        0ECC ? 3A B2 4B   LDA 4BB2H
        0ECF ? D3 60      OUT CON_DATA
        0ED1 ? DB 61      IN CON_CTL
        0ED3 ? E6 01      ANI 01H
        0ED5 ? CA D1 0E   JZ L0ED1
        0ED8 ? 3A B3 4B   LDA 4BB3H
        0EDB ? D3 60      OUT CON_DATA
        0EDD ? DB 61      IN CON_CTL
        0EDF ? E6 01      ANI 01H
        0EE1 ? CA DD 0E   JZ L0EDD
        0EE4 ? 3E 20      MVI A,20H
        0EE6 ? D3 60      OUT CON_DATA
        0EE8 ? 3A C0 48   LDA 48C0H
        0EEB ? E6 FE      ANI FEH
        0EED ? D3 61      OUT CON_CTL
        0EEF ? F1         POP PSW
        L0EF0:
        0EF0 * FE 06      CPI 06H
        0EF2 * CA 14 10   JZ aux_got_ack
        0EF5 * FE 15      CPI 15H
        0EF7 * CA 21 10   JZ aux_got_nak
        0EFA * 32 C1 48   STA 48C1H
        0EFD * 3A CD 48   LDA 48CDH
        0F00 * 07         RLC
        0F01 * D2 37 10   JNC L1037
        0F04 * 3E 64      MVI A,64H
        0F06 * 32 EA 48   STA 48EAH
        0F09 * DB 09      IN AUX_CTL
        0F0B * E6 38      ANI 38H
        0F0D * 3E 01      MVI A,01H
        0F0F * C2 7F 0F   JNZ L0F7F
        0F12 * 3A C1 48   LDA 48C1H
        0F15 * FE 7E      CPI 7EH
        0F17 * CA 5A 0F   JZ L0F5A
        0F1A * 3A CE 48   LDA 48CEH
        0F1D * 07         RLC
        0F1E * D2 37 10   JNC L1037
        0F21 * 3A C1 48   LDA 48C1H
        0F24 * FE 40      CPI 40H
        0F26 * CA A2 0F   JZ L0FA2
        0F29 * 3A CF 48   LDA 48CFH
        0F2C * 07         RLC
        0F2D * DC AA 0F   CC L0FAA
        0F30 * 3A D1 48   LDA 48D1H
        0F33 * 07         RLC
        0F34 * D4 D4 0F   CNC L0FD4
        0F37 * 3A C1 48   LDA 48C1H
        0F3A * CD 3D 25   CALL crc_update
        0F3D * 3A C2 48   LDA 48C2H
        0F40 * FE 00      CPI 00H
        0F42 * CA F4 0F   JZ L0FF4
        0F45 * 2A CB 48   LHLD 48CBH
        0F48 * 3A C1 48   LDA 48C1H
        0F4B * 77         MOV M,A
        0F4C * 23         INX H
        0F4D * 22 CB 48   SHLD 48CBH
        0F50 * 3A C2 48   LDA 48C2H
        0F53 * 3D         DCR A
        0F54 * 32 C2 48   STA 48C2H
        0F57 * C3 37 10   JMP L1037
        L0F5A:
        0F5A * 3A D1 48   LDA 48D1H
        0F5D * 07         RLC
        0F5E * DA 69 0F   JC L0F69
        0F61 * 3E FF      MVI A,FFH
        0F63 * 32 CE 48   STA 48CEH
        0F66 * C3 37 10   JMP L1037
        L0F69:
        0F69 * 3A D3 48   LDA 48D3H
        0F6C * 07         RLC
        0F6D * 3E 03      MVI A,03H
        0F6F * D2 7F 0F   JNC L0F7F
        0F72 * CD E6 0F   CALL aux_crc_ok
        0F75 * 3E 04      MVI A,04H
        0F77 * DA 7F 0F   JC L0F7F
        0F7A * 3E 00      MVI A,00H
        0F7C * C3 7F 0F   JMP L0F7F
        L0F7F:
        0F7F * 32 C3 48   STA AUX_STATUS
        0F82 * 3E 00      MVI A,00H
        0F84 * 32 CD 48   STA 48CDH
        0F87 * 32 CE 48   STA 48CEH
        0F8A * 32 D1 48   STA 48D1H
        0F8D * 32 CF 48   STA 48CFH
        0F90 * 32 D0 48   STA 48D0H
        0F93 * 32 D2 48   STA 48D2H
        0F96 * 32 D3 48   STA 48D3H
        0F99 * 01 C5 48   LXI B,SEM_AUX_RX
        0F9C * CD B5 00   CALL api_00B5
        0F9F * C3 37 10   JMP L1037
        L0FA2:
        0FA2 * 3E FF      MVI A,FFH
        0FA4 * 32 CF 48   STA 48CFH
        0FA7 * C3 37 10   JMP L1037
        L0FAA:
        0FAA * 3A D0 48   LDA 48D0H
        0FAD * 07         RLC
        0FAE * D2 C5 0F   JNC L0FC5
        0FB1 * 3A C1 48   LDA 48C1H
        0FB4 * 47         MOV B,A
        0FB5 * 3A C4 48   LDA 48C4H
        0FB8 * A8         XRA B
        0FB9 * 32 C1 48   STA 48C1H
        0FBC * 3E 00      MVI A,00H
        0FBE * 32 CF 48   STA 48CFH
        0FC1 * 32 D0 48   STA 48D0H
        0FC4 * C9         RET
        L0FC5:
        0FC5 * 3A C1 48   LDA 48C1H
        0FC8 * 32 C4 48   STA 48C4H
        0FCB * 3E FF      MVI A,FFH
        0FCD * 32 D0 48   STA 48D0H
        0FD0 * E1         POP H
        0FD1 * C3 37 10   JMP L1037
        L0FD4:
        0FD4 * 3E FF      MVI A,FFH
        0FD6 * 32 D1 48   STA 48D1H
        0FD9 * 3A C1 48   LDA 48C1H
        0FDC * 32 C2 48   STA 48C2H
        0FDF * 21 00 00   LXI H,0000H
        0FE2 * 22 B0 4B   SHLD AUX_CRC
        0FE5 * C9         RET

        ;----------------------------------------------------------------------
        ; aux_crc_ok  (0FE6H)
        ;   Carry clear when AUX_CRC = 0 (frame valid).
        ;----------------------------------------------------------------------
        aux_crc_ok:
        0FE6 * 2A B0 4B   LHLD AUX_CRC
        0FE9 * CD 85 00   CALL api_test_hl
        0FEC * CA F1 0F   JZ L0FF1
        0FEF   37         STC
        0FF0   C9         RET
        L0FF1:
        0FF1 * 37         STC
        0FF2 * 3F         CMC
        0FF3 * C9         RET
        L0FF4:
        0FF4 * 3A D2 48   LDA 48D2H
        0FF7 * 07         RLC
        0FF8 * DA 03 10   JC L1003
        0FFB * 3E FF      MVI A,FFH
        0FFD * 32 D2 48   STA 48D2H
        1000 * C3 37 10   JMP L1037
        L1003:
        1003 * 3A D3 48   LDA 48D3H
        1006 * 07         RLC
        1007 * 3E 02      MVI A,02H
        1009 * DA 7F 0F   JC L0F7F
        100C * 3E FF      MVI A,FFH
        100E * 32 D3 48   STA 48D3H
        1011 * C3 37 10   JMP L1037

        ;----------------------------------------------------------------------
        ; aux_got_ack  (1014H)
        ;   Handle a received ACK (06h).
        ;----------------------------------------------------------------------
        aux_got_ack:
        1014   3A EB 48   LDA 48EBH
        1017   FE 00      CPI 00H
        1019   C2 37 10   JNZ L1037
        101C   3E 01      MVI A,01H
        101E   C3 2B 10   JMP L102B

        ;----------------------------------------------------------------------
        ; aux_got_nak  (1021H)
        ;   Handle a received NAK (15h).
        ;----------------------------------------------------------------------
        aux_got_nak:
        1021   3A EB 48   LDA 48EBH
        1024   FE 00      CPI 00H
        1026   C2 37 10   JNZ L1037
        1029   3E 02      MVI A,02H
        L102B:
        102B   32 EB 48   STA 48EBH
        102E   01 B9 40   LXI B,SEM_AUX_FRAME
        1031   CD B5 00   CALL api_00B5
        1034   C3 37 10   JMP L1037
        L1037:
        1037 * E1         POP H
        1038 * D1         POP D
        1039 * C1         POP B
        103A * F1         POP PSW
        103B * FB         EI
        103C * C9         RET

        ;----------------------------------------------------------------------
        ; aux_receive_frame  (103DH)
        ;   API 00C4h: wait for a frame (SEM_AUX_RX) and return the status in A:
        ;   0 ok, 1 line error, 2 too long, 3 short, 4 CRC error.
        ;----------------------------------------------------------------------
        aux_receive_frame:
        103D * F3         DI
        103E * 22 CB 48   SHLD 48CBH
        1041 * 3E FF      MVI A,FFH
        1043 * 32 CD 48   STA 48CDH
        1046 * 3E 64      MVI A,64H
        1048 * 32 EA 48   STA 48EAH
        104B * 01 C5 48   LXI B,SEM_AUX_RX
        104E * CD B8 00   CALL api_sem_wait
        1051 * F3         DI
        1052 * 2A CB 48   LHLD 48CBH
        1055 * 3A C3 48   LDA AUX_STATUS
        1058 * FB         EI
        1059 * C9         RET

        ;----------------------------------------------------------------------
        ; aux_tx_isr  (105AH)
        ;   Aux transmit: send flag, stuffed data bytes (escape table at 1201h),
        ;   CRC, closing flag.
        ;----------------------------------------------------------------------
        aux_tx_isr:
        105A * C5         PUSH B
        105B * D5         PUSH D
        105C * E5         PUSH H
        105D * 3A E2 48   LDA 48E2H
        1060 * 07         RLC
        1061 * D2 B8 10   JNC L10B8
        1064 * 3A E3 48   LDA 48E3H
        1067 * 07         RLC
        1068 * DA 16 11   JC L1116
        106B * 3A D5 48   LDA 48D5H
        106E * FE 00      CPI 00H
        1070 * CA 3A 11   JZ L113A
        1073 * 2A DE 48   LHLD 48DEH
        1076 * 7E         MOV A,M
        1077 * 32 D4 48   STA 48D4H
        107A * 23         INX H
        107B * 22 DE 48   SHLD 48DEH
        107E * 3A E5 48   LDA 48E5H
        1081 * 07         RLC
        1082 * D4 64 11   CNC L1164
        1085 * 3A D5 48   LDA 48D5H
        1088 * 3D         DCR A
        1089 * 32 D5 48   STA 48D5H
        108C * 3A D4 48   LDA 48D4H
        108F * CD 24 25   CALL L2524
        L1092:
        1092 * CD 87 11   CALL L1187
        1095 * DA 76 11   JC L1176
        1098 * 3A D4 48   LDA 48D4H
        109B * D3 08      OUT AUX_DATA
        L109D:
        109D * 3A E7 48   LDA 48E7H
        10A0 * 07         RLC
        10A1 * DA A7 10   JC L10A7
        10A4 * C3 AB 11   JMP L11AB
        L10A7:
        10A7 * 3E 00      MVI A,00H
        10A9 * 32 E0 48   STA 48E0H
        10AC * 32 E5 48   STA 48E5H
        10AF * 32 E1 48   STA 48E1H
        10B2 * 32 E2 48   STA 48E2H
        10B5 * C3 AB 11   JMP L11AB
        L10B8:
        10B8 * 3E 7E      MVI A,7EH
        10BA * D3 08      OUT AUX_DATA
        10BC * 3A E0 48   LDA 48E0H
        10BF * 07         RLC
        10C0 * DA EF 10   JC L10EF
        10C3 * 3A E8 48   LDA 48E8H
        10C6 * 07         RLC
        10C7 * D2 E7 10   JNC L10E7
        10CA * 01 D8 48   LXI B,SEM_AUX_TX
        10CD * CD B5 00   CALL api_00B5
        10D0 * 3A E9 48   LDA 48E9H
        10D3 * E6 FE      ANI FEH
        10D5 * E6 37      ANI 37H
        10D7 * 32 E9 48   STA 48E9H
        10DA * D3 09      OUT AUX_CTL
        10DC * 3E 00      MVI A,00H
        10DE * 32 E7 48   STA 48E7H
        10E1 * 32 E8 48   STA 48E8H
        10E4 * C3 AB 11   JMP L11AB
        L10E7:
        10E7 * 3E FF      MVI A,FFH
        10E9 * 32 E8 48   STA 48E8H
        10EC * C3 AB 11   JMP L11AB
        L10EF:
        10EF * 3A E1 48   LDA 48E1H
        10F2 * 32 E2 48   STA 48E2H
        10F5 * 3E FF      MVI A,FFH
        10F7 * 32 E1 48   STA 48E1H
        10FA * 3E 00      MVI A,00H
        10FC * 32 E5 48   STA 48E5H
        10FF * 32 E6 48   STA 48E6H
        1102 * 32 E3 48   STA 48E3H
        1105 * 32 E4 48   STA 48E4H
        1108 * 32 E7 48   STA 48E7H
        110B * 32 E8 48   STA 48E8H
        110E * 3E FF      MVI A,FFH
        1110 * 32 D5 48   STA 48D5H
        1113 * C3 AB 11   JMP L11AB
        L1116:
        1116 * 3A E4 48   LDA 48E4H
        1119 * 07         RLC
        111A * DA 2A 11   JC L112A
        111D * 3A D6 48   LDA 48D6H
        1120 * D3 08      OUT AUX_DATA
        1122 * 3E FF      MVI A,FFH
        1124 * 32 E4 48   STA 48E4H
        1127 * C3 AB 11   JMP L11AB
        L112A:
        112A * 3A D7 48   LDA 48D7H
        112D * D3 08      OUT AUX_DATA
        112F * 3E 00      MVI A,00H
        1131 * 32 E3 48   STA 48E3H
        1134 * 32 E4 48   STA 48E4H
        1137 * C3 9D 10   JMP L109D
        L113A:
        113A * 3A E6 48   LDA 48E6H
        113D * 07         RLC
        113E * DA 50 11   JC L1150
        1141 * 2A AE 4B   LHLD 4BAEH
        1144 * 7C         MOV A,H
        1145 * 32 D4 48   STA 48D4H
        1148 * 3E FF      MVI A,FFH
        114A * 32 E6 48   STA 48E6H
        114D * C3 92 10   JMP L1092
        L1150:
        1150 * 2A AE 4B   LHLD 4BAEH
        1153 * 7D         MOV A,L
        1154 * 32 D4 48   STA 48D4H
        1157 * 3E 00      MVI A,00H
        1159 * 32 E6 48   STA 48E6H
        115C * 3E FF      MVI A,FFH
        115E * 32 E7 48   STA 48E7H
        1161 * C3 92 10   JMP L1092
        L1164:
        1164 * 3E FF      MVI A,FFH
        1166 * 32 E5 48   STA 48E5H
        1169 * 3A D4 48   LDA 48D4H
        116C * 32 D5 48   STA 48D5H
        116F * 21 00 00   LXI H,0000H
        1172 * 22 AE 4B   SHLD 4BAEH
        1175 * C9         RET
        L1176:
        1176 * 3E 40      MVI A,40H
        1178 * D3 08      OUT AUX_DATA
        117A * 3E FF      MVI A,FFH
        117C * 32 E3 48   STA 48E3H
        117F * 3E 00      MVI A,00H
        1181 * 32 E4 48   STA 48E4H
        1184 * C3 AB 11   JMP L11AB
        L1187:
        1187 * 21 01 12   LXI H,1201H
        118A * 4E         MOV C,M
        118B * 3A D4 48   LDA 48D4H
        118E * 47         MOV B,A
        118F * 23         INX H
        L1190:
        1190 * 7E         MOV A,M
        1191 * B8         CMP B
        1192 * CA 9F 11   JZ L119F
        1195 * 23         INX H
        1196 * 23         INX H
        1197 * 23         INX H
        1198 * 0D         DCR C
        1199 * C2 90 11   JNZ L1190
        119C * 37         STC
        119D * 3F         CMC
        119E * C9         RET
        L119F:
        119F * 23         INX H
        11A0 * 7E         MOV A,M
        11A1 * 32 D6 48   STA 48D6H
        11A4 * 23         INX H
        11A5 * 7E         MOV A,M
        11A6 * 32 D7 48   STA 48D7H
        11A9 * 37         STC
        11AA * C9         RET
        L11AB:
        11AB * E1         POP H
        11AC * D1         POP D
        11AD * C1         POP B
        11AE * F1         POP PSW
        11AF * FB         EI
        11B0 * C9         RET

        ;----------------------------------------------------------------------
        ; aux_send_frame  (11B1H)
        ;   API 00C1h: send the frame in the buffer.
        ;----------------------------------------------------------------------
        aux_send_frame:
        11B1 * F3         DI
        11B2 * 01 D8 48   LXI B,SEM_AUX_TX
        11B5 * CD B8 00   CALL api_sem_wait
        11B8 * F3         DI
        11B9 * 3E FF      MVI A,FFH
        11BB * 32 E0 48   STA 48E0H
        11BE * 3A E9 48   LDA 48E9H
        11C1 * F6 20      ORI 20H
        11C3 * E6 37      ANI 37H
        11C5 * 32 E9 48   STA 48E9H
        11C8 * D3 09      OUT AUX_CTL
        11CA * 22 DE 48   SHLD 48DEH
        11CD * FB         EI
        11CE * 21 05 00   LXI H,0005H
        11D1 * CD 8E 00   CALL api_008E
        11D4 * F3         DI
        11D5 * 3A E9 48   LDA 48E9H
        11D8 * F6 01      ORI 01H
        11DA * E6 37      ANI 37H
        11DC * 32 E9 48   STA 48E9H
        11DF * D3 09      OUT AUX_CTL
        11E1 * 01 D8 48   LXI B,SEM_AUX_TX
        11E4 * CD B8 00   CALL api_sem_wait
        11E7 * 21 05 00   LXI H,0005H
        11EA * CD 8E 00   CALL api_008E
        11ED * F3         DI
        11EE * 3A E9 48   LDA 48E9H
        11F1 * E6 DF      ANI DFH
        11F3 * E6 37      ANI 37H
        11F5 * D3 09      OUT AUX_CTL
        11F7 * 32 E9 48   STA 48E9H
        11FA * 01 D8 48   LXI B,SEM_AUX_TX
        11FD * CD B5 00   CALL api_00B5
        1200 * C9         RET

        ;============================================================================
        ; 1201-1218  BYTE-STUFFING TABLE (5 ENTRIES) AND VERSION STRING
        ;============================================================================
        1201            DB   05H             ; number of entries
        1202            DB   40H,F0H,B0H     ; 40H is sent as 40H,F0H,B0H
        1205            DB   7EH,F0H,8EH     ; 7EH is sent as 40H,F0H,8EH
        1208            DB   06H,FFH,F9H     ; 06H is sent as 40H,FFH,F9H
        120B            DB   15H,FFH,EAH     ; 15H is sent as 40H,FFH,EAH
        120E            DB   1BH,FFH,E4H     ; 1BH is sent as 40H,FFH,E4H
        VERSION:
        1211            DB   '88.03.14'  ; SPC/1 software date 88.03.14

        ;============================================================================
        ; 1219-13D3  SPC/1 INITIALISATION, MEMORY HELPERS
        ;============================================================================

        ;----------------------------------------------------------------------
        ; spc1_init  (1219H)
        ;   Initialise the SPC/1 runtime: allocate the I/O images and tables,
        ;   point USER_ENTRY at 807Ch, copy the function table (2800h) to
        ;   FUNK_RAM_TAB (7F5Fh).
        ;----------------------------------------------------------------------
        spc1_init:
        1219 * F3         DI
        121A * 21 7C 80   LXI H,USER_CODE
        121D * 22 D5 4B   SHLD USER_ENTRY
        1220 * 3E FF      MVI A,FFH
        1222 * 32 EB 48   STA 48EBH
        1225 * 3E 01      MVI A,01H
        1227 * 32 D7 4B   STA STARTUP_PENDING
        122A * 3E 00      MVI A,00H
        122C * 32 02 4C   STA PLC_STATE
        122F * 32 FC 4B   STA 4BFCH
        1232 * 32 E7 4B   STA 4BE7H
        1235 * 32 8D 50   STA 508DH
        1238 * 32 8F 50   STA 508FH
        123B * 21 8D 4D   LXI H,4D8DH
        123E * 22 E9 4B   SHLD 4BE9H
        1241 * 22 DE 4B   SHLD 4BDEH
        1244 * 21 00 00   LXI H,0000H
        1247 * 22 DC 4B   SHLD 4BDCH
        124A * 01 CB 40   LXI B,SEM_TXRING_SPACE
        124D * CD B2 00   CALL api_sem_signal
        1250 * 21 5F 7F   LXI H,FUNK_RAM_TAB
        1253 * 01 A0 00   LXI B,00A0H
        1256 * CD 5C 13   CALL memzero
        1259 * 21 00 28   LXI H,2800H
        125C * 11 5F 7F   LXI D,FUNK_RAM_TAB
        125F * 01 80 00   LXI B,0080H
        1262 * CD C4 13   CALL memcpy_c
        1265 * 21 5F 7F   LXI H,FUNK_RAM_TAB
        1268 * 22 D3 4B   SHLD FUNK_TAB_PTR
        126B * 21 11 51   LXI H,5111H
        126E * 22 D0 4B   SHLD 4BD0H
        1271 * 21 14 21   LXI H,2114H
        1274 * 22 C4 4B   SHLD IO_CFG_PTR
        1277 * 2A D0 4B   LHLD 4BD0H
        127A * 22 C6 4B   SHLD 4BC6H
        127D * 01 C0 00   LXI B,00C0H
        1280 * CD 5C 13   CALL memzero
        1283 * 09         DAD B
        1284 * 22 C8 4B   SHLD 4BC8H
        1287 * 01 00 00   LXI B,0000H
        128A * CD 5C 13   CALL memzero
        128D * 09         DAD B
        128E * 22 CA 4B   SHLD 4BCAH
        1291 * 01 00 00   LXI B,0000H
        1294 * CD 5C 13   CALL memzero
        1297 * 09         DAD B
        1298 * 22 CC 4B   SHLD 4BCCH
        129B * 01 C0 00   LXI B,00C0H
        129E * CD 5C 13   CALL memzero
        12A1 * 09         DAD B
        12A2 * 22 CE 4B   SHLD 4BCEH
        12A5 * 01 44 00   LXI B,0044H
        12A8 * CD 5C 13   CALL memzero
        12AB * 09         DAD B
        12AC * E5         PUSH H
        12AD * CD 30 21   CALL L2130
        12B0 * E1         POP H
        12B1 * 22 B4 4B   SHLD IMG_OUT_BASE
        12B4 * 01 80 07   LXI B,0780H
        12B7 * CD 5C 13   CALL memzero
        12BA * 09         DAD B
        12BB * 22 B6 4B   SHLD IMG_IN_BASE
        12BE * 01 80 07   LXI B,0780H
        12C1 * CD 5C 13   CALL memzero
        12C4 * 09         DAD B
        12C5 * 22 BE 4B   SHLD 4BBEH
        12C8 * 01 80 07   LXI B,0780H
        12CB * CD 5C 13   CALL memzero
        12CE * 09         DAD B
        12CF * 22 B8 4B   SHLD IMG_MARK_BASE
        12D2 * 01 00 04   LXI B,0400H
        12D5 * CD 5C 13   CALL memzero
        12D8 * 09         DAD B
        12D9 * 22 BA 4B   SHLD 4BBAH
        12DC * 01 34 02   LXI B,0234H
        12DF * CD 5C 13   CALL memzero
        12E2 * 09         DAD B
        12E3 * 22 BC 4B   SHLD 4BBCH
        12E6 * 01 00 00   LXI B,0000H
        12E9 * CD 5C 13   CALL memzero
        12EC * 09         DAD B
        12ED * 22 C0 4B   SHLD 4BC0H
        12F0 * 01 00 04   LXI B,0400H
        12F3 * CD 5C 13   CALL memzero
        12F6 * 09         DAD B
        12F7 * 22 C2 4B   SHLD 4BC2H
        12FA * 01 68 04   LXI B,0468H
        12FD * CD 5C 13   CALL memzero
        1300 * 09         DAD B
        1301 * 22 D0 4B   SHLD 4BD0H
        1304 * E5         PUSH H
        1305 * CD 7E 13   CALL L137E
        1308 * E1         POP H
        1309 * E5         PUSH H
        130A * CD 6D 00   CALL api_006D
        130D * EB         XCHG
        130E * 2A D0 4B   LHLD 4BD0H
        1311 * 19         DAD D
        1312 * D1         POP D
        1313 * EB         XCHG
        1314 * CD 6F 13   CALL L136F
        1317 * 2A CE 4B   LHLD 4BCEH
        131A * 7E         MOV A,M
        131B * B7         ORA A
        131C * CA 25 13   JZ L1325
        131F * E6 F8      ANI F8H
        1321 * 1F         RAR
        1322 * 1F         RAR
        1323 * 1F         RAR
        1324 * 3C         INR A
        L1325:
        1325 * 32 D2 4B   STA N_ADC
        1328 * CA 36 13   JZ L1336
        132B * CD 08 21   CALL L2108
        132E * 3E 1E      MVI A,1EH
        1330 * 32 43 48   STA 4843H
        1333 * 32 44 48   STA 4844H
        L1336:
        1336 * 3E 07      MVI A,07H
        1338 * 32 E0 4B   STA STARTUP_MSG
        133B * 3A FF 27   LDA 27FFH
        133E * 32 E1 4B   STA 4BE1H
        1341 * 3E 02      MVI A,02H
        1343 * 32 E2 4B   STA 4BE2H
        1346 * 3E 02      MVI A,02H
        1348 * 32 E3 4B   STA 4BE3H
        134B * 3E 79      MVI A,79H
        134D * 32 E4 4B   STA 4BE4H
        1350 * 3E 02      MVI A,02H
        1352 * 32 E5 4B   STA 4BE5H
        1355 * 3E 7A      MVI A,7AH
        1357 * 32 E6 4B   STA 4BE6H
        135A * FB         EI
        135B * C9         RET

        ;----------------------------------------------------------------------
        ; memzero  (135CH)
        ;   Zero BC bytes at HL.
        ;----------------------------------------------------------------------
        memzero:
        135C * 78         MOV A,B
        135D * B1         ORA C
        135E * CA 6E 13   JZ L136E
        1361 * E5         PUSH H
        1362 * C5         PUSH B
        L1363:
        1363 * 36 00      MVI M,00H
        1365 * 23         INX H
        1366 * 0B         DCX B
        1367 * 78         MOV A,B
        1368 * B1         ORA C
        1369 * C2 63 13   JNZ L1363
        136C * C1         POP B
        136D * E1         POP H
        L136E:
        136E * C9         RET
        L136F:
        136F * 79         MOV A,C
        1370 * B0         ORA B
        1371 * CA 7D 13   JZ L137D
        L1374:
        1374 * 36 FF      MVI M,FFH
        1376 * 23         INX H
        1377 * 1B         DCX D
        1378 * 7B         MOV A,E
        1379 * B2         ORA D
        137A * C2 74 13   JNZ L1374
        L137D:
        137D * C9         RET
        L137E:
        137E * 0E 00      MVI C,00H
        L1380:
        1380 * 06 00      MVI B,00H
        1382 * 2A CE 4B   LHLD 4BCEH
        1385 * 09         DAD B
        1386 * E5         PUSH H
        1387 * 7E         MOV A,M
        1388 * 23         INX H
        1389 * B6         ORA M
        138A * CA C0 13   JZ L13C0
        138D * 23         INX H
        138E * EB         XCHG
        138F * 2A D0 4B   LHLD 4BD0H
        1392 * EB         XCHG
        1393 * 73         MOV M,E
        1394 * 23         INX H
        1395 * 72         MOV M,D
        1396 * 69         MOV L,C
        1397 * 26 00      MVI H,00H
        1399 * 29         DAD H
        139A * 29         DAD H
        139B * 29         DAD H
        139C * 29         DAD H
        139D * 29         DAD H
        139E * EB         XCHG
        139F * CD 6A 00   CALL api_006A
        13A2 * E1         POP H
        13A3 * C5         PUSH B
        13A4 * 4E         MOV C,M
        13A5 * 23         INX H
        13A6 * 46         MOV B,M
        13A7 * 60         MOV H,B
        13A8 * 69         MOV L,C
        13A9 * 19         DAD D
        13AA * 23         INX H
        13AB * 29         DAD H
        13AC * 29         DAD H
        13AD * EB         XCHG
        13AE * 2A D0 4B   LHLD 4BD0H
        13B1 * 19         DAD D
        13B2 * 22 D0 4B   SHLD 4BD0H
        13B5 * C1         POP B
        L13B6:
        13B6 * 79         MOV A,C
        13B7 * C6 04      ADI 04H
        13B9 * FE 44      CPI 44H
        13BB * 4F         MOV C,A
        13BC * DA 80 13   JC L1380
        13BF * C9         RET
        L13C0:
        13C0 * E1         POP H
        13C1 * C3 B6 13   JMP L13B6

        ;----------------------------------------------------------------------
        ; memcpy_c  (13C4H)
        ;   Copy C bytes from (HL) to (DE).
        ;----------------------------------------------------------------------
        memcpy_c:
        13C4 * 79         MOV A,C
        13C5 * B7         ORA A
        13C6 * CA D3 13   JZ L13D3
        L13C9:
        13C9 * 7E         MOV A,M
        13CA * 12         STAX D
        13CB * 23         INX H
        13CC * 13         INX D
        13CD * 0D         DCR C
        13CE * 79         MOV A,C
        13CF * B7         ORA A
        13D0 * C2 C9 13   JNZ L13C9
        L13D3:
        13D3 * C9         RET

        ;============================================================================
        ; 13D4-151D  PROCESSES: AUX RECEIVE AND AUX MESSAGE HANDLING
        ;============================================================================

        ;----------------------------------------------------------------------
        ; proc_aux_rx  (13D4H)
        ;   Process (prio 3): receives frames from the aux link, accepts only
        ;   station address = ROM byte 27FFh (0FFh), rebuilds the header and
        ;   posts the message to MBOX_CMD.
        ;----------------------------------------------------------------------
        proc_aux_rx:
        13D4 * 21 08 4C   LXI H,AUX_RXBUF
        13D7 * CD C4 00   CALL api_aux_receive_frame
        13DA * F5         PUSH PSW
        13DB * FE 01      CPI 01H
        13DD * F3         DI
        13DE * CC 48 0E   CZ aux_init
        13E1 * FB         EI
        13E2 * F1         POP PSW
        13E3 * B7         ORA A
        13E4 * C2 D4 13   JNZ proc_aux_rx
        13E7 * F3         DI
        13E8 * 3E 01      MVI A,01H
        13EA * 32 E7 4B   STA 4BE7H
        13ED * 3A EB 48   LDA 48EBH
        13F0 * B7         ORA A
        13F1 * C2 FF 13   JNZ L13FF
        13F4 * 3E 01      MVI A,01H
        13F6 * 32 EB 48   STA 48EBH
        13F9 * 01 B9 40   LXI B,SEM_AUX_FRAME
        13FC * CD B2 00   CALL api_sem_signal
        L13FF:
        13FF * FB         EI
        1400 * 21 08 4C   LXI H,AUX_RXBUF
        1403 * 23         INX H
        1404 * 46         MOV B,M
        1405 * 3A FF 27   LDA 27FFH
        1408 * B8         CMP B
        1409 * C2 D4 13   JNZ proc_aux_rx
        140C * 3A 08 4C   LDA AUX_RXBUF
        140F * C6 02      ADI 02H
        1411 * 32 06 4C   STA AUX_MSG
        1414 * 3A 09 4C   LDA 4C09H
        1417 * 32 07 4C   STA 4C07H
        141A * 3A 0A 4C   LDA 4C0AH
        141D * 3C         INR A
        141E * 32 08 4C   STA AUX_RXBUF
        1421 * 3E 02      MVI A,02H
        1423 * 32 09 4C   STA 4C09H
        1426 * 3E 79      MVI A,79H
        1428 * 32 0A 4C   STA 4C0AH
        142B * 01 53 40   LXI B,MBOX_FREE
        142E * CD 58 00   CALL api_mbox_get
        1431 * E5         PUSH H
        1432 * 13         INX D
        1433 * 13         INX D
        1434 * 13         INX D
        1435 * 13         INX D
        1436 * EB         XCHG
        1437 * 11 06 4C   LXI D,AUX_MSG
        143A * 3A D7 4B   LDA STARTUP_PENDING
        143D * B7         ORA A
        143E * CA 49 14   JZ L1449
        1441 * 11 E0 4B   LXI D,STARTUP_MSG
        1444 * 3E 00      MVI A,00H
        1446 * 32 D7 4B   STA STARTUP_PENDING
        L1449:
        1449 * 73         MOV M,E
        144A * 23         INX H
        144B * 72         MOV M,D
        144C * E1         POP H
        144D * 01 BF 40   LXI B,MBOX_CMD
        1450 * CD AC 00   CALL api_mbox_put
        1453 * C3 D4 13   JMP proc_aux_rx

        ;----------------------------------------------------------------------
        ; proc_aux_msg  (1456H)
        ;   Process (prio 3): takes messages from MBOX_CMD, feeds each sub-
        ;   message to the command interpreter and streams the replies into the
        ;   transmit ring (4D8Dh-508Dh).
        ;----------------------------------------------------------------------
        proc_aux_msg:
        1456 * 01 BF 40   LXI B,MBOX_CMD
        1459 * CD 58 00   CALL api_mbox_get
        145C * E5         PUSH H
        145D * 13         INX D
        145E * 13         INX D
        145F * 13         INX D
        1460 * 13         INX D
        1461 * EB         XCHG
        1462 * 5E         MOV E,M
        1463 * 23         INX H
        1464 * 56         MOV D,M
        1465 * E1         POP H
        1466 * 01 53 40   LXI B,MBOX_FREE
        1469 * CD AC 00   CALL api_mbox_put
        146C * 13         INX D
        146D * 13         INX D
        146E * 1A         LDAX D
        146F * 32 E8 4B   STA SUBMSG_COUNT
        1472 * 13         INX D
        1473 * EB         XCHG
        L1474:
        1474 * 11 8C 4C   LXI D,CMD_BUF
        1477 * 4E         MOV C,M
        1478 * CD C4 13   CALL memcpy_c
        L147B:
        147B * 01 D7 40   LXI B,SEM_CMD_AVAIL
        147E * CD B2 00   CALL api_sem_signal
        1481 * 01 C5 40   LXI B,SEM_CMD_DONE
        1484 * CD B8 00   CALL api_sem_wait
        1487 * 3A 0E 4D   LDA 4D0EH
        148A * FE 3E      CPI 3EH
        148C * CA 11 15   JZ L1511
        148F * E5         PUSH H
        1490 * 2A E9 4B   LHLD 4BE9H
        1493 * EB         XCHG
        1494 * 01 CB 40   LXI B,SEM_TXRING_SPACE
        1497 * CD B8 00   CALL api_sem_wait
        149A * 21 0D 4D   LXI H,REPLY_BUF
        149D * 4E         MOV C,M
        149E * 06 00      MVI B,00H
        14A0 * C5         PUSH B
        L14A1:
        14A1 * 7E         MOV A,M
        14A2 * 12         STAX D
        14A3 * 23         INX H
        14A4 * 13         INX D
        14A5 * E5         PUSH H
        14A6 * 21 8D 50   LXI H,508DH
        14A9 * 7B         MOV A,E
        14AA * BD         CMP L
        14AB * C2 B6 14   JNZ L14B6
        14AE * 7A         MOV A,D
        14AF * BC         CMP H
        14B0 * C2 B6 14   JNZ L14B6
        14B3   11 8D 4D   LXI D,4D8DH
        L14B6:
        14B6 * E1         POP H
        14B7 * 0D         DCR C
        14B8 * C2 A1 14   JNZ L14A1
        14BB * C1         POP B
        14BC * 2A DC 4B   LHLD 4BDCH
        14BF * 03         INX B
        14C0 * 09         DAD B
        14C1 * 22 DC 4B   SHLD 4BDCH
        14C4 * 3A DD 4B   LDA 4BDDH
        14C7 * F5         PUSH PSW
        14C8 * 01 CB 40   LXI B,SEM_TXRING_SPACE
        14CB * CD B2 00   CALL api_sem_signal
        14CE * EB         XCHG
        14CF * 3A E8 4B   LDA SUBMSG_COUNT
        14D2 * FE 01      CPI 01H
        14D4 * 3E 00      MVI A,00H
        14D6 * CA DB 14   JZ L14DB
        14D9 * 3E 01      MVI A,01H
        L14DB:
        14DB * 77         MOV M,A
        14DC * 3A 0C 4D   LDA 4D0CH
        14DF * B6         ORA M
        14E0 * 77         MOV M,A
        14E1 * 23         INX H
        14E2 * EB         XCHG
        14E3 * 21 8D 50   LXI H,508DH
        14E6 * 7B         MOV A,E
        14E7 * BD         CMP L
        14E8 * C2 F3 14   JNZ L14F3
        14EB   7A         MOV A,D
        14EC   BC         CMP H
        14ED   C2 F3 14   JNZ L14F3
        14F0   11 8D 4D   LXI D,4D8DH
        L14F3:
        14F3 * EB         XCHG
        14F4 * 22 E9 4B   SHLD 4BE9H
        14F7 * 01 B3 40   LXI B,SEM_TXRING_DATA
        14FA * CD B2 00   CALL api_sem_signal
        14FD * F1         POP PSW
        14FE * E6 FE      ANI FEH
        1500 * CA 09 15   JZ L1509
        1503   01 D1 40   LXI B,40D1H
        1506   CD B8 00   CALL api_sem_wait
        L1509:
        1509 * E1         POP H
        150A * 3A 0C 4D   LDA 4D0CH
        150D * B7         ORA A
        150E * C2 7B 14   JNZ L147B
        L1511:
        1511 * 3A E8 4B   LDA SUBMSG_COUNT
        1514 * 3D         DCR A
        1515 * 32 E8 4B   STA SUBMSG_COUNT
        1518 * C2 74 14   JNZ L1474
        151B * C3 56 14   JMP proc_aux_msg

        ;============================================================================
        ; 151E-1CAA  COMMAND INTERPRETER (SPC/1 DIALOG PROTOCOL) AND COMMAND HANDLERS
        ;   Command codes are looked up in the 128-entry table at 1CABh. Replies seen in the emulator:
        ;   60h = version string, 61h = function table dump, 6Dh = I/O configuration, 6Eh/6Fh/70h = module tables,
        ;   1Eh = download, 20h = run control, 3Ah = restart, unknown codes reply 3Bh.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; proc_command  (151EH)
        ;   Process (prio 3): command interpreter. Waits for SEM_CMD_AVAIL,
        ;   dispatches on CMD_BUF[1] AND 7Fh through the table at 1CABh.
        ;----------------------------------------------------------------------
        proc_command:
        151E * 01 D7 40   LXI B,SEM_CMD_AVAIL
        1521 * CD B8 00   CALL api_sem_wait
        1524 * 21 8C 4C   LXI H,CMD_BUF
        1527 * 23         INX H
        1528 * 7E         MOV A,M
        1529 * E6 7F      ANI 7FH
        152B * 4F         MOV C,A
        152C * 87         ADD A
        152D * 5F         MOV E,A
        152E * 16 00      MVI D,00H
        1530 * 21 AB 1C   LXI H,1CABH
        1533 * 19         DAD D
        1534 * 5E         MOV E,M
        1535 * 23         INX H
        1536 * 56         MOV D,M
        1537 * 79         MOV A,C
        1538 * 32 0E 4D   STA 4D0EH
        153B * EB         XCHG
        153C * E9         PCHL

        ;----------------------------------------------------------------------
        ; cmd_02_04  (153DH)
        ;   Commands 02h/04h: image bit access (2-byte reply; waits on the
        ;   semaphore at 40DDh).
        ;----------------------------------------------------------------------
        cmd_02_04:
        153D * 01 DD 40   LXI B,40DDH
        1540 * CD B8 00   CALL api_sem_wait
        1543 * 3E 80      MVI A,80H
        1545 * 32 FD 4B   STA 4BFDH
        1548 * 3A 8E 4C   LDA 4C8EH
        154B * 4F         MOV C,A
        154C * 21 8F 4C   LXI H,4C8FH
        L154F:
        154F * 5E         MOV E,M
        1550 * 23         INX H
        1551 * E5         PUSH H
        1552 * 7E         MOV A,M
        1553 * E6 07      ANI 07H
        1555 * 57         MOV D,A
        1556 * 3A 8D 4C   LDA 4C8DH
        1559 * FE 04      CPI 04H
        155B * CA 7B 15   JZ L157B
        155E * D5         PUSH D
        155F * 21 20 00   LXI H,0020H
        1562 * CD 4F 00   CALL api_div_helper
        1565 * 62         MOV H,D
        1566 * 6B         MOV L,E
        1567 * 29         DAD H
        1568 * 19         DAD D
        1569 * 2A CC 4B   LHLD 4BCCH
        156C * 19         DAD D
        156D * 3A FD 4B   LDA 4BFDH
        1570 * A6         ANA M
        1571 * 32 FD 4B   STA 4BFDH
        1574 * D1         POP D
        1575 * 2A B4 4B   LHLD IMG_OUT_BASE
        1578 * C3 83 15   JMP L1583
        L157B:
        157B * 2A B8 4B   LHLD IMG_MARK_BASE
        157E * 3E 80      MVI A,80H
        1580 * 32 FD 4B   STA 4BFDH
        L1583:
        1583 * 19         DAD D
        1584 * EB         XCHG
        1585 * E1         POP H
        1586 * 7E         MOV A,M
        1587 * 17         RAL
        1588 * 1A         LDAX D
        1589 * 1F         RAR
        158A * 07         RLC
        158B * 12         STAX D
        158C * 23         INX H
        158D * 0D         DCR C
        158E * C2 4F 15   JNZ L154F
        1591 * 3A FD 4B   LDA 4BFDH
        1594 * 17         RAL
        1595 * 3F         CMC
        1596 * 17         RAL
        1597 * E6 01      ANI 01H
        1599 * 32 FD 4B   STA 4BFDH
        159C * C3 86 1C   JMP L1C86

        ;----------------------------------------------------------------------
        ; cmd_07  (159FH)
        ;   Command 07h: 5-byte status reply (meaning not decoded).
        ;----------------------------------------------------------------------
        cmd_07:
        159F * 01 DD 40   LXI B,40DDH
        15A2 * CD B8 00   CALL api_sem_wait
        15A5 * 2A 8E 4C   LHLD 4C8EH
        15A8 * 29         DAD H
        15A9 * EB         XCHG
        15AA * 2A C0 4B   LHLD 4BC0H
        15AD * 19         DAD D
        15AE * EB         XCHG
        15AF * 21 92 4C   LXI H,4C92H
        15B2 * 3A 90 4C   LDA 4C90H
        15B5 * 87         ADD A
        15B6 * 4F         MOV C,A
        15B7 * CD C4 13   CALL memcpy_c
        15BA * 3E 00      MVI A,00H
        15BC * 32 0C 4D   STA 4D0CH
        15BF * 32 13 4D   STA 4D13H
        15C2 * 3E 07      MVI A,07H
        15C4 * 32 0D 4D   STA REPLY_BUF
        15C7 * 3A 8D 4C   LDA 4C8DH
        15CA * 32 0E 4D   STA 4D0EH
        15CD * 2A 8E 4C   LHLD 4C8EH
        15D0 * 22 0F 4D   SHLD 4D0FH
        15D3 * 2A 90 4C   LHLD 4C90H
        15D6 * 22 11 4D   SHLD 4D11H
        15D9 * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_0A_0C  (15DCH)
        ;   Commands 0Ah/0Ch: 2-byte reply (image access, not decoded).
        ;----------------------------------------------------------------------
        cmd_0A_0C:
        15DC * 01 DD 40   LXI B,40DDH
        15DF * CD B8 00   CALL api_sem_wait
        15E2 * 3A 8E 4C   LDA 4C8EH
        15E5 * 4F         MOV C,A
        15E6 * 21 8F 4C   LXI H,4C8FH
        L15E9:
        15E9 * 5E         MOV E,M
        15EA * 23         INX H
        15EB * E5         PUSH H
        15EC * 7E         MOV A,M
        15ED * E6 07      ANI 07H
        15EF * 56         MOV D,M
        15F0 * 3A 8D 4C   LDA 4C8DH
        15F3 * FE 0C      CPI 0CH
        15F5 * CA FE 15   JZ L15FE
        15F8 * 2A B6 4B   LHLD IMG_IN_BASE
        15FB * C3 01 16   JMP L1601
        L15FE:
        15FE * 2A B4 4B   LHLD IMG_OUT_BASE
        L1601:
        1601 * 19         DAD D
        1602 * EB         XCHG
        1603 * E1         POP H
        1604 * 7E         MOV A,M
        1605 * 17         RAL
        1606 * 1A         LDAX D
        1607 * 17         RAL
        1608 * 0F         RRC
        1609 * 12         STAX D
        160A * 23         INX H
        160B * 0D         DCR C
        160C * C2 E9 15   JNZ L15E9
        160F * 3E 00      MVI A,00H
        1611 * 32 FD 4B   STA 4BFDH
        1614 * C3 86 1C   JMP L1C86

        ;----------------------------------------------------------------------
        ; cmd_0B_0D  (1617H)
        ;   Commands 0Bh/0Dh: 2-byte reply (image access, not decoded).
        ;----------------------------------------------------------------------
        cmd_0B_0D:
        1617 * 01 DD 40   LXI B,40DDH
        161A * CD B8 00   CALL api_sem_wait
        161D * 3A 8E 4C   LDA 4C8EH
        1620 * 4F         MOV C,A
        1621 * 21 8F 4C   LXI H,4C8FH
        L1624:
        1624 * 5E         MOV E,M
        1625 * 23         INX H
        1626 * E5         PUSH H
        1627 * 7E         MOV A,M
        1628 * E6 07      ANI 07H
        162A * 56         MOV D,M
        162B * 3A 8D 4C   LDA 4C8DH
        162E * FE 0C      CPI 0CH
        1630 * CA 39 16   JZ L1639
        1633 * 2A B6 4B   LHLD IMG_IN_BASE
        1636 * C3 01 16   JMP L1601
        L1639:
        1639   2A B4 4B   LHLD IMG_OUT_BASE
        163C   19         DAD D
        163D   EB         XCHG
        163E   1A         LDAX D
        163F   E6 BF      ANI BFH
        1641   47         MOV B,A
        1642   E1         POP H
        1643   7E         MOV A,M
        1644   E6 80      ANI 80H
        1646   0F         RRC
        1647   B0         ORA B
        1648   12         STAX D
        1649   23         INX H
        164A   0D         DCR C
        164B   C2 24 16   JNZ L1624
        164E   3E 00      MVI A,00H
        1650   32 FD 4B   STA 4BFDH
        1653   C3 86 1C   JMP L1C86

        ;----------------------------------------------------------------------
        ; cmd_0E  (1656H)
        ;   Command 0Eh: never answers in the emulator and blocks the
        ;   interpreter; probably waits for an event.
        ;----------------------------------------------------------------------
        cmd_0E:
        1656 * 01 DD 40   LXI B,40DDH
        1659 * CD B8 00   CALL api_sem_wait
        165C * 3A 8E 4C   LDA 4C8EH
        165F * 4F         MOV C,A
        1660 * 21 8F 4C   LXI H,4C8FH
        L1663:
        1663 * C5         PUSH B
        1664 * 5E         MOV E,M
        1665 * 23         INX H
        1666 * E5         PUSH H
        1667 * E5         PUSH H
        1668 * 7E         MOV A,M
        1669 * E6 0F      ANI 0FH
        166B * 57         MOV D,A
        166C * EB         XCHG
        166D * CD AB 1D   CALL L1DAB
        1670 * EB         XCHG
        1671 * 13         INX D
        1672 * 13         INX D
        1673 * E1         POP H
        1674 * 7E         MOV A,M
        1675 * 17         RAL
        1676 * 3F         CMC
        1677 * 1A         LDAX D
        1678 * 1F         RAR
        1679 * 07         RLC
        167A * 12         STAX D
        167B * E1         POP H
        167C * 0D         DCR C
        167D * C2 63 16   JNZ L1663
        1680   3E 00      MVI A,00H
        1682   32 FD 4B   STA 4BFDH
        1685   C3 86 1C   JMP L1C86

        ;----------------------------------------------------------------------
        ; cmd_0F_status  (1688H)
        ;   Command 0Fh: 5-byte status reply.
        ;----------------------------------------------------------------------
        cmd_0F_status:
        1688 * 01 DD 40   LXI B,40DDH
        168B * CD B8 00   CALL api_sem_wait
        168E * 11 92 4C   LXI D,4C92H
        1691 * 2A 8E 4C   LHLD 4C8EH
        1694 * 3A 90 4C   LDA 4C90H
        1697 * 4F         MOV C,A
        L1698:
        1698 * E5         PUSH H
        1699 * C5         PUSH B
        169A * D5         PUSH D
        169B * CD AB 1D   CALL L1DAB
        169E * EB         XCHG
        169F * 13         INX D
        16A0 * 13         INX D
        16A1 * E1         POP H
        16A2 * 7E         MOV A,M
        16A3 * F6 01      ORI 01H
        16A5 * 12         STAX D
        16A6 * 23         INX H
        16A7 * 13         INX D
        16A8 * 7E         MOV A,M
        16A9 * 12         STAX D
        16AA * 23         INX H
        16AB * EB         XCHG
        16AC * C1         POP B
        16AD * E1         POP H
        16AE * 23         INX H
        16AF * 0D         DCR C
        16B0 * C2 98 16   JNZ L1698
        16B3 * 3E 00      MVI A,00H
        16B5 * 32 0C 4D   STA 4D0CH
        16B8 * 32 13 4D   STA 4D13H
        16BB * 3E 07      MVI A,07H
        16BD * 32 0D 4D   STA REPLY_BUF
        16C0 * 3E 0F      MVI A,0FH
        16C2 * 32 0E 4D   STA 4D0EH
        16C5 * 2A 8E 4C   LHLD 4C8EH
        16C8 * 22 0F 4D   SHLD 4D0FH
        16CB * 2A 90 4C   LHLD 4C90H
        16CE * 22 11 4D   SHLD 4D11H
        16D1 * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_download  (16D4H)
        ;   Command 1Eh: program download block [1E][block no][more][data...];
        ;   block 0 resets DL_PTR to 8000h; the last block (more = 0) sets
        ;   PLC_STATE := 1.
        ;----------------------------------------------------------------------
        cmd_download:
        16D4 * 3A 02 4C   LDA PLC_STATE
        16D7 * FE 03      CPI 03H
        16D9 * CA 24 17   JZ L1724
        16DC * 3A 8E 4C   LDA 4C8EH
        16DF * B7         ORA A
        16E0 * C2 F7 16   JNZ L16F7
        16E3 * 3E 00      MVI A,00H
        16E5 * 32 FF 4B   STA DL_BLOCK_NO
        16E8 * 32 02 4C   STA PLC_STATE
        16EB * 21 00 80   LXI H,USER_PROG
        16EE * 22 00 4C   SHLD DL_PTR
        16F1 * CD 2E 17   CALL L172E
        16F4 * C3 0C 17   JMP L170C
        L16F7:
        16F7 * 3A 02 4C   LDA PLC_STATE
        16FA * B7         ORA A
        16FB * C2 29 17   JNZ L1729
        16FE * 3A FF 4B   LDA DL_BLOCK_NO
        1701 * 47         MOV B,A
        1702 * 3A 8E 4C   LDA 4C8EH
        1705 * B8         CMP B
        1706 * C2 29 17   JNZ L1729
        1709 * CD 2E 17   CALL L172E
        L170C:
        170C * 3E 00      MVI A,00H
        L170E:
        170E * 32 11 4D   STA 4D11H
        1711 * 3E 00      MVI A,00H
        1713 * 32 0C 4D   STA 4D0CH
        1716 * 3E 05      MVI A,05H
        1718 * 32 0D 4D   STA REPLY_BUF
        171B * 2A 8E 4C   LHLD 4C8EH
        171E * 22 0F 4D   SHLD 4D0FH
        1721 * C3 A2 1C   JMP L1CA2
        L1724:
        1724   3E 01      MVI A,01H
        1726   C3 0E 17   JMP L170E
        L1729:
        1729   3E 02      MVI A,02H
        172B   C3 0E 17   JMP L170E
        L172E:
        172E * 3A FF 4B   LDA DL_BLOCK_NO
        1731 * 3C         INR A
        1732 * 32 FF 4B   STA DL_BLOCK_NO
        1735 * 2A 00 4C   LHLD DL_PTR
        1738 * EB         XCHG
        1739 * 21 90 4C   LXI H,4C90H
        173C * 3A 8C 4C   LDA CMD_BUF
        173F * D6 04      SUI 04H
        1741 * 4F         MOV C,A
        1742 * CD C4 13   CALL memcpy_c
        1745 * EB         XCHG
        1746 * 22 00 4C   SHLD DL_PTR
        1749 * 3A 8F 4C   LDA 4C8FH
        174C * B7         ORA A
        174D * C2 55 17   JNZ L1755
        1750 * 3E 01      MVI A,01H
        1752 * 32 02 4C   STA PLC_STATE
        L1755:
        1755 * C9         RET

        ;----------------------------------------------------------------------
        ; cmd_run_control  (1756H)
        ;   Command 20h: 0 = stop, 1 = run (runs the loader 2359h first), 2 =
        ;   restart the system.
        ;----------------------------------------------------------------------
        cmd_run_control:
        1756 * 3A 8E 4C   LDA 4C8EH
        1759 * FE 02      CPI 02H
        175B * CA 00 00   JZ reset
        175E * FE 03      CPI 03H
        1760 * D2 AB 17   JNC L17AB
        1763 * 3A 02 4C   LDA PLC_STATE
        1766 * FE 01      CPI 01H
        1768 * DA B0 17   JC L17B0
        176B * C2 7A 17   JNZ L177A
        176E * CD 59 23   CALL program_loader
        1771 * B7         ORA A
        1772 * C2 B0 17   JNZ L17B0
        1775 * 3E 02      MVI A,02H
        1777 * 32 02 4C   STA PLC_STATE
        L177A:
        177A * 47         MOV B,A
        177B * E6 01      ANI 01H
        177D * 4F         MOV C,A
        177E * 3A 8E 4C   LDA 4C8EH
        1781 * E6 01      ANI 01H
        1783 * B9         CMP C
        1784 * CA A6 17   JZ L17A6
        1787 * 78         MOV A,B
        1788 * 1F         RAR
        1789 * 3F         CMC
        178A * 17         RAL
        178B * 32 02 4C   STA PLC_STATE
        178E * 3E 00      MVI A,00H
        L1790:
        1790 * 32 10 4D   STA 4D10H
        1793 * 3E 00      MVI A,00H
        1795 * 32 0C 4D   STA 4D0CH
        1798 * 3E 04      MVI A,04H
        179A * 32 0D 4D   STA REPLY_BUF
        179D * 3A 8E 4C   LDA 4C8EH
        17A0 * 32 0F 4D   STA 4D0FH
        17A3 * C3 A2 1C   JMP L1CA2
        L17A6:
        17A6   3E 01      MVI A,01H
        17A8   C3 90 17   JMP L1790
        L17AB:
        17AB   3E 02      MVI A,02H
        17AD   C3 90 17   JMP L1790
        L17B0:
        17B0   3E 03      MVI A,03H
        17B2   C3 90 17   JMP L1790

        ;----------------------------------------------------------------------
        ; cmd_34_5F  (17B5H)
        ;   Commands 34h/5Fh: 2-byte reply.
        ;----------------------------------------------------------------------
        cmd_34_5F:
        17B5 * 3E 00      MVI A,00H
        17B7 * 32 0C 4D   STA 4D0CH
        17BA * 32 10 4D   STA 4D10H
        17BD * 3A 8E 4C   LDA 4C8EH
        17C0 * 32 0F 4D   STA 4D0FH
        17C3 * 3E 04      MVI A,04H
        17C5 * 32 0D 4D   STA REPLY_BUF
        17C8 * 01 DD 40   LXI B,40DDH
        17CB * CD B8 00   CALL api_sem_wait
        17CE * 3A 8E 4C   LDA 4C8EH
        17D1 * B7         ORA A
        17D2 * CA DB 17   JZ L17DB
        17D5   32 44 48   STA 4844H
        17D8   C3 9C 1C   JMP L1C9C
        L17DB:
        17DB * 3E 1E      MVI A,1EH
        17DD * 32 44 48   STA 4844H
        17E0 * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_restart  (17E3H)
        ;   Command 3Ah: restart the system (JMP 0000h).
        ;----------------------------------------------------------------------
        cmd_restart:
        17E3   C3 00 00   JMP reset

        ;----------------------------------------------------------------------
        ; cmd_illegal  (17E6H)
        ;   Illegal command: reply code 3Bh.
        ;----------------------------------------------------------------------
        cmd_illegal:
        17E6 * 3E 00      MVI A,00H
        17E8 * 32 0C 4D   STA 4D0CH
        17EB * 32 0F 4D   STA 4D0FH
        17EE * 3E 3B      MVI A,3BH
        17F0 * 32 0E 4D   STA 4D0EH
        17F3 * 3E 03      MVI A,03H
        17F5 * 32 0D 4D   STA REPLY_BUF
        17F8 * C3 A2 1C   JMP L1CA2

        ;----------------------------------------------------------------------
        ; cmd_read_image  (17FBH)
        ;   Commands 40h/41h/43h: read from an image (40h input image, 41h
        ;   output image, 43h markers - inferred); 3-byte reply.
        ;----------------------------------------------------------------------
        cmd_read_image:
        17FB * 3A FC 4B   LDA 4BFCH
        17FE * B7         ORA A
        17FF * C2 66 18   JNZ L1866
        1802 * 01 DD 40   LXI B,40DDH
        1805 * CD B8 00   CALL api_sem_wait
        1808 * 3A 8E 4C   LDA 4C8EH
        180B * 6F         MOV L,A
        180C * 26 00      MVI H,00H
        180E * 29         DAD H
        180F * 29         DAD H
        1810 * 29         DAD H
        1811 * 29         DAD H
        1812 * 29         DAD H
        1813 * EB         XCHG
        1814 * D5         PUSH D
        1815 * 3A 8D 4C   LDA 4C8DH
        1818 * FE 40      CPI 40H
        181A * C2 24 18   JNZ L1824
        181D * 2A B6 4B   LHLD IMG_IN_BASE
        1820 * 19         DAD D
        1821 * C3 34 18   JMP L1834
        L1824:
        1824 * FE 41      CPI 41H
        1826 * C2 30 18   JNZ L1830
        1829 * 2A B4 4B   LHLD IMG_OUT_BASE
        182C * 19         DAD D
        182D * C3 34 18   JMP L1834
        L1830:
        1830 * 2A B8 4B   LHLD IMG_MARK_BASE
        1833 * 19         DAD D
        L1834:
        1834 * EB         XCHG
        1835 * C1         POP B
        1836 * 2A BE 4B   LHLD 4BBEH
        1839 * 09         DAD B
        183A * EB         XCHG
        183B * E5         PUSH H
        183C * D5         PUSH D
        183D * 3A 8F 4C   LDA 4C8FH
        1840 * 6F         MOV L,A
        1841 * 26 00      MVI H,00H
        1843 * 29         DAD H
        1844 * 29         DAD H
        1845 * 29         DAD H
        1846 * 29         DAD H
        1847 * 29         DAD H
        1848 * 4D         MOV C,L
        1849 * 44         MOV B,H
        184A * D1         POP D
        184B * E1         POP H
        184C * 79         MOV A,C
        184D * B0         ORA B
        184E * CA 5B 18   JZ L185B
        L1851:
        1851   7E         MOV A,M
        1852   12         STAX D
        1853   23         INX H
        1854   13         INX D
        1855   0B         DCX B
        1856   79         MOV A,C
        1857   B0         ORA B
        1858   C2 51 18   JNZ L1851
        L185B:
        185B * 3E 01      MVI A,01H
        185D * 32 FC 4B   STA 4BFCH
        1860 * 01 E3 40   LXI B,40E3H
        1863 * CD B2 00   CALL api_sem_signal
        L1866:
        1866 * 3E 80      MVI A,80H
        1868 * 32 FD 4B   STA 4BFDH
        186B * 3A 8F 4C   LDA 4C8FH
        186E * FE 1E      CPI 1EH
        1870 * 3E 1E      MVI A,1EH
        1872 * D2 78 18   JNC L1878
        1875 * 3A 8F 4C   LDA 4C8FH
        L1878:
        1878 * 4F         MOV C,A
        1879 * 3A 8E 4C   LDA 4C8EH
        187C * 81         ADD C
        187D * CA 81 18   JZ L1881
        1880   3D         DCR A
        L1881:
        1881 * 32 FE 4B   STA 4BFEH
        1884 * 3A 8E 4C   LDA 4C8EH
        1887 * 4F         MOV C,A
        1888 * 06 00      MVI B,00H
        188A * 2A C6 4B   LHLD 4BC6H
        188D * 3A 8D 4C   LDA 4C8DH
        1890 * FE 40      CPI 40H
        1892 * CA 98 18   JZ L1898
        1895 * 2A CC 4B   LHLD 4BCCH
        L1898:
        1898 * EB         XCHG
        1899 * 21 12 4D   LXI H,4D12H
        189C * D5         PUSH D
        L189D:
        189D * D1         POP D
        189E * D5         PUSH D
        189F * EB         XCHG
        18A0 * C5         PUSH B
        18A1 * 79         MOV A,C
        18A2 * F5         PUSH PSW
        18A3 * 87         ADD A
        18A4 * 81         ADD C
        18A5 * 4F         MOV C,A
        18A6 * 09         DAD B
        18A7 * 3A FD 4B   LDA 4BFDH
        18AA * A6         ANA M
        18AB * 32 FD 4B   STA 4BFDH
        18AE * EB         XCHG
        18AF * F1         POP PSW
        18B0 * 47         MOV B,A
        18B1 * 3A 8D 4C   LDA 4C8DH
        18B4 * FE 41      CPI 41H
        18B6 * C2 BF 18   JNZ L18BF
        18B9 * CD 41 1E   CALL L1E41
        18BC * C3 C2 18   JMP L18C2
        L18BF:
        18BF * CD 04 1E   CALL L1E04
        L18C2:
        18C2 * C1         POP B
        18C3 * 0C         INR C
        18C4 * 3A FE 4B   LDA 4BFEH
        18C7 * B9         CMP C
        18C8 * D2 9D 18   JNC L189D
        18CB * F1         POP PSW
        18CC * 3A 8F 4C   LDA 4C8FH
        18CF * FE 1E      CPI 1EH
        18D1 * D2 F5 18   JNC L18F5
        18D4 * 3E 00      MVI A,00H
        18D6 * 32 FC 4B   STA 4BFCH
        18D9 * 32 0C 4D   STA 4D0CH
        18DC * 3A 8F 4C   LDA 4C8FH
        18DF * 87         ADD A
        18E0 * 87         ADD A
        18E1 * C6 05      ADI 05H
        18E3 * 32 0D 4D   STA REPLY_BUF
        18E6 * 3A 8E 4C   LDA 4C8EH
        18E9 * 32 0F 4D   STA 4D0FH
        18EC * 3A 8F 4C   LDA 4C8FH
        18EF * 32 10 4D   STA 4D10H
        18F2 * C3 1A 19   JMP L191A
        L18F5:
        18F5   3E 01      MVI A,01H
        18F7   32 0C 4D   STA 4D0CH
        18FA   3E 7D      MVI A,7DH
        18FC   32 0D 4D   STA REPLY_BUF
        18FF   3A 8E 4C   LDA 4C8EH
        1902   32 0F 4D   STA 4D0FH
        1905   3E 1E      MVI A,1EH
        1907   32 10 4D   STA 4D10H
        190A   3A 8E 4C   LDA 4C8EH
        190D   C6 1E      ADI 1EH
        190F   32 8E 4C   STA 4C8EH
        1912   3A 8F 4C   LDA 4C8FH
        1915   D6 1E      SUI 1EH
        1917   32 8F 4C   STA 4C8FH
        L191A:
        191A * 3A 8D 4C   LDA 4C8DH
        191D * FE 43      CPI 43H
        191F * C2 27 19   JNZ L1927
        1922 * 3E 80      MVI A,80H
        1924 * 32 FD 4B   STA 4BFDH
        L1927:
        1927 * 3A FD 4B   LDA 4BFDH
        192A * 17         RAL
        192B * 3E 00      MVI A,00H
        192D * 3F         CMC
        192E * 17         RAL
        192F * 32 11 4D   STA 4D11H
        1932 * C3 A2 1C   JMP L1CA2

        ;----------------------------------------------------------------------
        ; cmd_42_44  (1935H)
        ;   Commands 42h/44h: 1-byte reply.
        ;----------------------------------------------------------------------
        cmd_42_44:
        1935 * 3A 8E 4C   LDA 4C8EH
        1938 * 87         ADD A
        1939 * 4F         MOV C,A
        193A * 21 8F 4C   LXI H,4C8FH
        193D * 11 11 4D   LXI D,4D11H
        1940 * CD C4 13   CALL memcpy_c
        1943 * 3E 80      MVI A,80H
        1945 * 32 FD 4B   STA 4BFDH
        1948 * 01 DD 40   LXI B,40DDH
        194B * CD B8 00   CALL api_sem_wait
        194E * 21 11 4D   LXI H,4D11H
        1951 * 3A 8E 4C   LDA 4C8EH
        1954 * 4F         MOV C,A
        1955 * 3A 8D 4C   LDA 4C8DH
        1958 * FE 44      CPI 44H
        195A * CA AD 19   JZ L19AD
        L195D:
        195D * 5E         MOV E,M
        195E * 23         INX H
        195F * E5         PUSH H
        1960 * 7E         MOV A,M
        1961 * E6 07      ANI 07H
        1963 * 57         MOV D,A
        1964 * D5         PUSH D
        1965 * 21 20 00   LXI H,0020H
        1968 * CD 4F 00   CALL api_div_helper
        196B * 62         MOV H,D
        196C * 6B         MOV L,E
        196D * 29         DAD H
        196E * 19         DAD D
        196F * 2A CC 4B   LHLD 4BCCH
        1972 * 19         DAD D
        1973 * 3A FD 4B   LDA 4BFDH
        1976 * A6         ANA M
        1977 * 32 FD 4B   STA 4BFDH
        197A * D1         POP D
        197B * 2A B4 4B   LHLD IMG_OUT_BASE
        197E * 19         DAD D
        197F * EB         XCHG
        1980 * 1A         LDAX D
        1981 * 1F         RAR
        1982 * 1F         RAR
        1983 * E1         POP H
        1984 * 7E         MOV A,M
        1985 * 17         RAL
        1986 * 0F         RRC
        1987 * 77         MOV M,A
        1988 * 23         INX H
        1989 * 0D         DCR C
        198A * C2 5D 19   JNZ L195D
        L198D:
        198D * 3E 00      MVI A,00H
        198F * 32 0C 4D   STA 4D0CH
        1992 * 3A 8C 4C   LDA CMD_BUF
        1995 * 3C         INR A
        1996 * 32 0D 4D   STA REPLY_BUF
        1999 * 3A FD 4B   LDA 4BFDH
        199C * 17         RAL
        199D * 3F         CMC
        199E * 17         RAL
        199F * E6 01      ANI 01H
        19A1 * 32 10 4D   STA 4D10H
        19A4 * 3A 8E 4C   LDA 4C8EH
        19A7 * 32 0F 4D   STA 4D0FH
        19AA * C3 9C 1C   JMP L1C9C
        L19AD:
        19AD * 5E         MOV E,M
        19AE * 23         INX H
        19AF * E5         PUSH H
        19B0 * 7E         MOV A,M
        19B1 * E6 03      ANI 03H
        19B3 * 57         MOV D,A
        19B4 * 2A B8 4B   LHLD IMG_MARK_BASE
        19B7 * 19         DAD D
        19B8 * EB         XCHG
        19B9 * 1A         LDAX D
        19BA * 1F         RAR
        19BB * E1         POP H
        19BC * 7E         MOV A,M
        19BD * 17         RAL
        19BE * 0F         RRC
        19BF * 77         MOV M,A
        19C0 * 23         INX H
        19C1 * 0D         DCR C
        19C2 * C2 AD 19   JNZ L19AD
        19C5 * C3 8D 19   JMP L198D

        ;----------------------------------------------------------------------
        ; cmd_45_59  (19C8H)
        ;   Commands 45h/59h: 5-byte reply.
        ;----------------------------------------------------------------------
        cmd_45_59:
        19C8 * 01 DD 40   LXI B,40DDH
        19CB * CD B8 00   CALL api_sem_wait
        19CE * 3E 00      MVI A,00H
        19D0 * 32 FD 4B   STA 4BFDH
        19D3 * 3A 91 4C   LDA 4C91H
        19D6 * B7         ORA A
        19D7 * C2 0F 1A   JNZ L1A0F
        19DA * 3A 90 4C   LDA 4C90H
        19DD * FE 3D      CPI 3DH
        19DF * D2 0F 1A   JNC L1A0F
        19E2 * 2A 90 4C   LHLD 4C90H
        19E5 * 22 11 4D   SHLD 4D11H
        19E8 * 2A 8E 4C   LHLD 4C8EH
        19EB * 22 0F 4D   SHLD 4D0FH
        19EE * EB         XCHG
        19EF * 21 14 4D   LXI H,4D14H
        19F2 * 3A 90 4C   LDA 4C90H
        19F5 * CD 54 1A   CALL L1A54
        19F8 * 3E 00      MVI A,00H
        19FA * 32 0C 4D   STA 4D0CH
        19FD * 3A FD 4B   LDA 4BFDH
        1A00 * 32 13 4D   STA 4D13H
        1A03 * 3A 90 4C   LDA 4C90H
        1A06 * 87         ADD A
        1A07 * C6 07      ADI 07H
        1A09 * 32 0D 4D   STA REPLY_BUF
        1A0C * C3 9C 1C   JMP L1C9C
        L1A0F:
        1A0F   2A 8E 4C   LHLD 4C8EH
        1A12   22 0F 4D   SHLD 4D0FH
        1A15   21 3C 00   LXI H,003CH
        1A18   22 11 4D   SHLD 4D11H
        1A1B   3A FD 4B   LDA 4BFDH
        1A1E   32 13 4D   STA 4D13H
        1A21   2A 8E 4C   LHLD 4C8EH
        1A24   EB         XCHG
        1A25   21 14 4D   LXI H,4D14H
        1A28   3E 3C      MVI A,3CH
        1A2A   CD 54 1A   CALL L1A54
        1A2D   2A 8E 4C   LHLD 4C8EH
        1A30   01 3C 00   LXI B,003CH
        1A33   09         DAD B
        1A34   22 8E 4C   SHLD 4C8EH
        1A37   2A 90 4C   LHLD 4C90H
        1A3A   01 C4 FF   LXI B,FFC4H
        1A3D   09         DAD B
        1A3E   22 90 4C   SHLD 4C90H
        1A41   3E 01      MVI A,01H
        1A43   32 0C 4D   STA 4D0CH
        1A46   3A FD 4B   LDA 4BFDH
        1A49   32 13 4D   STA 4D13H
        1A4C   3E 7F      MVI A,7FH
        1A4E   32 0D 4D   STA REPLY_BUF
        1A51   C3 9C 1C   JMP L1C9C
        L1A54:
        1A54 * F5         PUSH PSW
        1A55 * E5         PUSH H
        1A56 * D5         PUSH D
        1A57 * EB         XCHG
        1A58 * CD AB 1D   CALL L1DAB
        1A5B * D1         POP D
        1A5C * E1         POP H
        1A5D * F1         POP PSW
        1A5E * 71         MOV M,C
        1A5F * 23         INX H
        1A60 * 70         MOV M,B
        1A61 * 23         INX H
        1A62 * 13         INX D
        1A63 * 3D         DCR A
        1A64 * C2 54 1A   JNZ L1A54
        1A67 * C9         RET

        ;----------------------------------------------------------------------
        ; cmd_47  (1A68H)
        ;   Command 47h: 5-byte reply.
        ;----------------------------------------------------------------------
        cmd_47:
        1A68 * 01 DD 40   LXI B,40DDH
        1A6B * CD B8 00   CALL api_sem_wait
        1A6E * 3E 00      MVI A,00H
        1A70 * 32 FD 4B   STA 4BFDH
        1A73 * 3A 91 4C   LDA 4C91H
        1A76 * B7         ORA A
        1A77 * C2 B6 1A   JNZ L1AB6
        1A7A * 3A 90 4C   LDA 4C90H
        1A7D * FE 3D      CPI 3DH
        1A7F * D2 B6 1A   JNC L1AB6
        1A82 * 2A 90 4C   LHLD 4C90H
        1A85 * 22 11 4D   SHLD 4D11H
        1A88 * 2A 8E 4C   LHLD 4C8EH
        1A8B * 22 0F 4D   SHLD 4D0FH
        1A8E * 29         DAD H
        1A8F * EB         XCHG
        1A90 * 2A C0 4B   LHLD 4BC0H
        1A93 * 19         DAD D
        1A94 * 11 14 4D   LXI D,4D14H
        1A97 * 3A 90 4C   LDA 4C90H
        1A9A * 87         ADD A
        1A9B * 4F         MOV C,A
        1A9C * CD C4 13   CALL memcpy_c
        1A9F * 3E 00      MVI A,00H
        1AA1 * 32 0C 4D   STA 4D0CH
        1AA4 * 3A FD 4B   LDA 4BFDH
        1AA7 * 32 13 4D   STA 4D13H
        1AAA * 3A 90 4C   LDA 4C90H
        1AAD * 87         ADD A
        1AAE * C6 07      ADI 07H
        1AB0 * 32 0D 4D   STA REPLY_BUF
        1AB3 * C3 9C 1C   JMP L1C9C
        L1AB6:
        1AB6   2A 8E 4C   LHLD 4C8EH
        1AB9   22 0F 4D   SHLD 4D0FH
        1ABC   21 3C 00   LXI H,003CH
        1ABF   22 11 4D   SHLD 4D11H
        1AC2   3A FD 4B   LDA 4BFDH
        1AC5   32 13 4D   STA 4D13H
        1AC8   2A 8E 4C   LHLD 4C8EH
        1ACB   29         DAD H
        1ACC   EB         XCHG
        1ACD   2A C0 4B   LHLD 4BC0H
        1AD0   19         DAD D
        1AD1   11 14 4D   LXI D,4D14H
        1AD4   0E 78      MVI C,78H
        1AD6   CD C4 13   CALL memcpy_c
        1AD9   2A 8E 4C   LHLD 4C8EH
        1ADC   01 3C 00   LXI B,003CH
        1ADF   09         DAD B
        1AE0   22 8E 4C   SHLD 4C8EH
        1AE3   2A 90 4C   LHLD 4C90H
        1AE6   01 C4 FF   LXI B,FFC4H
        1AE9   09         DAD B
        1AEA   22 90 4C   SHLD 4C90H
        1AED   3E 01      MVI A,01H
        1AEF   32 0C 4D   STA 4D0CH
        1AF2   3A FD 4B   LDA 4BFDH
        1AF5   32 13 4D   STA 4D13H
        1AF8   3E 7F      MVI A,7FH
        1AFA   32 0D 4D   STA REPLY_BUF
        1AFD   C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_version  (1B00H)
        ;   Command 60h: reply carries the version string 88.03.14.
        ;----------------------------------------------------------------------
        cmd_version:
        1B00 * 3E 00      MVI A,00H
        1B02 * 32 0C 4D   STA 4D0CH
        1B05 * 32 10 4D   STA 4D10H
        1B08 * 3E 0C      MVI A,0CH
        1B0A * 32 0D 4D   STA REPLY_BUF
        1B0D * 3A 02 4C   LDA PLC_STATE
        1B10 * 32 0F 4D   STA 4D0FH
        1B13 * 11 11 4D   LXI D,4D11H
        1B16 * 21 11 12   LXI H,1211H
        1B19 * 0E 08      MVI C,08H
        1B1B * CD C4 13   CALL memcpy_c
        1B1E * 01 19 4D   LXI B,4D19H
        1B21 * 11 00 80   LXI D,USER_PROG
        1B24 * 2E 00      MVI L,00H
        L1B26:
        1B26 * 1A         LDAX D
        1B27 * 2C         INR L
        1B28 * 02         STAX B
        1B29 * 03         INX B
        1B2A * 13         INX D
        1B2B * FE 00      CPI 00H
        1B2D * CA 36 1B   JZ L1B36
        1B30   7D         MOV A,L
        1B31   FE 28      CPI 28H
        1B33   DA 26 1B   JC L1B26
        L1B36:
        1B36 * 3A 0D 4D   LDA REPLY_BUF
        1B39 * 85         ADD L
        1B3A * 32 0D 4D   STA REPLY_BUF
        1B3D * C3 A2 1C   JMP L1CA2

        ;----------------------------------------------------------------------
        ; cmd_function_table  (1B40H)
        ;   Command 61h: reply carries the function table (words from 2802h).
        ;----------------------------------------------------------------------
        cmd_function_table:
        1B40 * 01 DD 40   LXI B,40DDH
        1B43 * CD B8 00   CALL api_sem_wait
        1B46 * 3A 0C 4D   LDA 4D0CH
        1B49 * B7         ORA A
        1B4A * C2 58 1B   JNZ L1B58
        1B4D * 2A D3 4B   LHLD FUNK_TAB_PTR
        1B50 * 22 8F 4C   SHLD 4C8FH
        1B53 * 3E 80      MVI A,80H
        1B55 * 32 8E 4C   STA 4C8EH
        L1B58:
        1B58 * 2A 8F 4C   LHLD 4C8FH
        1B5B * EB         XCHG
        1B5C * 01 10 4D   LXI B,4D10H
        1B5F * 26 00      MVI H,00H
        L1B61:
        1B61 * 2E 02      MVI L,02H
        L1B63:
        1B63 * 1A         LDAX D
        1B64 * 02         STAX B
        1B65 * 13         INX D
        1B66 * 03         INX B
        1B67 * 24         INR H
        1B68 * 2D         DCR L
        1B69 * C2 63 1B   JNZ L1B63
        1B6C * 3A 8E 4C   LDA 4C8EH
        1B6F * D6 02      SUI 02H
        1B71 * CA 8B 1B   JZ L1B8B
        1B74 * 32 8E 4C   STA 4C8EH
        1B77 * 7C         MOV A,H
        1B78 * FE 40      CPI 40H
        1B7A * FA 61 1B   JM L1B61
        1B7D * 3E 01      MVI A,01H
        1B7F * 32 0C 4D   STA 4D0CH
        1B82 * 44         MOV B,H
        1B83 * EB         XCHG
        1B84 * 22 8F 4C   SHLD 4C8FH
        1B87 * 60         MOV H,B
        1B88 * C3 90 1B   JMP L1B90
        L1B8B:
        1B8B * 3E 00      MVI A,00H
        1B8D * 32 0C 4D   STA 4D0CH
        L1B90:
        1B90 * 7C         MOV A,H
        1B91 * C6 03      ADI 03H
        1B93 * 32 0D 4D   STA REPLY_BUF
        1B96 * 3E 00      MVI A,00H
        1B98 * 32 0F 4D   STA 4D0FH
        1B9B * 3A 8D 4C   LDA 4C8DH
        1B9E * 32 0E 4D   STA 4D0EH
        1BA1 * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_io_config  (1BA4H)
        ;   Command 6Dh: reply carries the I/O configuration table (2114h).
        ;----------------------------------------------------------------------
        cmd_io_config:
        1BA4 * 01 DD 40   LXI B,40DDH
        1BA7 * CD B8 00   CALL api_sem_wait
        1BAA * 3A 0C 4D   LDA 4D0CH
        1BAD * B7         ORA A
        1BAE * C2 BA 1B   JNZ L1BBA
        1BB1 * 32 8E 4C   STA 4C8EH
        1BB4 * 2A C4 4B   LHLD IO_CFG_PTR
        1BB7 * 22 8F 4C   SHLD 4C8FH
        L1BBA:
        1BBA * 2A 8F 4C   LHLD 4C8FH
        1BBD * EB         XCHG
        1BBE * 01 10 4D   LXI B,4D10H
        1BC1 * 26 00      MVI H,00H
        L1BC3:
        1BC3 * 2E 02      MVI L,02H
        L1BC5:
        1BC5 * 1A         LDAX D
        1BC6 * 02         STAX B
        1BC7 * 13         INX D
        1BC8 * 03         INX B
        1BC9 * 24         INR H
        1BCA * 2D         DCR L
        1BCB * C2 C5 1B   JNZ L1BC5
        1BCE * FE FF      CPI FFH
        1BD0 * CA E7 1B   JZ L1BE7
        1BD3 * 7C         MOV A,H
        1BD4 * FE 7C      CPI 7CH
        1BD6 * FA C3 1B   JM L1BC3
        1BD9   3E 01      MVI A,01H
        1BDB   32 0C 4D   STA 4D0CH
        1BDE   44         MOV B,H
        1BDF   EB         XCHG
        1BE0   22 8F 4C   SHLD 4C8FH
        1BE3   60         MOV H,B
        1BE4   C3 EC 1B   JMP L1BEC
        L1BE7:
        1BE7 * 3E 00      MVI A,00H
        1BE9 * 32 0C 4D   STA 4D0CH
        L1BEC:
        1BEC * 7C         MOV A,H
        1BED * C6 03      ADI 03H
        1BEF * 32 0D 4D   STA REPLY_BUF
        1BF2 * 3E 00      MVI A,00H
        1BF4 * 32 0F 4D   STA 4D0FH
        1BF7 * 3A 8D 4C   LDA 4C8DH
        1BFA * 32 0E 4D   STA 4D0EH
        1BFD * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_din_modules  (1C00H)
        ;   Command 6Eh: per-group flags of the digital input modules (five
        ;   groups, 82h).
        ;----------------------------------------------------------------------
        cmd_din_modules:
        1C00 * 01 DD 40   LXI B,40DDH
        1C03 * CD B8 00   CALL api_sem_wait
        1C06 * 3E 00      MVI A,00H
        1C08 * 32 0F 4D   STA 4D0FH
        1C0B * 32 0C 4D   STA 4D0CH
        1C0E * 2A C6 4B   LHLD 4BC6H
        1C11 * 11 10 4D   LXI D,4D10H
        1C14 * 0E 40      MVI C,40H
        1C16 * CD 42 1C   CALL L1C42
        1C19 * 3E 43      MVI A,43H
        1C1B * 32 0D 4D   STA REPLY_BUF
        1C1E * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_dout_modules  (1C21H)
        ;   Command 6Fh: per-group flags of the digital output modules (two
        ;   groups, 83h).
        ;----------------------------------------------------------------------
        cmd_dout_modules:
        1C21 * 01 DD 40   LXI B,40DDH
        1C24 * CD B8 00   CALL api_sem_wait
        1C27 * 3E 00      MVI A,00H
        1C29 * 32 0F 4D   STA 4D0FH
        1C2C * 32 0C 4D   STA 4D0CH
        1C2F * 2A CC 4B   LHLD 4BCCH
        1C32 * 11 10 4D   LXI D,4D10H
        1C35 * 0E 40      MVI C,40H
        1C37 * CD 42 1C   CALL L1C42
        1C3A * 3E 43      MVI A,43H
        1C3C * 32 0D 4D   STA REPLY_BUF
        1C3F * C3 9C 1C   JMP L1C9C
        L1C42:
        1C42 * 7E         MOV A,M
        1C43 * 12         STAX D
        1C44 * 23         INX H
        1C45 * 23         INX H
        1C46 * 23         INX H
        1C47 * 13         INX D
        1C48 * 0D         DCR C
        1C49 * C2 42 1C   JNZ L1C42
        1C4C * C9         RET

        ;----------------------------------------------------------------------
        ; cmd_module_table  (1C4DH)
        ;   Command 70h: module table reply.
        ;----------------------------------------------------------------------
        cmd_module_table:
        1C4D * 01 DD 40   LXI B,40DDH
        1C50 * CD B8 00   CALL api_sem_wait
        1C53 * 3E 00      MVI A,00H
        1C55 * 32 0F 4D   STA 4D0FH
        1C58 * 32 0C 4D   STA 4D0CH
        1C5B * 2A CE 4B   LHLD 4BCEH
        1C5E * 0E 44      MVI C,44H
        1C60 * 11 10 4D   LXI D,4D10H
        1C63 * CD C4 13   CALL memcpy_c
        1C66 * 3E 47      MVI A,47H
        1C68 * 32 0D 4D   STA REPLY_BUF
        1C6B * C3 9C 1C   JMP L1C9C

        ;----------------------------------------------------------------------
        ; cmd_ack  (1C6EH)
        ;   Commands 79h/7Ah: start-up/acknowledge replies.
        ;----------------------------------------------------------------------
        cmd_ack:
        1C6E * 3E 00      MVI A,00H
        1C70 * 32 0C 4D   STA 4D0CH
        1C73 * 32 0F 4D   STA 4D0FH
        1C76 * 2A 8C 4C   LHLD CMD_BUF
        1C79 * 22 0D 4D   SHLD REPLY_BUF
        1C7C * 3A 0D 4D   LDA REPLY_BUF
        1C7F * 3C         INR A
        1C80 * 32 0D 4D   STA REPLY_BUF
        1C83 * C3 A2 1C   JMP L1CA2
        L1C86:
        1C86 * 3E 00      MVI A,00H
        1C88 * 32 0C 4D   STA 4D0CH
        1C8B * 3A FD 4B   LDA 4BFDH
        1C8E * 32 10 4D   STA 4D10H
        1C91 * 3E 04      MVI A,04H
        1C93 * 32 0D 4D   STA REPLY_BUF
        1C96 * 3A 8E 4C   LDA 4C8EH
        1C99 * 32 0F 4D   STA 4D0FH
        L1C9C:
        1C9C * 01 E3 40   LXI B,40E3H
        1C9F * CD B2 00   CALL api_sem_signal
        L1CA2:
        1CA2 * 01 C5 40   LXI B,SEM_CMD_DONE
        1CA5 * CD B2 00   CALL api_sem_signal
        1CA8 * C3 1E 15   JMP proc_command

        ;============================================================================
        ; 1CAB-1DAA  COMMAND JUMP TABLE (128 WORDS, INDEXED BY COMMAND CODE)
        ;============================================================================
        1CAB            DW   cmd_illegal    ; command 00H
        1CAD            DW   cmd_illegal    ; command 01H
        1CAF            DW   cmd_02_04      ; command 02H
        1CB1            DW   cmd_illegal    ; command 03H
        1CB3            DW   cmd_02_04      ; command 04H
        1CB5            DW   cmd_illegal    ; command 05H
        1CB7            DW   cmd_illegal    ; command 06H
        1CB9            DW   cmd_07         ; command 07H
        1CBB            DW   cmd_illegal    ; command 08H
        1CBD            DW   cmd_illegal    ; command 09H
        1CBF            DW   cmd_0A_0C      ; command 0AH
        1CC1            DW   cmd_0B_0D      ; command 0BH
        1CC3            DW   cmd_0A_0C      ; command 0CH
        1CC5            DW   cmd_0B_0D      ; command 0DH
        1CC7            DW   cmd_0E         ; command 0EH
        1CC9            DW   cmd_0F_status  ; command 0FH
        1CCB            DW   cmd_illegal    ; command 10H
        1CCD            DW   cmd_illegal    ; command 11H
        1CCF            DW   cmd_illegal    ; command 12H
        1CD1            DW   cmd_illegal    ; command 13H
        1CD3            DW   cmd_illegal    ; command 14H
        1CD5            DW   cmd_illegal    ; command 15H
        1CD7            DW   cmd_illegal    ; command 16H
        1CD9            DW   cmd_illegal    ; command 17H
        1CDB            DW   cmd_illegal    ; command 18H
        1CDD            DW   cmd_illegal    ; command 19H
        1CDF            DW   cmd_illegal    ; command 1AH
        1CE1            DW   cmd_illegal    ; command 1BH
        1CE3            DW   cmd_illegal    ; command 1CH
        1CE5            DW   cmd_illegal    ; command 1DH
        1CE7            DW   cmd_download   ; command 1EH
        1CE9            DW   cmd_illegal    ; command 1FH
        1CEB            DW   cmd_run_control ; command 20H
        1CED            DW   cmd_illegal    ; command 21H
        1CEF            DW   cmd_illegal    ; command 22H
        1CF1            DW   cmd_illegal    ; command 23H
        1CF3            DW   cmd_illegal    ; command 24H
        1CF5            DW   cmd_illegal    ; command 25H
        1CF7            DW   cmd_illegal    ; command 26H
        1CF9            DW   cmd_illegal    ; command 27H
        1CFB            DW   cmd_illegal    ; command 28H
        1CFD            DW   cmd_illegal    ; command 29H
        1CFF            DW   cmd_illegal    ; command 2AH
        1D01            DW   cmd_illegal    ; command 2BH
        1D03            DW   cmd_illegal    ; command 2CH
        1D05            DW   cmd_illegal    ; command 2DH
        1D07            DW   cmd_illegal    ; command 2EH
        1D09            DW   cmd_illegal    ; command 2FH
        1D0B            DW   cmd_illegal    ; command 30H
        1D0D            DW   cmd_illegal    ; command 31H
        1D0F            DW   cmd_illegal    ; command 32H
        1D11            DW   cmd_illegal    ; command 33H
        1D13            DW   cmd_34_5F      ; command 34H
        1D15            DW   cmd_illegal    ; command 35H
        1D17            DW   cmd_illegal    ; command 36H
        1D19            DW   cmd_illegal    ; command 37H
        1D1B            DW   cmd_illegal    ; command 38H
        1D1D            DW   cmd_illegal    ; command 39H
        1D1F            DW   cmd_restart    ; command 3AH
        1D21            DW   cmd_illegal    ; command 3BH
        1D23            DW   cmd_illegal    ; command 3CH
        1D25            DW   cmd_illegal    ; command 3DH
        1D27            DW   cmd_illegal    ; command 3EH
        1D29            DW   cmd_illegal    ; command 3FH
        1D2B            DW   cmd_read_image ; command 40H
        1D2D            DW   cmd_read_image ; command 41H
        1D2F            DW   cmd_42_44      ; command 42H
        1D31            DW   cmd_read_image ; command 43H
        1D33            DW   cmd_42_44      ; command 44H
        1D35            DW   cmd_45_59      ; command 45H
        1D37            DW   cmd_illegal    ; command 46H
        1D39            DW   cmd_47         ; command 47H
        1D3B            DW   cmd_illegal    ; command 48H
        1D3D            DW   cmd_illegal    ; command 49H
        1D3F            DW   cmd_illegal    ; command 4AH
        1D41            DW   cmd_illegal    ; command 4BH
        1D43            DW   cmd_illegal    ; command 4CH
        1D45            DW   cmd_illegal    ; command 4DH
        1D47            DW   cmd_illegal    ; command 4EH
        1D49            DW   cmd_illegal    ; command 4FH
        1D4B            DW   cmd_illegal    ; command 50H
        1D4D            DW   cmd_illegal    ; command 51H
        1D4F            DW   cmd_illegal    ; command 52H
        1D51            DW   cmd_illegal    ; command 53H
        1D53            DW   cmd_illegal    ; command 54H
        1D55            DW   cmd_illegal    ; command 55H
        1D57            DW   cmd_illegal    ; command 56H
        1D59            DW   cmd_illegal    ; command 57H
        1D5B            DW   cmd_illegal    ; command 58H
        1D5D            DW   cmd_45_59      ; command 59H
        1D5F            DW   cmd_illegal    ; command 5AH
        1D61            DW   cmd_illegal    ; command 5BH
        1D63            DW   cmd_illegal    ; command 5CH
        1D65            DW   cmd_illegal    ; command 5DH
        1D67            DW   cmd_illegal    ; command 5EH
        1D69            DW   cmd_34_5F      ; command 5FH
        1D6B            DW   cmd_version    ; command 60H
        1D6D            DW   cmd_function_table ; command 61H
        1D6F            DW   cmd_illegal    ; command 62H
        1D71            DW   cmd_illegal    ; command 63H
        1D73            DW   cmd_illegal    ; command 64H
        1D75            DW   cmd_illegal    ; command 65H
        1D77            DW   cmd_illegal    ; command 66H
        1D79            DW   cmd_illegal    ; command 67H
        1D7B            DW   cmd_illegal    ; command 68H
        1D7D            DW   cmd_illegal    ; command 69H
        1D7F            DW   cmd_illegal    ; command 6AH
        1D81            DW   cmd_illegal    ; command 6BH
        1D83            DW   cmd_illegal    ; command 6CH
        1D85            DW   cmd_io_config  ; command 6DH
        1D87            DW   cmd_din_modules ; command 6EH
        1D89            DW   cmd_dout_modules ; command 6FH
        1D8B            DW   cmd_module_table ; command 70H
        1D8D            DW   cmd_illegal    ; command 71H
        1D8F            DW   cmd_illegal    ; command 72H
        1D91            DW   cmd_illegal    ; command 73H
        1D93            DW   cmd_illegal    ; command 74H
        1D95            DW   cmd_illegal    ; command 75H
        1D97            DW   cmd_illegal    ; command 76H
        1D99            DW   cmd_illegal    ; command 77H
        1D9B            DW   cmd_illegal    ; command 78H
        1D9D            DW   cmd_ack        ; command 79H
        1D9F            DW   cmd_ack        ; command 7AH
        1DA1            DW   cmd_illegal    ; command 7BH
        1DA3            DW   cmd_illegal    ; command 7CH
        1DA5            DW   cmd_illegal    ; command 7DH
        1DA7            DW   cmd_illegal    ; command 7EH
        1DA9            DW   cmd_illegal    ; command 7FH

        ;============================================================================
        ; 1DAB-1FB1  COMMAND HANDLERS (CONTINUED) AND AUX TRANSMIT PROCESS
        ;============================================================================
        L1DAB:
        1DAB * E5         PUSH H
        1DAC * 7D         MOV A,L
        1DAD * 07         RLC
        1DAE * 7C         MOV A,H
        1DAF * 17         RAL
        1DB0 * 6F         MOV L,A
        1DB1 * 3E 00      MVI A,00H
        1DB3 * 17         RAL
        1DB4 * 67         MOV H,A
        1DB5 * 29         DAD H
        1DB6 * 29         DAD H
        1DB7 * EB         XCHG
        1DB8 * 2A CE 4B   LHLD 4BCEH
        1DBB * 19         DAD D
        1DBC * D1         POP D
        1DBD * D5         PUSH D
        1DBE * 4E         MOV C,M
        1DBF * 23         INX H
        1DC0 * 7E         MOV A,M
        1DC1 * BA         CMP D
        1DC2 * DA FA 1D   JC L1DFA
        1DC5 * 79         MOV A,C
        1DC6 * BB         CMP E
        1DC7 * DA FA 1D   JC L1DFA
        1DCA * 23         INX H
        1DCB * 5E         MOV E,M
        1DCC * 23         INX H
        1DCD * 56         MOV D,M
        1DCE * EB         XCHG
        1DCF * D1         POP D
        1DD0 * 7B         MOV A,E
        1DD1 * E6 7F      ANI 7FH
        1DD3 * 5F         MOV E,A
        1DD4 * 16 00      MVI D,00H
        1DD6 * EB         XCHG
        1DD7 * 29         DAD H
        1DD8 * 29         DAD H
        1DD9 * EB         XCHG
        1DDA * 19         DAD D
        1DDB * E5         PUSH H
        1DDC * 23         INX H
        1DDD * 23         INX H
        1DDE * 7E         MOV A,M
        1DDF * E6 01      ANI 01H
        1DE1 * C2 E9 1D   JNZ L1DE9
        1DE4 * 4E         MOV C,M
        1DE5 * 23         INX H
        1DE6 * 46         MOV B,M
        1DE7 * E1         POP H
        1DE8 * C9         RET
        L1DE9:
        1DE9 * E1         POP H
        1DEA * 4E         MOV C,M
        1DEB * 23         INX H
        1DEC * 46         MOV B,M
        1DED * 2B         DCX H
        1DEE * 79         MOV A,C
        1DEF * E6 01      ANI 01H
        1DF1 * 5F         MOV E,A
        1DF2 * 3A FD 4B   LDA 4BFDH
        1DF5 * B3         ORA E
        1DF6 * 32 FD 4B   STA 4BFDH
        1DF9 * C9         RET
        L1DFA:
        1DFA * D1         POP D
        1DFB * 01 FF FF   LXI B,FFFFH
        1DFE * 3E 01      MVI A,01H
        1E00 * 32 FD 4B   STA 4BFDH
        1E03 * C9         RET
        L1E04:
        1E04 * D5         PUSH D
        1E05 * E5         PUSH H
        1E06 * 3A 8D 4C   LDA 4C8DH
        1E09 * FE 43      CPI 43H
        1E0B * C2 1A 1E   JNZ L1E1A
        1E0E * 68         MOV L,B
        1E0F * 26 00      MVI H,00H
        1E11 * 29         DAD H
        1E12 * 29         DAD H
        1E13 * 29         DAD H
        1E14 * 29         DAD H
        1E15 * 29         DAD H
        1E16 * EB         XCHG
        1E17 * C3 1F 1E   JMP L1E1F
        L1E1A:
        1E1A * EB         XCHG
        1E1B * 23         INX H
        1E1C * 5E         MOV E,M
        1E1D * 23         INX H
        1E1E * 56         MOV D,M
        L1E1F:
        1E1F * 2A BE 4B   LHLD 4BBEH
        1E22 * 19         DAD D
        1E23 * 0E 04      MVI C,04H
        L1E25:
        1E25 * C5         PUSH B
        1E26 * 06 00      MVI B,00H
        1E28 * 0E 08      MVI C,08H
        L1E2A:
        1E2A * 7E         MOV A,M
        1E2B * 1F         RAR
        1E2C * 78         MOV A,B
        1E2D * 17         RAL
        1E2E * 47         MOV B,A
        1E2F * 23         INX H
        1E30 * 0D         DCR C
        1E31 * C2 2A 1E   JNZ L1E2A
        1E34 * 78         MOV A,B
        1E35 * C1         POP B
        1E36 * D1         POP D
        1E37 * 12         STAX D
        1E38 * 13         INX D
        1E39 * D5         PUSH D
        1E3A * 0D         DCR C
        1E3B * C2 25 1E   JNZ L1E25
        1E3E * E1         POP H
        1E3F * D1         POP D
        1E40 * C9         RET
        L1E41:
        1E41 * D5         PUSH D
        1E42 * E5         PUSH H
        1E43 * EB         XCHG
        1E44 * 23         INX H
        1E45 * 5E         MOV E,M
        1E46 * 23         INX H
        1E47 * 56         MOV D,M
        1E48 * 2A BE 4B   LHLD 4BBEH
        1E4B * 19         DAD D
        1E4C * 0E 04      MVI C,04H
        L1E4E:
        1E4E * C5         PUSH B
        1E4F * 06 00      MVI B,00H
        1E51 * 0E 08      MVI C,08H
        L1E53:
        1E53 * 7E         MOV A,M
        1E54 * 1F         RAR
        1E55 * 1F         RAR
        1E56 * 78         MOV A,B
        1E57 * 17         RAL
        1E58 * 47         MOV B,A
        1E59 * 23         INX H
        1E5A * 0D         DCR C
        1E5B * C2 53 1E   JNZ L1E53
        1E5E * 78         MOV A,B
        1E5F * C1         POP B
        1E60 * D1         POP D
        1E61 * 12         STAX D
        1E62 * 13         INX D
        1E63 * D5         PUSH D
        1E64 * 0D         DCR C
        1E65 * C2 4E 1E   JNZ L1E4E
        1E68 * E1         POP H
        1E69 * D1         POP D
        1E6A * C9         RET

        ;----------------------------------------------------------------------
        ; proc_aux_tx  (1E6BH)
        ;   Process (prio 3): takes reply bytes from the transmit ring, builds
        ;   the frame at 5090h and starts transmission (1F5Bh).
        ;----------------------------------------------------------------------
        proc_aux_tx:
        1E6B * 3E 00      MVI A,00H
        1E6D * 32 8D 50   STA 508DH
        1E70 * 32 8F 50   STA 508FH
        1E73 * 21 90 50   LXI H,5090H
        1E76 * 22 DA 4B   SHLD 4BDAH
        L1E79:
        1E79 * 01 B3 40   LXI B,SEM_TXRING_DATA
        1E7C * CD B8 00   CALL api_sem_wait
        1E7F * 2A DE 4B   LHLD 4BDEH
        1E82 * 4E         MOV C,M
        1E83 * C5         PUSH B
        1E84 * 23         INX H
        1E85 * 11 8D 50   LXI D,508DH
        1E88 * 7B         MOV A,E
        1E89 * BD         CMP L
        1E8A * C2 95 1E   JNZ L1E95
        1E8D   7A         MOV A,D
        1E8E   BC         CMP H
        1E8F   C2 95 1E   JNZ L1E95
        1E92   21 8D 4D   LXI H,4D8DH
        L1E95:
        1E95 * 7E         MOV A,M
        1E96 * FE 79      CPI 79H
        1E98 * CA A3 1F   JZ L1FA3
        1E9B * 3A 8D 50   LDA 508DH
        1E9E * 81         ADD C
        1E9F * FE 80      CPI 80H
        1EA1 * DA AC 1E   JC L1EAC
        1EA4 * 2A DA 4B   LHLD 4BDAH
        1EA7 * 36 01      MVI M,01H
        1EA9 * CD 5B 1F   CALL start_tx_frame
        L1EAC:
        1EAC * C1         POP B
        1EAD * C5         PUSH B
        1EAE * 3A 8D 50   LDA 508DH
        1EB1 * 81         ADD C
        1EB2 * 32 8D 50   STA 508DH
        1EB5 * 79         MOV A,C
        1EB6 * 2F         CMA
        1EB7 * 5F         MOV E,A
        1EB8 * 16 FF      MVI D,FFH
        1EBA * 13         INX D
        1EBB * 01 CB 40   LXI B,SEM_TXRING_SPACE
        1EBE * CD B8 00   CALL api_sem_wait
        1EC1 * 2A DC 4B   LHLD 4BDCH
        1EC4 * 2B         DCX H
        1EC5 * 19         DAD D
        1EC6 * 22 DC 4B   SHLD 4BDCH
        1EC9 * 2A DA 4B   LHLD 4BDAH
        1ECC * EB         XCHG
        1ECD * 2A DE 4B   LHLD 4BDEH
        1ED0 * C1         POP B
        L1ED1:
        1ED1 * 7E         MOV A,M
        1ED2 * 12         STAX D
        1ED3 * 23         INX H
        1ED4 * 13         INX D
        1ED5 * D5         PUSH D
        1ED6 * EB         XCHG
        1ED7 * 21 8D 50   LXI H,508DH
        1EDA * 7B         MOV A,E
        1EDB * BD         CMP L
        1EDC * C2 E7 1E   JNZ L1EE7
        1EDF * 7A         MOV A,D
        1EE0 * BC         CMP H
        1EE1 * C2 E7 1E   JNZ L1EE7
        1EE4   11 8D 4D   LXI D,4D8DH
        L1EE7:
        1EE7 * EB         XCHG
        1EE8 * D1         POP D
        1EE9 * 0D         DCR C
        1EEA * C2 D1 1E   JNZ L1ED1
        1EED * D5         PUSH D
        1EEE * 01 CB 40   LXI B,SEM_TXRING_SPACE
        1EF1 * CD B2 00   CALL api_sem_signal
        1EF4 * 4E         MOV C,M
        1EF5 * 23         INX H
        1EF6 * EB         XCHG
        1EF7 * 21 8D 50   LXI H,508DH
        1EFA * 7B         MOV A,E
        1EFB * BD         CMP L
        1EFC * C2 07 1F   JNZ L1F07
        1EFF   7A         MOV A,D
        1F00   BC         CMP H
        1F01   C2 07 1F   JNZ L1F07
        1F04   11 8D 4D   LXI D,4D8DH
        L1F07:
        1F07 * EB         XCHG
        1F08 * 22 DE 4B   SHLD 4BDEH
        1F0B * D1         POP D
        1F0C * EB         XCHG
        1F0D * 22 DA 4B   SHLD 4BDAH
        1F10 * 3A 8F 50   LDA 508FH
        1F13 * 3C         INR A
        1F14 * 32 8F 50   STA 508FH
        1F17 * 79         MOV A,C
        1F18 * B7         ORA A
        1F19 * C2 34 1F   JNZ L1F34
        1F1C * 2A DA 4B   LHLD 4BDAH
        1F1F * 36 00      MVI M,00H
        1F21 * CD 5B 1F   CALL start_tx_frame
        1F24 * 3A D2 40   LDA 40D2H
        1F27 * B7         ORA A
        1F28 * CA 31 1F   JZ L1F31
        1F2B   01 D1 40   LXI B,40D1H
        1F2E   CD B2 00   CALL api_sem_signal
        L1F31:
        1F31 * C3 79 1E   JMP L1E79
        L1F34:
        1F34 * 3A D2 40   LDA 40D2H
        1F37 * B7         ORA A
        1F38 * CA 79 1E   JZ L1E79
        1F3B   01 CB 40   LXI B,SEM_TXRING_SPACE
        1F3E   CD B8 00   CALL api_sem_wait
        1F41   3A DC 4B   LDA 4BDCH
        1F44   47         MOV B,A
        1F45   3A DD 4B   LDA 4BDDH
        1F48   B0         ORA B
        1F49   01 CB 40   LXI B,SEM_TXRING_SPACE
        1F4C   CD B2 00   CALL api_sem_signal
        1F4F   C2 79 1E   JNZ L1E79
        1F52   01 D1 40   LXI B,40D1H
        1F55   CD B2 00   CALL api_sem_signal
        1F58   C3 79 1E   JMP L1E79

        ;----------------------------------------------------------------------
        ; start_tx_frame  (1F5BH)
        ;   Start sending the frame that was just built.
        ;----------------------------------------------------------------------
        start_tx_frame:
        1F5B * 3A FF 27   LDA 27FFH
        1F5E * 32 8E 50   STA 508EH
        1F61 * 3A 8D 50   LDA 508DH
        1F64 * C6 04      ADI 04H
        1F66 * 32 8D 50   STA 508DH
        L1F69:
        1F69 * 21 8D 50   LXI H,508DH
        1F6C * 3A E7 4B   LDA 4BE7H
        1F6F * B7         ORA A
        1F70 * C2 94 1F   JNZ L1F94
        1F73 * F3         DI
        1F74 * 3E 00      MVI A,00H
        1F76 * 32 EB 48   STA 48EBH
        1F79 * FB         EI
        1F7A * CD C1 00   CALL api_aux_send_frame
        1F7D * 01 B9 40   LXI B,SEM_AUX_FRAME
        1F80 * CD B8 00   CALL api_sem_wait
        1F83 * F3         DI
        1F84 * 3A EB 48   LDA 48EBH
        1F87 * F5         PUSH PSW
        1F88 * 3E FF      MVI A,FFH
        1F8A * 32 EB 48   STA 48EBH
        1F8D * FB         EI
        1F8E * F1         POP PSW
        1F8F * FE 02      CPI 02H
        1F91 * CA 69 1F   JZ L1F69
        L1F94:
        1F94 * 21 90 50   LXI H,5090H
        1F97 * 22 DA 4B   SHLD 4BDAH
        1F9A * 3E 00      MVI A,00H
        1F9C * 32 8D 50   STA 508DH
        1F9F * 32 8F 50   STA 508FH
        1FA2 * C9         RET
        L1FA3:
        1FA3 * 2A DA 4B   LHLD 4BDAH
        1FA6 * 36 01      MVI M,01H
        1FA8 * CD 5B 1F   CALL start_tx_frame
        1FAB * AF         XRA A
        1FAC * 32 E7 4B   STA 4BE7H
        1FAF * C3 AC 1E   JMP L1EAC

        ;============================================================================
        ; 1FB2-2358  PLC CYCLE: I/O SCAN, ANALOG SCAN, USER PROGRAM CALL
        ;   Digital inputs: groups of 4 ports from 20H, read active low into a byte-per-point image.
        ;   Digital outputs: groups of 4 ports from 10H. Analog: 6 modules, mux channel 0-7 cycled once per scan.
        ;============================================================================

        ;----------------------------------------------------------------------
        ; proc_plc_cycle  (1FB2H)
        ;   Process (prio 4): PLC main cycle: table I/O scan, analog scan, run
        ;   the user program, output scan, repeat.
        ;----------------------------------------------------------------------
        proc_plc_cycle:
        1FB2 * CD F1 1F   CALL scan_inputs
        1FB5 * CD 33 20   CALL scan_analog
        1FB8 * 3A DE 40   LDA 40DEH
        1FBB * B7         ORA A
        1FBC * CA CB 1F   JZ L1FCB
        1FBF * 01 DD 40   LXI B,40DDH
        1FC2 * CD B2 00   CALL api_sem_signal
        1FC5 * 01 E3 40   LXI B,40E3H
        1FC8 * CD B8 00   CALL api_sem_wait
        L1FCB:
        1FCB * CD DF 1F   CALL run_user_program
        1FCE * CD 12 20   CALL scan_outputs
        1FD1 * C3 B2 1F   JMP proc_plc_cycle
        1FD4 ? 3A 44 48   LDA 4844H
        1FD7 ? 32 43 48   STA 4843H
        1FDA ? FB         EI
        1FDB ? CD 33 20   CALL scan_analog
        1FDE ? C9         RET

        ;----------------------------------------------------------------------
        ; run_user_program  (1FDFH)
        ;   If PLC_STATE = 3 call the user program at USER_ENTRY (807Ch).
        ;----------------------------------------------------------------------
        run_user_program:
        1FDF * 3A 02 4C   LDA PLC_STATE
        1FE2 * FE 03      CPI 03H
        1FE4 * C2 F0 1F   JNZ L1FF0
        1FE7 * 21 F0 1F   LXI H,1FF0H
        1FEA * E5         PUSH H
        1FEB * 2A D5 4B   LHLD USER_ENTRY
        1FEE * E5         PUSH H
        1FEF * C9         RET
        L1FF0:
        1FF0 * C9         RET

        ;----------------------------------------------------------------------
        ; scan_inputs  (1FF1H)
        ;   Scan the input group table (digital inputs).
        ;----------------------------------------------------------------------
        scan_inputs:
        1FF1 * 16 00      MVI D,00H
        1FF3 * 01 00 00   LXI B,0000H
        L1FF6:
        1FF6 * 2A C6 4B   LHLD 4BC6H
        1FF9 * 09         DAD B
        1FFA * 7E         MOV A,M
        1FFB * E6 80      ANI 80H
        1FFD * CA 07 20   JZ L2007
        2000 * D5         PUSH D
        2001 * C5         PUSH B
        2002 * CD 96 22   CALL read_dig_in
        2005 * C1         POP B
        2006 * D1         POP D
        L2007:
        2007 * 14         INR D
        2008 * 79         MOV A,C
        2009 * C6 03      ADI 03H
        200B * 4F         MOV C,A
        200C * FE C0      CPI C0H
        200E * C2 F6 1F   JNZ L1FF6
        2011 * C9         RET

        ;----------------------------------------------------------------------
        ; scan_outputs  (2012H)
        ;   Scan the output group table (digital outputs).
        ;----------------------------------------------------------------------
        scan_outputs:
        2012 * 16 00      MVI D,00H
        2014 * 01 00 00   LXI B,0000H
        L2017:
        2017 * 2A CC 4B   LHLD 4BCCH
        201A * 09         DAD B
        201B * 7E         MOV A,M
        201C * E6 80      ANI 80H
        201E * CA 28 20   JZ L2028
        2021 * D5         PUSH D
        2022 * C5         PUSH B
        2023 * CD 03 23   CALL write_dig_out
        2026 * C1         POP B
        2027 * D1         POP D
        L2028:
        2028 * 14         INR D
        2029 * 79         MOV A,C
        202A * C6 03      ADI 03H
        202C * 4F         MOV C,A
        202D * FE C0      CPI C0H
        202F * C2 17 20   JNZ L2017
        2032 * C9         RET

        ;----------------------------------------------------------------------
        ; scan_analog  (2033H)
        ;   Analog scan: for each module strobe the odd port, wait for bit 4,
        ;   read 10 bits into the analog table.
        ;----------------------------------------------------------------------
        scan_analog:
        2033 * 3A D2 4B   LDA N_ADC
        2036 * B7         ORA A
        2037 * CA 51 20   JZ L2051
        203A * CD 52 20   CALL L2052
        203D * CD 87 20   CALL adc_read
        2040 * 3A F2 4B   LDA MUX_CHAN
        2043 * 3C         INR A
        2044 * FE 08      CPI 08H
        2046 * C2 4B 20   JNZ L204B
        2049 * 3E 00      MVI A,00H
        L204B:
        204B * 32 F2 4B   STA MUX_CHAN
        204E * CD 6B 20   CALL L206B
        L2051:
        2051 * C9         RET
        L2052:
        2052 * 1E 00      MVI E,00H
        2054 * 06 41      MVI B,41H
        L2056:
        2056 * F3         DI
        2057 * 78         MOV A,B
        2058 * 32 F2 48   STA OUT_STUB_PORT
        205B * CD F1 48   CALL 48F1H
        205E * FB         EI
        205F * C6 02      ADI 02H
        2061 * 47         MOV B,A
        2062 * 3A D2 4B   LDA N_ADC
        2065 * 1C         INR E
        2066 * BB         CMP E
        2067 * C2 56 20   JNZ L2056
        206A * C9         RET
        L206B:
        206B * 1E 00      MVI E,00H
        206D * 0E 3E      MVI C,3EH
        L206F:
        206F * F3         DI
        2070 * 79         MOV A,C
        2071 * C6 02      ADI 02H
        2073 * 4F         MOV C,A
        2074 * 32 F2 48   STA OUT_STUB_PORT
        2077 * 3A F2 4B   LDA MUX_CHAN
        207A * CD F1 48   CALL 48F1H
        207D * FB         EI
        207E * 3A D2 4B   LDA N_ADC
        2081 * 1C         INR E
        2082 * BB         CMP E
        2083 * C2 6F 20   JNZ L206F
        2086 * C9         RET

        ;----------------------------------------------------------------------
        ; adc_read  (2087H)
        ;   Read one analog conversion from module port pair.
        ;----------------------------------------------------------------------
        adc_read:
        2087 * 3E 40      MVI A,40H
        2089 * 32 F5 4B   STA 4BF5H
        208C * 3E 00      MVI A,00H
        208E * 32 F4 4B   STA 4BF4H
        L2091:
        2091 * CD E8 20   CALL L20E8
        2094 * F3         DI
        2095 * 3A F5 4B   LDA 4BF5H
        2098 * 3C         INR A
        2099 * 32 EF 48   STA IN_STUB_PORT
        209C * CD EE 48   CALL 48EEH
        209F * FB         EI
        20A0 * E6 10      ANI 10H
        20A2 * CA E1 20   JZ L20E1
        20A5 * F3         DI
        20A6 * 3A F5 4B   LDA 4BF5H
        20A9 * 32 EF 48   STA IN_STUB_PORT
        20AC * CD EE 48   CALL 48EEH
        20AF * 57         MOV D,A
        20B0 * 3A F5 4B   LDA 4BF5H
        20B3 * 3C         INR A
        20B4 * 32 EF 48   STA IN_STUB_PORT
        20B7 * CD EE 48   CALL 48EEH
        20BA * FB         EI
        20BB * 0F         RRC
        20BC * 0F         RRC
        20BD * E6 C0      ANI C0H
        20BF * 5F         MOV E,A
        20C0 * 7A         MOV A,D
        20C1 * 1F         RAR
        20C2 * 57         MOV D,A
        20C3 * 7B         MOV A,E
        20C4 * 1F         RAR
        20C5 * 5F         MOV E,A
        20C6 * 73         MOV M,E
        20C7 * 23         INX H
        20C8 * 72         MOV M,D
        L20C9:
        20C9 * 3A F5 4B   LDA 4BF5H
        20CC * C6 02      ADI 02H
        20CE * 32 F5 4B   STA 4BF5H
        20D1 * 3A F4 4B   LDA 4BF4H
        20D4 * 3C         INR A
        20D5 * 32 F4 4B   STA 4BF4H
        20D8 * 47         MOV B,A
        20D9 * 3A D2 4B   LDA N_ADC
        20DC * B8         CMP B
        20DD * C2 91 20   JNZ L2091
        20E0 * C9         RET
        L20E1:
        20E1   7E         MOV A,M
        20E2   F6 01      ORI 01H
        20E4   77         MOV M,A
        20E5   C3 C9 20   JMP L20C9
        L20E8:
        20E8 * 2A CE 4B   LHLD 4BCEH
        20EB * 23         INX H
        20EC * 23         INX H
        20ED * 5E         MOV E,M
        20EE * 23         INX H
        20EF * 56         MOV D,M
        20F0 * 3A F4 4B   LDA 4BF4H
        20F3 * 6F         MOV L,A
        20F4 * 26 00      MVI H,00H
        20F6 * 29         DAD H
        20F7 * 29         DAD H
        20F8 * 29         DAD H
        20F9 * 29         DAD H
        20FA * 29         DAD H
        20FB * 19         DAD D
        20FC * 3A F2 4B   LDA MUX_CHAN
        20FF * 07         RLC
        2100 * 07         RLC
        2101 * E6 FC      ANI FCH
        2103 * 4F         MOV C,A
        2104 * 06 00      MVI B,00H
        2106 * 09         DAD B
        2107 * C9         RET
        L2108:
        2108 * 3E 00      MVI A,00H
        210A * 32 F2 4B   STA MUX_CHAN
        210D * 32 F3 4B   STA 4BF3H
        2110 * CD 6B 20   CALL L206B
        2113 * C9         RET

        ;============================================================================
        ; 2114-2131  I/O CONFIGURATION TABLE (TYPE, BASE PORT PAIRS, ENDS FFFFH)
        ;   Type 02 = digital input group (ports 20,24,28,2C,30), type 03 = digital output group (10,14),
        ;   type 04 = analog module (40,42,44,46,48,4A).
        ;============================================================================
        2114            DB   02H,20H
        2116            DB   02H,24H
        2118            DB   02H,28H
        211A            DB   02H,2CH
        211C            DB   02H,30H
        211E            DB   03H,10H
        2120            DB   03H,14H
        2122            DB   04H,40H
        2124            DB   04H,42H
        2126            DB   04H,44H
        2128            DB   04H,46H
        212A            DB   04H,48H
        212C            DB   04H,4AH
        212E            DB   FFH,FFH
        L2130:
        2130 * 2A C4 4B   LHLD IO_CFG_PTR
        2133 * 23         INX H
        2134 * 22 FA 4B   SHLD 4BFAH
        2137 * 3E 00      MVI A,00H
        2139 * 32 F7 4B   STA 4BF7H
        213C * 2A FA 4B   LHLD 4BFAH
        L213F:
        213F * 46         MOV B,M
        2140 * 2B         DCX H
        2141 * 7E         MOV A,M
        2142 * 32 F6 4B   STA 4BF6H
        2145 * 3A F7 4B   LDA 4BF7H
        2148 * B8         CMP B
        2149 * CA 71 21   JZ L2171
        L214C:
        214C * 3A F6 4B   LDA 4BF6H
        214F * FE FF      CPI FFH
        2151 * CA 5F 21   JZ L215F
        L2154:
        2154 * 2A FA 4B   LHLD 4BFAH
        2157 * 23         INX H
        2158 * 23         INX H
        2159 * 22 FA 4B   SHLD 4BFAH
        215C * C3 3F 21   JMP L213F
        L215F:
        215F * 2A C4 4B   LHLD IO_CFG_PTR
        2162 * 23         INX H
        2163 * 22 FA 4B   SHLD 4BFAH
        2166 * 3A F7 4B   LDA 4BF7H
        2169 * 3C         INR A
        216A * 32 F7 4B   STA 4BF7H
        216D * C8         RZ
        216E * C3 3F 21   JMP L213F
        L2171:
        2171 * 3A F6 4B   LDA 4BF6H
        2174 * E6 0F      ANI 0FH
        2176 * FE 00      CPI 00H
        2178 * CA A6 21   JZ L21A6
        217B * FE 02      CPI 02H
        217D * CA A6 21   JZ L21A6
        2180 * FE 08      CPI 08H
        2182 * CA A6 21   JZ L21A6
        2185 * FE 01      CPI 01H
        2187 * CA EE 21   JZ L21EE
        218A * FE 03      CPI 03H
        218C * CA EE 21   JZ L21EE
        218F * FE 06      CPI 06H
        2191 * CA EE 21   JZ L21EE
        2194 * FE 08      CPI 08H
        2196 * CA EE 21   JZ L21EE
        2199 * FE 04      CPI 04H
        219B * CA 36 22   JZ L2236
        219E * FE 05      CPI 05H
        21A0 * CA 54 22   JZ L2254
        21A3 * C3 4C 21   JMP L214C
        L21A6:
        21A6 * 2A C6 4B   LHLD 4BC6H
        21A9 * 3A F7 4B   LDA 4BF7H
        21AC * D6 20      SUI 20H
        21AE * 0F         RRC
        21AF * DA 54 21   JC L2154
        21B2 * 0F         RRC
        21B3 * DA 54 21   JC L2154
        21B6 * E6 3F      ANI 3FH
        21B8 * 5F         MOV E,A
        21B9 * 16 00      MVI D,00H
        21BB * D5         PUSH D
        21BC * 47         MOV B,A
        21BD * 87         ADD A
        21BE * 80         ADD B
        21BF * 5F         MOV E,A
        21C0 * 16 00      MVI D,00H
        21C2 * 19         DAD D
        21C3 * 7E         MOV A,M
        21C4 * 06 80      MVI B,80H
        21C6 * A0         ANA B
        21C7 * C2 E0 21   JNZ L21E0
        21CA * 3A F6 4B   LDA 4BF6H
        21CD * B0         ORA B
        21CE * 77         MOV M,A
        21CF * D1         POP D
        21D0 * E5         PUSH H
        21D1 * EB         XCHG
        21D2 * 29         DAD H
        21D3 * 29         DAD H
        21D4 * 29         DAD H
        21D5 * 29         DAD H
        21D6 * 29         DAD H
        21D7 * EB         XCHG
        21D8 * E1         POP H
        21D9 * 23         INX H
        21DA * 73         MOV M,E
        21DB * 23         INX H
        21DC * 72         MOV M,D
        21DD * C3 54 21   JMP L2154
        L21E0:
        21E0   D1         POP D
        21E1   3A F6 4B   LDA 4BF6H
        21E4   46         MOV B,M
        21E5   B0         ORA B
        21E6   F6 10      ORI 10H
        21E8   E6 7F      ANI 7FH
        21EA   77         MOV M,A
        21EB   C3 54 21   JMP L2154
        L21EE:
        21EE * 2A CC 4B   LHLD 4BCCH
        21F1 * 3A F7 4B   LDA 4BF7H
        21F4 * D6 10      SUI 10H
        21F6 * 0F         RRC
        21F7 * DA 54 21   JC L2154
        21FA * 0F         RRC
        21FB * DA 54 21   JC L2154
        21FE * E6 3F      ANI 3FH
        2200 * 5F         MOV E,A
        2201 * 16 00      MVI D,00H
        2203 * D5         PUSH D
        2204 * 47         MOV B,A
        2205 * 87         ADD A
        2206 * 80         ADD B
        2207 * 5F         MOV E,A
        2208 * 16 00      MVI D,00H
        220A * 19         DAD D
        220B * 7E         MOV A,M
        220C * 06 80      MVI B,80H
        220E * A0         ANA B
        220F * C2 28 22   JNZ L2228
        2212 * 3A F6 4B   LDA 4BF6H
        2215 * B0         ORA B
        2216 * 77         MOV M,A
        2217 * D1         POP D
        2218 * E5         PUSH H
        2219 * EB         XCHG
        221A * 29         DAD H
        221B * 29         DAD H
        221C * 29         DAD H
        221D * 29         DAD H
        221E * 29         DAD H
        221F * EB         XCHG
        2220 * E1         POP H
        2221 * 23         INX H
        2222 * 73         MOV M,E
        2223 * 23         INX H
        2224 * 72         MOV M,D
        2225 * C3 54 21   JMP L2154
        L2228:
        2228   D1         POP D
        2229   3A F6 4B   LDA 4BF6H
        222C   46         MOV B,M
        222D   B0         ORA B
        222E   F6 10      ORI 10H
        2230   E6 7F      ANI 7FH
        2232   77         MOV M,A
        2233   C3 54 21   JMP L2154
        L2236:
        2236 * 3A F7 4B   LDA 4BF7H
        2239 * D6 40      SUI 40H
        223B * 4F         MOV C,A
        223C * E6 01      ANI 01H
        223E * C2 51 22   JNZ L2251
        2241 * 79         MOV A,C
        2242 * 07         RLC
        2243 * 07         RLC
        2244 * E6 F8      ANI F8H
        2246 * C6 07      ADI 07H
        2248 * 2A CE 4B   LHLD 4BCEH
        224B * 4E         MOV C,M
        224C * B9         CMP C
        224D * DA 51 22   JC L2251
        2250 * 77         MOV M,A
        L2251:
        2251 * C3 54 21   JMP L2154
        L2254:
        2254   3A F7 4B   LDA 4BF7H
        2257   4F         MOV C,A
        2258   5F         MOV E,A
        2259   E6 0F      ANI 0FH
        225B   FE 08      CPI 08H
        225D   D2 93 22   JNC L2293
        2260   79         MOV A,C
        2261   E6 F0      ANI F0H
        2263   C6 10      ADI 10H
        2265   1F         RAR
        2266   1F         RAR
        2267   6F         MOV L,A
        2268   26 00      MVI H,00H
        226A   EB         XCHG
        226B   2A CE 4B   LHLD 4BCEH
        226E   19         DAD D
        226F   E5         PUSH H
        2270   79         MOV A,C
        2271   E6 F0      ANI F0H
        2273   C6 10      ADI 10H
        2275   1F         RAR
        2276   1F         RAR
        2277   1F         RAR
        2278   1F         RAR
        2279   1F         RAR
        227A   67         MOV H,A
        227B   3E 00      MVI A,00H
        227D   1F         RAR
        227E   6F         MOV L,A
        227F   79         MOV A,C
        2280   E6 0F      ANI 0FH
        2282   3C         INR A
        2283   47         MOV B,A
        2284   07         RLC
        2285   07         RLC
        2286   07         RLC
        2287   07         RLC
        2288   90         SUB B
        2289   3D         DCR A
        228A   5F         MOV E,A
        228B   16 00      MVI D,00H
        228D   19         DAD D
        228E   EB         XCHG
        228F   E1         POP H
        2290   73         MOV M,E
        2291   23         INX H
        2292   72         MOV M,D
        L2293:
        2293   C3 54 21   JMP L2154

        ;----------------------------------------------------------------------
        ; read_dig_in  (2296H)
        ;   Read 4 input ports, invert (active low) and update the byte-per-
        ;   point input image (current and previous state bits).
        ;----------------------------------------------------------------------
        read_dig_in:
        2296 * 7A         MOV A,D
        2297 * 07         RLC
        2298 * 07         RLC
        2299 * E6 FC      ANI FCH
        229B * C6 20      ADI 20H
        229D * 32 F1 4B   STA 4BF1H
        22A0 * 4F         MOV C,A
        22A1 * 23         INX H
        22A2 * E5         PUSH H
        22A3 * 21 EC 4B   LXI H,4BECH
        22A6 * 06 04      MVI B,04H
        L22A8:
        22A8 * 79         MOV A,C
        22A9 * F3         DI
        22AA * 32 EF 48   STA IN_STUB_PORT
        22AD * CD EE 48   CALL 48EEH
        22B0 * FB         EI
        22B1 * 2F         CMA
        22B2 * 77         MOV M,A
        22B3 * 23         INX H
        22B4 * 0C         INR C
        22B5 * 05         DCR B
        22B6 * C2 A8 22   JNZ L22A8
        22B9 * E1         POP H
        22BA * 5E         MOV E,M
        22BB * 23         INX H
        22BC * 56         MOV D,M
        22BD * 2A B6 4B   LHLD IMG_IN_BASE
        22C0 * 19         DAD D
        22C1 * 3A EC 4B   LDA 4BECH
        22C4 * CD DE 22   CALL L22DE
        22C7 * 3A ED 4B   LDA 4BEDH
        22CA * CD DE 22   CALL L22DE
        22CD * 3A EE 4B   LDA 4BEEH
        22D0 * CD DE 22   CALL L22DE
        22D3 * 3A EF 4B   LDA 4BEFH
        22D6 * CD DE 22   CALL L22DE
        22D9 * 3E 20      MVI A,20H
        22DB * 37         STC
        22DC * 3F         CMC
        22DD * C9         RET
        L22DE:
        22DE * 57         MOV D,A
        22DF * 1E 08      MVI E,08H
        L22E1:
        22E1 * 7A         MOV A,D
        22E2 * 1F         RAR
        22E3 * 57         MOV D,A
        22E4 * CD ED 22   CALL L22ED
        22E7 * 23         INX H
        22E8 * 1D         DCR E
        22E9 * C2 E1 22   JNZ L22E1
        22EC * C9         RET
        L22ED:
        22ED * 7E         MOV A,M
        22EE * 47         MOV B,A
        22EF * 17         RAL
        22F0 * D2 F7 22   JNC L22F7
        22F3   07         RLC
        22F4   C3 FA 22   JMP L22FA
        L22F7:
        22F7 * 0F         RRC
        22F8 * 17         RAL
        22F9 * 17         RAL
        L22FA:
        22FA * E6 03      ANI 03H
        22FC * 4F         MOV C,A
        22FD * 78         MOV A,B
        22FE * E6 C0      ANI C0H
        2300 * B1         ORA C
        2301 * 77         MOV M,A
        2302 * C9         RET

        ;----------------------------------------------------------------------
        ; write_dig_out  (2303H)
        ;   Gather bits from the output image and write 4 output ports.
        ;----------------------------------------------------------------------
        write_dig_out:
        2303 * 7A         MOV A,D
        2304 * 07         RLC
        2305 * 07         RLC
        2306 * E6 FC      ANI FCH
        2308 * C6 10      ADI 10H
        230A * 32 F0 4B   STA 4BF0H
        230D * 23         INX H
        230E * 5E         MOV E,M
        230F * 23         INX H
        2310 * 56         MOV D,M
        2311 * 2A B4 4B   LHLD IMG_OUT_BASE
        2314 * 19         DAD D
        2315 * 0E 00      MVI C,00H
        L2317:
        2317 * 1E 08      MVI E,08H
        L2319:
        2319 * CD 3D 23   CALL L233D
        231C * 7A         MOV A,D
        231D * 1F         RAR
        231E * 57         MOV D,A
        231F * 23         INX H
        2320 * 1D         DCR E
        2321 * C2 19 23   JNZ L2319
        2324 * 3A F0 4B   LDA 4BF0H
        2327 * 81         ADD C
        2328 * F3         DI
        2329 * 32 F2 48   STA OUT_STUB_PORT
        232C * 7A         MOV A,D
        232D * CD F1 48   CALL 48F1H
        2330 * FB         EI
        2331 * 0C         INR C
        2332 * 79         MOV A,C
        2333 * FE 04      CPI 04H
        2335 * FA 17 23   JM L2317
        2338 * 37         STC
        2339 * 3F         CMC
        233A * 3E 20      MVI A,20H
        233C * C9         RET
        L233D:
        233D * 7E         MOV A,M
        233E * 47         MOV B,A
        233F * 17         RAL
        2340 * D2 47 23   JNC L2347
        2343   17         RAL
        2344   C3 49 23   JMP L2349
        L2347:
        2347 * 1F         RAR
        2348 * 1F         RAR
        L2349:
        2349 * 78         MOV A,B
        234A * DA 54 23   JC L2354
        234D * E6 FD      ANI FDH
        234F * 37         STC
        2350 * 3F         CMC
        2351 * C3 57 23   JMP L2357
        L2354:
        2354 * F6 02      ORI 02H
        2356 * 37         STC
        L2357:
        2357 * 77         MOV M,A
        2358 * C9         RET

        ;============================================================================
        ; 2359-24AF  PROGRAM LOADER / RELOCATOR
        ;   Accepted opcodes (tested): LXI H, CMA, MVI A, MOV B,A, MOV D,L, MOV M,A, MOV A,B, MOV A,M, ANA B/M,
        ;   ORA B/M, RNZ, RZ, JNZ, JMP, JZ, RET, ANI, POP/PUSH PSW, CALL n (function number).
        ;============================================================================

        ;----------------------------------------------------------------------
        ; program_loader  (2359H)
        ;   Relocate the downloaded program in place: LXI H operands (segment
        ;   nibble + 12-bit offset) -> image addresses, CALL n -> function table
        ;   entry, relative jumps -> absolute. Returns A=0 ok, 1 unresolved
        ;   function, 2 bad opcode.
        ;----------------------------------------------------------------------
        program_loader:
        2359 * 2A D5 4B   LHLD USER_ENTRY
        235C * 3E 00      MVI A,00H
        235E * 32 05 4C   STA 4C05H
        L2361:
        2361 * EB         XCHG
        2362 * 21 B0 24   LXI H,24B0H
        2365 * 4E         MOV C,M
        2366 * 1A         LDAX D
        2367 * 47         MOV B,A
        2368 * 23         INX H
        L2369:
        2369 * 7E         MOV A,M
        236A * B8         CMP B
        236B * CA 79 23   JZ L2379
        236E * 23         INX H
        236F * 23         INX H
        2370 * 0D         DCR C
        2371 * C2 69 23   JNZ L2369
        2374   3E 02      MVI A,02H
        2376   C3 13 24   JMP L2413
        L2379:
        2379 * D5         PUSH D
        237A * 23         INX H
        237B * 7E         MOV A,M
        237C * 83         ADD E
        237D * 5F         MOV E,A
        237E * 3E 00      MVI A,00H
        2380 * 8A         ADC D
        2381 * 57         MOV D,A
        2382 * E1         POP H
        2383 * 23         INX H
        2384 * D5         PUSH D
        2385 * 78         MOV A,B
        2386 * FE 21      CPI 21H
        2388 * C2 B0 23   JNZ L23B0
        238B * E5         PUSH H
        238C * 5E         MOV E,M
        238D * 23         INX H
        238E * 56         MOV D,M
        238F * 7A         MOV A,D
        2390 * E6 F0      ANI F0H
        2392 * 0F         RRC
        2393 * 0F         RRC
        2394 * 0F         RRC
        2395 * 0F         RRC
        2396 * 3D         DCR A
        2397 * 87         ADD A
        2398 * 4F         MOV C,A
        2399 * 06 00      MVI B,00H
        239B * 21 B4 4B   LXI H,IMG_OUT_BASE
        239E * 09         DAD B
        239F * 4E         MOV C,M
        23A0 * 23         INX H
        23A1 * 46         MOV B,M
        23A2 * 7A         MOV A,D
        23A3 * E6 0F      ANI 0FH
        23A5 * 57         MOV D,A
        23A6 * EB         XCHG
        23A7 * 09         DAD B
        23A8 * EB         XCHG
        23A9 * E1         POP H
        23AA * 73         MOV M,E
        23AB * 23         INX H
        23AC * 72         MOV M,D
        23AD * C3 14 24   JMP L2414
        L23B0:
        23B0 * FE CD      CPI CDH
        23B2 * C2 D8 23   JNZ L23D8
        23B5   E5         PUSH H
        23B6   7E         MOV A,M
        23B7   87         ADD A
        23B8   5F         MOV E,A
        23B9   16 00      MVI D,00H
        23BB   2A D3 4B   LHLD FUNK_TAB_PTR
        23BE   19         DAD D
        23BF   5E         MOV E,M
        23C0   23         INX H
        23C1   56         MOV D,M
        23C2   7B         MOV A,E
        23C3   B2         ORA D
        23C4   CA D3 23   JZ L23D3
        23C7   E1         POP H
        23C8   73         MOV M,E
        23C9   23         INX H
        23CA   72         MOV M,D
        23CB   3E 01      MVI A,01H
        23CD   32 05 4C   STA 4C05H
        23D0   C3 14 24   JMP L2414
        L23D3:
        23D3   3E 01      MVI A,01H
        23D5   C3 12 24   JMP L2412
        L23D8:
        23D8 * FE C3      CPI C3H
        23DA * CA E7 23   JZ L23E7
        23DD * FE CA      CPI CAH
        23DF * CA E7 23   JZ L23E7
        23E2 * FE C2      CPI C2H
        23E4 * C2 0B 24   JNZ L240B
        L23E7:
        23E7   E5         PUSH H
        23E8   E5         PUSH H
        23E9   5E         MOV E,M
        23EA   23         INX H
        23EB   56         MOV D,M
        23EC   E1         POP H
        23ED   19         DAD D
        23EE   EB         XCHG
        23EF   E1         POP H
        23F0   73         MOV M,E
        23F1   23         INX H
        23F2   72         MOV M,D
        23F3   3A 05 4C   LDA 4C05H
        23F6   B7         ORA A
        23F7   CA 08 24   JZ L2408
        23FA   CD 18 24   CALL L2418
        23FD   B7         ORA A
        23FE   C2 12 24   JNZ L2412
        2401   E1         POP H
        2402   D5         PUSH D
        2403   3E 00      MVI A,00H
        2405   32 05 4C   STA 4C05H
        L2408:
        2408   C3 14 24   JMP L2414
        L240B:
        240B * FE C9      CPI C9H
        240D * C2 14 24   JNZ L2414
        2410 * 3E 00      MVI A,00H
        L2412:
        2412 * E1         POP H
        L2413:
        2413 * C9         RET
        L2414:
        2414 * E1         POP H
        2415 * C3 61 23   JMP L2361
        L2418:
        2418   D5         PUSH D
        2419   23         INX H
        241A   7D         MOV A,L
        241B   BB         CMP E
        241C   C2 28 24   JNZ L2428
        241F   7C         MOV A,H
        2420   BA         CMP D
        2421   C2 28 24   JNZ L2428
        2424   3E 00      MVI A,00H
        2426   D1         POP D
        L2427:
        2427   C9         RET
        L2428:
        2428   7E         MOV A,M
        2429   B7         ORA A
        242A   CA AB 24   JZ L24AB
        242D   FE 05      CPI 05H
        242F   D2 50 24   JNC L2450
        2432   36 00      MVI M,00H
        2434   23         INX H
        2435   4E         MOV C,M
        2436   E5         PUSH H
        2437   23         INX H
        2438   46         MOV B,M
        2439   3D         DCR A
        243A   87         ADD A
        243B   5F         MOV E,A
        243C   16 00      MVI D,00H
        243E   21 B4 4B   LXI H,IMG_OUT_BASE
        2441   19         DAD D
        2442   5E         MOV E,M
        2443   23         INX H
        2444   56         MOV D,M
        2445   EB         XCHG
        2446   09         DAD B
        2447   EB         XCHG
        2448   E1         POP H
        2449   73         MOV M,E
        244A   23         INX H
        244B   72         MOV M,D
        244C   D1         POP D
        244D   C3 18 24   JMP L2418
        L2450:
        2450   FE 06      CPI 06H
        2452   C2 6C 24   JNZ L246C
        2455   36 00      MVI M,00H
        2457   23         INX H
        2458   5E         MOV E,M
        2459   E5         PUSH H
        245A   23         INX H
        245B   56         MOV D,M
        245C   EB         XCHG
        245D   29         DAD H
        245E   EB         XCHG
        245F   2A C0 4B   LHLD 4BC0H
        2462   19         DAD D
        2463   EB         XCHG
        2464   E1         POP H
        2465   73         MOV M,E
        2466   23         INX H
        2467   72         MOV M,D
        2468   D1         POP D
        2469   C3 18 24   JMP L2418
        L246C:
        246C   FE 07      CPI 07H
        246E   C2 83 24   JNZ L2483
        2471   23         INX H
        2472   5E         MOV E,M
        2473   E5         PUSH H
        2474   23         INX H
        2475   56         MOV D,M
        2476   EB         XCHG
        2477   CD AB 1D   CALL L1DAB
        247A   EB         XCHG
        247B   E1         POP H
        247C   73         MOV M,E
        247D   23         INX H
        247E   72         MOV M,D
        247F   D1         POP D
        2480   C3 18 24   JMP L2418
        L2483:
        2483   FE 09      CPI 09H
        2485   C2 8E 24   JNZ L248E
        2488   23         INX H
        2489   23         INX H
        248A   D1         POP D
        248B   C3 18 24   JMP L2418
        L248E:
        248E   FE 0A      CPI 0AH
        2490   C2 AA 24   JNZ L24AA
        2493   36 00      MVI M,00H
        2495   23         INX H
        2496   5E         MOV E,M
        2497   E5         PUSH H
        2498   23         INX H
        2499   56         MOV D,M
        249A   EB         XCHG
        249B   29         DAD H
        249C   EB         XCHG
        249D   2A C2 4B   LHLD 4BC2H
        24A0   19         DAD D
        24A1   EB         XCHG
        24A2   E1         POP H
        24A3   73         MOV M,E
        24A4   23         INX H
        24A5   72         MOV M,D
        24A6   D1         POP D
        24A7   C3 18 24   JMP L2418
        L24AA:
        24AA   D1         POP D
        L24AB:
        24AB   3E 03      MVI A,03H
        24AD   C3 27 24   JMP L2427

        ;============================================================================
        ; 24B0-24F2  LOADER OPCODE TABLE (COUNT, THEN 3 BYTES PER ENTRY - STRUCTURE NOT FULLY DECODED)
        ;============================================================================
        24B0            DB   16H
        24B1            DB   C9H,01H,2FH
        24B4            DB   01H,C3H,03H
        24B7            DB   E6H,02H,C2H
        24BA            DB   03H,CAH,03H
        24BD            DB   F5H,01H,F1H
        24C0            DB   01H,3EH,02H
        24C3            DB   21H,03H,7EH
        24C6            DB   01H,47H,01H
        24C9            DB   B0H,01H,77H
        24CC            DB   01H,78H,01H
        24CF            DB   A6H,01H,B6H
        24D2            DB   01H,CDH,03H
        24D5            DB   A0H,01H,55H
        24D8            DB   01H,C0H,01H
        24DB            DB   C8H,01H,06H
        24DE            DB   02H,1AH,CDH
        24E1            DB   F9H,24H,07H
        24E4            DB   07H,07H,07H
        24E7            DB   4FH,13H,1AH
        24EA            DB   CDH,F9H,24H
        24ED            DB   B1H,13H,05H
        24F0            DB   CAH,F7H,24H

        ;============================================================================
        ; 24F3-27FF  UTILITIES: HEX PARSE/PRINT, CRC, ROM STATION ADDRESS
        ;============================================================================
        24F3   67         MOV H,A
        24F4   C3 DF 24   JMP L24DF
        L24F7:
        24F7   6F         MOV L,A
        24F8   C9         RET
        L24F9:
        24F9   D6 30      SUI 30H
        24FB   FE 0A      CPI 0AH
        24FD   D8         RC
        24FE   D6 07      SUI 07H
        2500   C9         RET
        2501 ? 7A         MOV A,D
        2502 ? CD 12 25   CALL L2512
        2505 ? 7A         MOV A,D
        2506 ? CD 16 25   CALL L2516

        ;----------------------------------------------------------------------
        ; print_hex_byte  (2509H)
        ;   Format A as two hex digits (debug output).
        ;----------------------------------------------------------------------
        print_hex_byte:
        2509   7B         MOV A,E
        250A   CD 12 25   CALL L2512
        250D   7B         MOV A,E
        250E   CD 16 25   CALL L2516
        2511   C9         RET
        L2512:
        2512   0F         RRC
        2513   0F         RRC
        2514   0F         RRC
        2515   0F         RRC
        L2516:
        2516   E6 0F      ANI 0FH
        2518   FE 0A      CPI 0AH
        251A   DA 1F 25   JC L251F
        251D   C6 07      ADI 07H
        L251F:
        251F   C6 30      ADI 30H
        2521   77         MOV M,A
        2522   23         INX H
        2523   C9         RET
        L2524:
        2524 * 2A AE 4B   LHLD 4BAEH
        2527 * EB         XCHG
        2528 * AA         XRA D
        2529 * 4F         MOV C,A
        252A * 06 00      MVI B,00H
        252C * 21 A8 49   LXI H,CRC_TAB_T1
        252F * 09         DAD B
        2530 * 7E         MOV A,M
        2531 * AB         XRA E
        2532 * 57         MOV D,A
        2533 * 21 A8 4A   LXI H,CRC_TAB_T2
        2536 * 09         DAD B
        2537 * 5E         MOV E,M
        2538 * EB         XCHG
        2539 * 22 AE 4B   SHLD 4BAEH
        253C * C9         RET

        ;----------------------------------------------------------------------
        ; crc_update  (253DH)
        ;   CRC step: D:E = crc, idx = byte xor D, new D = T1[idx] xor E, new E
        ;   = T2[idx].
        ;----------------------------------------------------------------------
        crc_update:
        253D * 2A B0 4B   LHLD AUX_CRC
        2540 * EB         XCHG
        2541 * AA         XRA D
        2542 * 4F         MOV C,A
        2543 * 06 00      MVI B,00H
        2545 * 21 A8 49   LXI H,CRC_TAB_T1
        2548 * 09         DAD B
        2549 * 7E         MOV A,M
        254A * AB         XRA E
        254B * 57         MOV D,A
        254C * 21 A8 4A   LXI H,CRC_TAB_T2
        254F * 09         DAD B
        2550 * 5E         MOV E,M
        2551 * EB         XCHG
        2552 * 22 B0 4B   SHLD AUX_CRC
        2555 * C9         RET

        ;----------------------------------------------------------------------
        ; crc_init  (2556H)
        ;   Build the two 256-byte CRC tables (reflected polynomial 8408h) at
        ;   49A8h/4AA8h.
        ;----------------------------------------------------------------------
        crc_init:
        2556 * 01 08 84   LXI B,8408H
        2559 * 21 A8 49   LXI H,CRC_TAB_T1
        255C * 22 A8 4B   SHLD 4BA8H
        255F * 21 A8 4A   LXI H,CRC_TAB_T2
        2562 * 22 AA 4B   SHLD 4BAAH
        2565 * 21 00 00   LXI H,0000H
        2568 * 22 AC 4B   SHLD 4BACH
        L256B:
        256B * 1E 08      MVI E,08H
        L256D:
        256D * 37         STC
        256E * 3F         CMC
        256F * 7C         MOV A,H
        2570 * 1F         RAR
        2571 * 67         MOV H,A
        2572 * 7D         MOV A,L
        2573 * 1F         RAR
        2574 * 6F         MOV L,A
        2575 * D2 7E 25   JNC L257E
        2578 * 7D         MOV A,L
        2579 * A9         XRA C
        257A * 6F         MOV L,A
        257B * 7C         MOV A,H
        257C * A8         XRA B
        257D * 67         MOV H,A
        L257E:
        257E * 1D         DCR E
        257F * C2 6D 25   JNZ L256D
        2582 * EB         XCHG
        2583 * 2A A8 4B   LHLD 4BA8H
        2586 * 73         MOV M,E
        2587 * 23         INX H
        2588 * 22 A8 4B   SHLD 4BA8H
        258B * 2A AA 4B   LHLD 4BAAH
        258E * 72         MOV M,D
        258F * 23         INX H
        2590 * 22 AA 4B   SHLD 4BAAH
        2593 * 2A AC 4B   LHLD 4BACH
        2596 * 2C         INR L
        2597 * 22 AC 4B   SHLD 4BACH
        259A * C2 6B 25   JNZ L256B
        259D * C9         RET
        259E ? 23         INX H
        259F ? 72         MOV M,D
        25A0 ? D1         POP D
        25A1 ? C3 39 25   JMP L2539
        25A4 ? FE 09      CPI 09H
        25A6 ? C2 AF 25   JNZ L25AF
        25A9 ? 23         INX H
        25AA ? 23         INX H
        25AB ? D1         POP D
        25AC ? C3 39 25   JMP L2539
        25AF ? FE 0A      CPI 0AH
        25B1 ? C2 CB 25   JNZ L25CB
        25B4 ? 36 00      MVI M,00H
        25B6 ? 23         INX H
        25B7 ? 5E         MOV E,M
        25B8 ? E5         PUSH H
        25B9 ? 23         INX H
        25BA ? 56         MOV D,M
        25BB ? EB         XCHG
        25BC ? 29         DAD H
        25BD ? EB         XCHG
        25BE ? 2A C2 4B   LHLD 4BC2H
        25C1 ? 19         DAD D
        25C2 ? EB         XCHG
        25C3 ? E1         POP H
        25C4 ? 73         MOV M,E
        25C5 ? 23         INX H
        25C6 ? 72         MOV M,D
        25C7 ? D1         POP D
        25C8 ? C3 39 25   JMP L2539
        25CB ? D1         POP D
        25CC ? 3E 03      MVI A,03H
        25CE ? C3 48 25   JMP L2548
        25D1 ? 16 C9      MVI D,C9H
        25D3 ? 01 2F 01   LXI B,012FH
        25D6 ? C3 03 E6   JMP E603H
        25D9 ? 02         STAX B
        25DA ? C2 03 CA   JNZ CA03H
        25DD ? 03         INX B
        25DE ? F5         PUSH PSW
        25DF ? 01 F1 01   LXI B,01F1H
        25E2 ? 3E 02      MVI A,02H
        25E4 ? 21 03 7E   LXI H,7E03H
        25E7 ? 01 47 01   LXI B,0147H
        25EA ? B0         ORA B
        25EB ? 01 77 01   LXI B,0177H
        25EE ? 78         MOV A,B
        25EF ? 01 A6 01   LXI B,01A6H
        25F2 ? B6         ORA M
        25F3 ? 01 CD 03   LXI B,03CDH
        25F6 ? A0         ANA B
        25F7 ? 01 55 01   LXI B,0155H
        25FA ? C0         RNZ
        25FB ? 01 C8 01   LXI B,01C8H
        25FE ? 06 02      MVI B,02H
        2600 ? 1A         LDAX D
        2601 ? CD 1A 26   CALL L261A
        2604 ? 07         RLC
        2605 ? 07         RLC
        2606 ? 07         RLC
        2607 ? 07         RLC
        2608 ? 4F         MOV C,A
        2609 ? 13         INX D
        260A ? 1A         LDAX D
        260B ? CD 1A 26   CALL L261A
        260E ? B1         ORA C
        260F ? 13         INX D
        2610 ? 05         DCR B
        2611 ? CA 18 26   JZ L2618
        2614 ? 67         MOV H,A
        2615 ? C3 00 26   JMP L2600
        2618 ? 6F         MOV L,A
        2619 ? C9         RET
        261A ? D6 30      SUI 30H
        261C ? FE 0A      CPI 0AH
        261E ? D8         RC
        261F ? D6 07      SUI 07H
        2621 ? C9         RET
        2622 ? 7A         MOV A,D
        2623 ? CD 33 26   CALL L2633
        2626 ? 7A         MOV A,D
        2627 ? CD 37 26   CALL L2637
        262A ? 7B         MOV A,E
        262B ? CD 33 26   CALL L2633
        262E ? 7B         MOV A,E
        262F ? CD 37 26   CALL L2637
        2632 ? C9         RET
        2633 ? 0F         RRC
        2634 ? 0F         RRC
        2635 ? 0F         RRC
        2636 ? 0F         RRC
        2637 ? E6 0F      ANI 0FH
        2639 ? FE 0A      CPI 0AH
        263B ? DA 40 26   JC L2640
        263E ? C6 07      ADI 07H
        2640 ? C6 30      ADI 30H
        2642 ? 77         MOV M,A
        2643 ? 23         INX H
        2644 ? C9         RET
        2645 ? 2A AE 4B   LHLD 4BAEH
        2648 ? EB         XCHG
        2649 ? AA         XRA D
        264A ? 4F         MOV C,A
        264B ? 06 00      MVI B,00H
        264D ? 21 A8 49   LXI H,CRC_TAB_T1
        2650 ? 09         DAD B
        2651 ? 7E         MOV A,M
        2652 ? AB         XRA E
        2653 ? 57         MOV D,A
        2654 ? 21 A8 4A   LXI H,CRC_TAB_T2
        2657 ? 09         DAD B
        2658 ? 5E         MOV E,M
        2659 ? EB         XCHG
        265A ? 22 AE 4B   SHLD 4BAEH
        265D ? C9         RET
        265E ? 2A B0 4B   LHLD AUX_CRC
        2661 ? EB         XCHG
        2662 ? AA         XRA D
        2663 ? 4F         MOV C,A
        2664 ? 06 00      MVI B,00H
        2666 ? 21 A8 49   LXI H,CRC_TAB_T1
        2669 ? 09         DAD B
        266A ? 7E         MOV A,M
        266B ? AB         XRA E
        266C ? 57         MOV D,A
        266D ? 21 A8 4A   LXI H,CRC_TAB_T2
        2670 ? 09         DAD B
        2671 ? 5E         MOV E,M
        2672 ? EB         XCHG
        2673 ? 22 B0 4B   SHLD AUX_CRC
        2676 ? C9         RET
        2677 ? 01 08 84   LXI B,8408H
        267A ? 21 A8 49   LXI H,CRC_TAB_T1
        267D ? 22 A8 4B   SHLD 4BA8H
        2680 ? 21 A8 4A   LXI H,CRC_TAB_T2
        2683 ? 22 AA 4B   SHLD 4BAAH
        2686 ? 21 00 00   LXI H,0000H
        2689 ? 22 AC 4B   SHLD 4BACH
        268C ? 1E 08      MVI E,08H
        268E ? 37         STC
        268F ? 3F         CMC
        2690 ? 7C         MOV A,H
        2691 ? 1F         RAR
        2692 ? 67         MOV H,A
        2693 ? 7D         MOV A,L
        2694 ? 1F         RAR
        2695 ? 6F         MOV L,A
        2696 ? D2 9F 26   JNC L269F
        2699 ? 7D         MOV A,L
        269A ? A9         XRA C
        269B ? 6F         MOV L,A
        269C ? 7C         MOV A,H
        269D ? A8         XRA B
        269E ? 67         MOV H,A
        269F ? 1D         DCR E
        26A0 ? C2 8E 26   JNZ L268E
        26A3 ? EB         XCHG
        26A4 ? 2A A8 4B   LHLD 4BA8H
        26A7 ? 73         MOV M,E
        26A8 ? 23         INX H
        26A9 ? 22 A8 4B   SHLD 4BA8H
        26AC ? 2A AA 4B   LHLD 4BAAH
        26AF ? 72         MOV M,D
        26B0 ? 23         INX H
        26B1 ? 22 AA 4B   SHLD 4BAAH
        26B4 ? 2A AC 4B   LHLD 4BACH
        26B7 ? 2C         INR L
        26B8 ? 22 AC 4B   SHLD 4BACH
        26BB ? C2 8C 26   JNZ L268C
        26BE ? C9         RET
        26BF ? 00         NOP
        26C0 ? D1         POP D
        26C1 ? C9         RET
        26C2 ? 7E         MOV A,M
        26C3 ? B7         ORA A
        26C4 ? CA 45 27   JZ L2745
        26C7 ? FE 05      CPI 05H
        26C9 ? D2 EA 26   JNC L26EA
        26CC ? 36 00      MVI M,00H
        26CE ? 23         INX H
        26CF ? 4E         MOV C,M
        26D0 ? E5         PUSH H
        26D1 ? 23         INX H
        26D2 ? 46         MOV B,M
        26D3 ? 3D         DCR A
        26D4 ? 87         ADD A
        26D5 ? 5F         MOV E,A
        26D6 ? 16 00      MVI D,00H
        26D8 ? 21 B4 4B   LXI H,IMG_OUT_BASE
        26DB ? 19         DAD D
        26DC ? 5E         MOV E,M
        26DD ? 23         INX H
        26DE ? 56         MOV D,M
        26DF ? EB         XCHG
        26E0 ? 09         DAD B
        26E1 ? EB         XCHG
        26E2 ? E1         POP H
        26E3 ? 73         MOV M,E
        26E4 ? 23         INX H
        26E5 ? 72         MOV M,D
        26E6 ? D1         POP D
        26E7 ? C3 B2 26   JMP L26B2
        26EA ? FE 06      CPI 06H
        26EC ? C2 06 27   JNZ L2706
        26EF ? 36 00      MVI M,00H
        26F1 ? 23         INX H
        26F2 ? 5E         MOV E,M
        26F3 ? E5         PUSH H
        26F4 ? 23         INX H
        26F5 ? 56         MOV D,M
        26F6 ? EB         XCHG
        26F7 ? 29         DAD H
        26F8 ? EB         XCHG
        26F9 ? 2A C0 4B   LHLD 4BC0H
        26FC ? 19         DAD D
        26FD ? EB         XCHG
        26FE ? E1         POP H
        26FF ? 73         MOV M,E
        2700 ? 23         INX H
        2701 ? 72         MOV M,D
        2702 ? D1         POP D
        2703 ? C3 B2 26   JMP L26B2
        2706 ? FE 07      CPI 07H
        2708 ? C2 1D 27   JNZ L271D
        270B ? 23         INX H
        270C ? 5E         MOV E,M
        270D ? E5         PUSH H
        270E ? 23         INX H
        270F ? 56         MOV D,M
        2710 ? EB         XCHG
        2711 ? CD CC 1E   CALL L1ECC
        2714 ? EB         XCHG
        2715 ? E1         POP H
        2716 ? 73         MOV M,E
        2717 ? 23         INX H
        2718 ? 72         MOV M,D
        2719 ? D1         POP D
        271A ? C3 B2 26   JMP L26B2
        271D ? FE 09      CPI 09H
        271F ? C2 28 27   JNZ L2728
        2722 ? 23         INX H
        2723 ? 23         INX H
        2724 ? D1         POP D
        2725 ? C3 B2 26   JMP L26B2
        2728 ? FE 0A      CPI 0AH
        272A ? C2 44 27   JNZ L2744
        272D ? 36 00      MVI M,00H
        272F ? 23         INX H
        2730 ? 5E         MOV E,M
        2731 ? E5         PUSH H
        2732 ? 23         INX H
        2733 ? 56         MOV D,M
        2734 ? EB         XCHG
        2735 ? 29         DAD H
        2736 ? EB         XCHG
        2737 ? 2A C2 4B   LHLD 4BC2H
        273A ? 19         DAD D
        273B ? EB         XCHG
        273C ? E1         POP H
        273D ? 73         MOV M,E
        273E ? 23         INX H
        273F ? 72         MOV M,D
        2740 ? D1         POP D
        2741 ? C3 B2 26   JMP L26B2
        2744 ? D1         POP D
        2745 ? 3E 03      MVI A,03H
        2747 ? C3 C1 26   JMP L26C1
        274A ? 16 C9      MVI D,C9H
        274C ? 01 2F 01   LXI B,012FH
        274F ? C3 03 E6   JMP E603H
        2752 ? 02         STAX B
        2753 ? C2 03 CA   JNZ CA03H
        2756 ? 03         INX B
        2757 ? F5         PUSH PSW
        2758 ? 01 F1 01   LXI B,01F1H
        275B ? 3E 02      MVI A,02H
        275D ? 21 03 7E   LXI H,7E03H
        2760 ? 01 47 01   LXI B,0147H
        2763 ? B0         ORA B
        2764 ? 01 77 01   LXI B,0177H
        2767 ? 78         MOV A,B
        2768 ? 01 A6 01   LXI B,01A6H
        276B ? B6         ORA M
        276C ? 01 CD 03   LXI B,03CDH
        276F ? A0         ANA B
        2770 ? 01 55 01   LXI B,0155H
        2773 ? C0         RNZ
        2774 ? 01 C8 01   LXI B,01C8H
        2777 ? 06 02      MVI B,02H
        2779 ? 1A         LDAX D
        277A ? CD 93 27   CALL L2793
        277D ? 07         RLC
        277E ? 07         RLC
        277F ? 07         RLC
        2780 ? 07         RLC
        2781 ? 4F         MOV C,A
        2782 ? 13         INX D
        2783 ? 1A         LDAX D
        2784 ? CD 93 27   CALL L2793
        2787 ? B1         ORA C
        2788 ? 13         INX D
        2789 ? 05         DCR B
        278A ? CA 91 27   JZ L2791
        278D ? 67         MOV H,A
        278E ? C3 79 27   JMP L2779
        2791 ? 6F         MOV L,A
        2792 ? C9         RET
        2793 ? D6 30      SUI 30H
        2795 ? FE 0A      CPI 0AH
        2797 ? D8         RC
        2798 ? D6 07      SUI 07H
        279A ? C9         RET
        279B ? 7A         MOV A,D
        279C ? CD AC 27   CALL L27AC
        279F ? 7A         MOV A,D
        27A0 ? CD B0 27   CALL L27B0
        27A3 ? 7B         MOV A,E
        27A4 ? CD AC 27   CALL L27AC
        27A7 ? 7B         MOV A,E
        27A8 ? CD B0 27   CALL L27B0
        27AB ? C9         RET
        27AC ? 0F         RRC
        27AD ? 0F         RRC
        27AE ? 0F         RRC
        27AF ? 0F         RRC
        27B0 ? E6 0F      ANI 0FH
        27B2 ? FE 0A      CPI 0AH
        27B4 ? DA B9 27   JC L27B9
        27B7 ? C6 07      ADI 07H
        27B9 ? C6 30      ADI 30H
        27BB ? 77         MOV M,A
        27BC ? 23         INX H
        27BD ? C9         RET
        27BE ? 2A AE 4B   LHLD 4BAEH
        27C1 ? EB         XCHG
        27C2 ? AA         XRA D
        27C3 ? 4F         MOV C,A
        27C4 ? 06 00      MVI B,00H
        27C6 ? 21 A8 49   LXI H,CRC_TAB_T1
        27C9 ? 09         DAD B
        27CA ? 7E         MOV A,M
        27CB ? AB         XRA E
        27CC ? 57         MOV D,A
        27CD ? 21 A8 4A   LXI H,CRC_TAB_T2
        27D0 ? 09         DAD B
        27D1 ? 5E         MOV E,M
        27D2 ? EB         XCHG
        27D3 ? 22 AE 4B   SHLD 4BAEH
        27D6 ? C9         RET
        27D7 ? 2A B0 4B   LHLD AUX_CRC
        27DA ? EB         XCHG
        27DB ? AA         XRA D
        27DC ? 4F         MOV C,A
        27DD ? 06 00      MVI B,00H
        27DF ? 21 A8 49   LXI H,CRC_TAB_T1
        27E2 ? 09         DAD B
        27E3 ? 7E         MOV A,M
        27E4 ? AB         XRA E
        27E5 ? 57         MOV D,A
        27E6 ? 21 A8 4A   LXI H,CRC_TAB_T2
        27E9 ? 09         DAD B
        27EA ? 5E         MOV E,M
        27EB ? EB         XCHG
        27EC ? 22 B0 4B   SHLD AUX_CRC
        27EF ? C9         RET
        27F0 ? 01 08 84   LXI B,8408H
        27F3 ? 21 A8 49   LXI H,CRC_TAB_T1
        27F6 ? 22 A8 4B   SHLD 4BA8H
        27F9 ? 21 A8 4A   LXI H,CRC_TAB_T2
        27FC ? 22 AA 4B   SHLD 4BAAH
        27FF            DB   FFH             ; station address on the aux link (ADR 255)

        ;============================================================================
        ; 2800-287F  FUNK FUNCTION POINTER TABLE (64 WORDS; COPIED TO RAM AT 7F5FH BY 1219H)
        ;   Word n = entry of function block n; 0000 = not implemented.
        ;============================================================================
        2800            DW   0000H        ; function 0
        2802            DW   funk_01      ; function 1
        2804            DW   funk_02      ; function 2
        2806            DW   funk_03      ; function 3
        2808            DW   funk_04      ; function 4
        280A            DW   funk_05      ; function 5
        280C            DW   funk_06      ; function 6
        280E            DW   funk_07      ; function 7
        2810            DW   funk_08      ; function 8
        2812            DW   funk_09      ; function 9
        2814            DW   funk_0A      ; function 10
        2816            DW   0000H        ; function 11
        2818            DW   0000H        ; function 12
        281A            DW   0000H        ; function 13
        281C            DW   0000H        ; function 14
        281E            DW   0000H        ; function 15
        2820            DW   funk_10      ; function 16
        2822            DW   funk_11      ; function 17
        2824            DW   funk_12      ; function 18
        2826            DW   0000H        ; function 19
        2828            DW   funk_14      ; function 20
        282A            DW   funk_15      ; function 21
        282C            DW   funk_16      ; function 22
        282E            DW   funk_17      ; function 23
        2830            DW   funk_18      ; function 24
        2832            DW   funk_19      ; function 25
        2834            DW   funk_1A      ; function 26
        2836            DW   0000H        ; function 27
        2838            DW   funk_1C      ; function 28
        283A            DW   0000H        ; function 29
        283C            DW   funk_1E      ; function 30
        283E            DW   funk_1F      ; function 31
        2840            DW   0000H        ; function 32
        2842            DW   0000H        ; function 33
        2844            DW   0000H        ; function 34
        2846            DW   0000H        ; function 35
        2848            DW   0000H        ; function 36
        284A            DW   0000H        ; function 37
        284C            DW   0000H        ; function 38
        284E            DW   0000H        ; function 39
        2850            DW   0000H        ; function 40
        2852            DW   0000H        ; function 41
        2854            DW   0000H        ; function 42
        2856            DW   0000H        ; function 43
        2858            DW   0000H        ; function 44
        285A            DW   0000H        ; function 45
        285C            DW   0000H        ; function 46
        285E            DW   0000H        ; function 47
        2860            DW   0000H        ; function 48
        2862            DW   0000H        ; function 49
        2864            DW   0000H        ; function 50
        2866            DW   0000H        ; function 51
        2868            DW   0000H        ; function 52
        286A            DW   0000H        ; function 53
        286C            DW   0000H        ; function 54
        286E            DW   0000H        ; function 55
        2870            DW   0000H        ; function 56
        2872            DW   0000H        ; function 57
        2874            DW   0000H        ; function 58
        2876            DW   0000H        ; function 59
        2878            DW   0000H        ; function 60
        287A            DW   0000H        ; function 61
        287C            DW   0000H        ; function 62
        287E            DW   0000H        ; function 63

        ;============================================================================
        ; 2880-3FFF  FUNK FUNCTION LIBRARY
        ;   Subroutines called from compiled programs; arguments follow the CALL inline (POP H gives the argument address).
        ;============================================================================

        ;----------------------------------------------------------------------
        ; funk_01  (2880H)
        ;   Function block 1 (word 1 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_01:
        2880   E1         POP H
        2881   E5         PUSH H
        2882   23         INX H
        2883   23         INX H
        2884   23         INX H
        2885   4F         MOV C,A
        2886   E5         PUSH H
        2887   11 04 00   LXI D,0004H
        288A   19         DAD D
        288B   5E         MOV E,M
        288C   23         INX H
        288D   56         MOV D,M
        288E   1A         LDAX D
        288F   E6 01      ANI 01H
        2891   C2 C4 28   JNZ L28C4
        2894   D1         POP D
        2895   79         MOV A,C
        2896   E6 01      ANI 01H
        2898   CA B8 28   JZ L28B8
        289B   23         INX H
        289C   23         INX H
        289D   5E         MOV E,M
        289E   23         INX H
        289F   56         MOV D,M
        28A0   EB         XCHG
        28A1   5E         MOV E,M
        28A2   23         INX H
        28A3   56         MOV D,M
        28A4   7B         MOV A,E
        28A5   B2         ORA D
        28A6   CA AA 28   JZ L28AA
        28A9   1B         DCX D
        L28AA:
        28AA   7B         MOV A,E
        28AB   B2         ORA D
        28AC   72         MOV M,D
        28AD   2B         DCX H
        28AE   73         MOV M,E
        28AF   CA B5 28   JZ L28B5
        28B2   3E 00      MVI A,00H
        28B4   C9         RET
        L28B5:
        28B5   3E 01      MVI A,01H
        28B7   C9         RET
        L28B8:
        28B8   23         INX H
        28B9   23         INX H
        28BA   5E         MOV E,M
        28BB   23         INX H
        28BC   56         MOV D,M
        28BD   EB         XCHG
        28BE   5E         MOV E,M
        28BF   23         INX H
        28C0   56         MOV D,M
        28C1   C3 AA 28   JMP L28AA
        L28C4:
        28C4   E1         POP H
        28C5   7E         MOV A,M
        28C6   23         INX H
        28C7   5E         MOV E,M
        28C8   23         INX H
        28C9   56         MOV D,M
        28CA   E5         PUSH H
        28CB   FE 09      CPI 09H
        28CD   CA E5 28   JZ L28E5
        28D0   EB         XCHG
        28D1   4E         MOV C,M
        28D2   23         INX H
        28D3   46         MOV B,M
        L28D4:
        28D4   E1         POP H
        28D5   11 05 00   LXI D,0005H
        28D8   19         DAD D
        28D9   5E         MOV E,M
        28DA   23         INX H
        28DB   56         MOV D,M
        28DC   EB         XCHG
        28DD   71         MOV M,C
        28DE   23         INX H
        28DF   70         MOV M,B
        28E0   59         MOV E,C
        28E1   50         MOV D,B
        28E2   C3 AA 28   JMP L28AA
        L28E5:
        28E5   4B         MOV C,E
        28E6   42         MOV B,D
        28E7   C3 D4 28   JMP L28D4

        ;----------------------------------------------------------------------
        ; funk_02  (28EAH)
        ;   Function block 2 (word 2 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_02:
        28EA   E1         POP H
        28EB   E5         PUSH H
        28EC   23         INX H
        28ED   23         INX H
        28EE   23         INX H
        28EF   E6 01      ANI 01H
        28F1   CA 26 29   JZ L2926
        28F4   23         INX H
        28F5   23         INX H
        28F6   23         INX H
        28F7   23         INX H
        28F8   5E         MOV E,M
        28F9   23         INX H
        28FA   56         MOV D,M
        28FB   EB         XCHG
        28FC   5E         MOV E,M
        28FD   23         INX H
        28FE   56         MOV D,M
        28FF   7B         MOV A,E
        2900   B2         ORA D
        2901   CA 1E 29   JZ L291E
        2904   E5         PUSH H
        2905   2A 00 40   LHLD 4000H
        2908   CD BB 37   CALL L37BB
        290B   EB         XCHG
        290C   19         DAD D
        290D   7C         MOV A,H
        290E   17         RAL
        290F   EB         XCHG
        2910   E1         POP H
        2911   DA 1E 29   JC L291E
        2914   7A         MOV A,D
        2915   B3         ORA E
        2916   CA 1E 29   JZ L291E
        2919   3E 00      MVI A,00H
        291B   C3 25 29   JMP L2925
        L291E:
        291E   36 00      MVI M,00H
        2920   2B         DCX H
        2921   36 00      MVI M,00H
        2923   3E 01      MVI A,01H
        L2925:
        2925   C9         RET
        L2926:
        2926   7E         MOV A,M
        2927   23         INX H
        2928   5E         MOV E,M
        2929   23         INX H
        292A   56         MOV D,M
        292B   E5         PUSH H
        292C   FE 09      CPI 09H
        292E   CA 35 29   JZ L2935
        2931   EB         XCHG
        2932   5E         MOV E,M
        2933   23         INX H
        2934   56         MOV D,M
        L2935:
        2935   EB         XCHG
        2936   29         DAD H
        2937   E5         PUSH H
        2938   29         DAD H
        2939   29         DAD H
        293A   29         DAD H
        293B   E5         PUSH H
        293C   29         DAD H
        293D   D1         POP D
        293E   19         DAD D
        293F   D1         POP D
        2940   19         DAD D
        2941   EB         XCHG
        2942   2A 00 40   LHLD 4000H
        2945   19         DAD D
        2946   7C         MOV A,H
        2947   B5         ORA L
        2948   C2 4C 29   JNZ L294C
        294B   23         INX H
        L294C:
        294C   4D         MOV C,L
        294D   44         MOV B,H
        294E   E1         POP H
        294F   23         INX H
        2950   23         INX H
        2951   5E         MOV E,M
        2952   23         INX H
        2953   56         MOV D,M
        2954   EB         XCHG
        2955   71         MOV M,C
        2956   23         INX H
        2957   70         MOV M,B
        2958   AF         XRA A
        2959   C3 25 29   JMP L2925

        ;----------------------------------------------------------------------
        ; funk_03  (295CH)
        ;   Function block 3 (word 3 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_03:
        295C   E1         POP H
        295D   E5         PUSH H
        295E   23         INX H
        295F   23         INX H
        2960   23         INX H
        2961   E6 01      ANI 01H
        2963   CA 98 29   JZ L2998
        2966   23         INX H
        2967   23         INX H
        2968   23         INX H
        2969   23         INX H
        296A   5E         MOV E,M
        296B   23         INX H
        296C   56         MOV D,M
        296D   EB         XCHG
        296E   5E         MOV E,M
        296F   23         INX H
        2970   56         MOV D,M
        2971   7B         MOV A,E
        2972   B2         ORA D
        2973   CA 90 29   JZ L2990
        2976   E5         PUSH H
        2977   2A 00 40   LHLD 4000H
        297A   CD BB 37   CALL L37BB
        297D   EB         XCHG
        297E   19         DAD D
        297F   7C         MOV A,H
        2980   17         RAL
        2981   EB         XCHG
        2982   E1         POP H
        2983   DA 90 29   JC L2990
        2986   7A         MOV A,D
        2987   B3         ORA E
        2988   CA 90 29   JZ L2990
        298B   3E 00      MVI A,00H
        298D   C3 97 29   JMP L2997
        L2990:
        2990   36 00      MVI M,00H
        2992   2B         DCX H
        2993   36 00      MVI M,00H
        2995   3E 01      MVI A,01H
        L2997:
        2997   C9         RET
        L2998:
        2998   7E         MOV A,M
        2999   23         INX H
        299A   5E         MOV E,M
        299B   23         INX H
        299C   56         MOV D,M
        299D   E5         PUSH H
        299E   FE 09      CPI 09H
        29A0   CA A7 29   JZ L29A7
        29A3   EB         XCHG
        29A4   5E         MOV E,M
        29A5   23         INX H
        29A6   56         MOV D,M
        L29A7:
        29A7   21 14 00   LXI H,0014H
        29AA   CD 46 38   CALL L3846
        29AD   2A 00 40   LHLD 4000H
        29B0   19         DAD D
        29B1   7C         MOV A,H
        29B2   B5         ORA L
        29B3   C2 B7 29   JNZ L29B7
        29B6   23         INX H
        L29B7:
        29B7   4D         MOV C,L
        29B8   44         MOV B,H
        29B9   E1         POP H
        29BA   23         INX H
        29BB   23         INX H
        29BC   5E         MOV E,M
        29BD   23         INX H
        29BE   56         MOV D,M
        29BF   EB         XCHG
        29C0   71         MOV M,C
        29C1   23         INX H
        29C2   70         MOV M,B
        29C3   AF         XRA A
        29C4   C3 97 29   JMP L2997

        ;----------------------------------------------------------------------
        ; funk_04  (29C7H)
        ;   Function block 4 (word 4 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_04:
        29C7   E1         POP H
        29C8   E5         PUSH H
        29C9   23         INX H
        29CA   23         INX H
        29CB   23         INX H
        29CC   23         INX H
        29CD   5E         MOV E,M
        29CE   23         INX H
        29CF   56         MOV D,M
        29D0   EB         XCHG
        29D1   47         MOV B,A
        29D2   7E         MOV A,M
        29D3   70         MOV M,B
        29D4   E6 01      ANI 01H
        29D6   C2 E2 29   JNZ L29E2
        29D9   78         MOV A,B
        29DA   E6 01      ANI 01H
        29DC   CA E2 29   JZ L29E2
        29DF   3E 01      MVI A,01H
        29E1   C9         RET
        L29E2:
        29E2   3E 00      MVI A,00H
        29E4   C9         RET

        ;----------------------------------------------------------------------
        ; funk_05  (29E5H)
        ;   Function block 5 (word 5 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_05:
        29E5   E1         POP H
        29E6   E5         PUSH H
        29E7   23         INX H
        29E8   23         INX H
        29E9   23         INX H
        29EA   23         INX H
        29EB   E6 01      ANI 01H
        29ED   47         MOV B,A
        29EE   E5         PUSH H
        29EF   11 03 00   LXI D,0003H
        29F2   19         DAD D
        29F3   5E         MOV E,M
        29F4   23         INX H
        29F5   56         MOV D,M
        29F6   1A         LDAX D
        29F7   E6 01      ANI 01H
        29F9   4F         MOV C,A
        29FA   78         MOV A,B
        29FB   12         STAX D
        29FC   A9         XRA C
        29FD   C2 04 2A   JNZ L2A04
        2A00   E1         POP H
        2A01   3E 00      MVI A,00H
        2A03   C9         RET
        L2A04:
        2A04   E1         POP H
        2A05   5E         MOV E,M
        2A06   23         INX H
        2A07   56         MOV D,M
        2A08   1A         LDAX D
        2A09   E6 FE      ANI FEH
        2A0B   B0         ORA B
        2A0C   12         STAX D
        2A0D   3E 01      MVI A,01H
        2A0F   C9         RET

        ;----------------------------------------------------------------------
        ; funk_07  (2A10H)
        ;   Function block 7 (word 7 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_07:
        2A10   E6 01      ANI 01H
        2A12   C8         RZ
        2A13   E1         POP H
        2A14   E5         PUSH H
        2A15   23         INX H
        2A16   23         INX H
        2A17   23         INX H
        2A18   CD 75 37   CALL L3775
        2A1B   C5         PUSH B
        2A1C   CD 75 37   CALL L3775
        2A1F   7B         MOV A,E
        2A20   32 04 40   STA 4004H
        2A23   CD 75 37   CALL L3775
        2A26   D1         POP D
        2A27   C5         PUSH B
        2A28   D5         PUSH D
        2A29   3A 04 40   LDA 4004H
        2A2C   FE 00      CPI 00H
        2A2E   CA BC 2A   JZ L2ABC
        2A31   21 00 00   LXI H,0000H
        2A34   22 02 40   SHLD 4002H
        2A37   E1         POP H
        2A38   CD CC 2A   CALL L2ACC
        2A3B   FE 0A      CPI 0AH
        2A3D   D2 C9 2A   JNC L2AC9
        2A40   E5         PUSH H
        2A41   5F         MOV E,A
        2A42   16 00      MVI D,00H
        2A44   2A 02 40   LHLD 4002H
        2A47   19         DAD D
        2A48   22 02 40   SHLD 4002H
        2A4B   3A 04 40   LDA 4004H
        2A4E   FE 01      CPI 01H
        2A50   CA BC 2A   JZ L2ABC
        2A53   E1         POP H
        2A54   CD CC 2A   CALL L2ACC
        2A57   FE 0A      CPI 0AH
        2A59   D2 C9 2A   JNC L2AC9
        2A5C   E5         PUSH H
        2A5D   6F         MOV L,A
        2A5E   26 00      MVI H,00H
        2A60   01 0A 00   LXI B,000AH
        2A63   CD DE 37   CALL L37DE
        2A66   2A 02 40   LHLD 4002H
        2A69   19         DAD D
        2A6A   22 02 40   SHLD 4002H
        2A6D   3A 04 40   LDA 4004H
        2A70   FE 02      CPI 02H
        2A72   CA BC 2A   JZ L2ABC
        2A75   E1         POP H
        2A76   CD CC 2A   CALL L2ACC
        2A79   FE 0A      CPI 0AH
        2A7B   D2 C9 2A   JNC L2AC9
        2A7E   E5         PUSH H
        2A7F   6F         MOV L,A
        2A80   26 00      MVI H,00H
        2A82   01 64 00   LXI B,0064H
        2A85   CD DE 37   CALL L37DE
        2A88   2A 02 40   LHLD 4002H
        2A8B   19         DAD D
        2A8C   22 02 40   SHLD 4002H
        2A8F   3A 04 40   LDA 4004H
        2A92   FE 03      CPI 03H
        2A94   CA BC 2A   JZ L2ABC
        2A97   E1         POP H
        2A98   CD CC 2A   CALL L2ACC
        2A9B   FE 0A      CPI 0AH
        2A9D   D2 C9 2A   JNC L2AC9
        2AA0   E5         PUSH H
        2AA1   6F         MOV L,A
        2AA2   26 00      MVI H,00H
        2AA4   01 E8 03   LXI B,03E8H
        2AA7   CD DE 37   CALL L37DE
        2AAA   2A 02 40   LHLD 4002H
        2AAD   19         DAD D
        2AAE   22 02 40   SHLD 4002H
        2AB1   3A 04 40   LDA 4004H
        2AB4   FE 04      CPI 04H
        2AB6   CA BC 2A   JZ L2ABC
        2AB9   C3 C8 2A   JMP L2AC8
        L2ABC:
        2ABC   E1         POP H
        2ABD   2A 02 40   LHLD 4002H
        2AC0   EB         XCHG
        2AC1   E1         POP H
        2AC2   73         MOV M,E
        2AC3   23         INX H
        2AC4   72         MOV M,D
        2AC5   3E 01      MVI A,01H
        2AC7   C9         RET
        L2AC8:
        2AC8   E1         POP H
        L2AC9:
        2AC9   E1         POP H
        2ACA   AF         XRA A
        2ACB   C9         RET
        L2ACC:
        2ACC   0E 04      MVI C,04H
        L2ACE:
        2ACE   7E         MOV A,M
        2ACF   1F         RAR
        2AD0   78         MOV A,B
        2AD1   1F         RAR
        2AD2   47         MOV B,A
        2AD3   23         INX H
        2AD4   0D         DCR C
        2AD5   C2 CE 2A   JNZ L2ACE
        2AD8   78         MOV A,B
        2AD9   E6 F0      ANI F0H
        2ADB   0F         RRC
        2ADC   0F         RRC
        2ADD   0F         RRC
        2ADE   0F         RRC
        2ADF   C9         RET

        ;----------------------------------------------------------------------
        ; funk_08  (2AE0H)
        ;   Function block 8 (word 8 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_08:
        2AE0   E6 01      ANI 01H
        2AE2   C8         RZ
        2AE3   E1         POP H
        2AE4   E5         PUSH H
        2AE5   23         INX H
        2AE6   23         INX H
        2AE7   23         INX H
        2AE8   CD 75 37   CALL L3775
        2AEB   E5         PUSH H
        2AEC   7A         MOV A,D
        2AED   17         RAL
        2AEE   DA 62 2B   JC L2B62
        2AF1   21 10 27   LXI H,2710H
        2AF4   CD 46 38   CALL L3846
        2AF7   7B         MOV A,E
        2AF8   32 06 40   STA 4006H
        2AFB   EB         XCHG
        2AFC   21 E8 03   LXI H,03E8H
        2AFF   CD 46 38   CALL L3846
        2B02   7B         MOV A,E
        2B03   32 05 40   STA 4005H
        2B06   EB         XCHG
        2B07   21 64 00   LXI H,0064H
        2B0A   CD 46 38   CALL L3846
        2B0D   7B         MOV A,E
        2B0E   32 04 40   STA 4004H
        2B11   EB         XCHG
        2B12   21 0A 00   LXI H,000AH
        2B15   CD 46 38   CALL L3846
        2B18   7B         MOV A,E
        2B19   32 03 40   STA 4003H
        2B1C   7D         MOV A,L
        2B1D   32 02 40   STA 4002H
        2B20   E1         POP H
        2B21   CD 75 37   CALL L3775
        2B24   D5         PUSH D
        2B25   E5         PUSH H
        2B26   21 02 40   LXI H,4002H
        2B29   19         DAD D
        2B2A   3E 05      MVI A,05H
        2B2C   93         SUB E
        2B2D   5F         MOV E,A
        2B2E   0E 00      MVI C,00H
        L2B30:
        2B30   CA 3B 2B   JZ L2B3B
        2B33   79         MOV A,C
        2B34   B6         ORA M
        2B35   4F         MOV C,A
        2B36   23         INX H
        2B37   1D         DCR E
        2B38   C3 30 2B   JMP L2B30
        L2B3B:
        2B3B   79         MOV A,C
        2B3C   B7         ORA A
        2B3D   C2 61 2B   JNZ L2B61
        2B40   E1         POP H
        2B41   CD 75 37   CALL L3775
        2B44   D1         POP D
        2B45   21 02 40   LXI H,4002H
        L2B48:
        2B48   D5         PUSH D
        2B49   1E 04      MVI E,04H
        2B4B   56         MOV D,M
        L2B4C:
        2B4C   7A         MOV A,D
        2B4D   1F         RAR
        2B4E   57         MOV D,A
        2B4F   0A         LDAX B
        2B50   1F         RAR
        2B51   07         RLC
        2B52   02         STAX B
        2B53   03         INX B
        2B54   1D         DCR E
        2B55   C2 4C 2B   JNZ L2B4C
        2B58   23         INX H
        2B59   D1         POP D
        2B5A   1D         DCR E
        2B5B   C2 48 2B   JNZ L2B48
        2B5E   3E 01      MVI A,01H
        2B60   C9         RET
        L2B61:
        2B61   E1         POP H
        L2B62:
        2B62   E1         POP H
        2B63   AF         XRA A
        2B64   C9         RET

        ;----------------------------------------------------------------------
        ; funk_09  (2B65H)
        ;   Function block 9 (word 9 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_09:
        2B65   E6 01      ANI 01H
        2B67   C8         RZ
        2B68   E1         POP H
        2B69   E5         PUSH H
        2B6A   23         INX H
        2B6B   23         INX H
        2B6C   23         INX H
        2B6D   CD 75 37   CALL L3775
        2B70   C5         PUSH B
        2B71   CD 75 37   CALL L3775
        2B74   2A 00 40   LHLD 4000H
        2B77   7D         MOV A,L
        2B78   02         STAX B
        2B79   03         INX B
        2B7A   7C         MOV A,H
        2B7B   02         STAX B
        2B7C   CD C3 37   CALL L37C3
        2B7F   19         DAD D
        2B80   7C         MOV A,H
        2B81   E6 7F      ANI 7FH
        2B83   67         MOV H,A
        2B84   29         DAD H
        2B85   29         DAD H
        2B86   E5         PUSH H
        2B87   29         DAD H
        2B88   29         DAD H
        2B89   D1         POP D
        2B8A   19         DAD D
        2B8B   C1         POP B
        2B8C   7D         MOV A,L
        2B8D   02         STAX B
        2B8E   03         INX B
        2B8F   7C         MOV A,H
        2B90   02         STAX B
        2B91   3E 01      MVI A,01H
        2B93   C9         RET

        ;----------------------------------------------------------------------
        ; funk_0A  (2B94H)
        ;   Function block 10 (word 10 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_0A:
        2B94   E6 01      ANI 01H
        2B96   C8         RZ
        2B97   E1         POP H
        2B98   E5         PUSH H
        2B99   23         INX H
        2B9A   23         INX H
        2B9B   23         INX H
        2B9C   CD 75 37   CALL L3775
        2B9F   D5         PUSH D
        2BA0   CD C3 37   CALL L37C3
        2BA3   23         INX H
        2BA4   4E         MOV C,M
        2BA5   23         INX H
        2BA6   46         MOV B,M
        2BA7   EB         XCHG
        2BA8   7D         MOV A,L
        2BA9   B4         ORA H
        2BAA   CA D2 2B   JZ L2BD2
        2BAD   7C         MOV A,H
        2BAE   17         RAL
        2BAF   D2 D2 2B   JNC L2BD2
        2BB2   09         DAD B
        2BB3   7C         MOV A,H
        2BB4   17         RAL
        2BB5   DA D2 2B   JC L2BD2
        2BB8   E1         POP H
        2BB9   E5         PUSH H
        2BBA   29         DAD H
        2BBB   C1         POP B
        2BBC   09         DAD B
        2BBD   EB         XCHG
        2BBE   2B         DCX H
        2BBF   2B         DCX H
        2BC0   E5         PUSH H
        2BC1   19         DAD D
        2BC2   23         INX H
        2BC3   5E         MOV E,M
        2BC4   7B         MOV A,E
        2BC5   23         INX H
        2BC6   56         MOV D,M
        2BC7   B2         ORA D
        2BC8   3E 01      MVI A,01H
        2BCA   E1         POP H
        2BCB   CA D4 2B   JZ L2BD4
        2BCE   C1         POP B
        2BCF   19         DAD D
        2BD0   E5         PUSH H
        2BD1   C9         RET
        L2BD2:
        2BD2   E1         POP H
        2BD3   AF         XRA A
        L2BD4:
        2BD4   C9         RET

        ;----------------------------------------------------------------------
        ; funk_10  (2BD5H)
        ;   Function block 16 (word 16 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_10:
        2BD5   E6 01      ANI 01H
        2BD7   CA F5 2B   JZ L2BF5
        2BDA   E1         POP H
        2BDB   E5         PUSH H
        2BDC   23         INX H
        2BDD   23         INX H
        2BDE   23         INX H
        2BDF   CD 75 37   CALL L3775
        2BE2   D5         PUSH D
        2BE3   CD 75 37   CALL L3775
        2BE6   EB         XCHG
        2BE7   D1         POP D
        2BE8   7D         MOV A,L
        2BE9   BB         CMP E
        2BEA   C2 F5 2B   JNZ L2BF5
        2BED   7C         MOV A,H
        2BEE   BA         CMP D
        2BEF   C2 F5 2B   JNZ L2BF5
        2BF2   3E 01      MVI A,01H
        2BF4   C9         RET
        L2BF5:
        2BF5   3E 00      MVI A,00H
        2BF7   C9         RET

        ;----------------------------------------------------------------------
        ; funk_11  (2BF8H)
        ;   Function block 17 (word 17 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_11:
        2BF8   E6 01      ANI 01H
        2BFA   CA F5 2B   JZ L2BF5
        2BFD   E1         POP H
        2BFE   E5         PUSH H
        2BFF   23         INX H
        2C00   23         INX H
        2C01   23         INX H
        2C02   CD 75 37   CALL L3775
        2C05   D5         PUSH D
        2C06   CD 75 37   CALL L3775
        2C09   E1         POP H
        2C0A   7C         MOV A,H
        2C0B   AA         XRA D
        2C0C   17         RAL
        2C0D   D2 16 2C   JNC L2C16
        2C10   7A         MOV A,D
        2C11   17         RAL
        2C12   17         RAL
        2C13   E6 01      ANI 01H
        2C15   C9         RET
        L2C16:
        2C16   EB         XCHG
        2C17   7C         MOV A,H
        2C18   BA         CMP D
        2C19   CA 22 2C   JZ L2C22
        2C1C   DA 27 2C   JC L2C27
        2C1F   C3 F5 2B   JMP L2BF5
        L2C22:
        2C22   7D         MOV A,L
        2C23   BB         CMP E
        2C24   D2 F5 2B   JNC L2BF5
        L2C27:
        2C27   3E 01      MVI A,01H
        2C29   C9         RET

        ;----------------------------------------------------------------------
        ; funk_12  (2C2AH)
        ;   Function block 18 (word 18 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_12:
        2C2A   E6 01      ANI 01H
        2C2C   CA F5 2B   JZ L2BF5
        2C2F   E1         POP H
        2C30   E5         PUSH H
        2C31   23         INX H
        2C32   23         INX H
        2C33   23         INX H
        2C34   CD 75 37   CALL L3775
        2C37   D5         PUSH D
        2C38   CD 75 37   CALL L3775
        2C3B   E1         POP H
        2C3C   7C         MOV A,H
        2C3D   AA         XRA D
        2C3E   17         RAL
        2C3F   D2 48 2C   JNC L2C48
        2C42   7C         MOV A,H
        2C43   17         RAL
        2C44   17         RAL
        2C45   E6 01      ANI 01H
        2C47   C9         RET
        L2C48:
        2C48   EB         XCHG
        2C49   7A         MOV A,D
        2C4A   BC         CMP H
        2C4B   CA 54 2C   JZ L2C54
        2C4E   DA 27 2C   JC L2C27
        2C51   C3 F5 2B   JMP L2BF5
        L2C54:
        2C54   7B         MOV A,E
        2C55   BD         CMP L
        2C56   D2 F5 2B   JNC L2BF5
        2C59   C3 27 2C   JMP L2C27

        ;----------------------------------------------------------------------
        ; funk_06  (2C5CH)
        ;   Function block 6 (word 6 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_06:
        2C5C   E6 01      ANI 01H
        2C5E   CA 75 2C   JZ L2C75
        2C61   E1         POP H
        2C62   E5         PUSH H
        2C63   23         INX H
        2C64   23         INX H
        2C65   23         INX H
        2C66   F5         PUSH PSW
        2C67   CD 75 37   CALL L3775
        2C6A   D5         PUSH D
        2C6B   CD 75 37   CALL L3775
        2C6E   D1         POP D
        2C6F   7B         MOV A,E
        2C70   02         STAX B
        2C71   03         INX B
        2C72   7A         MOV A,D
        2C73   02         STAX B
        2C74   F1         POP PSW
        L2C75:
        2C75   C9         RET

        ;----------------------------------------------------------------------
        ; funk_14  (2C76H)
        ;   Function block 20 (word 20 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_14:
        2C76   E6 01      ANI 01H
        2C78   C8         RZ
        2C79   E1         POP H
        2C7A   E5         PUSH H
        2C7B   23         INX H
        2C7C   23         INX H
        2C7D   23         INX H
        2C7E   CD 75 37   CALL L3775
        2C81   22 02 40   SHLD 4002H
        2C84   CD 93 39   CALL L3993
        2C87   06 4F      MVI B,4FH
        2C89   26 00      MVI H,00H
        2C8B   2E 00      MVI L,00H
        2C8D   CD 89 3A   CALL L3A89
        2C90   2A 02 40   LHLD 4002H
        2C93   C5         PUSH B
        2C94   D5         PUSH D
        2C95   CD 75 37   CALL L3775
        2C98   22 02 40   SHLD 4002H
        2C9B   CD 93 39   CALL L3993
        2C9E   CD 87 38   CALL L3887
        2CA1   D1         POP D
        2CA2   78         MOV A,B
        2CA3   C1         POP B
        2CA4   47         MOV B,A
        2CA5   CD 2A 3A   CALL L3A2A
        2CA8   DA F6 2C   JC L2CF6
        2CAB   C5         PUSH B
        2CAC   D5         PUSH D
        2CAD   2A 02 40   LHLD 4002H
        2CB0   CD 75 37   CALL L3775
        2CB3   22 02 40   SHLD 4002H
        2CB6   CD 93 39   CALL L3993
        2CB9   CD 87 38   CALL L3887
        2CBC   D1         POP D
        2CBD   78         MOV A,B
        2CBE   C1         POP B
        2CBF   47         MOV B,A
        2CC0   CD 8C 38   CALL L388C
        2CC3   DA F6 2C   JC L2CF6
        2CC6   79         MOV A,C
        2CC7   B7         ORA A
        2CC8   C2 D1 2C   JNZ L2CD1
        2CCB   11 00 00   LXI D,0000H
        2CCE   C3 E5 2C   JMP L2CE5
        L2CD1:
        2CD1   79         MOV A,C
        2CD2   17         RAL
        2CD3   F5         PUSH PSW
        2CD4   1F         RAR
        2CD5   E6 7F      ANI 7FH
        2CD7   4F         MOV C,A
        2CD8   CD 13 3A   CALL L3A13
        2CDB   DA F5 2C   JC L2CF5
        2CDE   F1         POP PSW
        2CDF   D2 E5 2C   JNC L2CE5
        2CE2   CD C3 37   CALL L37C3
        L2CE5:
        2CE5   D5         PUSH D
        2CE6   2A 02 40   LHLD 4002H
        2CE9   CD 75 37   CALL L3775
        2CEC   D1         POP D
        2CED   7B         MOV A,E
        2CEE   02         STAX B
        2CEF   03         INX B
        2CF0   7A         MOV A,D
        2CF1   02         STAX B
        2CF2   3E 01      MVI A,01H
        2CF4   C9         RET
        L2CF5:
        2CF5   E1         POP H
        L2CF6:
        2CF6   AF         XRA A
        2CF7   C9         RET

        ;----------------------------------------------------------------------
        ; funk_15  (2CF8H)
        ;   Function block 21 (word 21 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_15:
        2CF8   E6 01      ANI 01H
        2CFA   C8         RZ
        2CFB   E1         POP H
        2CFC   E5         PUSH H
        2CFD   23         INX H
        2CFE   23         INX H
        2CFF   23         INX H
        2D00   CD 75 37   CALL L3775
        2D03   D5         PUSH D
        2D04   CD 75 37   CALL L3775
        2D07   C1         POP B
        2D08   79         MOV A,C
        2D09   83         ADD E
        2D0A   5F         MOV E,A
        2D0B   78         MOV A,B
        2D0C   8A         ADC D
        2D0D   4A         MOV C,D
        2D0E   57         MOV D,A
        2D0F   D5         PUSH D
        2D10   78         MOV A,B
        2D11   F5         PUSH PSW
        2D12   A9         XRA C
        2D13   E6 80      ANI 80H
        2D15   4F         MOV C,A
        2D16   7A         MOV A,D
        2D17   E6 80      ANI 80H
        2D19   B9         CMP C
        2D1A   CA 24 2D   JZ L2D24
        2D1D   F1         POP PSW
        2D1E   D2 34 2D   JNC L2D34
        2D21   C3 28 2D   JMP L2D28
        L2D24:
        2D24   F1         POP PSW
        2D25   DA 34 2D   JC L2D34
        L2D28:
        2D28   CD 75 37   CALL L3775
        2D2B   D1         POP D
        2D2C   7B         MOV A,E
        2D2D   02         STAX B
        2D2E   03         INX B
        2D2F   7A         MOV A,D
        2D30   02         STAX B
        2D31   3E 01      MVI A,01H
        2D33   C9         RET
        L2D34:
        2D34   D1         POP D
        2D35   AF         XRA A
        2D36   C9         RET

        ;----------------------------------------------------------------------
        ; funk_16  (2D37H)
        ;   Function block 22 (word 22 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_16:
        2D37   E6 01      ANI 01H
        2D39   C8         RZ
        2D3A   E1         POP H
        2D3B   E5         PUSH H
        2D3C   23         INX H
        2D3D   23         INX H
        2D3E   23         INX H
        2D3F   CD 75 37   CALL L3775
        2D42   D5         PUSH D
        2D43   CD 75 37   CALL L3775
        2D46   C1         POP B
        2D47   79         MOV A,C
        2D48   93         SUB E
        2D49   5F         MOV E,A
        2D4A   78         MOV A,B
        2D4B   9A         SBB D
        2D4C   4A         MOV C,D
        2D4D   57         MOV D,A
        2D4E   D5         PUSH D
        2D4F   78         MOV A,B
        2D50   F5         PUSH PSW
        2D51   A9         XRA C
        2D52   E6 80      ANI 80H
        2D54   4F         MOV C,A
        2D55   7A         MOV A,D
        2D56   E6 80      ANI 80H
        2D58   B9         CMP C
        2D59   CA 63 2D   JZ L2D63
        2D5C   F1         POP PSW
        2D5D   D2 73 2D   JNC L2D73
        2D60   C3 67 2D   JMP L2D67
        L2D63:
        2D63   F1         POP PSW
        2D64   DA 73 2D   JC L2D73
        L2D67:
        2D67   CD 75 37   CALL L3775
        2D6A   D1         POP D
        2D6B   7B         MOV A,E
        2D6C   02         STAX B
        2D6D   03         INX B
        2D6E   7A         MOV A,D
        2D6F   02         STAX B
        2D70   3E 01      MVI A,01H
        2D72   C9         RET
        L2D73:
        2D73   D1         POP D
        2D74   AF         XRA A
        2D75   C9         RET

        ;----------------------------------------------------------------------
        ; funk_17  (2D76H)
        ;   Function block 23 (word 23 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_17:
        2D76   E6 01      ANI 01H
        2D78   C8         RZ
        2D79   E1         POP H
        2D7A   E5         PUSH H
        2D7B   23         INX H
        2D7C   23         INX H
        2D7D   23         INX H
        2D7E   CD 75 37   CALL L3775
        2D81   D5         PUSH D
        2D82   CD 75 37   CALL L3775
        2D85   D5         PUSH D
        2D86   CD 75 37   CALL L3775
        2D89   D1         POP D
        2D8A   E1         POP H
        2D8B   C5         PUSH B
        2D8C   E5         PUSH H
        2D8D   CD 93 39   CALL L3993
        2D90   E1         POP H
        2D91   D5         PUSH D
        2D92   C5         PUSH B
        2D93   CD 92 39   CALL L3992
        2D96   CD 87 38   CALL L3887
        2D99   78         MOV A,B
        2D9A   C1         POP B
        2D9B   47         MOV B,A
        2D9C   D1         POP D
        2D9D   CD 2A 3A   CALL L3A2A
        2DA0   E1         POP H
        2DA1   DA AA 2D   JC L2DAA
        2DA4   CD C7 3B   CALL L3BC7
        2DA7   3E 01      MVI A,01H
        2DA9   C9         RET
        L2DAA:
        2DAA   AF         XRA A
        2DAB   C9         RET

        ;----------------------------------------------------------------------
        ; funk_18  (2DACH)
        ;   Function block 24 (word 24 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_18:
        2DAC   E6 01      ANI 01H
        2DAE   C8         RZ
        2DAF   E1         POP H
        2DB0   E5         PUSH H
        2DB1   23         INX H
        2DB2   23         INX H
        2DB3   23         INX H
        2DB4   CD 75 37   CALL L3775
        2DB7   E5         PUSH H
        2DB8   E5         PUSH H
        2DB9   69         MOV L,C
        2DBA   60         MOV H,B
        2DBB   CD C0 3B   CALL L3BC0
        2DBE   E1         POP H
        2DBF   D5         PUSH D
        2DC0   C5         PUSH B
        2DC1   CD 75 37   CALL L3775
        2DC4   CD 93 39   CALL L3993
        2DC7   CD 87 38   CALL L3887
        2DCA   78         MOV A,B
        2DCB   C1         POP B
        2DCC   47         MOV B,A
        2DCD   D1         POP D
        2DCE   CD 89 3A   CALL L3A89
        2DD1   DA 05 2E   JC L2E05
        2DD4   79         MOV A,C
        2DD5   B7         ORA A
        2DD6   C2 DF 2D   JNZ L2DDF
        2DD9   11 00 00   LXI D,0000H
        2DDC   C3 F3 2D   JMP L2DF3
        L2DDF:
        2DDF   79         MOV A,C
        2DE0   17         RAL
        2DE1   F5         PUSH PSW
        2DE2   1F         RAR
        2DE3   E6 7F      ANI 7FH
        2DE5   4F         MOV C,A
        2DE6   CD 13 3A   CALL L3A13
        2DE9   DA 04 2E   JC L2E04
        2DEC   F1         POP PSW
        2DED   D2 F3 2D   JNC L2DF3
        2DF0   CD C3 37   CALL L37C3
        L2DF3:
        2DF3   E1         POP H
        2DF4   D5         PUSH D
        2DF5   23         INX H
        2DF6   23         INX H
        2DF7   23         INX H
        2DF8   CD 75 37   CALL L3775
        2DFB   D1         POP D
        2DFC   7B         MOV A,E
        2DFD   02         STAX B
        2DFE   03         INX B
        2DFF   7A         MOV A,D
        2E00   02         STAX B
        2E01   3E 01      MVI A,01H
        2E03   C9         RET
        L2E04:
        2E04   E1         POP H
        L2E05:
        2E05   E1         POP H
        2E06   AF         XRA A
        2E07   C9         RET

        ;----------------------------------------------------------------------
        ; funk_19  (2E08H)
        ;   Function block 25 (word 25 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_19:
        2E08   E6 01      ANI 01H
        2E0A   C8         RZ
        2E0B   E1         POP H
        2E0C   E5         PUSH H
        2E0D   23         INX H
        2E0E   23         INX H
        2E0F   23         INX H
        2E10   CD 75 37   CALL L3775
        2E13   C5         PUSH B
        2E14   CD 75 37   CALL L3775
        2E17   D1         POP D
        2E18   D5         PUSH D
        2E19   E5         PUSH H
        2E1A   EB         XCHG
        2E1B   CD BB 37   CALL L37BB
        2E1E   09         DAD B
        2E1F   59         MOV E,C
        2E20   50         MOV D,B
        2E21   1B         DCX D
        2E22   7D         MOV A,L
        2E23   B4         ORA H
        2E24   CA 3A 2E   JZ L2E3A
        L2E27:
        2E27   E5         PUSH H
        2E28   1A         LDAX D
        2E29   E6 01      ANI 01H
        2E2B   6F         MOV L,A
        2E2C   0A         LDAX B
        2E2D   E6 FE      ANI FEH
        2E2F   B5         ORA L
        2E30   02         STAX B
        2E31   E1         POP H
        2E32   0B         DCX B
        2E33   1B         DCX D
        2E34   2B         DCX H
        2E35   7D         MOV A,L
        2E36   B4         ORA H
        2E37   C2 27 2E   JNZ L2E27
        L2E3A:
        2E3A   E1         POP H
        2E3B   CD 75 37   CALL L3775
        2E3E   D1         POP D
        2E3F   0A         LDAX B
        2E40   E6 01      ANI 01H
        2E42   4F         MOV C,A
        2E43   1A         LDAX D
        2E44   E6 FE      ANI FEH
        2E46   B1         ORA C
        2E47   12         STAX D
        2E48   3E 01      MVI A,01H
        2E4A   C9         RET

        ;----------------------------------------------------------------------
        ; funk_1A  (2E4BH)
        ;   Function block 26 (word 26 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_1A:
        2E4B   E6 01      ANI 01H
        2E4D   C8         RZ
        2E4E   E1         POP H
        2E4F   E5         PUSH H
        2E50   23         INX H
        2E51   23         INX H
        2E52   23         INX H
        2E53   CD 75 37   CALL L3775
        2E56   C5         PUSH B
        2E57   CD 75 37   CALL L3775
        2E5A   D1         POP D
        2E5B   D5         PUSH D
        2E5C   E5         PUSH H
        2E5D   EB         XCHG
        2E5E   CD BB 37   CALL L37BB
        2E61   09         DAD B
        2E62   03         INX B
        2E63   59         MOV E,C
        2E64   50         MOV D,B
        2E65   1B         DCX D
        2E66   1B         DCX D
        2E67   7D         MOV A,L
        2E68   B4         ORA H
        2E69   CA 76 2E   JZ L2E76
        L2E6C:
        2E6C   1A         LDAX D
        2E6D   02         STAX B
        2E6E   1B         DCX D
        2E6F   0B         DCX B
        2E70   2B         DCX H
        2E71   7D         MOV A,L
        2E72   B4         ORA H
        2E73   C2 6C 2E   JNZ L2E6C
        L2E76:
        2E76   E1         POP H
        2E77   CD 75 37   CALL L3775
        2E7A   D1         POP D
        2E7B   0A         LDAX B
        2E7C   12         STAX D
        2E7D   03         INX B
        2E7E   13         INX D
        2E7F   0A         LDAX B
        2E80   12         STAX D
        2E81   3E 01      MVI A,01H
        2E83   C9         RET

        ;----------------------------------------------------------------------
        ; funk_1C  (2E84H)
        ;   Function block 28 (word 28 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_1C:
        2E84   E6 01      ANI 01H
        2E86   C8         RZ
        2E87   E1         POP H
        2E88   E5         PUSH H
        2E89   23         INX H
        2E8A   23         INX H
        2E8B   23         INX H
        2E8C   CD 75 37   CALL L3775
        2E8F   E5         PUSH H
        2E90   CD 93 39   CALL L3993
        2E93   06 4F      MVI B,4FH
        2E95   21 00 00   LXI H,0000H
        2E98   CD 89 3A   CALL L3A89
        2E9B   21 02 40   LXI H,4002H
        2E9E   CD C7 3B   CALL L3BC7
        2EA1   E1         POP H
        2EA2   CD 01 31   CALL L3101
        2EA5   E5         PUSH H
        2EA6   21 02 40   LXI H,4002H
        2EA9   CD B7 3B   CALL L3BB7
        2EAC   D5         PUSH D
        2EAD   C5         PUSH B
        2EAE   CD 7A 38   CALL L387A
        2EB1   21 02 40   LXI H,4002H
        2EB4   CD C7 3B   CALL L3BC7
        2EB7   C1         POP B
        2EB8   D1         POP D
        2EB9   06 40      MVI B,40H
        2EBB   21 00 00   LXI H,0000H
        2EBE   CD 7A 38   CALL L387A
        2EC1   21 02 40   LXI H,4002H
        2EC4   CD B7 3B   CALL L3BB7
        2EC7   CD 86 3A   CALL L3A86
        2ECA   21 02 40   LXI H,4002H
        2ECD   CD C7 3B   CALL L3BC7
        2ED0   E1         POP H
        2ED1   CD 01 31   CALL L3101
        2ED4   E5         PUSH H
        2ED5   CD 82 3B   CALL L3B82
        2ED8   21 0E 40   LXI H,400EH
        2EDB   CD C7 3B   CALL L3BC7
        2EDE   E1         POP H
        2EDF   CD 01 31   CALL L3101
        2EE2   E5         PUSH H
        2EE3   CD 82 3B   CALL L3B82
        2EE6   21 0E 40   LXI H,400EH
        2EE9   CD B7 3B   CALL L3BB7
        2EEC   CD 7D 38   CALL L387D
        2EEF   21 02 40   LXI H,4002H
        2EF2   CD B7 3B   CALL L3BB7
        2EF5   CD 2A 3A   CALL L3A2A
        2EF8   21 0E 40   LXI H,400EH
        2EFB   CD B7 3B   CALL L3BB7
        2EFE   CD 8C 38   CALL L388C
        2F01   21 02 40   LXI H,4002H
        2F04   CD C7 3B   CALL L3BC7
        2F07   E1         POP H
        2F08   CD 75 37   CALL L3775
        2F0B   E5         PUSH H
        2F0C   CD 93 39   CALL L3993
        2F0F   06 4F      MVI B,4FH
        2F11   21 00 00   LXI H,0000H
        2F14   CD 89 3A   CALL L3A89
        2F17   21 05 40   LXI H,4005H
        2F1A   CD C7 3B   CALL L3BC7
        2F1D   E1         POP H
        2F1E   CD 01 31   CALL L3101
        2F21   E5         PUSH H
        2F22   21 05 40   LXI H,4005H
        2F25   CD B7 3B   CALL L3BB7
        2F28   D5         PUSH D
        2F29   C5         PUSH B
        2F2A   CD 7A 38   CALL L387A
        2F2D   21 05 40   LXI H,4005H
        2F30   CD C7 3B   CALL L3BC7
        2F33   C1         POP B
        2F34   D1         POP D
        2F35   06 40      MVI B,40H
        2F37   21 00 00   LXI H,0000H
        2F3A   CD 7A 38   CALL L387A
        2F3D   21 05 40   LXI H,4005H
        2F40   CD B7 3B   CALL L3BB7
        2F43   CD 86 3A   CALL L3A86
        2F46   21 05 40   LXI H,4005H
        2F49   CD C7 3B   CALL L3BC7
        2F4C   E1         POP H
        2F4D   CD 01 31   CALL L3101
        2F50   E5         PUSH H
        2F51   21 0E 40   LXI H,400EH
        2F54   CD C7 3B   CALL L3BC7
        2F57   E1         POP H
        2F58   CD 01 31   CALL L3101
        2F5B   E5         PUSH H
        2F5C   21 0E 40   LXI H,400EH
        2F5F   CD B7 3B   CALL L3BB7
        2F62   CD 7D 38   CALL L387D
        2F65   21 05 40   LXI H,4005H
        2F68   CD B7 3B   CALL L3BB7
        2F6B   CD 2A 3A   CALL L3A2A
        2F6E   21 0E 40   LXI H,400EH
        2F71   CD B7 3B   CALL L3BB7
        2F74   CD 8C 38   CALL L388C
        2F77   21 05 40   LXI H,4005H
        2F7A   CD C7 3B   CALL L3BC7
        2F7D   E1         POP H
        2F7E   CD 75 37   CALL L3775
        2F81   E5         PUSH H
        2F82   CD 93 39   CALL L3993
        2F85   06 4F      MVI B,4FH
        2F87   21 00 00   LXI H,0000H
        2F8A   CD 89 3A   CALL L3A89
        2F8D   21 08 40   LXI H,4008H
        2F90   CD C7 3B   CALL L3BC7
        2F93   E1         POP H
        2F94   CD 01 31   CALL L3101
        2F97   E5         PUSH H
        2F98   21 08 40   LXI H,4008H
        2F9B   CD B7 3B   CALL L3BB7
        2F9E   D5         PUSH D
        2F9F   C5         PUSH B
        2FA0   CD 7A 38   CALL L387A
        2FA3   21 08 40   LXI H,4008H
        2FA6   CD C7 3B   CALL L3BC7
        2FA9   C1         POP B
        2FAA   D1         POP D
        2FAB   06 40      MVI B,40H
        2FAD   21 00 00   LXI H,0000H
        2FB0   CD 7A 38   CALL L387A
        2FB3   21 08 40   LXI H,4008H
        2FB6   CD B7 3B   CALL L3BB7
        2FB9   CD 86 3A   CALL L3A86
        2FBC   21 08 40   LXI H,4008H
        2FBF   CD C7 3B   CALL L3BC7
        2FC2   E1         POP H
        2FC3   CD 01 31   CALL L3101
        2FC6   E5         PUSH H
        2FC7   21 0E 40   LXI H,400EH
        2FCA   CD C7 3B   CALL L3BC7
        2FCD   E1         POP H
        2FCE   CD 01 31   CALL L3101
        2FD1   E5         PUSH H
        2FD2   21 0E 40   LXI H,400EH
        2FD5   CD B7 3B   CALL L3BB7
        2FD8   CD 7D 38   CALL L387D
        2FDB   21 08 40   LXI H,4008H
        2FDE   CD B7 3B   CALL L3BB7
        2FE1   CD 2A 3A   CALL L3A2A
        2FE4   21 0E 40   LXI H,400EH
        2FE7   CD B7 3B   CALL L3BB7
        2FEA   CD 8C 38   CALL L388C
        2FED   21 08 40   LXI H,4008H
        2FF0   CD C7 3B   CALL L3BC7
        2FF3   E1         POP H
        2FF4   CD 75 37   CALL L3775
        2FF7   E5         PUSH H
        2FF8   CD 93 39   CALL L3993
        2FFB   06 4F      MVI B,4FH
        2FFD   21 00 00   LXI H,0000H
        3000   CD 89 3A   CALL L3A89
        3003   21 0B 40   LXI H,400BH
        3006   CD C7 3B   CALL L3BC7
        3009   E1         POP H
        300A   CD 01 31   CALL L3101
        300D   E5         PUSH H
        300E   21 0B 40   LXI H,400BH
        3011   CD B7 3B   CALL L3BB7
        3014   D5         PUSH D
        3015   C5         PUSH B
        3016   CD 7A 38   CALL L387A
        3019   21 0B 40   LXI H,400BH
        301C   CD C7 3B   CALL L3BC7
        301F   C1         POP B
        3020   D1         POP D
        3021   06 40      MVI B,40H
        3023   21 00 00   LXI H,0000H
        3026   CD 7A 38   CALL L387A
        3029   21 0B 40   LXI H,400BH
        302C   CD B7 3B   CALL L3BB7
        302F   CD 86 3A   CALL L3A86
        3032   21 0B 40   LXI H,400BH
        3035   CD C7 3B   CALL L3BC7
        3038   E1         POP H
        3039   CD 01 31   CALL L3101
        303C   E5         PUSH H
        303D   21 0E 40   LXI H,400EH
        3040   CD C7 3B   CALL L3BC7
        3043   E1         POP H
        3044   CD 01 31   CALL L3101
        3047   E5         PUSH H
        3048   21 0E 40   LXI H,400EH
        304B   CD B7 3B   CALL L3BB7
        304E   CD 7D 38   CALL L387D
        3051   21 0B 40   LXI H,400BH
        3054   CD B7 3B   CALL L3BB7
        3057   CD 2A 3A   CALL L3A2A
        305A   21 0E 40   LXI H,400EH
        305D   CD B7 3B   CALL L3BB7
        3060   CD 8C 38   CALL L388C
        3063   21 0B 40   LXI H,400BH
        3066   CD C7 3B   CALL L3BC7
        3069   21 02 40   LXI H,4002H
        306C   CD C0 3B   CALL L3BC0
        306F   79         MOV A,C
        3070   17         RAL
        3071   DA EE 30   JC L30EE
        3074   41         MOV B,C
        3075   62         MOV H,D
        3076   6B         MOV L,E
        3077   CD 2A 3A   CALL L3A2A
        307A   21 05 40   LXI H,4005H
        307D   CD B7 3B   CALL L3BB7
        3080   78         MOV A,B
        3081   17         RAL
        3082   DA EE 30   JC L30EE
        3085   CD 2A 3A   CALL L3A2A
        3088   C5         PUSH B
        3089   D5         PUSH D
        308A   21 08 40   LXI H,4008H
        308D   CD C0 3B   CALL L3BC0
        3090   79         MOV A,C
        3091   17         RAL
        3092   DA EC 30   JC L30EC
        3095   21 0B 40   LXI H,400BH
        3098   CD B7 3B   CALL L3BB7
        309B   78         MOV A,B
        309C   17         RAL
        309D   DA EC 30   JC L30EC
        30A0   CD 2A 3A   CALL L3A2A
        30A3   E1         POP H
        30A4   79         MOV A,C
        30A5   C1         POP B
        30A6   41         MOV B,C
        30A7   4F         MOV C,A
        30A8   CD 86 3A   CALL L3A86
        30AB   DA EE 30   JC L30EE
        30AE   CD 82 3B   CALL L3B82
        30B1   DA EE 30   JC L30EE
        30B4   21 0E 40   LXI H,400EH
        30B7   CD C7 3B   CALL L3BC7
        30BA   E1         POP H
        30BB   CD 01 31   CALL L3101
        30BE   E5         PUSH H
        30BF   21 0E 40   LXI H,400EH
        30C2   CD B7 3B   CALL L3BB7
        30C5   CD 2A 3A   CALL L3A2A
        30C8   DA EE 30   JC L30EE
        30CB   79         MOV A,C
        30CC   17         RAL
        30CD   F5         PUSH PSW
        30CE   1F         RAR
        30CF   E6 7F      ANI 7FH
        30D1   CD 13 3A   CALL L3A13
        30D4   DA ED 30   JC L30ED
        30D7   F1         POP PSW
        30D8   D2 DE 30   JNC L30DE
        30DB   CD C3 37   CALL L37C3
        L30DE:
        30DE   E1         POP H
        30DF   D5         PUSH D
        30E0   CD 75 37   CALL L3775
        30E3   D1         POP D
        30E4   69         MOV L,C
        30E5   60         MOV H,B
        30E6   73         MOV M,E
        30E7   23         INX H
        30E8   72         MOV M,D
        30E9   3E 01      MVI A,01H
        30EB   C9         RET
        L30EC:
        30EC   E1         POP H
        L30ED:
        30ED   E1         POP H
        L30EE:
        30EE   E1         POP H
        30EF   E1         POP H
        30F0   E5         PUSH H
        30F1   11 5D 00   LXI D,005DH
        30F4   19         DAD D
        30F5   CD 75 37   CALL L3775
        30F8   60         MOV H,B
        30F9   69         MOV L,C
        30FA   36 00      MVI M,00H
        30FC   23         INX H
        30FD   36 00      MVI M,00H
        30FF   AF         XRA A
        3100   C9         RET
        L3101:
        3101   23         INX H
        3102   4E         MOV C,M
        3103   23         INX H
        3104   23         INX H
        3105   23         INX H
        3106   56         MOV D,M
        3107   23         INX H
        3108   5E         MOV E,M
        3109   23         INX H
        310A   C9         RET

        ;----------------------------------------------------------------------
        ; funk_1E  (310BH)
        ;   Function block 30 (word 30 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_1E:
        310B   E1         POP H
        310C   E5         PUSH H
        310D   F5         PUSH PSW
        310E   23         INX H
        310F   23         INX H
        3110   23         INX H
        3111   22 02 40   SHLD 4002H
        3114   F1         POP PSW
        3115   11 10 00   LXI D,0010H
        3118   19         DAD D
        3119   5E         MOV E,M
        311A   23         INX H
        311B   56         MOV D,M
        311C   EB         XCHG
        311D   46         MOV B,M
        311E   E6 01      ANI 01H
        3120   77         MOV M,A
        3121   C2 3A 31   JNZ L313A
        3124   78         MOV A,B
        3125   E6 01      ANI 01H
        3127   C8         RZ
        3128   2A 02 40   LHLD 4002H
        312B   11 06 00   LXI D,0006H
        312E   19         DAD D
        312F   CD 75 37   CALL L3775
        3132   AF         XRA A
        3133   02         STAX B
        3134   CD 75 37   CALL L3775
        3137   AF         XRA A
        3138   02         STAX B
        3139   C9         RET
        L313A:
        313A   2A 02 40   LHLD 4002H
        313D   CD 75 37   CALL L3775
        3140   EB         XCHG
        3141   22 07 40   SHLD 4007H
        3144   EB         XCHG
        3145   CD 75 37   CALL L3775
        3148   E5         PUSH H
        3149   EB         XCHG
        314A   22 0F 40   SHLD 400FH
        314D   E1         POP H
        314E   CD 75 37   CALL L3775
        3151   E5         PUSH H
        3152   69         MOV L,C
        3153   60         MOV H,B
        3154   22 0B 40   SHLD 400BH
        3157   E1         POP H
        3158   CD 75 37   CALL L3775
        315B   E5         PUSH H
        315C   69         MOV L,C
        315D   60         MOV H,B
        315E   22 0D 40   SHLD 400DH
        3161   E1         POP H
        3162   CD 75 37   CALL L3775
        3165   EB         XCHG
        3166   22 09 40   SHLD 4009H
        3169   C3 83 36   JMP L3683

        ;----------------------------------------------------------------------
        ; funk_1F  (316CH)
        ;   Function block 31 (word 31 of the table at 2800h). Called from
        ;   compiled programs; arguments follow the CALL inline.
        ;----------------------------------------------------------------------
        funk_1F:
        316C   E1         POP H
        316D   E5         PUSH H
        316E   F5         PUSH PSW
        316F   23         INX H
        3170   23         INX H
        3171   23         INX H
        3172   22 02 40   SHLD 4002H
        3175   11 1C 00   LXI D,001CH
        3178   19         DAD D
        3179   5E         MOV E,M
        317A   23         INX H
        317B   56         MOV D,M
        317C   EB         XCHG
        317D   22 04 40   SHLD 4004H
        3180   AF         XRA A
        3181   32 06 40   STA 4006H
        3184   F1         POP PSW
        3185   2A 02 40   LHLD 4002H
        3188   11 19 00   LXI D,0019H
        318B   19         DAD D
        318C   5E         MOV E,M
        318D   23         INX H
        318E   56         MOV D,M
        318F   EB         XCHG
        3190   46         MOV B,M
        3191   E6 01      ANI 01H
        3193   77         MOV M,A
        3194   C2 B3 31   JNZ L31B3
        3197   78         MOV A,B
        3198   E6 01      ANI 01H
        319A   C2 A1 31   JNZ L31A1
        319D   CD 59 37   CALL L3759
        31A0   C9         RET
        L31A1:
        31A1   2A 02 40   LHLD 4002H
        31A4   11 06 00   LXI D,0006H
        31A7   19         DAD D
        31A8   CD 75 37   CALL L3775
        31AB   AF         XRA A
        31AC   02         STAX B
        31AD   CD 75 37   CALL L3775
        31B0   AF         XRA A
        31B1   02         STAX B
        31B2   C9         RET
        L31B3:
        31B3   78         MOV A,B
        31B4   E6 01      ANI 01H
        31B6   C2 D3 31   JNZ L31D3
        31B9   2A 02 40   LHLD 4002H
        31BC   23         INX H
        31BD   23         INX H
        31BE   23         INX H
        31BF   CD 75 37   CALL L3775
        31C2   D5         PUSH D
        31C3   2A 02 40   LHLD 4002H
        31C6   11 15 00   LXI D,0015H
        31C9   19         DAD D
        31CA   CD 75 37   CALL L3775
        31CD   D1         POP D
        31CE   7B         MOV A,E
        31CF   02         STAX B
        31D0   03         INX B
        31D1   7A         MOV A,D
        31D2   02         STAX B
        L31D3:
        31D3   2A 02 40   LHLD 4002H
        31D6   11 13 00   LXI D,0013H
        31D9   19         DAD D
        31DA   5E         MOV E,M
        31DB   23         INX H
        31DC   56         MOV D,M
        31DD   D5         PUSH D
        31DE   2A 04 40   LHLD 4004H
        31E1   11 0A 00   LXI D,000AH
        31E4   19         DAD D
        31E5   4E         MOV C,M
        31E6   06 00      MVI B,00H
        31E8   E1         POP H
        31E9   E5         PUSH H
        31EA   09         DAD B
        31EB   36 00      MVI M,00H
        31ED   D1         POP D
        31EE   E5         PUSH H
        31EF   EB         XCHG
        31F0   7E         MOV A,M
        31F1   E6 01      ANI 01H
        31F3   CA 02 32   JZ L3202
        31F6   3E 00      MVI A,00H
        31F8   23         INX H
        31F9   36 00      MVI M,00H
        L31FB:
        31FB   23         INX H
        31FC   36 00      MVI M,00H
        L31FE:
        31FE   E1         POP H
        31FF   C3 25 32   JMP L3225
        L3202:
        3202   23         INX H
        3203   7E         MOV A,M
        3204   E6 01      ANI 01H
        3206   CA 0E 32   JZ L320E
        3209   3E 01      MVI A,01H
        320B   C3 FB 31   JMP L31FB
        L320E:
        320E   23         INX H
        320F   7E         MOV A,M
        3210   E6 01      ANI 01H
        3212   CA 1A 32   JZ L321A
        3215   3E 02      MVI A,02H
        3217   C3 FE 31   JMP L31FE
        L321A:
        321A   E1         POP H
        321B   36 01      MVI M,01H
        321D   2A 04 40   LHLD 4004H
        3220   11 0A 00   LXI D,000AH
        3223   19         DAD D
        3224   7E         MOV A,M
        L3225:
        3225   2A 04 40   LHLD 4004H
        3228   11 08 00   LXI D,0008H
        322B   19         DAD D
        322C   77         MOV M,A
        322D   B7         ORA A
        322E   C2 55 32   JNZ L3255
        3231   2A 04 40   LHLD 4004H
        3234   11 04 00   LXI D,0004H
        3237   19         DAD D
        3238   EB         XCHG
        3239   2A 00 40   LHLD 4000H
        323C   EB         XCHG
        323D   73         MOV M,E
        323E   23         INX H
        323F   72         MOV M,D
        L3240:
        3240   2A 02 40   LHLD 4002H
        3243   11 16 00   LXI D,0016H
        3246   19         DAD D
        3247   5E         MOV E,M
        3248   23         INX H
        3249   56         MOV D,M
        324A   EB         XCHG
        324B   5E         MOV E,M
        324C   23         INX H
        324D   56         MOV D,M
        324E   EB         XCHG
        324F   22 07 40   SHLD 4007H
        3252   C3 41 36   JMP L3641
        L3255:
        3255   2A 04 40   LHLD 4004H
        3258   11 04 00   LXI D,0004H
        325B   19         DAD D
        325C   E5         PUSH H
        325D   5E         MOV E,M
        325E   23         INX H
        325F   56         MOV D,M
        3260   2A 00 40   LHLD 4000H
        3263   CD BB 37   CALL L37BB
        3266   EB         XCHG
        3267   19         DAD D
        3268   7C         MOV A,H
        3269   17         RAL
        326A   DA 76 32   JC L3276
        326D   7C         MOV A,H
        326E   B5         ORA L
        326F   CA 76 32   JZ L3276
        3272   E1         POP H
        3273   C3 40 32   JMP L3240
        L3276:
        3276   2A 04 40   LHLD 4004H
        3279   11 06 00   LXI D,0006H
        327C   19         DAD D
        327D   5E         MOV E,M
        327E   23         INX H
        327F   56         MOV D,M
        3280   2A 00 40   LHLD 4000H
        3283   19         DAD D
        3284   EB         XCHG
        3285   E1         POP H
        3286   73         MOV M,E
        3287   23         INX H
        3288   72         MOV M,D
        3289   2A 04 40   LHLD 4004H
        328C   11 08 00   LXI D,0008H
        328F   19         DAD D
        3290   46         MOV B,M
        3291   23         INX H
        3292   23         INX H
        3293   4E         MOV C,M
        3294   78         MOV A,B
        3295   B9         CMP C
        3296   CA 2F 34   JZ L342F
        3299   FE 02      CPI 02H
        329B   CA B3 32   JZ L32B3
        329E   2A 02 40   LHLD 4002H
        32A1   CD 75 37   CALL L3775
        32A4   D5         PUSH D
        32A5   11 13 00   LXI D,0013H
        32A8   19         DAD D
        32A9   5E         MOV E,M
        32AA   23         INX H
        32AB   56         MOV D,M
        32AC   EB         XCHG
        32AD   23         INX H
        32AE   23         INX H
        32AF   D1         POP D
        32B0   73         MOV M,E
        32B1   23         INX H
        32B2   72         MOV M,D
        L32B3:
        32B3   2A 04 40   LHLD 4004H
        32B6   11 12 00   LXI D,0012H
        32B9   19         DAD D
        32BA   36 00      MVI M,00H
        32BC   23         INX H
        32BD   36 00      MVI M,00H
        32BF   23         INX H
        32C0   36 00      MVI M,00H
        32C2   2A 02 40   LHLD 4002H
        32C5   11 16 00   LXI D,0016H
        32C8   19         DAD D
        32C9   5E         MOV E,M
        32CA   23         INX H
        32CB   56         MOV D,M
        32CC   EB         XCHG
        32CD   E5         PUSH H
        32CE   E5         PUSH H
        32CF   E5         PUSH H
        32D0   11 0E 00   LXI D,000EH
        32D3   19         DAD D
        32D4   E5         PUSH H
        32D5   5E         MOV E,M
        32D6   23         INX H
        32D7   56         MOV D,M
        32D8   D5         PUSH D
        32D9   2A 04 40   LHLD 4004H
        32DC   11 20 00   LXI D,0020H
        32DF   19         DAD D
        32E0   D1         POP D
        32E1   E5         PUSH H
        32E2   CD 93 39   CALL L3993
        32E5   E1         POP H
        32E6   CD C7 3B   CALL L3BC7
        32E9   E1         POP H
        32EA   11 04 00   LXI D,0004H
        32ED   19         DAD D
        32EE   5E         MOV E,M
        32EF   23         INX H
        32F0   56         MOV D,M
        32F1   EB         XCHG
        32F2   E5         PUSH H
        32F3   29         DAD H
        32F4   29         DAD H
        32F5   D1         POP D
        32F6   19         DAD D
        32F7   7D         MOV A,L
        32F8   B4         ORA H
        32F9   CA 2D 37   JZ L372D
        32FC   E5         PUSH H
        32FD   2A 04 40   LHLD 4004H
        3300   11 06 00   LXI D,0006H
        3303   19         DAD D
        3304   D1         POP D
        3305   73         MOV M,E
        3306   23         INX H
        3307   72         MOV M,D
        3308   E1         POP H
        3309   D5         PUSH D
        330A   11 0A 00   LXI D,000AH
        330D   19         DAD D
        330E   46         MOV B,M
        330F   23         INX H
        3310   23         INX H
        3311   56         MOV D,M
        3312   23         INX H
        3313   5E         MOV E,M
        3314   EB         XCHG
        3315   0E 42      MVI C,42H
        3317   16 40      MVI D,40H
        3319   1E 00      MVI E,00H
        331B   CD 2A 3A   CALL L3A2A
        331E   E1         POP H
        331F   C5         PUSH B
        3320   D5         PUSH D
        3321   EB         XCHG
        3322   CD A7 39   CALL L39A7
        3325   CD 87 38   CALL L3887
        3328   78         MOV A,B
        3329   D1         POP D
        332A   C1         POP B
        332B   47         MOV B,A
        332C   79         MOV A,C
        332D   B7         ORA A
        332E   C2 36 33   JNZ L3336
        3331   0E 00      MVI C,00H
        3333   C3 41 33   JMP L3341
        L3336:
        3336   CD 86 3A   CALL L3A86
        3339   D2 41 33   JNC L3341
        333C   3E 01      MVI A,01H
        333E   32 06 40   STA 4006H
        L3341:
        3341   E1         POP H
        3342   D5         PUSH D
        3343   C5         PUSH B
        3344   11 06 00   LXI D,0006H
        3347   19         DAD D
        3348   C1         POP B
        3349   46         MOV B,M
        334A   23         INX H
        334B   23         INX H
        334C   56         MOV D,M
        334D   23         INX H
        334E   5E         MOV E,M
        334F   EB         XCHG
        3350   D1         POP D
        3351   CD 2A 3A   CALL L3A2A
        3354   D5         PUSH D
        3355   2A 04 40   LHLD 4004H
        3358   11 1C 00   LXI D,001CH
        335B   19         DAD D
        335C   D1         POP D
        335D   CD C7 3B   CALL L3BC7
        3360   E1         POP H
        3361   11 06 00   LXI D,0006H
        3364   19         DAD D
        3365   EB         XCHG
        3366   2A 04 40   LHLD 4004H
        3369   01 0E 00   LXI B,000EH
        336C   09         DAD B
        336D   23         INX H
        336E   23         INX H
        336F   1A         LDAX D
        3370   77         MOV M,A
        3371   13         INX D
        3372   13         INX D
        3373   2B         DCX H
        3374   1A         LDAX D
        3375   77         MOV M,A
        3376   13         INX D
        3377   2B         DCX H
        3378   1A         LDAX D
        3379   77         MOV M,A
        337A   2A 02 40   LHLD 4002H
        337D   11 16 00   LXI D,0016H
        3380   19         DAD D
        3381   5E         MOV E,M
        3382   23         INX H
        3383   56         MOV D,M
        3384   D5         PUSH D
        3385   21 14 00   LXI H,0014H
        3388   19         DAD D
        3389   46         MOV B,M
        338A   23         INX H
        338B   23         INX H
        338C   56         MOV D,M
        338D   23         INX H
        338E   5E         MOV E,M
        338F   EB         XCHG
        3390   D1         POP D
        3391   E5         PUSH H
        3392   C5         PUSH B
        3393   21 12 00   LXI H,0012H
        3396   19         DAD D
        3397   5E         MOV E,M
        3398   23         INX H
        3399   56         MOV D,M
        339A   EB         XCHG
        339B   CD 92 39   CALL L3992
        339E   79         MOV A,C
        339F   C1         POP B
        33A0   4F         MOV C,A
        33A1   E1         POP H
        33A2   CD 86 3A   CALL L3A86
        33A5   D5         PUSH D
        33A6   2A 04 40   LHLD 4004H
        33A9   11 0E 00   LXI D,000EH
        33AC   19         DAD D
        33AD   CD B7 3B   CALL L3BB7
        33B0   D1         POP D
        33B1   CD 2A 3A   CALL L3A2A
        33B4   D5         PUSH D
        33B5   2A 04 40   LHLD 4004H
        33B8   11 16 00   LXI D,0016H
        33BB   19         DAD D
        33BC   D1         POP D
        33BD   CD C7 3B   CALL L3BC7
        33C0   2A 04 40   LHLD 4004H
        33C3   11 08 00   LXI D,0008H
        33C6   19         DAD D
        33C7   7E         MOV A,M
        33C8   FE 02      CPI 02H
        33CA   CA 17 34   JZ L3417
        33CD   2A 02 40   LHLD 4002H
        33D0   11 16 00   LXI D,0016H
        33D3   19         DAD D
        33D4   5E         MOV E,M
        33D5   23         INX H
        33D6   56         MOV D,M
        33D7   EB         XCHG
        33D8   5E         MOV E,M
        33D9   23         INX H
        33DA   56         MOV D,M
        33DB   D5         PUSH D
        33DC   11 0D 00   LXI D,000DH
        33DF   19         DAD D
        33E0   5E         MOV E,M
        33E1   23         INX H
        33E2   56         MOV D,M
        33E3   CD C3 37   CALL L37C3
        33E6   E1         POP H
        33E7   19         DAD D
        33E8   CD 92 39   CALL L3992
        33EB   CD 87 38   CALL L3887
        33EE   E5         PUSH H
        33EF   C5         PUSH B
        33F0   2A 04 40   LHLD 4004H
        33F3   11 1C 00   LXI D,001CH
        33F6   19         DAD D
        33F7   CD C0 3B   CALL L3BC0
        33FA   79         MOV A,C
        33FB   B7         ORA A
        33FC   C1         POP B
        33FD   4F         MOV C,A
        33FE   E1         POP H
        33FF   C2 08 34   JNZ L3408
        3402   0E 40      MVI C,40H
        3404   16 00      MVI D,00H
        3406   1E 00      MVI E,00H
        L3408:
        3408   CD 86 3A   CALL L3A86
        340B   D5         PUSH D
        340C   2A 04 40   LHLD 4004H
        340F   11 12 00   LXI D,0012H
        3412   19         DAD D
        3413   D1         POP D
        3414   CD C7 3B   CALL L3BC7
        L3417:
        3417   11 06 00   LXI D,0006H
        341A   CD 46 37   CALL L3746
        341D   2A 02 40   LHLD 4002H
        3420   CD 75 37   CALL L3775
        3423   D5         PUSH D
        3424   2A 04 40   LHLD 4004H
        3427   11 1A 00   LXI D,001AH
        342A   19         DAD D
        342B   D1         POP D
        342C   73         MOV M,E
        342D   23         INX H
        342E   72         MOV M,D
        L342F:
        342F   2A 04 40   LHLD 4004H
        3432   11 08 00   LXI D,0008H
        3435   19         DAD D
        3436   7E         MOV A,M
        3437   FE 02      CPI 02H
        3439   2A 02 40   LHLD 4002H
        343C   11 16 00   LXI D,0016H
        343F   19         DAD D
        3440   5E         MOV E,M
        3441   23         INX H
        3442   56         MOV D,M
        3443   13         INX D
        3444   13         INX D
        3445   EB         XCHG
        3446   CA 4F 34   JZ L344F
        3449   5E         MOV E,M
        344A   23         INX H
        344B   56         MOV D,M
        344C   C3 54 34   JMP L3454
        L344F:
        344F   23         INX H
        3450   23         INX H
        3451   5E         MOV E,M
        3452   23         INX H
        3453   56         MOV D,M
        L3454:
        3454   D5         PUSH D
        3455   2A 04 40   LHLD 4004H
        3458   11 0C 00   LXI D,000CH
        345B   19         DAD D
        345C   D1         POP D
        345D   73         MOV M,E
        345E   23         INX H
        345F   72         MOV M,D
        3460   3A 06 40   LDA 4006H
        3463   B7         ORA A
        3464   C2 30 37   JNZ L3730
        3467   2A 04 40   LHLD 4004H
        346A   36 00      MVI M,00H
        346C   23         INX H
        346D   36 00      MVI M,00H
        346F   23         INX H
        3470   36 00      MVI M,00H
        3472   2A 04 40   LHLD 4004H
        3475   11 0C 00   LXI D,000CH
        3478   19         DAD D
        3479   5E         MOV E,M
        347A   23         INX H
        347B   56         MOV D,M
        347C   D5         PUSH D
        347D   2A 02 40   LHLD 4002H
        3480   CD 75 37   CALL L3775
        3483   CD C3 37   CALL L37C3
        3486   E1         POP H
        3487   19         DAD D
        3488   CD 92 39   CALL L3992
        348B   79         MOV A,C
        348C   B7         ORA A
        348D   CA F1 34   JZ L34F1
        3490   D5         PUSH D
        3491   2A 04 40   LHLD 4004H
        3494   11 0E 00   LXI D,000EH
        3497   19         DAD D
        3498   CD B7 3B   CALL L3BB7
        349B   D1         POP D
        349C   D5         PUSH D
        349D   C5         PUSH B
        349E   CD 2A 3A   CALL L3A2A
        34A1   2A 04 40   LHLD 4004H
        34A4   CD C7 3B   CALL L3BC7
        34A7   2A 02 40   LHLD 4002H
        34AA   11 19 00   LXI D,0019H
        34AD   19         DAD D
        34AE   5E         MOV E,M
        34AF   23         INX H
        34B0   56         MOV D,M
        34B1   EB         XCHG
        34B2   23         INX H
        34B3   E5         PUSH H
        34B4   7E         MOV A,M
        34B5   0F         RRC
        34B6   6F         MOV L,A
        34B7   79         MOV A,C
        34B8   2F         CMA
        34B9   A5         ANA L
        34BA   07         RLC
        34BB   E1         POP H
        34BC   DA EF 34   JC L34EF
        34BF   23         INX H
        34C0   7E         MOV A,M
        34C1   0F         RRC
        34C2   6F         MOV L,A
        34C3   79         MOV A,C
        34C4   A5         ANA L
        34C5   07         RLC
        34C6   DA EF 34   JC L34EF
        34C9   2A 04 40   LHLD 4004H
        34CC   11 1C 00   LXI D,001CH
        34CF   19         DAD D
        34D0   CD C0 3B   CALL L3BC0
        34D3   79         MOV A,C
        34D4   B7         ORA A
        34D5   CA EF 34   JZ L34EF
        34D8   2A 04 40   LHLD 4004H
        34DB   11 12 00   LXI D,0012H
        34DE   19         DAD D
        34DF   C1         POP B
        34E0   D1         POP D
        34E1   E5         PUSH H
        34E2   CD B7 3B   CALL L3BB7
        34E5   CD 8C 38   CALL L388C
        34E8   E1         POP H
        34E9   CD C7 3B   CALL L3BC7
        34EC   C3 F1 34   JMP L34F1
        L34EF:
        34EF   E1         POP H
        34F0   E1         POP H
        L34F1:
        34F1   2A 04 40   LHLD 4004H
        34F4   11 1C 00   LXI D,001CH
        34F7   19         DAD D
        34F8   CD C0 3B   CALL L3BC0
        34FB   79         MOV A,C
        34FC   B7         ORA A
        34FD   C2 06 35   JNZ L3506
        3500   0E 40      MVI C,40H
        3502   16 00      MVI D,00H
        3504   1E 00      MVI E,00H
        L3506:
        3506   D5         PUSH D
        3507   2A 04 40   LHLD 4004H
        350A   11 12 00   LXI D,0012H
        350D   19         DAD D
        350E   D1         POP D
        350F   CD B7 3B   CALL L3BB7
        3512   CD 2A 3A   CALL L3A2A
        3515   2A 04 40   LHLD 4004H
        3518   CD B7 3B   CALL L3BB7
        351B   CD 8C 38   CALL L388C
        351E   2A 04 40   LHLD 4004H
        3521   CD C7 3B   CALL L3BC7
        3524   2A 04 40   LHLD 4004H
        3527   11 16 00   LXI D,0016H
        352A   19         DAD D
        352B   CD C0 3B   CALL L3BC0
        352E   79         MOV A,C
        352F   B7         ORA A
        3530   CA 7C 35   JZ L357C
        3533   2A 02 40   LHLD 4002H
        3536   CD 75 37   CALL L3775
        3539   D5         PUSH D
        353A   2A 04 40   LHLD 4004H
        353D   11 1A 00   LXI D,001AH
        3540   19         DAD D
        3541   5E         MOV E,M
        3542   23         INX H
        3543   56         MOV D,M
        3544   CD C3 37   CALL L37C3
        3547   E1         POP H
        3548   19         DAD D
        3549   CD 92 39   CALL L3992
        354C   D5         PUSH D
        354D   2A 04 40   LHLD 4004H
        3550   11 16 00   LXI D,0016H
        3553   19         DAD D
        3554   CD B7 3B   CALL L3BB7
        3557   D1         POP D
        3558   CD 2A 3A   CALL L3A2A
        355B   2A 04 40   LHLD 4004H
        355E   CD B7 3B   CALL L3BB7
        3561   CD 7A 38   CALL L387A
        3564   2A 04 40   LHLD 4004H
        3567   CD C7 3B   CALL L3BC7
        356A   2A 02 40   LHLD 4002H
        356D   CD 75 37   CALL L3775
        3570   D5         PUSH D
        3571   2A 04 40   LHLD 4004H
        3574   11 1A 00   LXI D,001AH
        3577   19         DAD D
        3578   D1         POP D
        3579   73         MOV M,E
        357A   23         INX H
        357B   72         MOV M,D
        L357C:
        357C   2A 04 40   LHLD 4004H
        357F   11 20 00   LXI D,0020H
        3582   19         DAD D
        3583   CD C0 3B   CALL L3BC0
        3586   CD 87 38   CALL L3887
        3589   E5         PUSH H
        358A   2A 04 40   LHLD 4004H
        358D   CD C0 3B   CALL L3BC0
        3590   E1         POP H
        3591   CD 8C 38   CALL L388C
        3594   79         MOV A,C
        3595   17         RAL
        3596   F5         PUSH PSW
        3597   1F         RAR
        3598   E6 7F      ANI 7FH
        359A   4F         MOV C,A
        359B   CD 13 3A   CALL L3A13
        359E   DA 36 37   JC L3736
        35A1   F1         POP PSW
        35A2   D2 A8 35   JNC L35A8
        35A5   CD C3 37   CALL L37C3
        L35A8:
        35A8   EB         XCHG
        35A9   E5         PUSH H
        35AA   E5         PUSH H
        35AB   2A 02 40   LHLD 4002H
        35AE   11 0C 00   LXI D,000CH
        35B1   19         DAD D
        35B2   CD 75 37   CALL L3775
        35B5   EB         XCHG
        35B6   D1         POP D
        35B7   D5         PUSH D
        35B8   7A         MOV A,D
        35B9   AC         XRA H
        35BA   17         RAL
        35BB   D2 C6 35   JNC L35C6
        35BE   7C         MOV A,H
        35BF   17         RAL
        35C0   DA F8 35   JC L35F8
        35C3   C3 CF 35   JMP L35CF
        L35C6:
        35C6   CD C3 37   CALL L37C3
        35C9   19         DAD D
        35CA   7C         MOV A,H
        35CB   17         RAL
        35CC   DA F8 35   JC L35F8
        L35CF:
        35CF   2A 02 40   LHLD 4002H
        35D2   11 0F 00   LXI D,000FH
        35D5   19         DAD D
        35D6   CD 75 37   CALL L3775
        35D9   E1         POP H
        35DA   7A         MOV A,D
        35DB   AC         XRA H
        35DC   17         RAL
        35DD   D2 EA 35   JNC L35EA
        35E0   7C         MOV A,H
        35E1   17         RAL
        35E2   DA 0A 36   JC L360A
        35E5   E1         POP H
        35E6   AF         XRA A
        35E7   C3 18 36   JMP L3618
        L35EA:
        35EA   CD C3 37   CALL L37C3
        35ED   19         DAD D
        35EE   7C         MOV A,H
        35EF   17         RAL
        35F0   DA 0A 36   JC L360A
        35F3   E1         POP H
        35F4   AF         XRA A
        35F5   C3 18 36   JMP L3618
        L35F8:
        35F8   E1         POP H
        35F9   E1         POP H
        35FA   2A 02 40   LHLD 4002H
        35FD   11 0C 00   LXI D,000CH
        3600   19         DAD D
        3601   CD 75 37   CALL L3775
        3604   EB         XCHG
        3605   3E 01      MVI A,01H
        3607   C3 18 36   JMP L3618
        L360A:
        360A   E1         POP H
        360B   2A 02 40   LHLD 4002H
        360E   11 0F 00   LXI D,000FH
        3611   19         DAD D
        3612   CD 75 37   CALL L3775
        3615   EB         XCHG
        3616   3E 02      MVI A,02H
        L3618:
        3618   22 07 40   SHLD 4007H
        361B   4D         MOV C,L
        361C   44         MOV B,H
        361D   2A 02 40   LHLD 4002H
        3620   11 16 00   LXI D,0016H
        3623   19         DAD D
        3624   5E         MOV E,M
        3625   23         INX H
        3626   56         MOV D,M
        3627   EB         XCHG
        3628   71         MOV M,C
        3629   23         INX H
        362A   70         MOV M,B
        362B   2A 02 40   LHLD 4002H
        362E   11 19 00   LXI D,0019H
        3631   19         DAD D
        3632   5E         MOV E,M
        3633   23         INX H
        3634   56         MOV D,M
        3635   EB         XCHG
        3636   23         INX H
        3637   4F         MOV C,A
        3638   E6 01      ANI 01H
        363A   77         MOV M,A
        363B   23         INX H
        363C   79         MOV A,C
        363D   1F         RAR
        363E   E6 01      ANI 01H
        3640   77         MOV M,A
        L3641:
        3641   2A 04 40   LHLD 4004H
        3644   11 08 00   LXI D,0008H
        3647   19         DAD D
        3648   7E         MOV A,M
        3649   23         INX H
        364A   23         INX H
        364B   77         MOV M,A
        364C   2A 02 40   LHLD 4002H
        364F   23         INX H
        3650   23         INX H
        3651   23         INX H
        3652   CD 75 37   CALL L3775
        3655   E5         PUSH H
        3656   EB         XCHG
        3657   22 0F 40   SHLD 400FH
        365A   E1         POP H
        365B   CD 75 37   CALL L3775
        365E   E5         PUSH H
        365F   69         MOV L,C
        3660   60         MOV H,B
        3661   22 0B 40   SHLD 400BH
        3664   E1         POP H
        3665   CD 75 37   CALL L3775
        3668   69         MOV L,C
        3669   60         MOV H,B
        366A   22 0D 40   SHLD 400DH
        366D   2A 02 40   LHLD 4002H
        3670   11 16 00   LXI D,0016H
        3673   19         DAD D
        3674   5E         MOV E,M
        3675   23         INX H
        3676   56         MOV D,M
        3677   EB         XCHG
        3678   11 10 00   LXI D,0010H
        367B   19         DAD D
        367C   5E         MOV E,M
        367D   23         INX H
        367E   56         MOV D,M
        367F   EB         XCHG
        3680   22 09 40   SHLD 4009H
        L3683:
        3683   2A 07 40   LHLD 4007H
        3686   7C         MOV A,H
        3687   EB         XCHG
        3688   2A 09 40   LHLD 4009H
        368B   E5         PUSH H
        368C   D5         PUSH D
        368D   19         DAD D
        368E   E6 80      ANI 80H
        3690   C2 9C 36   JNZ L369C
        3693   7C         MOV A,H
        3694   E6 80      ANI 80H
        3696   CA 9C 36   JZ L369C
        3699   21 FF 7F   LXI H,7FFFH
        L369C:
        369C   CD BB 37   CALL L37BB
        369F   EB         XCHG
        36A0   2A 0F 40   LHLD 400FH
        36A3   19         DAD D
        36A4   CD BB 37   CALL L37BB
        36A7   7C         MOV A,H
        36A8   17         RAL
        36A9   E1         POP H
        36AA   D1         POP D
        36AB   3E 01      MVI A,01H
        36AD   DA 11 37   JC L3711
        36B0   CD C3 37   CALL L37C3
        36B3   19         DAD D
        36B4   EB         XCHG
        36B5   CD C3 37   CALL L37C3
        36B8   2A 0F 40   LHLD 400FH
        36BB   19         DAD D
        36BC   7C         MOV A,H
        36BD   17         RAL
        36BE   3E 02      MVI A,02H
        36C0   DA 11 37   JC L3711
        36C3   2A 0B 40   LHLD 400BH
        36C6   7E         MOV A,M
        36C7   B7         ORA A
        36C8   CA EA 36   JZ L36EA
        36CB   2A 0F 40   LHLD 400FH
        36CE   EB         XCHG
        36CF   CD C3 37   CALL L37C3
        36D2   2A 07 40   LHLD 4007H
        36D5   19         DAD D
        36D6   7C         MOV A,H
        36D7   B5         ORA L
        36D8   CA E0 36   JZ L36E0
        36DB   7C         MOV A,H
        36DC   17         RAL
        36DD   D2 2A 37   JNC L372A
        L36E0:
        36E0   2A 0B 40   LHLD 400BH
        36E3   7E         MOV A,M
        36E4   E6 FE      ANI FEH
        36E6   77         MOV M,A
        36E7   C3 2A 37   JMP L372A
        L36EA:
        36EA   2A 0D 40   LHLD 400DH
        36ED   7E         MOV A,M
        36EE   B7         ORA A
        36EF   CA 2A 37   JZ L372A
        36F2   2A 07 40   LHLD 4007H
        36F5   CD BB 37   CALL L37BB
        36F8   EB         XCHG
        36F9   2A 0F 40   LHLD 400FH
        36FC   19         DAD D
        36FD   7C         MOV A,H
        36FE   B5         ORA L
        36FF   CA 07 37   JZ L3707
        3702   7C         MOV A,H
        3703   17         RAL
        3704   D2 2A 37   JNC L372A
        L3707:
        3707   2A 0D 40   LHLD 400DH
        370A   7E         MOV A,M
        370B   E6 FE      ANI FEH
        370D   77         MOV M,A
        370E   C3 2A 37   JMP L372A
        L3711:
        3711   4F         MOV C,A
        3712   2A 0B 40   LHLD 400BH
        3715   1F         RAR
        3716   E6 01      ANI 01H
        3718   47         MOV B,A
        3719   7E         MOV A,M
        371A   E6 FE      ANI FEH
        371C   B0         ORA B
        371D   77         MOV M,A
        371E   2A 0D 40   LHLD 400DH
        3721   79         MOV A,C
        3722   E6 01      ANI 01H
        3724   4F         MOV C,A
        3725   7E         MOV A,M
        3726   E6 FE      ANI FEH
        3728   B1         ORA C
        3729   77         MOV M,A
        L372A:
        372A   3E 01      MVI A,01H
        372C   C9         RET
        L372D:
        372D   E1         POP H
        372E   E1         POP H
        372F   E1         POP H
        L3730:
        3730   CD 59 37   CALL L3759
        3733   C3 A1 31   JMP L31A1
        L3736:
        3736   F1         POP PSW
        3737   DA 40 37   JC L3740
        373A   11 FF 7F   LXI D,7FFFH
        373D   C3 A8 35   JMP L35A8
        L3740:
        3740   11 00 80   LXI D,USER_PROG
        3743   C3 A8 35   JMP L35A8
        L3746:
        3746   2A 04 40   LHLD 4004H
        3749   19         DAD D
        374A   E5         PUSH H
        374B   5E         MOV E,M
        374C   23         INX H
        374D   56         MOV D,M
        374E   2A 00 40   LHLD 4000H
        3751   19         DAD D
        3752   EB         XCHG
        3753   E1         POP H
        3754   2B         DCX H
        3755   72         MOV M,D
        3756   2B         DCX H
        3757   73         MOV M,E
        3758   C9         RET
        L3759:
        3759   2A 04 40   LHLD 4004H
        375C   11 08 00   LXI D,0008H
        375F   19         DAD D
        3760   36 00      MVI M,00H
        3762   2A 02 40   LHLD 4002H
        3765   11 12 00   LXI D,0012H
        3768   19         DAD D
        3769   CD 75 37   CALL L3775
        376C   3E 01      MVI A,01H
        376E   02         STAX B
        376F   03         INX B
        3770   AF         XRA A
        3771   02         STAX B
        3772   03         INX B
        3773   02         STAX B
        3774   C9         RET
        L3775:
        3775   7E         MOV A,M
        3776   FE 09      CPI 09H
        3778   C2 84 37   JNZ L3784
        377B   23         INX H
        377C   5E         MOV E,M
        377D   23         INX H
        377E   56         MOV D,M
        377F   23         INX H
        3780   01 00 00   LXI B,0000H
        3783   C9         RET
        L3784:
        3784   FE 07      CPI 07H
        3786   C2 AD 37   JNZ L37AD
        3789   23         INX H
        378A   5E         MOV E,M
        378B   23         INX H
        378C   56         MOV D,M
        378D   23         INX H
        378E   E5         PUSH H
        378F   EB         XCHG
        3790   23         INX H
        3791   23         INX H
        3792   7E         MOV A,M
        3793   E6 01      ANI 01H
        3795   CA A3 37   JZ L37A3
        3798   2B         DCX H
        3799   56         MOV D,M
        379A   2B         DCX H
        379B   7E         MOV A,M
        379C   E6 FE      ANI FEH
        379E   5F         MOV E,A
        379F   4D         MOV C,L
        37A0   44         MOV B,H
        37A1   E1         POP H
        37A2   C9         RET
        L37A3:
        37A3   4D         MOV C,L
        37A4   44         MOV B,H
        37A5   7E         MOV A,M
        37A6   E6 FE      ANI FEH
        37A8   5F         MOV E,A
        37A9   23         INX H
        37AA   56         MOV D,M
        37AB   E1         POP H
        37AC   C9         RET
        L37AD:
        37AD   23         INX H
        37AE   5E         MOV E,M
        37AF   23         INX H
        37B0   56         MOV D,M
        37B1   23         INX H
        37B2   E5         PUSH H
        37B3   EB         XCHG
        37B4   4D         MOV C,L
        37B5   44         MOV B,H
        37B6   5E         MOV E,M
        37B7   23         INX H
        37B8   56         MOV D,M
        37B9   E1         POP H
        37BA   C9         RET
        L37BB:
        37BB   7C         MOV A,H
        37BC   2F         CMA
        37BD   67         MOV H,A
        37BE   7D         MOV A,L
        37BF   2F         CMA
        37C0   6F         MOV L,A
        37C1   23         INX H
        37C2   C9         RET
        L37C3:
        37C3   7A         MOV A,D
        37C4   2F         CMA
        37C5   57         MOV D,A
        37C6   7B         MOV A,E
        37C7   2F         CMA
        37C8   5F         MOV E,A
        37C9   13         INX D
        37CA   C9         RET
        37CB ? 78         MOV A,B
        37CC ? 2F         CMA
        37CD ? 47         MOV B,A
        37CE ? 79         MOV A,C
        37CF ? 2F         CMA
        37D0 ? 4F         MOV C,A
        37D1 ? 03         INX B
        37D2 ? C9         RET
        37D3 ? 97         SUB A
        37D4 ? B4         ORA H
        37D5 ? 07         RLC
        37D6 ? 3F         CMC
        37D7 ? C0         RNZ
        37D8 ? B5         ORA L
        37D9 ? C8         RZ
        37DA ? 97         SUB A
        37DB ? 3C         INR A
        37DC ? 37         STC
        37DD ? C9         RET
        L37DE:
        37DE   11 00 00   LXI D,0000H
        37E1   79         MOV A,C
        L37E2:
        37E2   48         MOV C,B
        37E3   06 08      MVI B,08H
        L37E5:
        37E5   1F         RAR
        37E6   D2 EC 37   JNC L37EC
        37E9   EB         XCHG
        37EA   19         DAD D
        37EB   EB         XCHG
        L37EC:
        37EC   29         DAD H
        37ED   05         DCR B
        37EE   C2 E5 37   JNZ L37E5
        37F1   79         MOV A,C
        37F2   A7         ANA A
        37F3   C2 E2 37   JNZ L37E2
        37F6   C9         RET
        37F7 ? 44         MOV B,H
        37F8 ? 4D         MOV C,L
        37F9 ? 97         SUB A
        37FA ? BD         CMP L
        37FB ? C2 05 38   JNZ L3805
        37FE ? B4         ORA H
        37FF ? 37         STC
        3800 ? C8         RZ
        3801 ? FE 80      CPI 80H
        3803 ? 37         STC
        3804 ? C8         RZ
        3805 ? 7C         MOV A,H
        3806 ? A7         ANA A
        3807 ? FA 26 38   JM L3826
        380A ? B2         ORA D
        380B ? FA 12 38   JM L3812
        380E ? CD 46 38   CALL L3846
        3811 ? C9         RET
        3812 ? CD C3 37   CALL L37C3
        3815 ? CD 46 38   CALL L3846
        3818 ? CD C3 37   CALL L37C3
        381B ? CD D3 37   CALL L37D3
        381E ? C8         RZ
        381F ? 1B         DCX D
        3820 ? CD BB 37   CALL L37BB
        3823 ? 09         DAD B
        3824 ? A7         ANA A
        3825 ? C9         RET
        3826 ? CD BB 37   CALL L37BB
        3829 ? 7A         MOV A,D
        382A ? A7         ANA A
        382B ? FA 3C 38   JM L383C
        382E ? CD 46 38   CALL L3846
        3831 ? CD C3 37   CALL L37C3
        3834 ? CD D3 37   CALL L37D3
        3837 ? C8         RZ
        3838 ? 1B         DCX D
        3839 ? 09         DAD B
        383A ? A7         ANA A
        383B ? C9         RET
        383C ? CD C3 37   CALL L37C3
        383F ? CD 46 38   CALL L3846
        3842 ? CD BB 37   CALL L37BB
        3845 ? C9         RET
        L3846:
        3846   C5         PUSH B
        3847   97         SUB A
        L3848:
        3848   3C         INR A
        3849   29         DAD H
        384A   D2 48 38   JNC L3848
        384D   4D         MOV C,L
        384E   44         MOV B,H
        384F   21 00 00   LXI H,0000H
        L3852:
        3852   F5         PUSH PSW
        3853   78         MOV A,B
        3854   1F         RAR
        3855   47         MOV B,A
        3856   79         MOV A,C
        3857   1F         RAR
        3858   4F         MOV C,A
        3859   29         DAD H
        385A   7B         MOV A,E
        385B   91         SUB C
        385C   5F         MOV E,A
        385D   7A         MOV A,D
        385E   98         SBB B
        385F   57         MOV D,A
        3860   D2 69 38   JNC L3869
        3863   EB         XCHG
        3864   09         DAD B
        3865   EB         XCHG
        3866   C3 6A 38   JMP L386A
        L3869:
        3869   23         INX H
        L386A:
        386A   F1         POP PSW
        386B   D6 01      SUI 01H
        386D   C2 52 38   JNZ L3852
        3870   C1         POP B
        3871   EB         XCHG
        3872   C9         RET
        3873 ? 79         MOV A,C
        3874 ? A7         ANA A
        3875 ? F2 AC 38   JP L38AC
        3878 ? 06 00      MVI B,00H
        L387A:
        387A   CD 87 38   CALL L3887
        L387D:
        387D   78         MOV A,B
        387E   A7         ANA A
        387F   C8         RZ
        3880   EE 80      XRI 80H
        3882   47         MOV B,A
        3883   97         SUB A
        3884   C3 8F 38   JMP L388F
        L3887:
        3887   78         MOV A,B
        3888   41         MOV B,C
        3889   4F         MOV C,A
        388A   EB         XCHG
        388B   C9         RET
        L388C:
        388C   97         SUB A
        388D   B8         CMP B
        388E   C8         RZ
        L388F:
        388F   B9         CMP C
        3890   CA 87 38   JZ L3887
        3893   78         MOV A,B
        3894   A9         XRA C
        3895   E6 80      ANI 80H
        3897   81         ADD C
        3898   90         SUB B
        3899   CA 72 39   JZ L3972
        389C   FC 87 38   CM L3887
        389F   79         MOV A,C
        38A0   90         SUB B
        38A1   41         MOV B,C
        38A2   C5         PUSH B
        38A3   47         MOV B,A
        38A4   E6 7F      ANI 7FH
        38A6   FE 13      CPI 13H
        38A8   DA B1 38   JC L38B1
        38AB   C1         POP B
        38AC   79         MOV A,C
        L38AD:
        38AD   4F         MOV C,A
        38AE   97         SUB A
        38AF   47         MOV B,A
        38B0   C9         RET
        L38B1:
        38B1   E6 07      ANI 07H
        38B3   0E 01      MVI C,01H
        38B5   CA C4 38   JZ L38C4
        38B8   D6 08      SUI 08H
        38BA   4F         MOV C,A
        38BB   3E 01      MVI A,01H
        L38BD:
        38BD   29         DAD H
        38BE   8F         ADC A
        38BF   0C         INR C
        38C0   C2 BD 38   JNZ L38BD
        38C3   4F         MOV C,A
        L38C4:
        38C4   78         MOV A,B
        38C5   87         ADD A
        38C6   FE 22      CPI 22H
        38C8   FA D1 38   JM L38D1
        38CB   7D         MOV A,L
        38CC   B4         ORA H
        38CD   6F         MOV L,A
        38CE   61         MOV H,C
        38CF   0E 00      MVI C,00H
        L38D1:
        38D1   78         MOV A,B
        38D2   06 00      MVI B,00H
        38D4   87         ADD A
        38D5   DA 52 39   JC L3952
        38D8   C8         RZ
        38D9   FE 12      CPI 12H
        38DB   7B         MOV A,E
        38DC   F2 E4 38   JP L38E4
        38DF   84         ADD H
        38E0   65         MOV H,L
        38E1   C3 E6 38   JMP L38E6
        L38E4:
        38E4   81         ADD C
        38E5   48         MOV C,B
        L38E6:
        38E6   5F         MOV E,A
        38E7   7A         MOV A,D
        38E8   89         ADC C
        38E9   57         MOV D,A
        38EA   78         MOV A,B
        L38EB:
        38EB   88         ADC B
        38EC   CA 22 39   JZ L3922
        38EF   21 01 00   LXI H,0001H
        38F2   4D         MOV C,L
        38F3   19         DAD D
        38F4   89         ADC C
        38F5   1F         RAR
        38F6   7C         MOV A,H
        38F7   1F         RAR
        38F8   57         MOV D,A
        38F9   7D         MOV A,L
        38FA   1F         RAR
        38FB   5F         MOV E,A
        38FC   79         MOV A,C
        38FD   C3 2C 39   JMP L392C
        L3900:
        3900   D2 21 39   JNC L3921
        L3903:
        3903   7A         MOV A,D
        3904   B8         CMP B
        L3905:
        3905   C2 16 39   JNZ L3916
        3908   7B         MOV A,E
        3909   B4         ORA H
        390A   7B         MOV A,E
        390B   68         MOV L,B
        390C   06 F8      MVI B,F8H
        390E   C2 18 39   JNZ L3918
        3911   C1         POP B
        3912   01 00 EE   LXI B,EE00H
        3915   C9         RET
        L3916:
        3916   6C         MOV L,H
        3917   63         MOV H,E
        L3918:
        3918   29         DAD H
        3919   8F         ADC A
        391A   05         DCR B
        391B   D2 18 39   JNC L3918
        391E   57         MOV D,A
        391F   5C         MOV E,H
        3920   65         MOV H,L
        L3921:
        3921   97         SUB A
        L3922:
        3922   29         DAD H
        3923   D2 2B 39   JNC L392B
        3926   21 01 00   LXI H,0001H
        3929   19         DAD D
        L392A:
        392A   EB         XCHG
        L392B:
        392B   88         ADC B
        L392C:
        392C   C1         POP B
        392D   68         MOV L,B
        392E   47         MOV B,A
        392F   81         ADD C
        3930   4F         MOV C,A
        3931   87         ADD A
        3932   CA 38 39   JZ L3938
        3935   1F         RAR
        3936   AD         XRA L
        3937   F0         RP
        L3938:
        3938   7D         MOV A,L
        3939   87         ADD A
        393A   FA 4A 39   JM L394A
        393D   61         MOV H,C
        393E   97         SUB A
        393F   4F         MOV C,A
        3940   D6 FD      SUI FDH
        3942   C9         RET
        L3943:
        3943   81         ADD C
        3944   17         RAL
        3945   C2 4B 39   JNZ L394B
        3948   37         STC
        3949   C9         RET
        L394A:
        394A   61         MOV H,C
        L394B:
        394B   3E FF      MVI A,FFH
        394D   1F         RAR
        394E   4F         MOV C,A
        394F   3E 04      MVI A,04H
        3951   C9         RET
        L3952:
        3952   C6 EE      ADI EEH
        3954   D2 5C 39   JNC L395C
        3957   78         MOV A,B
        3958   95         SUB L
        3959   6C         MOV L,H
        395A   61         MOV H,C
        395B   48         MOV C,B
        L395C:
        395C   78         MOV A,B
        395D   9D         SBB L
        395E   6F         MOV L,A
        395F   7B         MOV A,E
        3960   9C         SBB H
        3961   5F         MOV E,A
        3962   7A         MOV A,D
        3963   99         SBB C
        3964   57         MOV D,A
        3965   65         MOV H,L
        3966   C3 00 39   JMP L3900
        L3969:
        3969   2B         DCX H
        396A   1B         DCX D
        L396B:
        396B   C1         POP B
        396C   EB         XCHG
        396D   41         MOV B,C
        396E   79         MOV A,C
        396F   EE 80      XRI 80H
        3971   4F         MOV C,A
        L3972:
        3972   79         MOV A,C
        3973   A8         XRA B
        3974   17         RAL
        3975   41         MOV B,C
        3976   C5         PUSH B
        3977   47         MOV B,A
        3978   DA 81 39   JC L3981
        397B   19         DAD D
        397C   EB         XCHG
        397D   3C         INR A
        397E   C3 EB 38   JMP L38EB
        L3981:
        3981   7B         MOV A,E
        3982   95         SUB L
        3983   4F         MOV C,A
        3984   7A         MOV A,D
        3985   9C         SBB H
        3986   DA 6B 39   JC L396B
        3989   59         MOV E,C
        398A   60         MOV H,B
        398B   C3 05 39   JMP L3905
        398E ? 6F         MOV L,A
        398F ? 17         RAL
        3990 ? 9F         SBB A
        3991 ? 67         MOV H,A
        L3992:
        3992   EB         XCHG
        L3993:
        3993   7A         MOV A,D
        3994   17         RAL
        L3995:
        3995   21 00 00   LXI H,0000H
        3998   0E 50      MVI C,50H
        399A   41         MOV B,C
        399B   C5         PUSH B
        399C   44         MOV B,H
        399D   DA 69 39   JC L3969
        39A0   C3 03 39   JMP L3903
        39A3 ? 6F         MOV L,A
        39A4 ? 26 00      MVI H,00H
        39A6 ? EB         XCHG
        L39A7:
        39A7   97         SUB A
        39A8   C3 95 39   JMP L3995
        39AB ? 63         MOV H,E
        39AC ? 5A         MOV E,D
        39AD ? 57         MOV D,A
        39AE ? 0E 58      MVI C,58H
        39B0 ? 41         MOV B,C
        39B1 ? C5         PUSH B
        39B2 ? 06 00      MVI B,00H
        39B4 ? C3 03 39   JMP L3903
        39B7 ? CD 87 38   CALL L3887
        L39BA:
        39BA   79         MOV A,C
        39BB   87         ADD A
        39BC   C6 52      ADI 52H
        39BE   D2 CC 39   JNC L39CC
        39C1   06 01      MVI B,01H
        39C3   B2         ORA D
        39C4   B3         ORA E
        39C5   90         SUB B
        39C6   78         MOV A,B
        39C7   1F         RAR
        39C8   A1         ANA C
        39C9   B8         CMP B
        39CA   05         DCR B
        39CB   C9         RET
        L39CC:
        39CC   2F         CMA
        39CD   1F         RAR
        39CE   D6 06      SUI 06H
        39D0   EB         XCHG
        39D1   11 00 00   LXI D,0000H
        39D4   DA E2 39   JC L39E2
        39D7   FE 11      CPI 11H
        39D9   DA E2 39   JC L39E2
        39DC   7A         MOV A,D
        39DD   42         MOV B,D
        39DE   62         MOV H,D
        39DF   C0         RNZ
        39E0   3E 10      MVI A,10H
        L39E2:
        39E2   59         MOV E,C
        39E3   42         MOV B,D
        39E4   57         MOV D,A
        39E5   CD B1 38   CALL L38B1
        39E8   7A         MOV A,D
        39E9   51         MOV D,C
        39EA   3D         DCR A
        39EB   FA 01 3A   JM L3A01
        39EE   FE 08      CPI 08H
        39F0   7D         MOV A,L
        39F1   6C         MOV L,H
        39F2   62         MOV H,D
        39F3   FA F9 39   JM L39F9
        39F6   7D         MOV A,L
        39F7   6C         MOV L,H
        39F8   60         MOV H,B
        L39F9:
        39F9   17         RAL
        39FA   78         MOV A,B
        39FB   17         RAL
        39FC   4F         MOV C,A
        39FD   09         DAD B
        39FE   78         MOV A,B
        39FF   17         RAL
        3A00   57         MOV D,A
        L3A01:
        3A01   EB         XCHG
        3A02   7C         MOV A,H
        3A03   2C         INR L
        3A04   2D         DCR L
        3A05   F0         RP
        3A06   78         MOV A,B
        3A07   93         SUB E
        3A08   5F         MOV E,A
        3A09   78         MOV A,B
        3A0A   9A         SBB D
        3A0B   57         MOV D,A
        3A0C   78         MOV A,B
        3A0D   9C         SBB H
        3A0E   A7         ANA A
        3A0F   C9         RET
        3A10 ? CD 87 38   CALL L3887
        L3A13:
        3A13   CD BA 39   CALL L39BA
        3A16   D8         RC
        3A17   7A         MOV A,D
        3A18   17         RAL
        3A19   7C         MOV A,H
        3A1A   88         ADC B
        3A1B   A7         ANA A
        3A1C   C8         RZ
        3A1D   97         SUB A
        3A1E   D6 FB      SUI FBH
        3A20   C9         RET
        3A21 ? 21 00 00   LXI H,0000H
        3A24 ? C3 2A 3A   JMP L3A2A
        3A27 ? 41         MOV B,C
        3A28 ? 62         MOV H,D
        3A29 ? 6B         MOV L,E
        L3A2A:
        3A2A   78         MOV A,B
        3A2B   C6 FF      ADI FFH
        3A2D   9F         SBB A
        3A2E   A1         ANA C
        3A2F   CA AD 38   JZ L38AD
        3A32   E5         PUSH H
        3A33   80         ADD B
        3A34   D6 40      SUI 40H
        3A36   6F         MOV L,A
        3A37   79         MOV A,C
        3A38   E6 80      ANI 80H
        3A3A   A8         XRA B
        3A3B   67         MOV H,A
        3A3C   E3         XTHL
        3A3D   06 00      MVI B,00H
        3A3F   7C         MOV A,H
        3A40   B5         ORA L
        3A41   CA EB 38   JZ L38EB
        3A44   E5         PUSH H
        3A45   4C         MOV C,H
        3A46   7D         MOV A,L
        3A47   60         MOV H,B
        3A48   68         MOV L,B
        3A49   B8         CMP B
        3A4A   C4 63 3A   CNZ L3A63
        3A4D   6F         MOV L,A
        3A4E   79         MOV A,C
        3A4F   4C         MOV C,H
        3A50   60         MOV H,B
        3A51   CD 63 3A   CALL L3A63
        3A54   09         DAD B
        3A55   88         ADC B
        3A56   4D         MOV C,L
        3A57   6C         MOV L,H
        3A58   67         MOV H,A
        3A59   19         DAD D
        3A5A   78         MOV A,B
        3A5B   88         ADC B
        3A5C   D1         POP D
        3A5D   19         DAD D
        3A5E   EB         XCHG
        3A5F   61         MOV H,C
        3A60   C3 EB 38   JMP L38EB
        L3A63:
        3A63   CD 66 3A   CALL L3A66
        L3A66:
        3A66   29         DAD H
        3A67   8F         ADC A
        3A68   D2 6D 3A   JNC L3A6D
        3A6B   19         DAD D
        3A6C   88         ADC B
        L3A6D:
        3A6D   29         DAD H
        3A6E   8F         ADC A
        3A6F   D2 74 3A   JNC L3A74
        3A72   19         DAD D
        3A73   88         ADC B
        L3A74:
        3A74   29         DAD H
        3A75   8F         ADC A
        3A76   D2 7B 3A   JNC L3A7B
        3A79   19         DAD D
        3A7A   88         ADC B
        L3A7B:
        3A7B   29         DAD H
        3A7C   8F         ADC A
        3A7D   D0         RNC
        3A7E   19         DAD D
        3A7F   88         ADC B
        3A80   C9         RET
        3A81 ? 21 00 00   LXI H,0000H
        3A84 ? 06 40      MVI B,40H
        L3A86:
        3A86   CD 87 38   CALL L3887
        L3A89:
        3A89   97         SUB A
        3A8A   B8         CMP B
        3A8B   CA 43 39   JZ L3943
        3A8E   B9         CMP C
        3A8F   CA AD 38   JZ L38AD
        3A92   E5         PUSH H
        3A93   79         MOV A,C
        3A94   90         SUB B
        3A95   C6 40      ADI 40H
        3A97   6F         MOV L,A
        3A98   79         MOV A,C
        3A99   F6 7F      ORI 7FH
        3A9B   A8         XRA B
        3A9C   67         MOV H,A
        3A9D   E3         XTHL
        3A9E   EB         XCHG
        3A9F   97         SUB A
        3AA0   93         SUB E
        3AA1   4F         MOV C,A
        3AA2   3E 00      MVI A,00H
        3AA4   9A         SBB D
        3AA5   47         MOV B,A
        3AA6   D2 2A 39   JNC L392A
        3AA9   3E 01      MVI A,01H
        3AAB   CD D2 3A   CALL L3AD2
        3AAE   F5         PUSH PSW
        3AAF   3E 01      MVI A,01H
        3AB1   CD CB 3A   CALL L3ACB
        3AB4   F5         PUSH PSW
        3AB5   3E 20      MVI A,20H
        3AB7   CD C5 3A   CALL L3AC5
        3ABA   0F         RRC
        3ABB   0F         RRC
        3ABC   0F         RRC
        3ABD   E1         POP H
        3ABE   6F         MOV L,A
        3ABF   F1         POP PSW
        3AC0   06 01      MVI B,01H
        3AC2   C3 18 39   JMP L3918
        L3AC5:
        3AC5   DA D7 3A   JC L3AD7
        3AC8   C3 ED 3A   JMP L3AED
        L3ACB:
        3ACB   D2 E4 3A   JNC L3AE4
        L3ACE:
        3ACE   29         DAD H
        3ACF   D2 D6 3A   JNC L3AD6
        L3AD2:
        3AD2   09         DAD B
        3AD3   D2 EC 3A   JNC L3AEC
        L3AD6:
        3AD6   17         RAL
        L3AD7:
        3AD7   29         DAD H
        3AD8   D2 DF 3A   JNC L3ADF
        3ADB   09         DAD B
        3ADC   D2 F5 3A   JNC L3AF5
        L3ADF:
        3ADF   17         RAL
        3AE0   D2 CE 3A   JNC L3ACE
        3AE3   C9         RET
        L3AE4:
        3AE4   29         DAD H
        3AE5   DA EC 3A   JC L3AEC
        3AE8   19         DAD D
        3AE9   DA D6 3A   JC L3AD6
        L3AEC:
        3AEC   17         RAL
        L3AED:
        3AED   29         DAD H
        3AEE   DA F5 3A   JC L3AF5
        3AF1   19         DAD D
        3AF2   DA DF 3A   JC L3ADF
        L3AF5:
        3AF5   17         RAL
        3AF6   D2 E4 3A   JNC L3AE4
        3AF9   3F         CMC
        3AFA   C9         RET
        3AFB ? 79         MOV A,C
        3AFC ? A8         XRA B
        3AFD ? 79         MOV A,C
        3AFE ? FA 11 3B   JM L3B11
        3B01 ? 90         SUB B
        3B02 ? C2 10 3B   JNZ L3B10
        3B05 ? 81         ADD C
        3B06 ? C8         RZ
        3B07 ? 7A         MOV A,D
        3B08 ? 94         SUB H
        3B09 ? C2 0F 3B   JNZ L3B0F
        3B0C ? 7B         MOV A,E
        3B0D ? 95         SUB L
        3B0E ? C8         RZ
        3B0F ? 1F         RAR
        3B10 ? A9         XRA C
        3B11 ? F6 01      ORI 01H
        3B13 ? C9         RET
        3B14 ? 97         SUB A
        3B15 ? 47         MOV B,A
        3B16 ? 81         ADD C
        3B17 ? C8         RZ
        3B18 ? 50         MOV D,B
        3B19 ? 58         MOV E,B
        3B1A ? E6 80      ANI 80H
        3B1C ? C6 40      ADI 40H
        3B1E ? 4F         MOV C,A
        3B1F ? C9         RET
        3B20 ? 97         SUB A
        3B21 ? 47         MOV B,A
        3B22 ? 81         ADD C
        3B23 ? C3 18 3B   JMP L3B18
        3B26 ? 0E 40      MVI C,40H
        3B28 ? 11 00 00   LXI D,0000H
        3B2B ? 78         MOV A,B
        3B2C ? A7         ANA A
        3B2D ? 21 2A 3A   LXI H,3A2AH
        3B30 ? F2 38 3B   JP L3B38
        3B33 ? 21 89 3A   LXI H,3A89H
        3B36 ? 2F         CMA
        3B37 ? 3C         INR A
        3B38 ? C3 45 3B   JMP L3B45
        3B3B ? D2 43 3B   JNC L3B43
        3B3E ? 33         INX SP
        3B3F ? 33         INX SP
        3B40 ? 33         INX SP
        3B41 ? 33         INX SP
        3B42 ? C9         RET
        3B43 ? E1         POP H
        3B44 ? F1         POP PSW
        3B45 ? 47         MOV B,A
        3B46 ? A7         ANA A
        3B47 ? C8         RZ
        3B48 ? FE 08      CPI 08H
        3B4A ? FA 4F 3B   JM L3B4F
        3B4D ? 06 07      MVI B,07H
        3B4F ? 90         SUB B
        3B50 ? F5         PUSH PSW
        3B51 ? E5         PUSH H
        3B52 ? E5         PUSH H
        3B53 ? 21 3B 3B   LXI H,3B3BH
        3B56 ? E3         XTHL
        3B57 ? E5         PUSH H
        3B58 ? 79         MOV A,C
        3B59 ? 48         MOV C,B
        3B5A ? 06 00      MVI B,00H
        3B5C ? 21 6C 3B   LXI H,3B6CH
        3B5F ? 09         DAD B
        3B60 ? 09         DAD B
        3B61 ? 09         DAD B
        3B62 ? 4F         MOV C,A
        3B63 ? 46         MOV B,M
        3B64 ? 2B         DCX H
        3B65 ? 7E         MOV A,M
        3B66 ? 2B         DCX H
        3B67 ? 6E         MOV L,M
        3B68 ? 67         MOV H,A
        3B69 ? C9         RET
        3B6A ? 00         NOP
        3B6B ? 00         NOP
        3B6C ? 40         MOV B,B
        3B6D ? 00         NOP
        3B6E ? 40         MOV B,B
        3B6F ? 43         MOV B,E
        3B70 ? 00         NOP
        3B71 ? 90         SUB B
        3B72 ? 46         MOV B,M
        3B73 ? 00         NOP
        3B74 ? F4 49 80   CP 8049H
        3B77 ? 38         DB 38H ; undocumented
        3B78 ? 4D         MOV C,L
        3B79 ? A0         ANA B
        3B7A ? 86         ADD M
        3B7B ? 50         MOV D,B
        3B7C ? 48         MOV C,B
        3B7D ? E8         RPE
        3B7E ? 53         MOV D,E
        3B7F ? 2D         DCR L
        3B80 ? 31 57 41   LXI SP,4157H
        3B83   97         SUB A
        3B84   4F         MOV C,A
        3B85   B8         CMP B
        3B86   C8         RZ
        3B87   F0         RP
        3B88   D5         PUSH D
        3B89   C5         PUSH B
        3B8A   48         MOV C,B
        3B8B   6F         MOV L,A
        3B8C   78         MOV A,B
        3B8D   C6 40      ADI 40H
        3B8F   1F         RAR
        3B90   47         MOV B,A
        3B91   7A         MOV A,D
        3B92   1F         RAR
        3B93   D6 09      SUI 09H
        3B95   D2 99 3B   JNC L3B99
        3B98   97         SUB A
        L3B99:
        3B99   67         MOV H,A
        3B9A   E5         PUSH H
        3B9B   C5         PUSH B
        3B9C   CD 89 3A   CALL L3A89
        3B9F   F1         POP PSW
        3BA0   47         MOV B,A
        3BA1   E1         POP H
        3BA2   CD 8C 38   CALL L388C
        3BA5   0D         DCR C
        3BA6   F1         POP PSW
        3BA7   E1         POP H
        3BA8   41         MOV B,C
        3BA9   C5         PUSH B
        3BAA   D5         PUSH D
        3BAB   47         MOV B,A
        3BAC   CD 86 3A   CALL L3A86
        3BAF   E1         POP H
        3BB0   F1         POP PSW
        3BB1   47         MOV B,A
        3BB2   CD 8C 38   CALL L388C
        3BB5   0D         DCR C
        3BB6   C9         RET
        L3BB7:
        3BB7   23         INX H
        3BB8   23         INX H
        3BB9   46         MOV B,M
        3BBA   2B         DCX H
        3BBB   7E         MOV A,M
        3BBC   2B         DCX H
        3BBD   6E         MOV L,M
        3BBE   67         MOV H,A
        3BBF   C9         RET
        L3BC0:
        3BC0   5E         MOV E,M
        3BC1   23         INX H
        3BC2   56         MOV D,M
        3BC3   23         INX H
        3BC4   4E         MOV C,M
        3BC5   23         INX H
        3BC6   C9         RET
        L3BC7:
        3BC7   73         MOV M,E
        3BC8   23         INX H
        3BC9   72         MOV M,D
        3BCA   23         INX H
        3BCB   71         MOV M,C
        3BCC   23         INX H
        3BCD   C9         RET
        3BCE ? 63         MOV H,E
        3BCF ? 63         MOV H,E
        3BD0 ? 63         MOV H,E
        3BD1 ? 63         MOV H,E
        3BD2 ? 63         MOV H,E
        3BD3 ? 63         MOV H,E
        3BD4 ? 63         MOV H,E
        3BD5 ? 63         MOV H,E
        3BD6 ? 63         MOV H,E
        3BD7 ? 63         MOV H,E
        3BD8 ? 63         MOV H,E
        3BD9 ? 63         MOV H,E
        3BDA ? 63         MOV H,E
        3BDB ? 63         MOV H,E
        3BDC ? 63         MOV H,E
        3BDD ? 63         MOV H,E
        3BDE ? 63         MOV H,E
        3BDF ? 63         MOV H,E
        3BE0 ? 63         MOV H,E
        3BE1 ? 63         MOV H,E
        3BE2 ? 63         MOV H,E
        3BE3 ? 63         MOV H,E
        3BE4 ? 63         MOV H,E
        3BE5 ? 63         MOV H,E
        3BE6 ? 63         MOV H,E
        3BE7 ? 63         MOV H,E
        3BE8 ? 63         MOV H,E
        3BE9 ? 63         MOV H,E
        3BEA ? 63         MOV H,E
        3BEB ? 63         MOV H,E
        3BEC ? 63         MOV H,E
        3BED ? 63         MOV H,E
        3BEE ? 63         MOV H,E
        3BEF ? 63         MOV H,E
        3BF0 ? 63         MOV H,E
        3BF1 ? 63         MOV H,E
        3BF2 ? 63         MOV H,E
        3BF3 ? 63         MOV H,E
        3BF4 ? 63         MOV H,E
        3BF5 ? 63         MOV H,E
        3BF6 ? 63         MOV H,E
        3BF7 ? 63         MOV H,E
        3BF8 ? 63         MOV H,E
        3BF9 ? 63         MOV H,E
        3BFA ? 63         MOV H,E
        3BFB ? 63         MOV H,E
        3BFC ? 63         MOV H,E
        3BFD ? 63         MOV H,E
        3BFE ? 63         MOV H,E
        3BFF ? 63         MOV H,E
        3C00 ? 63         MOV H,E
        3C01 ? 63         MOV H,E
        3C02 ? 63         MOV H,E
        3C03 ? 63         MOV H,E
        3C04 ? 63         MOV H,E
        3C05 ? 63         MOV H,E
        3C06 ? 63         MOV H,E
        3C07 ? 63         MOV H,E
        3C08 ? 63         MOV H,E
        3C09 ? 63         MOV H,E
        3C0A ? 63         MOV H,E
        3C0B ? 63         MOV H,E
        3C0C ? 63         MOV H,E
        3C0D ? 63         MOV H,E
        3C0E ? 63         MOV H,E
        3C0F ? 63         MOV H,E
        3C10 ? 63         MOV H,E
        3C11 ? 63         MOV H,E
        3C12 ? 63         MOV H,E
        3C13 ? 63         MOV H,E
        3C14 ? 63         MOV H,E
        3C15 ? 63         MOV H,E
        3C16 ? 63         MOV H,E
        3C17 ? 63         MOV H,E
        3C18 ? 63         MOV H,E
        3C19 ? 63         MOV H,E
        3C1A ? 63         MOV H,E
        3C1B ? 63         MOV H,E
        3C1C ? 63         MOV H,E
        3C1D ? 63         MOV H,E
        3C1E ? 63         MOV H,E
        3C1F ? 63         MOV H,E
        3C20 ? 63         MOV H,E
        3C21 ? 63         MOV H,E
        3C22 ? 63         MOV H,E
        3C23 ? 63         MOV H,E
        3C24 ? 63         MOV H,E
        3C25 ? 63         MOV H,E
        3C26 ? 63         MOV H,E
        3C27 ? 63         MOV H,E
        3C28 ? 63         MOV H,E
        3C29 ? 63         MOV H,E
        3C2A ? 63         MOV H,E
        3C2B ? 63         MOV H,E
        3C2C ? 63         MOV H,E
        3C2D ? 63         MOV H,E
        3C2E ? 63         MOV H,E
        3C2F ? 63         MOV H,E
        3C30 ? 63         MOV H,E
        3C31 ? 63         MOV H,E
        3C32 ? 63         MOV H,E
        3C33 ? 63         MOV H,E
        3C34 ? 63         MOV H,E
        3C35 ? 63         MOV H,E
        3C36 ? 63         MOV H,E
        3C37 ? 63         MOV H,E
        3C38 ? 63         MOV H,E
        3C39 ? 63         MOV H,E
        3C3A ? 63         MOV H,E
        3C3B ? 63         MOV H,E
        3C3C ? 63         MOV H,E
        3C3D ? 63         MOV H,E
        3C3E ? 63         MOV H,E
        3C3F ? 63         MOV H,E
        3C40 ? 63         MOV H,E
        3C41 ? 63         MOV H,E
        3C42 ? 63         MOV H,E
        3C43 ? 63         MOV H,E
        3C44 ? 63         MOV H,E
        3C45 ? 63         MOV H,E
        3C46 ? 63         MOV H,E
        3C47 ? 63         MOV H,E
        3C48 ? 63         MOV H,E
        3C49 ? 63         MOV H,E
        3C4A ? 63         MOV H,E
        3C4B ? 63         MOV H,E
        3C4C ? 63         MOV H,E
        3C4D ? 63         MOV H,E
        3C4E ? 63         MOV H,E
        3C4F ? 63         MOV H,E
        3C50 ? 63         MOV H,E
        3C51 ? 63         MOV H,E
        3C52 ? 63         MOV H,E
        3C53 ? 63         MOV H,E
        3C54 ? 63         MOV H,E
        3C55 ? 63         MOV H,E
        3C56 ? 63         MOV H,E
        3C57 ? 63         MOV H,E
        3C58 ? 63         MOV H,E
        3C59 ? 63         MOV H,E
        3C5A ? 63         MOV H,E
        3C5B ? 63         MOV H,E
        3C5C ? 63         MOV H,E
        3C5D ? 63         MOV H,E
        3C5E ? 63         MOV H,E
        3C5F ? 63         MOV H,E
        3C60 ? 63         MOV H,E
        3C61 ? 63         MOV H,E
        3C62 ? 63         MOV H,E
        3C63 ? 63         MOV H,E
        3C64 ? 63         MOV H,E
        3C65 ? 63         MOV H,E
        3C66 ? 63         MOV H,E
        3C67 ? 63         MOV H,E
        3C68 ? 63         MOV H,E
        3C69 ? 63         MOV H,E
        3C6A ? 63         MOV H,E
        3C6B ? 63         MOV H,E
        3C6C ? 63         MOV H,E
        3C6D ? 63         MOV H,E
        3C6E ? 63         MOV H,E
        3C6F ? 63         MOV H,E
        3C70 ? 63         MOV H,E
        3C71 ? 63         MOV H,E
        3C72 ? 63         MOV H,E
        3C73 ? 63         MOV H,E
        3C74 ? 63         MOV H,E
        3C75 ? 63         MOV H,E
        3C76 ? 63         MOV H,E
        3C77 ? 63         MOV H,E
        3C78 ? 63         MOV H,E
        3C79 ? 63         MOV H,E
        3C7A ? 63         MOV H,E
        3C7B ? 63         MOV H,E
        3C7C ? 63         MOV H,E
        3C7D ? 63         MOV H,E
        3C7E ? 63         MOV H,E
        3C7F ? 63         MOV H,E
        3C80 ? 63         MOV H,E
        3C81 ? 63         MOV H,E
        3C82 ? 63         MOV H,E
        3C83 ? 63         MOV H,E
        3C84 ? 63         MOV H,E
        3C85 ? 63         MOV H,E
        3C86 ? 63         MOV H,E
        3C87 ? 63         MOV H,E
        3C88 ? 63         MOV H,E
        3C89 ? 63         MOV H,E
        3C8A ? 63         MOV H,E
        3C8B ? 63         MOV H,E
        3C8C ? 63         MOV H,E
        3C8D ? 63         MOV H,E
        3C8E ? 63         MOV H,E
        3C8F ? 63         MOV H,E
        3C90 ? 63         MOV H,E
        3C91 ? 63         MOV H,E
        3C92 ? 63         MOV H,E
        3C93 ? 63         MOV H,E
        3C94 ? 63         MOV H,E
        3C95 ? 63         MOV H,E
        3C96 ? 63         MOV H,E
        3C97 ? 63         MOV H,E
        3C98 ? 63         MOV H,E
        3C99 ? 63         MOV H,E
        3C9A ? 63         MOV H,E
        3C9B ? 63         MOV H,E
        3C9C ? 63         MOV H,E
        3C9D ? 63         MOV H,E
        3C9E ? 63         MOV H,E
        3C9F ? 63         MOV H,E
        3CA0 ? 63         MOV H,E
        3CA1 ? 63         MOV H,E
        3CA2 ? 63         MOV H,E
        3CA3 ? 63         MOV H,E
        3CA4 ? 63         MOV H,E
        3CA5 ? 63         MOV H,E
        3CA6 ? 63         MOV H,E
        3CA7 ? 63         MOV H,E
        3CA8 ? 63         MOV H,E
        3CA9 ? 63         MOV H,E
        3CAA ? 63         MOV H,E
        3CAB ? 63         MOV H,E
        3CAC ? 63         MOV H,E
        3CAD ? 63         MOV H,E
        3CAE ? 63         MOV H,E
        3CAF ? 63         MOV H,E
        3CB0 ? 63         MOV H,E
        3CB1 ? 63         MOV H,E
        3CB2 ? 63         MOV H,E
        3CB3 ? 63         MOV H,E
        3CB4 ? 63         MOV H,E
        3CB5 ? 63         MOV H,E
        3CB6 ? 63         MOV H,E
        3CB7 ? 63         MOV H,E
        3CB8 ? 63         MOV H,E
        3CB9 ? 63         MOV H,E
        3CBA ? 63         MOV H,E
        3CBB ? 63         MOV H,E
        3CBC ? 63         MOV H,E
        3CBD ? 63         MOV H,E
        3CBE ? 63         MOV H,E
        3CBF ? 63         MOV H,E
        3CC0 ? 63         MOV H,E
        3CC1 ? 63         MOV H,E
        3CC2 ? 63         MOV H,E
        3CC3 ? 63         MOV H,E
        3CC4 ? 63         MOV H,E
        3CC5 ? 63         MOV H,E
        3CC6 ? 63         MOV H,E
        3CC7 ? 63         MOV H,E
        3CC8 ? 63         MOV H,E
        3CC9 ? 63         MOV H,E
        3CCA ? 63         MOV H,E
        3CCB ? 63         MOV H,E
        3CCC ? 63         MOV H,E
        3CCD ? 63         MOV H,E
        3CCE ? 63         MOV H,E
        3CCF ? 63         MOV H,E
        3CD0 ? 63         MOV H,E
        3CD1 ? 63         MOV H,E
        3CD2 ? 63         MOV H,E
        3CD3 ? 63         MOV H,E
        3CD4 ? 63         MOV H,E
        3CD5 ? 63         MOV H,E
        3CD6 ? 63         MOV H,E
        3CD7 ? 63         MOV H,E
        3CD8 ? 63         MOV H,E
        3CD9 ? 63         MOV H,E
        3CDA ? 63         MOV H,E
        3CDB ? 63         MOV H,E
        3CDC ? 63         MOV H,E
        3CDD ? 63         MOV H,E
        3CDE ? 63         MOV H,E
        3CDF ? 63         MOV H,E
        3CE0 ? 63         MOV H,E
        3CE1 ? 63         MOV H,E
        3CE2 ? 63         MOV H,E
        3CE3 ? 63         MOV H,E
        3CE4 ? 63         MOV H,E
        3CE5 ? 63         MOV H,E
        3CE6 ? 63         MOV H,E
        3CE7 ? 63         MOV H,E
        3CE8 ? 63         MOV H,E
        3CE9 ? 63         MOV H,E
        3CEA ? 63         MOV H,E
        3CEB ? 63         MOV H,E
        3CEC ? 63         MOV H,E
        3CED ? 63         MOV H,E
        3CEE ? 63         MOV H,E
        3CEF ? 63         MOV H,E
        3CF0 ? 63         MOV H,E
        3CF1 ? 63         MOV H,E
        3CF2 ? 63         MOV H,E
        3CF3 ? 63         MOV H,E
        3CF4 ? 63         MOV H,E
        3CF5 ? 63         MOV H,E
        3CF6 ? 63         MOV H,E
        3CF7 ? 63         MOV H,E
        3CF8 ? 63         MOV H,E
        3CF9 ? 63         MOV H,E
        3CFA ? 63         MOV H,E
        3CFB ? 63         MOV H,E
        3CFC ? 63         MOV H,E
        3CFD ? 63         MOV H,E
        3CFE ? 63         MOV H,E
        3CFF ? 63         MOV H,E
        3D00 ? 63         MOV H,E
        3D01 ? 63         MOV H,E
        3D02 ? 63         MOV H,E
        3D03 ? 63         MOV H,E
        3D04 ? 63         MOV H,E
        3D05 ? 63         MOV H,E
        3D06 ? 63         MOV H,E
        3D07 ? 63         MOV H,E
        3D08 ? 63         MOV H,E
        3D09 ? 63         MOV H,E
        3D0A ? 63         MOV H,E
        3D0B ? 63         MOV H,E
        3D0C ? 63         MOV H,E
        3D0D ? 63         MOV H,E
        3D0E ? 63         MOV H,E
        3D0F ? 63         MOV H,E
        3D10 ? 63         MOV H,E
        3D11 ? 63         MOV H,E
        3D12 ? 63         MOV H,E
        3D13 ? 63         MOV H,E
        3D14 ? 63         MOV H,E
        3D15 ? 63         MOV H,E
        3D16 ? 63         MOV H,E
        3D17 ? 63         MOV H,E
        3D18 ? 63         MOV H,E
        3D19 ? 63         MOV H,E
        3D1A ? 63         MOV H,E
        3D1B ? 63         MOV H,E
        3D1C ? 63         MOV H,E
        3D1D ? 63         MOV H,E
        3D1E ? 63         MOV H,E
        3D1F ? 63         MOV H,E
        3D20 ? 63         MOV H,E
        3D21 ? 63         MOV H,E
        3D22 ? 63         MOV H,E
        3D23 ? 63         MOV H,E
        3D24 ? 63         MOV H,E
        3D25 ? 63         MOV H,E
        3D26 ? 63         MOV H,E
        3D27 ? 63         MOV H,E
        3D28 ? 63         MOV H,E
        3D29 ? 63         MOV H,E
        3D2A ? 63         MOV H,E
        3D2B ? 63         MOV H,E
        3D2C ? 63         MOV H,E
        3D2D ? 63         MOV H,E
        3D2E ? 63         MOV H,E
        3D2F ? 63         MOV H,E
        3D30 ? 63         MOV H,E
        3D31 ? 63         MOV H,E
        3D32 ? 63         MOV H,E
        3D33 ? 63         MOV H,E
        3D34 ? 63         MOV H,E
        3D35 ? 63         MOV H,E
        3D36 ? 63         MOV H,E
        3D37 ? 63         MOV H,E
        3D38 ? 63         MOV H,E
        3D39 ? 63         MOV H,E
        3D3A ? 63         MOV H,E
        3D3B ? 63         MOV H,E
        3D3C ? 63         MOV H,E
        3D3D ? 63         MOV H,E
        3D3E ? 63         MOV H,E
        3D3F ? 63         MOV H,E
        3D40 ? 63         MOV H,E
        3D41 ? 63         MOV H,E
        3D42 ? 63         MOV H,E
        3D43 ? 63         MOV H,E
        3D44 ? 63         MOV H,E
        3D45 ? 63         MOV H,E
        3D46 ? 63         MOV H,E
        3D47 ? 63         MOV H,E
        3D48 ? 63         MOV H,E
        3D49 ? 63         MOV H,E
        3D4A ? 63         MOV H,E
        3D4B ? 63         MOV H,E
        3D4C ? 63         MOV H,E
        3D4D ? 63         MOV H,E
        3D4E ? 63         MOV H,E
        3D4F ? 63         MOV H,E
        3D50 ? 63         MOV H,E
        3D51 ? 63         MOV H,E
        3D52 ? 63         MOV H,E
        3D53 ? 63         MOV H,E
        3D54 ? 63         MOV H,E
        3D55 ? 63         MOV H,E
        3D56 ? 63         MOV H,E
        3D57 ? 63         MOV H,E
        3D58 ? 63         MOV H,E
        3D59 ? 63         MOV H,E
        3D5A ? 63         MOV H,E
        3D5B ? 63         MOV H,E
        3D5C ? 63         MOV H,E
        3D5D ? 63         MOV H,E
        3D5E ? 63         MOV H,E
        3D5F ? 63         MOV H,E
        3D60 ? 63         MOV H,E
        3D61 ? 63         MOV H,E
        3D62 ? 63         MOV H,E
        3D63 ? 63         MOV H,E
        3D64 ? 63         MOV H,E
        3D65 ? 63         MOV H,E
        3D66 ? 63         MOV H,E
        3D67 ? 63         MOV H,E
        3D68 ? 63         MOV H,E
        3D69 ? 63         MOV H,E
        3D6A ? 63         MOV H,E
        3D6B ? 63         MOV H,E
        3D6C ? 63         MOV H,E
        3D6D ? 63         MOV H,E
        3D6E ? 63         MOV H,E
        3D6F ? 63         MOV H,E
        3D70 ? 63         MOV H,E
        3D71 ? 63         MOV H,E
        3D72 ? 63         MOV H,E
        3D73 ? 63         MOV H,E
        3D74 ? 63         MOV H,E
        3D75 ? 63         MOV H,E
        3D76 ? 63         MOV H,E
        3D77 ? 63         MOV H,E
        3D78 ? 63         MOV H,E
        3D79 ? 63         MOV H,E
        3D7A ? 63         MOV H,E
        3D7B ? 63         MOV H,E
        3D7C ? 63         MOV H,E
        3D7D ? 63         MOV H,E
        3D7E ? 63         MOV H,E
        3D7F ? 63         MOV H,E
        3D80 ? 63         MOV H,E
        3D81 ? 63         MOV H,E
        3D82 ? 63         MOV H,E
        3D83 ? 63         MOV H,E
        3D84 ? 63         MOV H,E
        3D85 ? 63         MOV H,E
        3D86 ? 63         MOV H,E
        3D87 ? 63         MOV H,E
        3D88 ? 63         MOV H,E
        3D89 ? 63         MOV H,E
        3D8A ? 63         MOV H,E
        3D8B ? 63         MOV H,E
        3D8C ? 63         MOV H,E
        3D8D ? 63         MOV H,E
        3D8E ? 63         MOV H,E
        3D8F ? 63         MOV H,E
        3D90 ? 63         MOV H,E
        3D91 ? 63         MOV H,E
        3D92 ? 63         MOV H,E
        3D93 ? 63         MOV H,E
        3D94 ? 63         MOV H,E
        3D95 ? 63         MOV H,E
        3D96 ? 63         MOV H,E
        3D97 ? 63         MOV H,E
        3D98 ? 63         MOV H,E
        3D99 ? 63         MOV H,E
        3D9A ? 63         MOV H,E
        3D9B ? 63         MOV H,E
        3D9C ? 63         MOV H,E
        3D9D ? 63         MOV H,E
        3D9E ? 63         MOV H,E
        3D9F ? 63         MOV H,E
        3DA0 ? 63         MOV H,E
        3DA1 ? 63         MOV H,E
        3DA2 ? 63         MOV H,E
        3DA3 ? 63         MOV H,E
        3DA4 ? 63         MOV H,E
        3DA5 ? 63         MOV H,E
        3DA6 ? 63         MOV H,E
        3DA7 ? 63         MOV H,E
        3DA8 ? 63         MOV H,E
        3DA9 ? 63         MOV H,E
        3DAA ? 63         MOV H,E
        3DAB ? 63         MOV H,E
        3DAC ? 63         MOV H,E
        3DAD ? 63         MOV H,E
        3DAE ? 63         MOV H,E
        3DAF ? 63         MOV H,E
        3DB0 ? 63         MOV H,E
        3DB1 ? 63         MOV H,E
        3DB2 ? 63         MOV H,E
        3DB3 ? 63         MOV H,E
        3DB4 ? 63         MOV H,E
        3DB5 ? 63         MOV H,E
        3DB6 ? 63         MOV H,E
        3DB7 ? 63         MOV H,E
        3DB8 ? 63         MOV H,E
        3DB9 ? 63         MOV H,E
        3DBA ? 63         MOV H,E
        3DBB ? 63         MOV H,E
        3DBC ? 63         MOV H,E
        3DBD ? 63         MOV H,E
        3DBE ? 63         MOV H,E
        3DBF ? 63         MOV H,E
        3DC0 ? 63         MOV H,E
        3DC1 ? 63         MOV H,E
        3DC2 ? 63         MOV H,E
        3DC3 ? 63         MOV H,E
        3DC4 ? 63         MOV H,E
        3DC5 ? 63         MOV H,E
        3DC6 ? 63         MOV H,E
        3DC7 ? 63         MOV H,E
        3DC8 ? 63         MOV H,E
        3DC9 ? 63         MOV H,E
        3DCA ? 63         MOV H,E
        3DCB ? 63         MOV H,E
        3DCC ? 63         MOV H,E
        3DCD ? 63         MOV H,E
        3DCE ? 63         MOV H,E
        3DCF ? 63         MOV H,E
        3DD0 ? 63         MOV H,E
        3DD1 ? 63         MOV H,E
        3DD2 ? 63         MOV H,E
        3DD3 ? 63         MOV H,E
        3DD4 ? 63         MOV H,E
        3DD5 ? 63         MOV H,E
        3DD6 ? 63         MOV H,E
        3DD7 ? 63         MOV H,E
        3DD8 ? 63         MOV H,E
        3DD9 ? 63         MOV H,E
        3DDA ? 63         MOV H,E
        3DDB ? 63         MOV H,E
        3DDC ? 63         MOV H,E
        3DDD ? 63         MOV H,E
        3DDE ? 63         MOV H,E
        3DDF ? 63         MOV H,E
        3DE0 ? 63         MOV H,E
        3DE1 ? 63         MOV H,E
        3DE2 ? 63         MOV H,E
        3DE3 ? 63         MOV H,E
        3DE4 ? 63         MOV H,E
        3DE5 ? 63         MOV H,E
        3DE6 ? 63         MOV H,E
        3DE7 ? 63         MOV H,E
        3DE8 ? 63         MOV H,E
        3DE9 ? 63         MOV H,E
        3DEA ? 63         MOV H,E
        3DEB ? 63         MOV H,E
        3DEC ? 63         MOV H,E
        3DED ? 63         MOV H,E
        3DEE ? 63         MOV H,E
        3DEF ? 63         MOV H,E
        3DF0 ? 63         MOV H,E
        3DF1 ? 63         MOV H,E
        3DF2 ? 63         MOV H,E
        3DF3 ? 63         MOV H,E
        3DF4 ? 63         MOV H,E
        3DF5 ? 63         MOV H,E
        3DF6 ? 63         MOV H,E
        3DF7 ? 63         MOV H,E
        3DF8 ? 63         MOV H,E
        3DF9 ? 63         MOV H,E
        3DFA ? 63         MOV H,E
        3DFB ? 63         MOV H,E
        3DFC ? 63         MOV H,E
        3DFD ? 63         MOV H,E
        3DFE ? 63         MOV H,E
        3DFF ? 63         MOV H,E
        3E00 ? 63         MOV H,E
        3E01 ? 63         MOV H,E
        3E02 ? 63         MOV H,E
        3E03 ? 63         MOV H,E
        3E04 ? 63         MOV H,E
        3E05 ? 63         MOV H,E
        3E06 ? 63         MOV H,E
        3E07 ? 63         MOV H,E
        3E08 ? 63         MOV H,E
        3E09 ? 63         MOV H,E
        3E0A ? 63         MOV H,E
        3E0B ? 63         MOV H,E
        3E0C ? 63         MOV H,E
        3E0D ? 63         MOV H,E
        3E0E ? 63         MOV H,E
        3E0F ? 63         MOV H,E
        3E10 ? 63         MOV H,E
        3E11 ? 63         MOV H,E
        3E12 ? 63         MOV H,E
        3E13 ? 63         MOV H,E
        3E14 ? 63         MOV H,E
        3E15 ? 63         MOV H,E
        3E16 ? 63         MOV H,E
        3E17 ? 63         MOV H,E
        3E18 ? 63         MOV H,E
        3E19 ? 63         MOV H,E
        3E1A ? 63         MOV H,E
        3E1B ? 63         MOV H,E
        3E1C ? 63         MOV H,E
        3E1D ? 63         MOV H,E
        3E1E ? 63         MOV H,E
        3E1F ? 63         MOV H,E
        3E20 ? 63         MOV H,E
        3E21 ? 63         MOV H,E
        3E22 ? 63         MOV H,E
        3E23 ? 63         MOV H,E
        3E24 ? 63         MOV H,E
        3E25 ? 63         MOV H,E
        3E26 ? 63         MOV H,E
        3E27 ? 63         MOV H,E
        3E28 ? 63         MOV H,E
        3E29 ? 63         MOV H,E
        3E2A ? 63         MOV H,E
        3E2B ? 63         MOV H,E
        3E2C ? 63         MOV H,E
        3E2D ? 63         MOV H,E
        3E2E ? 63         MOV H,E
        3E2F ? 63         MOV H,E
        3E30 ? 63         MOV H,E
        3E31 ? 63         MOV H,E
        3E32 ? 63         MOV H,E
        3E33 ? 63         MOV H,E
        3E34 ? 63         MOV H,E
        3E35 ? 63         MOV H,E
        3E36 ? 63         MOV H,E
        3E37 ? 63         MOV H,E
        3E38 ? 63         MOV H,E
        3E39 ? 63         MOV H,E
        3E3A ? 63         MOV H,E
        3E3B ? 63         MOV H,E
        3E3C ? 63         MOV H,E
        3E3D ? 63         MOV H,E
        3E3E ? 63         MOV H,E
        3E3F ? 63         MOV H,E
        3E40 ? 63         MOV H,E
        3E41 ? 63         MOV H,E
        3E42 ? 63         MOV H,E
        3E43 ? 63         MOV H,E
        3E44 ? 63         MOV H,E
        3E45 ? 63         MOV H,E
        3E46 ? 63         MOV H,E
        3E47 ? 63         MOV H,E
        3E48 ? 63         MOV H,E
        3E49 ? 63         MOV H,E
        3E4A ? 63         MOV H,E
        3E4B ? 63         MOV H,E
        3E4C ? 63         MOV H,E
        3E4D ? 63         MOV H,E
        3E4E ? 63         MOV H,E
        3E4F ? 63         MOV H,E
        3E50 ? 63         MOV H,E
        3E51 ? 63         MOV H,E
        3E52 ? 63         MOV H,E
        3E53 ? 63         MOV H,E
        3E54 ? 63         MOV H,E
        3E55 ? 63         MOV H,E
        3E56 ? 63         MOV H,E
        3E57 ? 63         MOV H,E
        3E58 ? 63         MOV H,E
        3E59 ? 63         MOV H,E
        3E5A ? 63         MOV H,E
        3E5B ? 63         MOV H,E
        3E5C ? 63         MOV H,E
        3E5D ? 63         MOV H,E
        3E5E ? 63         MOV H,E
        3E5F ? 63         MOV H,E
        3E60 ? 63         MOV H,E
        3E61 ? 63         MOV H,E
        3E62 ? 63         MOV H,E
        3E63 ? 63         MOV H,E
        3E64 ? 63         MOV H,E
        3E65 ? 63         MOV H,E
        3E66 ? 63         MOV H,E
        3E67 ? 63         MOV H,E
        3E68 ? 63         MOV H,E
        3E69 ? 63         MOV H,E
        3E6A ? 63         MOV H,E
        3E6B ? 63         MOV H,E
        3E6C ? 63         MOV H,E
        3E6D ? 63         MOV H,E
        3E6E ? 63         MOV H,E
        3E6F ? 63         MOV H,E
        3E70 ? 63         MOV H,E
        3E71 ? 63         MOV H,E
        3E72 ? 63         MOV H,E
        3E73 ? 63         MOV H,E
        3E74 ? 63         MOV H,E
        3E75 ? 63         MOV H,E
        3E76 ? 63         MOV H,E
        3E77 ? 63         MOV H,E
        3E78 ? 63         MOV H,E
        3E79 ? 63         MOV H,E
        3E7A ? 63         MOV H,E
        3E7B ? 63         MOV H,E
        3E7C ? 63         MOV H,E
        3E7D ? 63         MOV H,E
        3E7E ? 63         MOV H,E
        3E7F ? 63         MOV H,E
        3E80 ? 63         MOV H,E
        3E81 ? 63         MOV H,E
        3E82 ? 63         MOV H,E
        3E83 ? 63         MOV H,E
        3E84 ? 63         MOV H,E
        3E85 ? 63         MOV H,E
        3E86 ? 63         MOV H,E
        3E87 ? 63         MOV H,E
        3E88 ? 63         MOV H,E
        3E89 ? 63         MOV H,E
        3E8A ? 63         MOV H,E
        3E8B ? 63         MOV H,E
        3E8C ? 63         MOV H,E
        3E8D ? 63         MOV H,E
        3E8E ? 63         MOV H,E
        3E8F ? 63         MOV H,E
        3E90 ? 63         MOV H,E
        3E91 ? 63         MOV H,E
        3E92 ? 63         MOV H,E
        3E93 ? 63         MOV H,E
        3E94 ? 63         MOV H,E
        3E95 ? 63         MOV H,E
        3E96 ? 63         MOV H,E
        3E97 ? 63         MOV H,E
        3E98 ? 63         MOV H,E
        3E99 ? 63         MOV H,E
        3E9A ? 63         MOV H,E
        3E9B ? 63         MOV H,E
        3E9C ? 63         MOV H,E
        3E9D ? 63         MOV H,E
        3E9E ? 63         MOV H,E
        3E9F ? 63         MOV H,E
        3EA0 ? 63         MOV H,E
        3EA1 ? 63         MOV H,E
        3EA2 ? 63         MOV H,E
        3EA3 ? 63         MOV H,E
        3EA4 ? 63         MOV H,E
        3EA5 ? 63         MOV H,E
        3EA6 ? 63         MOV H,E
        3EA7 ? 63         MOV H,E
        3EA8 ? 63         MOV H,E
        3EA9 ? 63         MOV H,E
        3EAA ? 63         MOV H,E
        3EAB ? 63         MOV H,E
        3EAC ? 63         MOV H,E
        3EAD ? 63         MOV H,E
        3EAE ? 63         MOV H,E
        3EAF ? 63         MOV H,E
        3EB0 ? 63         MOV H,E
        3EB1 ? 63         MOV H,E
        3EB2 ? 63         MOV H,E
        3EB3 ? 63         MOV H,E
        3EB4 ? 63         MOV H,E
        3EB5 ? 63         MOV H,E
        3EB6 ? 63         MOV H,E
        3EB7 ? 63         MOV H,E
        3EB8 ? 63         MOV H,E
        3EB9 ? 63         MOV H,E
        3EBA ? 63         MOV H,E
        3EBB ? 63         MOV H,E
        3EBC ? 63         MOV H,E
        3EBD ? 63         MOV H,E
        3EBE ? 63         MOV H,E
        3EBF ? 63         MOV H,E
        3EC0 ? 63         MOV H,E
        3EC1 ? 63         MOV H,E
        3EC2 ? 63         MOV H,E
        3EC3 ? 63         MOV H,E
        3EC4 ? 63         MOV H,E
        3EC5 ? 63         MOV H,E
        3EC6 ? 63         MOV H,E
        3EC7 ? 63         MOV H,E
        3EC8 ? 63         MOV H,E
        3EC9 ? 63         MOV H,E
        3ECA ? 63         MOV H,E
        3ECB ? 63         MOV H,E
        3ECC ? 63         MOV H,E
        3ECD ? 63         MOV H,E
        3ECE ? 63         MOV H,E
        3ECF ? 63         MOV H,E
        3ED0 ? 63         MOV H,E
        3ED1 ? 63         MOV H,E
        3ED2 ? 63         MOV H,E
        3ED3 ? 63         MOV H,E
        3ED4 ? 63         MOV H,E
        3ED5 ? 63         MOV H,E
        3ED6 ? 63         MOV H,E
        3ED7 ? 63         MOV H,E
        3ED8 ? 63         MOV H,E
        3ED9 ? 63         MOV H,E
        3EDA ? 63         MOV H,E
        3EDB ? 63         MOV H,E
        3EDC ? 63         MOV H,E
        3EDD ? 63         MOV H,E
        3EDE ? 63         MOV H,E
        3EDF ? 63         MOV H,E
        3EE0 ? 63         MOV H,E
        3EE1 ? 63         MOV H,E
        3EE2 ? 63         MOV H,E
        3EE3 ? 63         MOV H,E
        3EE4 ? 63         MOV H,E
        3EE5 ? 63         MOV H,E
        3EE6 ? 63         MOV H,E
        3EE7 ? 63         MOV H,E
        3EE8 ? 63         MOV H,E
        3EE9 ? 63         MOV H,E
        3EEA ? 63         MOV H,E
        3EEB ? 63         MOV H,E
        3EEC ? 63         MOV H,E
        3EED ? 63         MOV H,E
        3EEE ? 63         MOV H,E
        3EEF ? 63         MOV H,E
        3EF0 ? 63         MOV H,E
        3EF1 ? 63         MOV H,E
        3EF2 ? 63         MOV H,E
        3EF3 ? 63         MOV H,E
        3EF4 ? 63         MOV H,E
        3EF5 ? 63         MOV H,E
        3EF6 ? 63         MOV H,E
        3EF7 ? 63         MOV H,E
        3EF8 ? 63         MOV H,E
        3EF9 ? 63         MOV H,E
        3EFA ? 63         MOV H,E
        3EFB ? 63         MOV H,E
        3EFC ? 63         MOV H,E
        3EFD ? 63         MOV H,E
        3EFE ? 63         MOV H,E
        3EFF ? 63         MOV H,E
        3F00 ? 63         MOV H,E
        3F01 ? 63         MOV H,E
        3F02 ? 63         MOV H,E
        3F03 ? 63         MOV H,E
        3F04 ? 63         MOV H,E
        3F05 ? 63         MOV H,E
        3F06 ? 63         MOV H,E
        3F07 ? 63         MOV H,E
        3F08 ? 63         MOV H,E
        3F09 ? 63         MOV H,E
        3F0A ? 63         MOV H,E
        3F0B ? 63         MOV H,E
        3F0C ? 63         MOV H,E
        3F0D ? 63         MOV H,E
        3F0E ? 63         MOV H,E
        3F0F ? 63         MOV H,E
        3F10 ? 63         MOV H,E
        3F11 ? 63         MOV H,E
        3F12 ? 63         MOV H,E
        3F13 ? 63         MOV H,E
        3F14 ? 63         MOV H,E
        3F15 ? 63         MOV H,E
        3F16 ? 63         MOV H,E
        3F17 ? 63         MOV H,E
        3F18 ? 63         MOV H,E
        3F19 ? 63         MOV H,E
        3F1A ? 63         MOV H,E
        3F1B ? 63         MOV H,E
        3F1C ? 63         MOV H,E
        3F1D ? 63         MOV H,E
        3F1E ? 63         MOV H,E
        3F1F ? 63         MOV H,E
        3F20 ? 63         MOV H,E
        3F21 ? 63         MOV H,E
        3F22 ? 63         MOV H,E
        3F23 ? 63         MOV H,E
        3F24 ? 63         MOV H,E
        3F25 ? 63         MOV H,E
        3F26 ? 63         MOV H,E
        3F27 ? 63         MOV H,E
        3F28 ? 63         MOV H,E
        3F29 ? 63         MOV H,E
        3F2A ? 63         MOV H,E
        3F2B ? 63         MOV H,E
        3F2C ? 63         MOV H,E
        3F2D ? 63         MOV H,E
        3F2E ? 63         MOV H,E
        3F2F ? 63         MOV H,E
        3F30 ? 63         MOV H,E
        3F31 ? 63         MOV H,E
        3F32 ? 63         MOV H,E
        3F33 ? 63         MOV H,E
        3F34 ? 63         MOV H,E
        3F35 ? 63         MOV H,E
        3F36 ? 63         MOV H,E
        3F37 ? 63         MOV H,E
        3F38 ? 63         MOV H,E
        3F39 ? 63         MOV H,E
        3F3A ? 63         MOV H,E
        3F3B ? 63         MOV H,E
        3F3C ? 63         MOV H,E
        3F3D ? 63         MOV H,E
        3F3E ? 63         MOV H,E
        3F3F ? 63         MOV H,E
        3F40 ? 63         MOV H,E
        3F41 ? 63         MOV H,E
        3F42 ? 63         MOV H,E
        3F43 ? 63         MOV H,E
        3F44 ? 63         MOV H,E
        3F45 ? 63         MOV H,E
        3F46 ? 63         MOV H,E
        3F47 ? 63         MOV H,E
        3F48 ? 63         MOV H,E
        3F49 ? 63         MOV H,E
        3F4A ? 63         MOV H,E
        3F4B ? 63         MOV H,E
        3F4C ? 63         MOV H,E
        3F4D ? 63         MOV H,E
        3F4E ? 63         MOV H,E
        3F4F ? 63         MOV H,E
        3F50 ? 63         MOV H,E
        3F51 ? 63         MOV H,E
        3F52 ? 63         MOV H,E
        3F53 ? 63         MOV H,E
        3F54 ? 63         MOV H,E
        3F55 ? 63         MOV H,E
        3F56 ? 63         MOV H,E
        3F57 ? 63         MOV H,E
        3F58 ? 63         MOV H,E
        3F59 ? 63         MOV H,E
        3F5A ? 63         MOV H,E
        3F5B ? 63         MOV H,E
        3F5C ? 63         MOV H,E
        3F5D ? 63         MOV H,E
        3F5E ? 63         MOV H,E
        3F5F ? 63         MOV H,E
        3F60 ? 63         MOV H,E
        3F61 ? 63         MOV H,E
        3F62 ? 63         MOV H,E
        3F63 ? 63         MOV H,E
        3F64 ? 63         MOV H,E
        3F65 ? 63         MOV H,E
        3F66 ? 63         MOV H,E
        3F67 ? 63         MOV H,E
        3F68 ? 63         MOV H,E
        3F69 ? 63         MOV H,E
        3F6A ? 63         MOV H,E
        3F6B ? 63         MOV H,E
        3F6C ? 63         MOV H,E
        3F6D ? 63         MOV H,E
        3F6E ? 63         MOV H,E
        3F6F ? 63         MOV H,E
        3F70 ? 63         MOV H,E
        3F71 ? 63         MOV H,E
        3F72 ? 63         MOV H,E
        3F73 ? 63         MOV H,E
        3F74 ? 63         MOV H,E
        3F75 ? 63         MOV H,E
        3F76 ? 63         MOV H,E
        3F77 ? 63         MOV H,E
        3F78 ? 63         MOV H,E
        3F79 ? 63         MOV H,E
        3F7A ? 63         MOV H,E
        3F7B ? 63         MOV H,E
        3F7C ? 63         MOV H,E
        3F7D ? 63         MOV H,E
        3F7E ? 63         MOV H,E
        3F7F ? 63         MOV H,E
        3F80 ? 63         MOV H,E
        3F81 ? 63         MOV H,E
        3F82 ? 63         MOV H,E
        3F83 ? 63         MOV H,E
        3F84 ? 63         MOV H,E
        3F85 ? 63         MOV H,E
        3F86 ? 63         MOV H,E
        3F87 ? 63         MOV H,E
        3F88 ? 63         MOV H,E
        3F89 ? 63         MOV H,E
        3F8A ? 63         MOV H,E
        3F8B ? 63         MOV H,E
        3F8C ? 63         MOV H,E
        3F8D ? 63         MOV H,E
        3F8E ? 63         MOV H,E
        3F8F ? 63         MOV H,E
        3F90 ? 63         MOV H,E
        3F91 ? 63         MOV H,E
        3F92 ? 63         MOV H,E
        3F93 ? 63         MOV H,E
        3F94 ? 63         MOV H,E
        3F95 ? 63         MOV H,E
        3F96 ? 63         MOV H,E
        3F97 ? 63         MOV H,E
        3F98 ? 63         MOV H,E
        3F99 ? 63         MOV H,E
        3F9A ? 63         MOV H,E
        3F9B ? 63         MOV H,E
        3F9C ? 63         MOV H,E
        3F9D ? 63         MOV H,E
        3F9E ? 63         MOV H,E
        3F9F ? 63         MOV H,E
        3FA0 ? 63         MOV H,E
        3FA1 ? 63         MOV H,E
        3FA2 ? 63         MOV H,E
        3FA3 ? 63         MOV H,E
        3FA4 ? 63         MOV H,E
        3FA5 ? 63         MOV H,E
        3FA6 ? 63         MOV H,E
        3FA7 ? 63         MOV H,E
        3FA8 ? 63         MOV H,E
        3FA9 ? 63         MOV H,E
        3FAA ? 63         MOV H,E
        3FAB ? 63         MOV H,E
        3FAC ? 63         MOV H,E
        3FAD ? 63         MOV H,E
        3FAE ? 63         MOV H,E
        3FAF ? 63         MOV H,E
        3FB0 ? 63         MOV H,E
        3FB1 ? 63         MOV H,E
        3FB2 ? 63         MOV H,E
        3FB3 ? 63         MOV H,E
        3FB4 ? 63         MOV H,E
        3FB5 ? 63         MOV H,E
        3FB6 ? 63         MOV H,E
        3FB7 ? 63         MOV H,E
        3FB8 ? 63         MOV H,E
        3FB9 ? 63         MOV H,E
        3FBA ? 63         MOV H,E
        3FBB ? 63         MOV H,E
        3FBC ? 63         MOV H,E
        3FBD ? 63         MOV H,E
        3FBE ? 63         MOV H,E
        3FBF ? 63         MOV H,E
        3FC0 ? 63         MOV H,E
        3FC1 ? 63         MOV H,E
        3FC2 ? 63         MOV H,E
        3FC3 ? 63         MOV H,E
        3FC4 ? 63         MOV H,E
        3FC5 ? 63         MOV H,E
        3FC6 ? 63         MOV H,E
        3FC7 ? 63         MOV H,E
        3FC8 ? 63         MOV H,E
        3FC9 ? 63         MOV H,E
        3FCA ? 63         MOV H,E
        3FCB ? 63         MOV H,E
        3FCC ? 63         MOV H,E
        3FCD ? 63         MOV H,E
        3FCE ? 63         MOV H,E
        3FCF ? 63         MOV H,E
        3FD0 ? 63         MOV H,E
        3FD1 ? 63         MOV H,E
        3FD2 ? 63         MOV H,E
        3FD3 ? 63         MOV H,E
        3FD4 ? 63         MOV H,E
        3FD5 ? 63         MOV H,E
        3FD6 ? 63         MOV H,E
        3FD7 ? 63         MOV H,E
        3FD8 ? 63         MOV H,E
        3FD9 ? 63         MOV H,E
        3FDA ? 63         MOV H,E
        3FDB ? 63         MOV H,E
        3FDC ? 63         MOV H,E
        3FDD ? 63         MOV H,E
        3FDE ? 63         MOV H,E
        3FDF ? 63         MOV H,E
        3FE0 ? 63         MOV H,E
        3FE1 ? 63         MOV H,E
        3FE2 ? 63         MOV H,E
        3FE3 ? 63         MOV H,E
        3FE4 ? 63         MOV H,E
        3FE5 ? 63         MOV H,E
        3FE6 ? 63         MOV H,E
        3FE7 ? 63         MOV H,E
        3FE8 ? 63         MOV H,E
        3FE9 ? 63         MOV H,E
        3FEA ? 63         MOV H,E
        3FEB ? 63         MOV H,E
        3FEC ? 63         MOV H,E
        3FED ? 63         MOV H,E
        3FEE ? 63         MOV H,E
        3FEF ? 63         MOV H,E
        3FF0 ? 63         MOV H,E
        3FF1 ? 63         MOV H,E
        3FF2 ? 63         MOV H,E
        3FF3 ? 63         MOV H,E
        3FF4 ? 63         MOV H,E
        3FF5 ? 63         MOV H,E
        3FF6 ? 63         MOV H,E
        3FF7 ? 63         MOV H,E
        3FF8 ? 63         MOV H,E
        3FF9 ? 63         MOV H,E
        3FFA ? 63         MOV H,E
        3FFB ? 63         MOV H,E
        3FFC ? 63         MOV H,E
        3FFD ? 63         MOV H,E
        3FFE ? 63         MOV H,E
        3FFF ? 63         MOV H,E
                END


