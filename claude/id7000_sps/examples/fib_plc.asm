; ===========================================================================
;  FIBONACCI for the PLC runtime - loadable with aux command 1Eh and started
;  with aux command 20h 01 (no P command needed).
;
;  The PLC loader (2359h) only accepts a small "compiled PLC" opcode set (no
;  ADD, no INX, no SHLD ...), but it relocates the code in a straight line and
;  stops at the FIRST RET.  This program uses that:
;     807CH  JMP MAIN      the loader accepts it and makes the operand absolute
;     807FH  RET           the loader stops scanning here
;     8080H  MAIN ...      ordinary 8080 code, which the loader never looks at
;  The PLC cycle calls the entry once per cycle, so MAIN must return quickly.
;  It keeps its state in variables that are part of the downloaded image
;  (a fresh download starts the sequence again; stop/run continues it).
;
;  Once about every second (see TICKS_PER_SEC) it computes the next number and
;  writes it at 7100H as four ASCII hex digits and a 00H terminator:
;     7100H: '0' '0' '0' '5' 00H   = 5
;  Sequence 0, 1, 1, 2, 3, 5, 8, 0DH ... 0B520H (largest 16-bit), then again.
; ===========================================================================
UPTIME        EQU 4000H        ; word, +1 every 2 timer ticks (kernel)
OUT_ADDR      EQU 7100H        ; result: 4 hex digits + 00H
TICKS_PER_SEC EQU 500          ; timer ticks per second (assumption)
HALF_TICKS    EQU TICKS_PER_SEC/2

              ORG 807CH
ENTRY:        JMP MAIN-807DH   ; relative: the loader adds the operand's own address
              RET              ; the loader stops scanning at this first RET

MAIN:         LDA INIT
              ORA A
              JNZ CHECK
              MVI A,1          ; first call: start the sequence 0, 1, ...
              STA INIT
              LXI H,0
              SHLD FIB_A
              INX H
              SHLD FIB_B
              XRA A
              STA RESTART
              LHLD FIB_A
              CALL PUT_HEX
              JMP SETDUE       ; (tail call, returns to the PLC cycle)

CHECK:        LHLD UPTIME
              XCHG             ; DE = now
              LHLD DUE
              MOV A,E
              SUB L
              MOV A,D
              SBB H            ; now - due (16 bit)
              RM               ; negative: not yet, back to the PLC cycle
              CALL NEXT
              LHLD FIB_A
              CALL PUT_HEX
SETDUE:       LHLD UPTIME
              LXI D,HALF_TICKS
              DAD D
              SHLD DUE
              RET

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
              STAX D
              RET
HEX2:         PUSH PSW
              RRC
              RRC
              RRC
              RRC
              CALL NIBBLE
              POP PSW
NIBBLE:       ANI 0FH
              ADI 90H
              DAA
              ACI 40H
              DAA              ; 0-9 -> '0'-'9', 0AH-0FH -> 'A'-'F'
              STAX D
              INX D
              RET

; ---- variables (part of the image, so a new download resets them) ------------
INIT:         DB 0
FIB_A:        DW 0
FIB_B:        DW 1
DUE:          DW 0
RESTART:      DB 0
