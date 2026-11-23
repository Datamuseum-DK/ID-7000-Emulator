"""Simultaneous console sessions on the ID-7000.

The board-5 ROM runs 12 async console channels (USARTs at 60h-77h). Each
channel is its own Mode-4 "site" on the Cyber sync link:

    console channel n  <->  site address 70h+n  (the ROM prints it in octal,
                             e.g. "[CYBER LINK: SITE ADDRESS 161 NOT ACTIVE]")

A site only goes active once the host has polled it. After that every
channel has its own poll / text / write / ACK cycle, so the host just has to
poll each site in turn and keep one CyberOS session per channel.

    MultiCyberHost   per-channel CyberOS sessions over one sync link
    ConsoleServer    TCP front end: each connection gets a free channel,
                     all of them share one emulated ID-7000 + Cyber host

Run:  python3 consoles.py [--port 7000] [--channels 12]
then  nc 127.0.0.1 7000  (or telnet) from as many terminals as you like.

By default the client is expected to work line by line and echo locally
(nc, or telnet on a non-23 port), so the server sends nothing but console
output. --telnet makes the server negotiate WILL ECHO / WILL SGA and echo
typed characters itself, for clients that run character-at-a-time.
"""
import time
from sync import CyberHost as _LinkHost, frame, ENQ
from cyber import CyberOS, clean, to_display, WRITE, END_TEXT

NCH = 12
TEXT = 0x13                 # terminal -> host: text block (ctl in poll reply)

def find_rom(name='board5_eproms_0_to_6.bin'):
    import os
    for d in ('roms', '../../src/roms/ID7K0018'):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), d, name)
        if os.path.exists(p): return p
    raise FileNotFoundError(name)

class Cyber:
    """Shared host state: one CyberOS session per channel + a 'who' table."""
    def __init__(self, name='CYBER 170'):
        self.name = name; self.sessions = {}
    def session(self, ch):
        if ch not in self.sessions: self.sessions[ch] = SessionOS(self, ch)
        return self.sessions[ch]
    def drop(self, ch):
        self.sessions.pop(ch, None)

class SessionOS(CyberOS):
    """CyberOS for one console, aware of the other sessions on the host."""
    def __init__(self, system, ch):
        super().__init__(system.name); self.system = system; self.channel = ch
    def cmd_HELP(self, a):
        return super().cmd_HELP(a) + '\n WHO  TERM'
    def cmd_WHO(self, a):
        rows = [f' {"*" if ch == self.channel else " "}SITE {0x70 + ch:o}  CH {ch:>2}  '
                f'{s.user or "(NOT LOGGED IN)"}'
                for ch, s in sorted(self.system.sessions.items())]
        return '\n'.join(rows) or ' NO SESSIONS'
    def cmd_TERM(self, a):
        return f' CHANNEL {self.channel}  SITE ADDRESS {0x70 + self.channel:o}'

class MultiCyberHost(_LinkHost):
    """Cyber host driving every console channel over the one sync link."""
    def __init__(self, m, s, system=None, dev=0x60, log=None):
        super().__init__(m, s)
        self.system = system or Cyber(); self.dev = dev
        self.active = set(); self.log = log or (lambda *a: None)

    # Faster than sync.CyberHost._send: stop once the reply frame is complete.
    def exchange(self, addr, dev, ctl, data=b'', steps=3000, limit=300000):
        s, m = self.s, self.m
        s.tx.clear()
        for byte in frame(addr, dev, ctl, data):
            s.rx.append(byte); m.irq(2); m.run(steps)
        ran = 0
        while ran < limit:
            m.run(5000); ran += 5000
            tx = bytes(s.tx); i = tx.find(b'\x01')
            if i >= 0 and 0 <= tx.find(b'\x03', i + 4) < len(tx) - 1: break
        m.run(5000)                         # let the ROM finish the transmit
        return self.parse(bytes(s.tx))

    def activate(self, ch):
        """Bring site 70h+ch up (the ROM prints [CYBER LINK ESTABLISHED])."""
        r = self.poll(ch, self.dev)
        if r is not None: self.active.add(ch)
        return r

    def service(self, ch):
        """Poll one channel; if it sent text, run it in that channel's session.
        Returns (input_text, reply_text) or None."""
        if ch not in self.active and self.activate(ch) is None: return None
        r = self.poll(ch, self.dev)
        if r is None:
            self.log(ch, 'no reply to poll'); self.active.discard(ch); return None
        if r['ctl'] != TEXT: return None
        text = clean(r['data'])
        reply = self.system.session(ch).run(text) if text else ''
        ack = self.say(ch, to_display(reply), WRITE, END_TEXT, self.dev)   # also ACKs
        self.log(ch, repr(text), '->', repr(reply), 'ack', ack and hex(ack['ctl']))
        return text, reply

    def service_all(self, channels=None):
        """One round-robin pass; returns {channel: (input, reply)}."""
        out = {}
        for ch in (range(NCH) if channels is None else channels):
            r = self.service(ch)
            if r: out[ch] = r
        return out

    def logout(self, ch):
        self.system.drop(ch)

