"""Simple CDC Cyber host emulator for the ID-7000.

Speaks the Mode-4 style framing already used by sync.py:
    SYN SYN SYN SOH addr dev ctl data... ETX LRC
The host polls the terminal (ctl ENQ). When the terminal answers with text
the user typed, the host runs it through a tiny command interpreter and
writes the answer back (ctl 11h, text + ESC B), followed by a "/" prompt.

Three layers, so it can be driven in-process or over a socket:
    Mode4Decoder  bytes from the terminal -> frame dicts
    CyberOS       command line -> reply text  (the "operating system")
    CyberHost     poll / interpret / write loop on top of sync.CyberHost
    serve_tcp()   same loop over a raw TCP byte stream (external terminal)
"""
import time
from sync import CyberHost as _LinkHost, frame, SOH, ETX, ENQ, SYN

WRITE = 0x11            # host -> terminal text write (see sync.CyberHost.say)
END_TEXT = b'\x1bB'     # trailer the ROM expects after display text

def lrc(body):
    l = 0xFE
    for b in body: l ^= b
    return l & 0x7F

class Mode4Decoder:
    """Incremental decoder: feed() raw link bytes, get complete frames back."""
    def __init__(self): self.buf = bytearray(); self.bad_lrc = 0
    def feed(self, data):
        self.buf += data; out = []
        while True:
            i = self.buf.find(SOH)
            if i < 0: self.buf.clear(); return out
            e = self.buf.find(ETX, i + 1)
            if e < 0 or e + 1 >= len(self.buf):
                del self.buf[:i]; return out          # wait for ETX + LRC
            body = bytes(self.buf[i + 1:e + 1]); got = self.buf[e + 1]
            del self.buf[:e + 2]
            if len(body) < 4: continue
            ok = lrc(body) == (got & 0x7F)
            if not ok: self.bad_lrc += 1
            out.append(dict(addr=body[0], dev=body[1], ctl=body[2],
                            data=body[3:-1], lrc=got, lrc_ok=ok))

def clean(data):
    """Terminal input -> printable command text (drops ESC pairs, controls)."""
    out = []; i = 0
    while i < len(data):
        b = data[i]
        if b == 0x1B: i += 2; continue
        if 32 <= b < 127: out.append(chr(b))
        i += 1
    return ''.join(out).strip()

class CyberOS:
    """A very small NOS-flavoured command interpreter.

    A session starts logged out: the only command accepted is
        LOGIN USER,PASSWORD      (password = user name, e.g. LOGIN ALICE,ALICE)
    BYE/LOGOUT returns to the logged-out state."""
    LOGGED_OUT_OK = ('LOGIN',)

    FILES = {'HELLO': 'PROGRAM HELLO\n  PRINT *, \'HELLO FROM THE CYBER\'\n  END',
             'README': 'THIS IS A SIMULATED CDC CYBER HOST.\nTYPE HELP FOR COMMANDS.',
             'JOBLOG': '10.00.00 JOB STARTED\n10.00.01 JOB ENDED'}

    def __init__(self, name='CYBER 170'):
        self.name = name;
        self.user = None;
        self.lines = 0
        self.started = time.time()

    def banner(self):
        return f'{self.name} EMULATOR  {time.strftime("%y/%m/%d. %H.%M.%S.")}\nREADY.'

    def run(self, line):
        """Return reply text for one command line ('' = no reply)."""
        line = line.strip().upper()
        if not line: return ''
        self.lines += 1
        verb, _, arg = line.replace(',', ' ').partition(' ')
        arg = arg.strip()
        if self.user is None and verb not in self.LOGGED_OUT_OK:
            return ' NOT LOGGED IN. TYPE LOGIN USER,PASSWORD'
        f = getattr(self, 'cmd_' + verb, None)
        return f(arg) if f else f' ILLEGAL COMMAND: {verb}'

    def cmd_HELP(self, a):
        return ('COMMANDS:\n LOGIN USER,PASSWORD  BYE/LOGOUT  DATE  TIME\n'
                ' ECHO TEXT  CATLIST  LIST FILE  STATUS  HELP')
    @staticmethod
    def check_password(user, password):
        return password == user
    
    def cmd_LOGIN(self, a):
        user, _, password = a.partition(' ')
        password = password.strip()
        if not user or not password: return ' USAGE: LOGIN USER,PASSWORD'
        if not self.check_password(user, password): return ' IMPROPER PASSWORD.'
        self.user = user
        return f'{self.banner()}\nUSER {self.user} LOGGED IN.'
    
    def cmd_BYE(self, a):
        u, self.user = self.user, None
        return f'{u or "NOBODY"} LOG OFF  {time.strftime("%H.%M.%S.")}'
    
    cmd_LOGOUT = cmd_BYE
    
    def cmd_DATE(self, a): return time.strftime(' %y/%m/%d.')
    def cmd_TIME(self, a): return time.strftime(' %H.%M.%S.')
    def cmd_ECHO(self, a): return a
    def cmd_CATLIST(self, a):
        return '\n'.join(f' {n:<8} {len(t):>5} CHARS' for n, t in self.FILES.items())
    def cmd_LIST(self, a):
        t = self.FILES.get(a)
        return t if t is not None else f' FILE {a or "?"} NOT FOUND.'
    def cmd_STATUS(self, a):
        up = int(time.time() - self.started)
        return (f' HOST {self.name}  UP {up}S  COMMANDS {self.lines}\n'
                f' USER {self.user or "NONE"}')

