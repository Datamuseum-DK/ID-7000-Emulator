; ===========================================================================
;  FIBONACCI PROCESS for the IPC/1 operating system (ID-7000, SPS/FUNK image)
;
;  Computes one Fibonacci number about once per second and writes it at 7100H
;  as four ASCII hexadecimal digits (most significant first, upper case)
;  followed by a 00H terminator:   7100H: '0' '0' '0' '5' 00H   = 5
;  The sequence is 0, 1, 1, 2, 3, 5, 8, 0DH, 15H ... 0B520H (F24, the largest
;  that fits in 16 bits); after that it starts again from 0.
;
;  Start it from the operator menu:   P  <Enter>   3  <Enter>   807C  <Enter>
;  (priority 1-3: a process of priority 4 or lower is starved by the PLC cycle).
;  To load the code with the front end: Ctrl-] L, file examples/fib.hex
;  (the download puts the first code byte at 807CH).
;
;  How the one-second delay works
;   * The kernel has no sleep call.  The timer interrupt signals the semaphore
;     SEM_TICK5 every 5th timer tick, and the clock process (prio 0) waits on it.
;   * This process waits on the same semaphore and forwards every event it
;     receives back to the clock process, so the clock still sees all events.
;   * Elapsed time is taken from the OS tick counter UPTIME (4000H), which
;     counts once per 2 timer ticks, so the delay does not depend on how the
;     events are shared between the two processes.
;   * TICKS_PER_SEC is an assumption taken from the clock process, which counts
;     4 x 25 events of 5 ticks per cycle.  Change it if your tick rate differs.
; ===========================================================================
UPTIME        EQU 4000H        ; word, +1 every 2 timer ticks (kernel)
SEM_TICK5     EQU 4047H        ; semaphore signalled every 5th timer tick
API_SEM_WAIT  EQU 00B8H        ; OS API: wait on semaphore (BC = address)
API_SEM_SIGNAL EQU 00B2H       ; OS API: signal semaphore  (BC = address)
OUT_ADDR      EQU 7FF0H        ; result: 4 hex digits + 00H
TICKS_PER_SEC EQU 500          ; timer ticks per second (assumption, see above)
HALF_TICKS    EQU TICKS_PER_SEC/2

              ORG 807CH

START:        LXI H,0
              SHLD FIB_A       ; a = 0
              INX H
              SHLD FIB_B       ; b = 1
              XRA A
              STA RESTART

LOOP:         LHLD FIB_A
              CALL PUT_HEX     ; publish a at OUT_ADDR
              CALL DELAY_1S
              CALL NEXT        ; advance the sequence
              JMP LOOP

; ---- advance: (a, b) := (b, a+b); restart after the last 16-bit number -------
NEXT:         LDA RESTART
              ORA A
              JZ ADVANCE
              XRA A            ; the previous number was the last that fits
              STA RESTART
              LXI H,0
              SHLD FIB_A
              INX H
              SHLD FIB_B
              RET
ADVANCE:      LHLD FIB_A
              XCHG             ; DE = a
              LHLD FIB_B       ; HL = b
              SHLD FIB_A       ; a = b
              DAD D            ; HL = a + b
              JNC STORE_B
              MVI A,1          ; the sum no longer fits: show b once, then restart
              STA RESTART
              RET
STORE_B:      SHLD FIB_B
              RET

; ---- HL -> four ASCII hex digits at OUT_ADDR, then 00H ------------------------
PUT_HEX:      LXI D,OUT_ADDR
              MOV A,H
              CALL HEX2
              MOV A,L
              CALL HEX2
              XRA A
              STAX D           ; terminator
              RET
HEX2:         PUSH PSW
              RRC
              RRC
              RRC
              RRC              ; high nibble into the low four bits
              CALL NIBBLE
              POP PSW          ; low nibble
NIBBLE:       ANI 0FH
              ADI 90H
              DAA
              ACI 40H
              DAA              ; 0-9 -> '0'-'9', 0AH-0FH -> 'A'-'F'
              STAX D
              INX D
              RET

; ---- wait about one second ---------------------------------------------------
DELAY_1S:     LHLD UPTIME
              LXI D,HALF_TICKS
              DAD D
              SHLD TARGET      ; wake-up time on the UPTIME scale
WAIT:         LXI B,SEM_TICK5
              CALL API_SEM_WAIT      ; next 5-tick event handed to this process
              LXI B,SEM_TICK5
              CALL API_SEM_SIGNAL    ; pass it on to the clock process
              LHLD UPTIME
              XCHG             ; DE = now
              LHLD TARGET
              MOV A,E
              SUB L
              MOV A,D
              SBB H            ; now - target (16 bit)
              JM WAIT          ; negative: not yet
              RET

FIB_A:        DW 0
FIB_B:        DW 1
TARGET:       DW 0
RESTART:      DB 0
