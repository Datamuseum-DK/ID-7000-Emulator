; 32-bit increment routine for Intel 8080
; COUNTER points to 4 bytes in RAM (LSB to MSB)

COUNT0  EQU 7FF0H
COUNT2  EQU 7FF2H

        ORG 807CH
; =====================================================================
; 32-Bit Counter Increment for Intel 8080
; Modifies: A, H, L, Flags
; =====================================================================

LOOP:   LXI B,4047h         ; (SEM_TICK5)
        CALL 00B8h          ; (sem_wait)
        LHLD    COUNT0      ; Load bytes 0 and 1 into HL pair
        INX     H           ; Increment the lower 16 bits (does not affect Carry)
        SHLD    COUNT0      ; Store updated lower 16 bits back to memory

        ; Check if the lower 16 bits rolled over from FFFFh to 0000h
        MOV     A, H        ; Copy H to Accumulator
        ORA     L           ; OR with L to check if both H and L are zero
        JNZ     LOOP        ; If HL != 0, no overflow occurred; return early

        ; Ripple carry into byte 2
        LHLD    COUNT2      ; Load bytes 2 and 3 into HL pair
        MOV     A, L        ; Move byte 2 to Accumulator
        ADI     1           ; Add 1 (this sets the Carry flag if byte 2 overflows)
        MOV     L, A        ; Store back into L

        ; Ripple carry into byte 3
        MOV     A, H        ; Move byte 3 to Accumulator
        ACI     0           ; Add 0 + Carry flag from the previous addition
        MOV     H, A        ; Store back into H

        SHLD    COUNT2      ; Store updated upper 16 bits back to memory
        JP      LOOP        ; Return to caller
