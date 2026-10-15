from multiprocessing import shared_memory


"""Memory utilities used on top of Korarev's z80 emulator"""

class Memory():

    def __init__(self, m):
        self.mem = m.memory
        self.sz = len(m.memory)
        self.shm = shared_memory.SharedMemory(name='id7k_shm', create=False, size=65536, track=False)
        self.verbose = True


    def print(self, s):
        if self.verbose:
            print(s)


    def clear(self, val: int):
        # Clear memory (set to val)
        for i in range(self.sz):
            self.writeu8(i, val)


    def loader(self, program : dict) -> int:
        # The main program loader
        print(f'loading program: {program["descr"]}')
        pc = program["start"]
        for datatype, source, addr in program["data"]:
            if datatype == "file":
                self._loadfile(source, addr)
            elif datatype == "snippet":
                self._loaddata(source, addr)
            else:
                print(f"Ignoring unknown data soure: {datatype}")
        return pc


    # This should be the only place we reference self.mem and shm for writes
    def writeu8(self, addr: int, val: int):
        assert 0 <= val <= 255
        self.mem[addr] = val
        self.shm.buf[addr] = val

    def writeu16(self, addr: int, val: int):
        hi = val >> 8
        lo = val & 0xFF
        self.writeu8(addr  , lo)
        self.writeu8(addr+1, hi)

    # This should be the only place to referenve mem for reads
    def getu8(self, address: int) -> int:
        # Get byte from memory
        val = self.mem[address]
        assert 0 <= val <= 255
        return val


    def getu16(self, address: int):
        # Get 2-byte word from memory
        return self.getu8(address) + (self.getu8(address+1) << 8)


    def getu32(self, address: int):
        # Get 4-byte word from memory
        lo = self.getu16(address)
        hi = self.getu16(address+2)
        return lo + (hi << 16)


    def _loadfile(self, file: str, address: int):
        # Helper code to load a file into a specidied address
        with open(file, 'rb') as fh:
            block = list(fh.read())
            assert len(block) + address < 65535
            for i, d in enumerate(block):
                self.writeu8(address +i, d)
            print(f'loaded {len(block)} bytes from {file} at address {address:04x}h')


    def _loaddata(self, data: list, address: int):
        # Helper code to load a list of bytes into a specified address
        for i, d in enumerate(data):
            self.writeu8(address+i, d)
        print(f'loaded {len(data)} bytes from list at address {address:04x}h')


if __name__ == '__main__':

    class Standin():
        def __init__(self):
            self.memory = [0 for i in range(65536)]
            self.memory[0] = 0
            self.memory[1] = 1
            self.memory[2] = 2
            self.memory[3] = 3

    standin = Standin()
    mem = Memory(standin)

    assert mem.getu8(0) == 0
    assert mem.getu8(1) == 1
    assert mem.getu16(0) == 256
    assert mem.getu32(0) == mem.getu16(0) + mem.getu16(2)*65536
