"""Printer stub for the ID-7000 emulator: an 8255 PPI (ports 50h-53h) plus a
Centronics-style printer behind it.

Wiring inferred from the ROM (printer_out at 19E1h):
    PA (50h)  data out
    PB5       BUSY    (input, 1 = busy; ROM yields and retries)
    PB3       HOLD    (input; only looked at after a busy: 1 = keep waiting,
                       0 = retry now - looks like an offline/fault line)
    PC7       STROBE  (output, idles high, ROM pulses it low then high)
    PC4       set low then high at init; purpose unknown, tracked only
"""
ESC = 0x1B

class Printer:
    def __init__(self, busy_reads=0, capture_on='fall'):
        self.raw = bytearray()          # every byte the printer accepted
        self.busy_reads = busy_reads    # busy for N reads of port B after each char
        self.hold = False               # PB3 level
        self.force_busy = False         # keep PB5 high until cleared
        self.capture_on = capture_on    # 'fall' or 'rise' edge of /STROBE latches PA
        self.mode = None
        self.pa = 0; self.pc = 0
        self._busy_left = 0
        self._seen_fall = False
        self.strobes = 0
        self.log = []                   # (event, value) for debugging

    # ---- 8255 registers
    def read(self, port):
        if port == 0x51:                # port B: status inputs
            busy = self.force_busy or self._busy_left > 0
            if self._busy_left > 0: self._busy_left -= 1
            return (0x20 if busy else 0) | (0x08 if self.hold else 0)
        if port == 0x50: return self.pa
        if port == 0x52: return self.pc
        return 0xFF                     # control register is write-only

    def write(self, port, v):
        if port == 0x50: self.pa = v
        elif port == 0x52: self.pc = v
        elif port == 0x53: self._control(v)

    def _control(self, v):
        if v & 0x80:                    # mode set: clears A and C latches
            self.mode = v; self.pa = 0; self.pc = 0; self._seen_fall = False
            if v != 0x82: self.log.append(('unexpected mode', v))
            return
        bit = (v >> 1) & 7; on = v & 1  # bit set/reset on port C
        old = (self.pc >> bit) & 1
        self.pc = (self.pc | (1 << bit)) if on else (self.pc & ~(1 << bit))
        if bit == 7 and old != on:
            if not on:                  # falling edge: strobe asserted
                self._seen_fall = True
                if self.capture_on == 'fall': self._latch()
            elif self._seen_fall:       # rising edge after a real pulse
                self._seen_fall = False
                if self.capture_on == 'rise': self._latch()

    def _latch(self):
        self.raw.append(self.pa); self.strobes += 1
        self._busy_left = self.busy_reads

    # ---- rendering
    def pages(self):
        """Interpret CR/LF/FF and return pages as lists of lines (overprint keeps the last char)."""
        pages=[[]]; line={}; col=0
        def flush():
            pages[-1].append(''.join(line.get(i,' ') for i in range(max(line)+1)) if line else '')
        for b in self.raw:
            if b == 0x0D: col = 0
            elif b == 0x0A: flush(); line = {}
            elif b == 0x0C:
                flush(); line = {}; pages.append([]); col = 0
            elif 32 <= b < 127: line[col] = chr(b); col += 1
        if line: flush()
        return [p for p in pages if p or len(pages) == 1]

    def text(self):
        return '\f'.join('\n'.join(p) for p in self.pages())

def attach_printer(machine, printer):
    for p in (0x50, 0x51, 0x52, 0x53):
        machine.bus.in_handlers[p]  = lambda port, pr=printer: pr.read(port)
        machine.bus.out_handlers[p] = lambda port, v, pr=printer: pr.write(port, v)
    return printer

# ---- helpers for building host print data (formats decoded from printer_task)
def tab(n):    # ESC + (20h+n): n spaces, 3..31
    assert 3 <= n <= 31; return bytes([ESC, 0x20 + n])
def zeros(n):  # ESC + (40h+n): n zero digits, 3..15
    assert 3 <= n <= 15; return bytes([ESC, 0x40 + n])
CR_OVERPRINT = bytes([ESC, 0x40])           # ESC @ : carriage return without line feed

def print_via_host(host, text, cc=' ', channel=0, eol=b'\r\n'):
    """Send one print block from the Cyber host stub.
    cc = carriage-control char: ' ' (and any other) = LF CR, 'A' = form feed, 'J' = extra LF.
    Data frame uses ctl 12h and the ESC-space trailer that selects the printer."""
    if isinstance(text, str): text = text.encode('latin1')
    return host.exchange(0x70 + channel, 0x60, 0x12, cc.encode() + text + eol + b'\x1b ')
