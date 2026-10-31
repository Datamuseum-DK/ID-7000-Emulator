#!/usr/bin/env python3
"""Interactive curses front end for the ID-7000 IPC/1 + SPC/1 emulator.

    python3 interactive.py            run with the panel and the built-in debugger
    python3 interactive.py --ascii    show the Danish letters as [ \\ ] { | } (raw ROM text)
    python3 interactive.py --tick-hz 100   timer ticks per second at speed x1 (default 500)
    python3 interactive.py --watch 7100    show 8 bytes at this (hex) address in the panel
    python3 interactive.py --selftest scripted test without a terminal

Keys
  everything        goes to the operator console (Enter = CR, Backspace = 08h, Esc = 1Bh)
  Ctrl-]            emulator prefix, then one of:
      q quit         p pause/resume      h help          s change speed
      i toggle a digital input point     a set an analog value
      l load demo program (aux link)     L load a hex file (@file = raw image from 8000h)
      N set the program name stored at 8000h by l and L     r run     x stop
      c send a raw aux command           v show version string
      R restart the system (stops every process)
      b break into the debugger          d show/hide the info panel
      n switch Danish/raw characters

The ROM's "D - HOP TIL DEBUGGER" command does DI; CALL F008h. The debugger ROM is not in the
image, so this program intercepts F008h (and the TRAP vector target F000h) with a small
built-in monitor: s step, c continue (RET to the caller), g go, m dump, b breakpoint, q quit.
"""
import argparse, curses, locale, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from machine import Machine, attach_analog
from terminal import Terminal
from aux import AuxHost
from disasm import disasm

PREFIX = '\x1d'                       # Ctrl-]
SPEEDS = [0.25, 0.5, 1, 2, 4, 0]      # 0 = as fast as possible
BASE_HZ = 400_000                     # emulated instructions per second at x1 (100 ticks/s)
NAT_OUT = str.maketrans('[\\]{|}', 'ÆØÅæøå')
NAT_IN = {'Æ': '[', 'Ø': '\\', 'Å': ']', 'æ': '{', 'ø': '|', 'å': '}'}
DEMO_PROG = bytes([0x21, 0x00, 0x20, 0x7E, 0x21, 0x00, 0x10, 0x77, 0xC9])   # out0 := in0
PLC_STATE = {0: 'none', 1: 'loaded', 2: 'stopped', 3: 'RUN'}
HELP = """\
 Everything you type goes to the operator console.
 Ctrl-]  then:
   q quit            p pause           s speed            h this help
   i toggle input    a analog value    d panel on/off     n Danish/raw text
   l demo program    L hex file        r run              x stop
   c raw aux command v version         b debugger        R restart (stops all)
   N program name (stored at 8000h by l/L; L @file sends a raw image)
 Menu in the ROM:  C (stub)   D debugger   P start process   Esc = back to menu
 Debugger: s step  c continue(RET)  g go  m addr dump  b addr breakpoint  q resume
 Digital inputs are active low: the panel shows '#' for an active point."""


class DebugBreak(Exception):
    pass


