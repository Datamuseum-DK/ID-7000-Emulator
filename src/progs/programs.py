"""Module to specify a list of loadable programs"""

# New abstraction to make it possible to load different roms and/or
# custom code snippets into memory with a user defined start address

import progs.id7k0018
import progs.sps

proglist = {
        "id7ka"       : progs.id7k0018.id7ka,
        "spsa"        : progs.sps.spsa
    }
