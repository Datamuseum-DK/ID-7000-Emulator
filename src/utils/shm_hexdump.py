
import argparse
import time
from multiprocessing import shared_memory


def main(args):
    # Attach to the existing shared memory block
    # do not create it and do not track it. Assume
    # creator destroys it.
    shm = shared_memory.SharedMemory(name='id7k_shm', create=False, track=False)

    try:
        count = 0
        while True:
            print("\033c")
            print(f'{count}')
            for i in range(args.start, args.start + args.length, 16):
                b = list(shm.buf[i:i+16].tobytes())
                bstr = ""
                astr = ""
                for d in b:
                    bstr = bstr + f'{d:02x} '
                    if 32 <= d <= 126:
                        astr = astr + chr(d)
                    else:
                        astr = astr + '.'
                print(f'{i:04x}', bstr, astr)
            if args.once:
                break
            count += 1
            time.sleep(1)

    except:
        pass


if __name__ == "__main__":

    def auto_int(x):
        return int(x, 0)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", help = "start address",
                        type = auto_int, default = 0x0000)
    parser.add_argument("-l", "--length", help = "bytes to show",
                        type = auto_int, default = 0x0000)

    parser.add_argument("-o", "--once", help = "do not loop",
                        action='store_true')

    args = parser.parse_args()

    main(args)