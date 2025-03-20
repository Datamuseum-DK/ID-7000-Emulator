import sys
import termios
from select import select



class KeyboardCodes:

    def __init__(self, input="macos"):
        if input == "macos":
            self.input = self.macos
        else:
            assert False, 'no known keyboard input provided'


    # Macos mappings - to be adapted to ID7000 if applicable
    macos = {
        # "TAB"         :    9,  # TAB
        "RETURN"      :   10,  # RETURN
        # "GO"          :  169,  # opt-g
    }

    windows = {
    }

    # Key codes - to be adapted to ID7000 if applicable
    q1key = {
        # "TAB CLR"     : 0x02,
        # ...
        # "INSERT MODE" : 0x1e
    }

    # get input key value for Q1 keyboard
    def ikey(self, s):
        assert s in self.input
        return self.input[s]

    # get output key value for Q1
    def okey(self, s):
        assert s in self.q1key
        return self.q1key[s]




class Key:

    def __init__(self):
        # save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # new terminal setting unbuffered
        self.new_term[3] = self.new_term[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)


    def __del__(self):
        # switch to normal terminal
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def putch(self, ch):
        sys.stdout.write(ch)

    def getch(self):
        return sys.stdin.read(1)

    def getche(self):
        ch = self.getch()
        self.putch(ch)
        return ch

    def kbhit(self):
        dr,_,_ = select([sys.stdin], [], [], 0)
        return dr != []


if __name__ == '__main__':

    kbd = Key()

    while 1:
        if kbd.kbhit():
            char = kbd.getch()
            break
        print("A")
        #sys.stdout.write('.')

    print(f'done {char}')
