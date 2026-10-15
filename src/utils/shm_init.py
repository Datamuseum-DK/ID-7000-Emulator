
import argparse
import time
from multiprocessing import shared_memory


def main():
    shm = shared_memory.SharedMemory(name='id7k_shm', size=65535, create=True, track=True)

    print("sleeping.... ctrl-c to kill shared memory")
    while True:    
        time.sleep(2)


if __name__ == "__main__":

    main()