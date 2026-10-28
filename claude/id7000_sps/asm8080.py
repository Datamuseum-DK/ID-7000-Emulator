#!/usr/bin/env python3
"""Tiny two-pass Intel 8080 assembler (no macros).

    python3 asm8080.py prog.asm [-o prog.bin] [--hex prog.hex] [-l] [-D NAME=VALUE ...]

Syntax: LABEL: MNEMONIC operands ; comment      directives: ORG, EQU, DB, DW, DS
Numbers: 1234, 0x1F, 1FH, 101B, 'A'.  Expressions: + - * / ( ) $ (current address), LOW(x), HIGH(x).
"""
import argparse, re, sys

REG = {'B': 0, 'C': 1, 'D': 2, 'E': 3, 'H': 4, 'L': 5, 'M': 6, 'A': 7}
RP = {'B': 0, 'D': 1, 'H': 2, 'SP': 3}
RPP = {'B': 0, 'D': 1, 'H': 2, 'PSW': 3}
ALU = {'ADD': 0x80, 'ADC': 0x88, 'SUB': 0x90, 'SBB': 0x98, 'ANA': 0xA0, 'XRA': 0xA8, 'ORA': 0xB0, 'CMP': 0xB8}
ALUI = {'ADI': 0xC6, 'ACI': 0xCE, 'SUI': 0xD6, 'SBI': 0xDE, 'ANI': 0xE6, 'XRI': 0xEE, 'ORI': 0xF6, 'CPI': 0xFE}
COND = ['NZ', 'Z', 'NC', 'C', 'PO', 'PE', 'P', 'M']
NOARG = {'NOP': 0x00, 'HLT': 0x76, 'RLC': 0x07, 'RRC': 0x0F, 'RAL': 0x17, 'RAR': 0x1F, 'DAA': 0x27, 'CMA': 0x2F,
         'STC': 0x37, 'CMC': 0x3F, 'XCHG': 0xEB, 'XTHL': 0xE3, 'SPHL': 0xF9, 'PCHL': 0xE9, 'EI': 0xFB, 'DI': 0xF3,
         'RET': 0xC9}
ABS16 = {'JMP': 0xC3, 'CALL': 0xCD, 'LDA': 0x3A, 'STA': 0x32, 'LHLD': 0x2A, 'SHLD': 0x22}
for i, c in enumerate(COND):
    ABS16['J' + c] = 0xC2 | i << 3
    ABS16['C' + c] = 0xC4 | i << 3
    NOARG['R' + c] = 0xC0 | i << 3


class AsmError(Exception):
    pass


def split_operands(s):
    out, cur, q = [], '', False
    for ch in s:
        if ch == "'": q = not q
        if ch == ',' and not q: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out


def strip_comment(line):
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q: q = None
        elif ch in "'\"": q = ch
        elif ch == ';': return line[:i]
    return line


def number(tok):
    t = tok.strip()
    if len(t) == 3 and t[0] == t[2] == "'": return ord(t[1])
    if re.fullmatch(r'0[xX][0-9a-fA-F]+', t): return int(t, 16)
    if re.fullmatch(r'[0-9][0-9a-fA-F]*[hH]', t): return int(t[:-1], 16)
    if re.fullmatch(r'[01]+[bB]', t): return int(t[:-1], 2)
    if re.fullmatch(r'[0-9]+', t): return int(t)
    raise ValueError(tok)


def evaluate(expr, syms, pc):
    def sub(m):
        t = m.group(0)
        if t == '$': return str(pc)
        try: return str(number(t))
        except ValueError: pass
        if t.upper() in ('LOW', 'HIGH'): return t.upper()
        if t in syms: return str(syms[t])
        raise AsmError('undefined symbol %s' % t)
    e = re.sub(r"'.'|\$|0[xX][0-9a-fA-F]+|[0-9][0-9a-fA-F]*[hH]|[A-Za-z_][A-Za-z_0-9]*|[0-9]+", sub, expr)
    e = e.replace('/', '//')
    return eval(e, {'__builtins__': {}}, {'LOW': lambda x: x & 255, 'HIGH': lambda x: (x >> 8) & 255})