def build(rom_file=None, log=None):
    """Boot an ID-7000 with the sync link attached and every site active.
    Returns (machine, host, greetings) where greetings[ch] is what the
    channel's console showed during boot + link-up."""
    from machine import Machine
    from sync import Sync8251, attach
    m = Machine(rom_file or find_rom()); s = Sync8251(); attach(m, s); banner0 = m.boot()
    host = MultiCyberHost(m, s, log=log)
    for ch in range(NCH): host.activate(ch)
    greet = wait_quiet(m, range(NCH))
    greet[0] = banner0 + greet[0]
    return m, host, greet

# --------------------------------------------------------------- TCP front end
IAC = 0xFF

def telnet_filter(state, data):
    """Strip telnet IAC sequences, map CR LF / CR NUL / LF to CR.
    state is a dict kept per connection."""
    out = bytearray()
    for b in data:
        st = state.get('s')
        if st == 'iac':
            state['s'] = 'opt' if b in (0xFB, 0xFC, 0xFD, 0xFE) else \
                         'sb' if b == 0xFA else None
            continue
        if st == 'opt': state['s'] = None; continue
        if st == 'sb':
            if b == 0xF0: state['s'] = None
            continue
        if b == IAC: state['s'] = 'iac'; continue
        if state.get('cr') and b in (0x0A, 0x00): state['cr'] = False; continue
        state['cr'] = b == 0x0D
        if b == 0x0A: b = 0x0D
        if b in (0x08, 0x7F) and out: out.pop(); continue
        out.append(b)
    return bytes(out)

QUIET = 60000               # steps without console output = "done printing"

def wait_quiet(m, channels, quiet=QUIET, limit=3000000, chunk=10000):
    """Run until none of channels has printed for quiet steps.
    Returns {channel: bytes printed meanwhile}."""
    out = {ch: bytearray() for ch in channels}; idle = ran = 0
    while idle < quiet and ran < limit:
        m.run(chunk); ran += chunk; idle += chunk
        for ch in channels:
            b = m.take_tx(ch)
            if b: out[ch] += b; idle = 0
    return {ch: bytes(b) for ch, b in out.items()}

class Conn:
    def __init__(self, sock, peer, ch, now):
        self.sock = sock; self.peer = peer; self.ch = ch
        self.tstate = {}; self.inbuf = bytearray()
        self.last_out = now          # machine step of the last console output
        self.sent_at = None          # step a line went to the ROM, until polled
        self.last_poll = 0.0