class App:
    def __init__(self, scr, args, machine=None):
        self.scr = scr
        self.args = args
        self.m = machine or Machine(args.rom)
        self.m.TICK = max(1, BASE_HZ // max(1, getattr(args, 'tick_hz', 500)))   # steps between timer ticks
        if not hasattr(self.m, 'adc'):
            self.adc = attach_analog(self.m)
        self.term = Terminal()
        self.host = AuxHost(self.m)
        self.paused = False
        self.speed = 2
        self.national = not args.ascii
        self.show_panel = True
        self.overlay = False
        self.show_help = False
        self.prefix = False
        self.prompt = None            # [label, text, callback]
        self.status = 'Ctrl-] h = help'
        self.log = []
        self.quit = False
        self.prog_name = ''
        self.dbg = None
        self.breaks = set()
        self.watch = {0xF000, 0xF008}
        self.last = time.perf_counter()
        self.rate_t, self.rate_s, self.rate = self.last, 0, 0.0
        self.aux_frames = 0
        self._orig_step = self.m.cpu.step
        self.m.cpu.step = self._hooked_step

    # ------------------------------------------------------------- emulation
    def _hooked_step(self):
        pc = self.m.cpu.pc
        if pc in self.watch or pc in self.breaks:
            raise DebugBreak(pc)
        self._orig_step()

    def run_steps(self, n):
        """Run n steps; a break enters the debugger. Returns the steps executed."""
        start = self.m.steps
        try:
            self.m.run(n)
        except DebugBreak as e:
            self.enter_debugger(e.args[0])
        return self.m.steps - start

    def emulate(self, dt):
        if self.paused or self.dbg:
            return
        if self.args.fixed:
            self.run_steps(self.args.fixed)
        else:
            hz = BASE_HZ * SPEEDS[self.speed] if SPEEDS[self.speed] else 1e9
            budget = min(int(hz * dt), 400_000)
            end = time.perf_counter() + 0.035
            done = 0
            while done < budget and not self.dbg and time.perf_counter() < end:
                n = self.run_steps(min(2000, budget - done))
                done += n
                if n == 0:
                    break
        self.term.feed(self.m.take())

    # ------------------------------------------------------------- debugger
    def enter_debugger(self, pc):
        self.term.feed(self.m.take())
        why = {0xF008: 'CALL F008h (D command)', 0xF000: 'TRAP vector target'}.get(pc, 'breakpoint %04X' % pc)
        self.dbg = {'why': why, 'mem': 0x4000, 'prompt': None}
        self.status = 'DEBUGGER: ' + why

    def dbg_step_once(self):
        self.m.cpu.step = self._orig_step
        try:
            self._orig_step()
            self.m.steps += 1
        finally:
            self.m.cpu.step = self._hooked_step

    def dbg_key(self, k):
        d = self.dbg
        if d['prompt']:
            label, text, cb = d['prompt']
            if k in ('\n', '\r') or k == curses.KEY_ENTER:
                d['prompt'] = None; cb(text)
            elif k == '\x1b':
                d['prompt'] = None
            elif k in ('\x7f', '\b') or k == curses.KEY_BACKSPACE:
                d['prompt'][1] = text[:-1]
            elif isinstance(k, str) and k.isprintable():
                d['prompt'][1] += k
            return
        if not isinstance(k, str):
            return
        c = self.m.cpu
        if k == 's':
            self.dbg_step_once()
        elif k == 'c':                                   # act like the debugger: RET to the caller
            c.pc = c.pop(); self.leave_debugger()
        elif k in ('g', 'q'):
            self.dbg_step_once(); self.leave_debugger()
        elif k == 'm':
            d['prompt'] = ['dump address (hex): ', '', lambda t: self._set_mem(t)]
        elif k == 'b':
            d['prompt'] = ['toggle breakpoint (hex): ', '', lambda t: self._toggle_break(t)]
        elif k == 'x':
            self.quit = True

    def _set_mem(self, t):
        try: self.dbg['mem'] = int(t, 16) & 0xFFFF
        except ValueError: self.status = 'bad address'

    def _toggle_break(self, t):
        try:
            a = int(t, 16) & 0xFFFF
            (self.breaks.discard if a in self.breaks else self.breaks.add)(a)
        except ValueError:
            self.status = 'bad address'

    def leave_debugger(self):
        self.dbg = None
        self.status = 'running'

    # ------------------------------------------------------------- aux link actions
    def aux(self, code, *args):
        self.status = 'aux %02X ...' % code
        self.draw(); self.scr.refresh()
        reply = self.host.command(code, *args)
        self.aux_frames += 1
        self.log.append('> %02X %s' % (code, bytes(args).hex(' ')))
        self.log.append('< ' + ('no reply' if reply is None else self._fmt_reply(reply)))
        self.log = self.log[-14:]
        self.term.feed(self.m.take())
        return reply

    @staticmethod
    def _fmt_reply(reply):
        import re
        out = []
        for code, data in reply:
            if code == 0x79: continue                       # frame acknowledge
            runs = re.findall(rb'[\x20-\x7e]{4,}', data)
            txt = ('"%s" ' % ' '.join(r.decode() for r in runs) if runs else '') + data.hex(' ')
            out.append('%02X:%s' % (code, txt))
        return ' | '.join(out) or 'ack'

    def connect(self):
        if not getattr(self, '_connected', False):
            self.host.connect(); self._connected = True

    def header(self):
        """The 7Ch-byte program header: the program name (zero terminated, at most 39 characters) then zeros."""
        name = self.prog_name.encode('latin1', 'replace')[:39] + b'\0'
        return name + bytes(0x7C - len(name))

    def download(self, code, raw=False):
        """Send code to the PLC download area. Normally a header carrying the program name is put in front, so that
        the first code byte lands at 807Ch, the fixed program entry. raw=True sends the bytes exactly as given,
        starting at 8000h (the file must then contain the header itself)."""
        self.connect()
        image = code if raw else self.header() + code
        blocks = [image[i:i + 32] for i in range(0, len(image), 32)]
        for n, b in enumerate(blocks):
            reply = self.aux(0x1E, n, 0 if n == len(blocks) - 1 else 1, *b)
            data = next((d for c, d in (reply or []) if c == 0x1E), b'')
            if len(data) >= 3 and data[2] != 0:
                why = {1: 'the PLC program is running - stop it first (Ctrl-] x)', 2: 'block out of sequence'}.get(data[2], 'status %d' % data[2])
                self.status = 'download refused: ' + why
                return False
        self.status = 'downloaded %d bytes to 8000h-%04X, PLC state %s' % (len(image), 0x8000 + len(image) - 1, PLC_STATE.get(self.m.bus.ram[0x4C02], '?'))
        return True

    # ------------------------------------------------------------- prompts and prefix keys
    def ask(self, label, cb):
        self.prompt = [label, '', cb]

    def ctl_key(self, k):
        k = k if isinstance(k, str) else ''
        m = self.m
        if k == 'q': self.quit = True
        elif k == 'p': self.paused = not self.paused; self.status = 'paused' if self.paused else 'running'
        elif k == 'h': self.show_help = not self.show_help
        elif k == 's': self.speed = (self.speed + 1) % len(SPEEDS); self.status = 'speed x%s' % (SPEEDS[self.speed] or 'max')
        elif k == 'd':
            self.show_panel = not self.show_panel
            self.overlay = self.show_panel and self.scr.getmaxyx()[1] < 120
        elif k == 'n': self.national = not self.national
        elif k == 'b': self.enter_debugger(m.cpu.pc); self.dbg['why'] = 'manual break'
        elif k == 'l': self.download(DEMO_PROG)
        elif k == 'r': self.connect(); self.aux(0x20, 1); self.status = 'PLC state %s' % PLC_STATE.get(m.bus.ram[0x4C02], '?')
        elif k == 'x': self.connect(); self.aux(0x20, 0); self.status = 'PLC state %s' % PLC_STATE.get(m.bus.ram[0x4C02], '?')
        elif k == 'v': self.connect(); self.aux(0x60)
        elif k == 'R': self.restart()
        elif k == 'i': self.ask('toggle input point (0-159): ', self._toggle_input)
        elif k == 'a': self.ask('analog  module channel value  (e.g. 0 3 512): ', self._set_analog)
        elif k == 'c': self.ask('aux command: code [args], hex: ', self._raw_aux)
        elif k == 'L': self.ask('hex file (prefix @ = raw image from 8000h): ', self._load_file)
        elif k == 'N': self.ask('program name for downloads (max 39 chars): ', self._set_name)
        else: self.status = 'unknown emulator key'

    def prompt_key(self, k):
        label, text, cb = self.prompt
        if k in ('\n', '\r') or k == curses.KEY_ENTER:
            self.prompt = None
            try: cb(text)
            except Exception as e: self.status = 'error: %s' % e
        elif k == '\x1b': self.prompt = None
        elif k in ('\x7f', '\b') or k == curses.KEY_BACKSPACE: self.prompt[1] = text[:-1]
        elif isinstance(k, str) and k.isprintable(): self.prompt[1] += k

    def _toggle_input(self, t):
        p = int(t)
        port, bit = 0x20 + p // 8, 1 << (p % 8)
        active = bool(self.m.bus.inputs[port] & bit)       # currently inactive (bit set) -> activate
        self.m.set_din(p, active)
        self.status = 'input %d %s' % (p, 'active' if active else 'inactive')

    def _set_analog(self, t):
        mod, ch, val = (int(x, 0) for x in t.split())
        self.m.adc[mod].values[ch] = val & 0x3FF
        self.status = 'analog module %d channel %d = %d' % (mod, ch, val & 0x3FF)

    def restart(self):
        """Restart the system with aux command 3Ah. This is the only way to stop operator-started processes."""
        self.connect(); self.aux(0x3A); self._connected = False
        self.status = 'restart sent: all processes stopped, the system boots again'

    def _raw_aux(self, t):
        parts = [int(x, 16) for x in t.split()]
        self.connect(); self.aux(parts[0], *parts[1:])
        if parts[0] == 0x3A or parts[:2] == [0x20, 2]: self._connected = False     # the link restarts with the system

    def _set_name(self, t):
        self.prog_name = t.strip()[:39]
        self.status = 'program name: %r' % self.prog_name

    def _load_file(self, path):
        path = path.strip(); raw = path.startswith('@')
        text = open(os.path.expanduser(path.lstrip('@'))).read()
        self.download(bytes.fromhex(''.join(text.split())), raw=raw)

    # ------------------------------------------------------------- keys
    def map_key(self, k):
        if isinstance(k, int):
            return {curses.KEY_BACKSPACE: 0x08, curses.KEY_ENTER: 0x0D}.get(k)
        if k in NAT_IN: return ord(NAT_IN[k])
        if k in ('\n', '\r'): return 0x0D
        if k in ('\x7f', '\b'): return 0x08
        return ord(k) if ord(k) < 128 else None

    def on_key(self, k):
        if self.dbg: return self.dbg_key(k)
        if self.prompt: return self.prompt_key(k)
        if self.prefix:
            self.prefix = False; self.status = ''; return self.ctl_key(k)
        if k == PREFIX:
            self.prefix = True; self.status = 'Ctrl-] : q p h s i a l L N r x c v b d n R'; return
        b = self.map_key(k)
        if b is not None:
            self.m.con.rx.append(b)

    # ------------------------------------------------------------- one frame
    def frame(self):
        now = time.perf_counter(); dt = now - self.last; self.last = now
        while True:
            try: k = self.scr.get_wch()
            except curses.error: break
            self.on_key(k)
            if self.quit: return
        s0 = self.m.steps
        self.emulate(dt)
        if now - self.rate_t >= 1.0:
            self.rate = (self.m.steps - self.rate_s) / (now - self.rate_t); self.rate_t, self.rate_s = now, self.m.steps
        self.draw()

    def loop(self):
        while not self.quit:
            self.frame()

    # ------------------------------------------------------------- drawing
    def put(self, y, x, text, attr=0):
        h, w = self.scr.getmaxyx()
        if y >= h or x >= w: return
        try: self.scr.addstr(y, x, text[:max(0, w - x - (1 if y == h - 1 else 0))], attr)
        except curses.error: pass

    def draw(self):
        scr = self.scr; scr.erase(); h, w = scr.getmaxyx()
        if h < 26 or w < 80:
            self.put(0, 0, 'Terminal too small: need 80x26, have %dx%d' % (w, h)); scr.refresh(); return
        if self.dbg: self.draw_debugger()
        elif self.show_help: self.draw_help()
        elif self.show_panel and self.overlay: self.draw_panel(0, 0, w)
        else:
            self.draw_console()
            if self.show_panel and w >= 120: self.draw_panel(0, 82, w - 82)
        self.draw_status(h, w)
        if not (self.dbg or self.show_help or self.overlay) and not self.prompt:
            try:
                scr.move(self.term.r, self.term.c)
            except curses.error: pass
        scr.refresh()

    def text(self, row):
        s = ''.join(row)
        return s.translate(NAT_OUT) if self.national else s

    def draw_console(self):
        self.put(0, 0, '')
        for i, row in enumerate(self.term.g): self.put(i, 0, self.text(row).rstrip())
        for i in range(24): self.put(i, 80, '|')

    def draw_status(self, h, w):
        if self.prompt: line = self.prompt[0] + self.prompt[1] + '_'
        elif self.dbg and self.dbg['prompt']: line = self.dbg['prompt'][0] + self.dbg['prompt'][1] + '_'
        else:
            st = 'PAUSED ' if self.paused else ''
            line = '%s%s  | %.2f Msteps/s  x%s  ticks %d' % (st, self.status, self.rate / 1e6, SPEEDS[self.speed] or 'max', self.m.ticks)
        self.put(h - 2, 0, '-' * (w - 1))
        self.put(h - 1, 0, line, curses.A_REVERSE)

    def draw_help(self):
        for i, l in enumerate(HELP.split('\n')): self.put(i, 0, l)

    def draw_panel(self, y0, x0, width):
        m, r = self.m, self.m.bus.ram
        y = y0
        def line(txt, attr=0):
            nonlocal y; self.put(y, x0, txt, attr); y += 1
        line(' ID-7000  IPC/1 + SPC/1 ', curses.A_REVERSE)
        line(' steps %-12s ticks %d' % (format(m.steps, ','), m.ticks))
        state = PLC_STATE.get(r[0x4C02], str(r[0x4C02]))
        entry = r[0x4BD5] | r[0x4BD6] << 8
        line(' PLC %-7s entry %04X  aux frames %d' % (state, entry, self.aux_frames))
        nm = bytes(r[0x8000:0x8028]).split(b'\0')[0]
        line(' Program name: %s' % (nm.decode('latin1') if nm and all(32 <= c < 127 for c in nm) else '-'))
        line('')
        line(' Digital inputs  (ports 20-33, active low)', curses.A_BOLD)
        act = [p for p in range(160) if not (m.bus.inputs[0x20 + p // 8] >> (p % 8)) & 1]
        for g in range(0, 20, 5):
            line('  ' + ' '.join('%02X:%02X' % (0x20 + g + i, m.bus.inputs[0x20 + g + i]) for i in range(5)))
        line('  active: %s' % (', '.join(map(str, act[:14])) + (' ...' if len(act) > 14 else '') if act else 'none'))
        line(' Digital outputs (ports 10-17)', curses.A_BOLD)
        line('  ' + ' '.join('%02X:%02X' % (0x10 + i, m.bus.outputs[0x10 + i]) for i in range(8)))
        on = [p for p in range(64) if (m.bus.outputs[0x10 + p // 8] >> (p % 8)) & 1]
        line('  on:     %s' % (', '.join(map(str, on[:14])) + (' ...' if len(on) > 14 else '') if on else 'none'))
        line(' Analog (module: ch0..ch7)', curses.A_BOLD)
        for i, a in enumerate(m.adc): line('  %d: %s' % (i, ' '.join('%4d' % v for v in a.values)))
        line(' Break at: ' + (' '.join('%04X' % b for b in sorted(self.breaks)) or '-'))
        w = getattr(self.args, 'watch', None)
        if w is not None:
            bs = [r[(w + i) & 0xFFFF] for i in range(8)]
            line(' Watch %04X: %s  "%s"' % (w, ' '.join('%02X' % b for b in bs), ''.join(chr(b) if 32 <= b < 127 else '.' for b in bs)))
        room = self.scr.getmaxyx()[0] - 2 - y - 1                    # rows left above the status line
        line(' Aux link log', curses.A_BOLD)
        for l in self.log[-max(0, min(7, room)):]: line('  ' + l[:max(20, width - 3)])

    def draw_debugger(self):
        c, d, m = self.m.cpu, self.dbg, self.m
        rd = lambda a: m.bus.read(a & 0xFFFF)
        self.put(0, 0, ' DEBUGGER (built-in monitor) - %s ' % d['why'], curses.A_REVERSE)
        flags = ''.join(f if v else '-' for f, v in zip('SZAPC', (c.s, c.z, c.ac, c.p, c.cy)))
        self.put(2, 1, 'A=%02X  B=%02X C=%02X  D=%02X E=%02X  H=%02X L=%02X   SP=%04X  PC=%04X  flags %s  IE=%d'
                 % (c.a, c.b, c.c, c.d, c.e, c.h, c.l, c.sp, c.pc, flags, int(c.ie)))
        self.put(4, 1, 'Code', curses.A_BOLD)
        a = c.pc
        for i in range(10):
            n, t = disasm(rd, a)
            mark = '>' if i == 0 else (('*' if a in self.breaks else ' '))
            self.put(5 + i, 1, '%s %04X  %-9s %s' % (mark, a, ' '.join('%02X' % rd(a + j) for j in range(n)), t)); a += n
        self.put(4, 50, 'Stack', curses.A_BOLD)
        for i in range(6):
            sp = (c.sp + 2 * i) & 0xFFFF
            self.put(5 + i, 50, '%04X: %04X' % (sp, rd(sp) | rd(sp + 1) << 8))
        self.put(16, 1, 'Memory %04X' % d['mem'], curses.A_BOLD)
        for i in range(6):
            base = (d['mem'] + 16 * i) & 0xFFFF
            bs = [rd(base + j) for j in range(16)]
            self.put(17 + i, 1, '%04X  %s  %s' % (base, ' '.join('%02X' % b for b in bs), ''.join(chr(b) if 32 <= b < 127 else '.' for b in bs)))
        self.put(23, 1, 's step  c continue (RET)  g go  m dump  b breakpoint  x quit emulator')



# ----------------------------------------------------------------------------- self-test
class FakeScreen:
    """Just enough of a curses window for scripted tests (no terminal needed)."""
    def __init__(self, h=30, w=130):
        self.h, self.w, self.keys = h, w, []
        self.erase()
    def erase(self): self.g = [[' '] * self.w for _ in range(self.h)]; self.cur = (0, 0)
    def getmaxyx(self): return self.h, self.w
    def addstr(self, y, x, s, attr=0):
        for i, ch in enumerate(s):
            if 0 <= y < self.h and 0 <= x + i < self.w: self.g[y][x + i] = ch
    def move(self, y, x): self.cur = (y, x)
    def refresh(self): pass
    def get_wch(self):
        if not self.keys: raise curses.error('no input')
        return self.keys.pop(0)
    def text(self): return '\n'.join(''.join(r).rstrip() for r in self.g)


def selftest(rom):
    args = argparse.Namespace(ascii=False, fixed=150000, watch=0x7100)
    args.rom=rom
    scr = FakeScreen(); app = App(scr, args)
    def frames(n=6):
        for _ in range(n): app.frame()
    def press(s):
        scr.keys += list(s)
    frames(20)
    assert 'VELKOMMEN TIL IPC/1 OPERATIVSYSTEMET' in scr.text(), 'menu missing'
    assert 'VÆLG IMELLEM' in scr.text(), 'national mapping failed'
    print('1 boot + menu .......... ok')
    press('X\r'); frames(8)
    assert 'KOMMANDO' in scr.text(); print('2 console keyboard ..... ok')
    # PLC: demo program, run, toggle input 0, expect output 0 on
    press(PREFIX + 'l'); frames(1)
    press(PREFIX + 'r'); frames(1)
    assert app.m.bus.ram[0x4C02] == 3, 'PLC not running'
    press(PREFIX + 'i' + '0\r'); frames(6)
    assert app.m.dout(0), 'output 0 should be on'
    assert 'on:     0' in scr.text(), 'panel does not show output'
    press(PREFIX + 'i' + '0\r'); frames(6)
    assert not app.m.dout(0)
    print('3 aux download/run/input toggle ..... ok')
    press(PREFIX + 'a' + '0 1 700\r'); frames(2)
    assert app.m.adc[0].values[1] == 700; print('4 analog set ........... ok')
    press(PREFIX + 'v'); frames(1)
    assert '88.03.14' in scr.text(); print('5 version over aux ..... ok')
    # D command -> built-in debugger, then continue
    press('D\r'); frames(8)
    assert app.dbg and 'DEBUGGER' in scr.text() and 'CALL F008' in app.dbg['why'], 'debugger not entered'
    assert app.m.cpu.pc == 0xF008
    print('6 D enters debugger .... ok  (PC=%04X SP=%04X)' % (app.m.cpu.pc, app.m.cpu.sp))
    press('s'); frames(1); assert app.m.cpu.pc == 0xF009
    press('c'); frames(10)
    assert app.dbg is None and app.m.cpu.pc != 0xF009
    assert 'KOMMANDO' in scr.text() and 'VELKOMMEN' not in scr.text(), 'did not return to the menu after RET'
    print('7 debugger step/continue (RET, no reboot) ... ok')
    press(PREFIX + 'p'); frames(1); assert app.paused
    press(PREFIX + 'h'); frames(1); assert 'Ctrl-]  then' in scr.text(); print('8 pause / help ......... ok')
    # Fibonacci example process: load with L, start with P, watch 7100h, ESC returns to the menu
    here = os.path.dirname(os.path.abspath(__file__))
    app.paused = False; app.show_help = False
    press(PREFIX + 'l'); frames(1)                      # the PLC program from test 3 is still running
    assert 'download refused' in app.status and 'running' in app.status, 'download while running was not refused: %s' % app.status
    press(PREFIX + 'x'); frames(1)                      # stop it
    assert app.m.bus.ram[0x4C02] == 2
    press(PREFIX + 'N' + 'FIBONACCI\r'); frames(1)
    press(PREFIX + 'L' + os.path.join(here, 'examples', 'fib_noname.hex') + '\r'); frames(1)
    assert app.m.bus.ram[0x807C] == 0x21, 'fib.hex not downloaded'
    assert bytes(app.m.bus.ram[0x8000:0x800A]) == b'FIBONACCI\0', 'program name not at 8000h'
    press(PREFIX + 'v'); frames(1); assert 'FIBONACCI' in scr.text(), 'name missing in the version reply / panel'
    press(PREFIX + 'L' + '@' + os.path.join(here, 'examples', 'fib.hex') + '\r'); frames(1)     # raw image with its own header
    assert bytes(app.m.bus.ram[0x8000:0x800E]) == b'FIB-FROM-FILE\0' and app.m.bus.ram[0x807C] == 0x21, 'raw image not placed at 8000h'
    press('P\r'); frames(4); press('3\r'); frames(4); press('807C\r'); frames(6)
    vals = []
    for _ in range(40):
        frames(1); t = bytes(app.m.bus.ram[0x7100:0x7104]).decode('latin1')
        if all(c in '0123456789ABCDEF' for c in t) and (not vals or vals[-1] != t): vals.append(t)
    assert vals, 'the process wrote nothing at 7100h'
    fib = [0, 1]
    while fib[-1] + fib[-2] < 65536: fib.append(fib[-1] + fib[-2])
    ok = all(int(v, 16) in fib for v in vals) and int(vals[-1], 16) >= 8
    assert ok, 'fibonacci values wrong: %s' % vals
    assert 'Watch 7100: ' in scr.text() and '"%s.' % vals[-1] in scr.text(), 'panel watch line missing'
    press('\x1b'); frames(8)
    assert 'KOMMANDO' in scr.text(), 'ESC did not return to the menu while the process runs'
    assert app.m.bus.ram[0x4846] == 1
    print('9 Fibonacci process via L + P ... ok  (7100h shows: %s)' % ' '.join(vals))
    press(PREFIX + 'R'); frames(12)                     # restart: the only way to stop the process
    r = app.m.bus.ram; v1 = bytes(r[0x7100:0x7104]); frames(6); v2 = bytes(r[0x7100:0x7104])
    assert r[0x4846] == 0 and v1 == v2, 'restart did not stop the process'
    assert 'VELKOMMEN' in scr.text(), 'system did not boot again'
    press(PREFIX + 'v'); frames(1); assert 'aux link needs' not in app.status
    print('10 restart (Ctrl-] R) stops the process and boots again ... ok')
    print('\n--- screen dump ---'); app.show_help = False; app.paused = False; app.frame(); print(scr.text()[:2600])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rom', type=str, default='../../src/roms/sps_and_funk.bin', help='rom image')
    ap.add_argument('--ascii', action='store_true', help='show raw ROM characters instead of Danish letters')
    ap.add_argument('--tick-hz', type=int, default=500, help='timer ticks per second at speed x1 (default 500: the OS clock then counts real seconds)')
    ap.add_argument('--watch', type=lambda t: int(t, 16), default=None, metavar='ADDR', help='hex address whose 8 bytes are shown in the panel')
    ap.add_argument('--fixed', type=int, default=0, help='run this many steps per frame (testing)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest: return selftest(args.rom)
    locale.setlocale(locale.LC_ALL, '')

    def run(scr):
        try: curses.curs_set(1)
        except curses.error: pass
        curses.raw(); scr.keypad(True); scr.timeout(15)
        try: curses.set_escdelay(25)
        except AttributeError: os.environ['ESCDELAY'] = '25'
        App(scr, args).loop()
    curses.wrapper(run)


if __name__ == '__main__':
    main()
