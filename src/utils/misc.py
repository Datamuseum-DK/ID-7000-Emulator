


def isprintable(value : int):
    return 32 <= value < 127


def ascii(value : int):
    if isprintable(value):
        return chr(value)
    return '.'


def hexdump(lst, width, maxbytes):
    hexdp = '0000: '
    ascii = ''
    l = 0
    for i, d in enumerate(lst):
        if i > maxbytes:
            break
        hexdp += f'{d:02x} '
        ascii += chr(d) if 32 <= d < 127 else '.'
        l += 1
        if l == width:
            print(hexdp, ascii)
            hexdp = f'{i+1:04x}: '
            ascii = ''
            l = 0
    if len(ascii) != width:
        print(hexdp, ascii)