class ConsoleServer:
    """Every TCP connection is one console; all share one emulated ID-7000.

    The loop alternates: read sockets, run the CPU a slice, copy each
    console's USART TX to its socket, and drive each console:
      * the ROM discards keystrokes that arrive while it is printing, so typed
        lines wait in Conn.inbuf until that console has been quiet for QUIET
        steps and its previous line has been answered;
      * a line handed to the ROM is followed by a poll of that site, which
        brings the text to the host and its answer back;
      * an idle poll every few seconds keeps the site alive, like a real host.
    """
    def __init__(self, port=7000, bind='127.0.0.1', channels=NCH, telnet=False,
                 idle_poll=5.0, rom_file=None, verbose=True):
        self.say = print if verbose else (lambda *a: None)
        self.m, self.host, self.greet = build(rom_file,
                                              log=lambda *a: self.say('  cyber ch', *a))
        self.channels = list(range(channels)); self.telnet = telnet
        self.idle_poll = idle_poll; self.conns = {}
        self.srv = None
        if port is not None:                          # port=None: add_client() only
            import socket
            self.srv = socket.socket()
            self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.srv.bind((bind, port)); self.srv.listen(len(self.channels))
            self.srv.setblocking(False)
            self.say(f'id7000: {len(self.channels)} consoles on {bind}:{port}')

    def free_channel(self):
        used = {c.ch for c in self.conns.values()}
        return next((ch for ch in self.channels if ch not in used), None)

    def _accept(self):
        self.add_client(*self.srv.accept())

    def add_client(self, sock, peer='local'):
        """Attach an already connected socket as a new console."""
        ch = self.free_channel()
        if ch is None:
            sock.sendall(b'\r\nID-7000: ALL CONSOLES BUSY\r\n'); sock.close(); return
        sock.setblocking(False)
        if self.telnet: sock.sendall(b'\xff\xfb\x01\xff\xfb\x03')   # WILL ECHO, WILL SGA
        c = self.conns[sock] = Conn(sock, peer, ch, self.m.steps)
        self.m.ch[ch].rx.clear(); self.m.take_tx(ch)
        self._send(c, self.greet[ch] or b'\r\nID-7000 CONSOLE %d\r\n' % ch)
        self.say(f'id7000: {peer} -> console {ch}')

    def _close(self, c):
        if self.conns.pop(c.sock, None) is None: return
        try: c.sock.close()
        except OSError: pass
        self.host.logout(c.ch); self.m.ch[c.ch].rx.clear(); self.m.take_tx(c.ch)
        self.say(f'id7000: {c.peer} left console {c.ch}')

    def _send(self, c, data):
        data = data.replace(b'\x00', b'')
        if not data: return
        try: c.sock.sendall(data)
        except OSError: self._close(c)

    def _read(self, c):
        try: data = c.sock.recv(4096)
        except BlockingIOError: return
        except OSError: data = b''
        if not data: self._close(c); return
        data = telnet_filter(c.tstate, data)
        if not data: return
        if self.telnet: self._send(c, data.replace(b'\r', b'\r\n'))   # we echo
        c.inbuf += data

    def _drive(self, c, now):
        m = self.m; st = m.steps
        out = m.take_tx(c.ch)
        if out: c.last_out = st; self._send(c, out)
        if c.sock not in self.conns: return
        if c.sent_at is not None:                     # line typed: poll for it
            if st - c.sent_at >= 40000:
                c.sent_at = None; c.last_poll = now; self.host.service(c.ch)
                c.last_out = m.steps                  # answer is on its way
            return
        if c.inbuf and st - c.last_out >= QUIET:      # release one line
            i = c.inbuf.find(b'\r')
            chunk = c.inbuf if i < 0 else c.inbuf[:i + 1]
            m.feed(c.ch, bytes(chunk)); del c.inbuf[:len(chunk)]
            if i >= 0: c.sent_at = st
            return
        if now - c.last_poll > self.idle_poll and not c.inbuf:
            c.last_poll = now; self.host.service(c.ch)

    def step(self, timeout=0.01):
        import select
        socks = [c.sock for c in self.conns.values()] + ([self.srv] if self.srv else [])
        r, _, _ = select.select(socks, [], [], timeout if not self.conns else 0)
        for s in r:
            if s is self.srv: self._accept()
            elif s in self.conns: self._read(self.conns[s])
        self.m.run(20000)
        now = time.time()
        for c in list(self.conns.values()): self._drive(c, now)

    def serve_forever(self):
        try:
            while True: self.step()
        except KeyboardInterrupt: pass
        finally:
            for c in list(self.conns.values()): self._close(c)
            if self.srv: self.srv.close()

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='ID-7000 with simultaneous console sessions')
    ap.add_argument('--port', type=int, default=7000)
    ap.add_argument('--bind', default='127.0.0.1')
    ap.add_argument('--channels', type=int, default=NCH, help='consoles to offer (1-12)')
    ap.add_argument('--telnet', action='store_true',
                    help='negotiate WILL ECHO/SGA and echo typed characters '
                         '(default: client echoes locally, nothing extra is sent)')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--rom')
    a = ap.parse_args()
    ConsoleServer(a.port, a.bind, max(1, min(NCH, a.channels)), a.telnet,
                  rom_file=a.rom, verbose=not a.quiet).serve_forever()