def assemble(text, defines=None):
    syms = dict(defines or {})
    lines = []
    for n, raw in enumerate(text.split('\n'), 1):
        s = strip_comment(raw).strip()
        if not s: continue
        label = None
        m = re.match(r'^([A-Za-z_][A-Za-z_0-9]*):\s*(.*)$', s)
        if m: label, s = m.group(1), m.group(2)
        m = re.match(r'^([A-Za-z_][A-Za-z_0-9]*)\s+EQU\s+(.*)$', s, re.I)
        if m: label, s = None, 'EQU ' + m.group(1) + ' ' + m.group(2)
        lines.append((n, label, s, raw))
    out = {}
    listing = []
    for pas in (1, 2):
        pc = 0; org = None; image = {}; listing = []
        for n, label, s, raw in lines:
            if label:
                if pas == 1 and label in syms and label not in (defines or {}): raise AsmError('line %d: duplicate label %s' % (n, label))
                if label not in (defines or {}): syms[label] = pc
            if not s:
                continue
            parts = s.split(None, 1); op = parts[0].upper(); rest = parts[1] if len(parts) > 1 else ''
            ops = split_operands(rest)
            data = b''
            try:
                ev = lambda e: evaluate(e, syms, pc) if pas == 2 else 0
                if op == 'ORG': pc = evaluate(ops[0], syms, pc); org = pc if org is None else org; continue
                elif op == 'EQU':
                    name, expr = rest.split(None, 1)
                    if name not in (defines or {}):
                        try: syms[name] = evaluate(expr, syms, pc)
                        except AsmError:
                            if pas == 2: raise
                            syms[name] = 0
                    continue
                elif op == 'DB':
                    b = bytearray()
                    for o in ops:
                        if len(o) >= 2 and o[0] == '"' and o[-1] == '"': b += o[1:-1].encode('latin1')
                        else: b.append(ev(o) & 255)
                    data = bytes(b)
                elif op == 'DW': data = b''.join((ev(o) & 0xFFFF).to_bytes(2, 'little') for o in ops)
                elif op == 'DS': data = bytes(ev(ops[0]) if pas == 2 else 0)
                elif op in NOARG: data = bytes([NOARG[op]])
                elif op == 'MOV': data = bytes([0x40 | REG[ops[0].upper()] << 3 | REG[ops[1].upper()]])
                elif op == 'MVI': data = bytes([0x06 | REG[ops[0].upper()] << 3, ev(ops[1]) & 255])
                elif op == 'LXI': data = bytes([0x01 | RP[ops[0].upper()] << 4]) + (ev(ops[1]) & 0xFFFF).to_bytes(2, 'little')
                elif op == 'INR': data = bytes([0x04 | REG[ops[0].upper()] << 3])
                elif op == 'DCR': data = bytes([0x05 | REG[ops[0].upper()] << 3])
                elif op == 'INX': data = bytes([0x03 | RP[ops[0].upper()] << 4])
                elif op == 'DCX': data = bytes([0x0B | RP[ops[0].upper()] << 4])
                elif op == 'DAD': data = bytes([0x09 | RP[ops[0].upper()] << 4])
                elif op == 'PUSH': data = bytes([0xC5 | RPP[ops[0].upper()] << 4])
                elif op == 'POP': data = bytes([0xC1 | RPP[ops[0].upper()] << 4])
                elif op in ALU: data = bytes([ALU[op] | REG[ops[0].upper()]])
                elif op in ALUI: data = bytes([ALUI[op], ev(ops[0]) & 255])
                elif op in ABS16: data = bytes([ABS16[op]]) + (ev(ops[0]) & 0xFFFF).to_bytes(2, 'little')
                elif op == 'LDAX': data = bytes([{'B': 0x0A, 'D': 0x1A}[ops[0].upper()]])
                elif op == 'STAX': data = bytes([{'B': 0x02, 'D': 0x12}[ops[0].upper()]])
                elif op == 'IN': data = bytes([0xDB, ev(ops[0]) & 255])
                elif op == 'OUT': data = bytes([0xD3, ev(ops[0]) & 255])
                elif op == 'RST': data = bytes([0xC7 | (ev(ops[0]) & 7) << 3])
                else: raise AsmError('unknown mnemonic %s' % op)
            except (KeyError, IndexError):
                raise AsmError('line %d: bad operands: %s' % (n, raw.strip()))
            except AsmError as e:
                raise AsmError('line %d: %s' % (n, e))
            if pas == 2:
                listing.append((pc, data, raw.rstrip()))
                for i, b in enumerate(data): image[pc + i] = b
            pc += len(data)
    if not image: return 0, b'', syms, listing
    lo = min(image); hi = max(image)
    blob = bytes(image.get(a, 0) for a in range(lo, hi + 1))
    return lo, blob, syms, listing


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('source'); ap.add_argument('-o', help='binary output'); ap.add_argument('--hex', help='text file of hex bytes')
    ap.add_argument('-l', action='store_true', help='print a listing'); ap.add_argument('-D', action='append', default=[], metavar='NAME=VALUE')
    a = ap.parse_args()
    defs = {k: evaluate(v, {}, 0) for k, v in (d.split('=', 1) for d in a.D)}
    try: org, blob, syms, lst = assemble(open(a.source).read(), defs)
    except AsmError as e: sys.exit('error: %s' % e)
    if a.l:
        for pc, data, raw in lst:
            print('%04X  %-12s %s' % (pc, data[:4].hex(' ') + ('..' if len(data) > 4 else ''), raw))
    print('assembled %d bytes at %04X-%04X' % (len(blob), org, org + len(blob) - 1), file=sys.stderr)
    if a.o: open(a.o, 'wb').write(blob)
    if a.hex:
        open(a.hex, 'w').write('\n'.join(blob[i:i + 16].hex(' ') for i in range(0, len(blob), 16)) + '\n')


if __name__ == '__main__':
    main()
