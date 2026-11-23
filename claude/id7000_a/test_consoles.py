"""Simultaneous console sessions: run with  python3 test_consoles.py"""
import unittest, time
from consoles import build, telnet_filter, wait_quiet, NCH

show = lambda b: b.replace(b'\x00', b'').decode(errors='replace')

class MultiConsole(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.host, cls.greet = build()

    def type_all(self, lines):
        """Type lines on several channels with the keystrokes interleaved."""
        width = max(len(t) for t in lines.values()) + 1
        for i in range(width):
            for ch, t in lines.items():
                t += '\r'
                if i < len(t): self.m.feed(ch, t[i])
            self.m.run(20000)
        self.m.run(60000)

    def answers(self, channels=range(NCH)):
        """Poll every site, then collect what each console printed."""
        got = self.host.service_all()
        out = wait_quiet(self.m, list(channels))
        return got, {ch: show(b) for ch, b in out.items()}

    def test_0_every_site_comes_up(self):
        for ch in range(NCH):
            g = show(self.greet[ch])
            self.assertIn('ID-7000 *READY* (200UT/SIM) VERSION 01.02.83', g, ch)
            self.assertIn('CYBER LINK ESTABLISHED', g, ch)
            self.assertLess(g.index('*READY*'), g.index('CYBER LINK'), ch)
        self.assertEqual(self.host.active, set(range(NCH)))

    def test_1_independent_sessions(self):
        users = {0: 'ALICE', 3: 'BOB', 7: 'CAROL', 11: 'DAVE'}
        self.type_all({ch: f'LOGIN {u},{u}' for ch, u in users.items()})
        got, out = self.answers()
        self.assertEqual(set(got), set(users))
        for ch, u in users.items():
            self.assertEqual(got[ch][0], f'LOGIN {u},{u}')
            self.assertIn(f'USER {u} LOGGED IN', out[ch])
            for other in set(users.values()) - {u}: self.assertNotIn(other, out[ch])
        for ch in set(range(NCH)) - set(users): self.assertEqual(out[ch], '')
        # each session keeps its own state
        self.type_all({ch: 'STATUS' for ch in users})
        got, out = self.answers()
        for ch, u in users.items(): self.assertIn(f'USER {u}', out[ch])
        # WHO sees all of them, from any console
        self.type_all({3: 'WHO'})
        got, out = self.answers()
        for u in users.values(): self.assertIn(u, out[3])
        self.assertIn('*SITE 163', out[3])
        # logging one out leaves the others alone
        self.type_all({7: 'BYE'})
        got, out = self.answers()
        self.assertIn('CAROL LOG OFF', out[7])
        self.type_all({0: 'STATUS', 7: 'STATUS'})
        got, out = self.answers()
        self.assertIn('USER ALICE', out[0]); self.assertIn('NOT LOGGED IN', out[7])

    def test_2_all_twelve_at_once(self):
        self.type_all({ch: f'LOGIN U{ch},U{ch}' for ch in range(NCH)})
        got, out = self.answers()
        for ch in range(NCH): self.assertIn(f'USER U{ch} LOGGED IN', out[ch])
        self.type_all({ch: f'ECHO CONSOLE{ch}' for ch in range(NCH)})
        got, out = self.answers()
        self.assertEqual(sorted(got), list(range(NCH)))
        for ch in range(NCH): self.assertIn(f'CONSOLE{ch}\r\n/', out[ch])

    def test_3_idle_poll_is_quiet(self):
        got, out = self.answers()
        self.assertEqual(got, {}); self.assertFalse(any(out.values()))

class Server(unittest.TestCase):
    """Server loop end to end: three clients typing at once (socketpairs, so
    it runs where listening on a port is not allowed)."""
    def test_sessions(self):
        import socket
        from consoles import ConsoleServer
        srv = ConsoleServer(port=None, channels=3, verbose=False)
        socks = []
        for i in range(3):
            a, b = socket.socketpair(); srv.add_client(a, f'client{i}'); socks.append(b)
        a, b = socket.socketpair(); srv.add_client(a, 'extra')
        self.assertIn(b'ALL CONSOLES BUSY', b.recv(100)); b.close()
        for _ in range(20): srv.step()
        for i, s in enumerate(socks): s.sendall(f'LOGIN U{i},U{i}\r\nWHO\r\n'.encode())
        t0 = time.time()
        while time.time() - t0 < 60:
            srv.step()
            if all(c.sent_at is None and not c.inbuf for c in srv.conns.values()) \
               and time.time() - t0 > 3:
                for _ in range(40): srv.step()
                break
        outs = []
        for s in socks:
            s.setblocking(False); buf = b''
            try:
                while True:
                    d = s.recv(65536)
                    if not d: break
                    buf += d
            except BlockingIOError: pass
            outs.append(buf.decode(errors='replace')); s.close()
        for i, o in enumerate(outs):
            self.assertIn(f'USER U{i} LOGGED IN', o, o)
            self.assertNotIn('\xff', o)                      # no telnet negotiation
            self.assertEqual(o.count(f'LOGIN U{i}'), 0, o)   # client echoes, not us
            self.assertIn(f'*SITE {0o160 + i:o}', o)
            for j in range(3): self.assertIn(f'U{j}', o.split('WHO')[-1])
        self.assertEqual(sorted(c.ch for c in srv.conns.values()), [0, 1, 2])
        for _ in range(5): srv.step()
        self.assertEqual(srv.conns, {}); self.assertEqual(srv.host.system.sessions, {})

    def test_telnet_mode(self):
        import socket
        from consoles import ConsoleServer
        srv = ConsoleServer(port=None, channels=1, telnet=True, verbose=False)
        a, b = socket.socketpair(); srv.add_client(a, 'telnet')
        self.assertEqual(b.recv(6), b'\xff\xfb\x01\xff\xfb\x03')
        b.sendall(b'\xff\xfd\x01ECHO HI\r\n')
        for _ in range(5): srv.step()
        b.setblocking(False)
        self.assertIn(b'ECHO HI\r\n', b.recv(65536))           # server echoed it
        b.close(); srv.step()

class Login(unittest.TestCase):
    def test_gate(self):
        from cyber import CyberOS
        os_ = CyberOS()
        for cmd in ('HELP', 'STATUS', 'CATLIST', 'HELLO ALICE', 'ECHO HI', 'FOO'):
            self.assertIn('NOT LOGGED IN', os_.run(cmd), cmd)
        self.assertIn('USAGE', os_.run('LOGIN'))
        self.assertIn('USAGE', os_.run('LOGIN ALICE'))
        self.assertIn('IMPROPER PASSWORD', os_.run('LOGIN ALICE,BOB'))
        self.assertIsNone(os_.user)
        self.assertIn('USER ALICE LOGGED IN', os_.run('login alice,alice'))
        self.assertEqual(os_.run('ECHO HI'), 'HI')
        self.assertIn('ALICE LOG OFF', os_.run('BYE'))
        self.assertIn('NOT LOGGED IN', os_.run('ECHO HI'))
        self.assertIn('USER BOB LOGGED IN', os_.run('LOGIN BOB BOB'))

class Telnet(unittest.TestCase):
    def test_filter(self):
        st = {}
        self.assertEqual(telnet_filter(st, b'\xff\xfd\x01AB\x08C\r\n'), b'AC\r')
        self.assertEqual(telnet_filter(st, b'X\r\x00Y\n'), b'X\rY\r')

if __name__ == '__main__':
    unittest.main(verbosity=2)