def to_display(text, prompt=True):
    """Reply text -> bytes for a WRITE frame: CR LF line ends, '/' prompt."""
    body = text.replace('\n', '\r\n') + ('\r\n' if text else '')
    if prompt: body += '/'
    return body.encode('latin1')

class CyberHost(_LinkHost):
    """In-process host wired to Machine + Sync8251 (see sync.attach).

    service() = one poll; if the terminal sent text, interpret and answer.
    Returns (input_text, reply_text) or None when the terminal had nothing.
    """
    def __init__(self, m, s, os_=None, channel=0, dev=0x60, log=None):
        super().__init__(m, s)
        self.os = os_ or CyberOS(); self.channel = channel; self.dev = dev
        self.log = log or (lambda *a: None)

    def service(self):
        r = self.poll(self.channel, self.dev)
        if r is None: self.log('no reply to poll'); return None
        self.log('poll reply', hex(r['ctl']), r['data'])
        text = clean(r['data'])
        if not text: return None
        reply = self.os.run(text)
        ack = self.say(self.channel, to_display(reply), WRITE, END_TEXT, self.dev)
        self.log('write ack', ack and hex(ack['ctl']))
        return text, reply

def serve_tcp(port=6610, host='127.0.0.1', poll_interval=0.2, channel=0,
              dev=0x60, verbose=True):
    """Act as the Cyber end of a raw TCP link: whatever the ID-7000 side writes
    to the socket is its sync-line TX, whatever we write is its sync-line RX."""
    import socket
    os_ = CyberOS(); addr = 0x70 + channel
    say = print if verbose else (lambda *a: None)
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port)); srv.listen(1)
    say(f'cyber: listening on {host}:{port}')
    while True:
        conn, peer = srv.accept(); say('cyber: terminal connected', peer)
        conn.settimeout(poll_interval); dec = Mode4Decoder()
        try:
            while True:
                conn.sendall(frame(addr, dev, ENQ))
                try: data = conn.recv(4096)
                except socket.timeout: continue
                if not data: break
                for f in dec.feed(data):
                    text = clean(f['data'])
                    if not text: continue
                    reply = os_.run(text); say(f'cyber: {text!r} -> {reply!r}')
                    conn.sendall(frame(addr, dev, WRITE, to_display(reply) + END_TEXT))
        except OSError as e: say('cyber: link error', e)
        finally: conn.close(); say('cyber: terminal disconnected')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Simple CDC Cyber host for the ID-7000')
    ap.add_argument('--port', type=int, default=6610)
    ap.add_argument('--bind', default='127.0.0.1')
    ap.add_argument('--console', action='store_true',
                    help='no link: just try the command interpreter on stdin')
    a = ap.parse_args()
    if a.console:
        o = CyberOS(); print(o.banner())
        while True:
            try: print(o.run(input('/')))
            except EOFError: break
    else:
        serve_tcp(a.port, a.bind)
