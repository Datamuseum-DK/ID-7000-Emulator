#!/usr/bin/env python3

import curses
import socket

width = 40
height = 12
stdscr = curses.initscr()
curses.resize_term(height+2, width+2)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


def main(stdscr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.clear()
    stdscr.border()
    curses.curs_set(True)
    stdscr.addstr(10, 1, '  Q1 display emulator', curses.color_pair(1))
    stdscr.refresh()

    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        x = int(data[0])
        y = int(data[1])
        data = data[2:]
        for i in range(height):
            line = data[i*width:i*width+width]
            stdscr.addstr(i+1, 1, '{}'.format(line.decode('utf-8')), curses.color_pair(1))
        stdscr.move(y+1,x)
        stdscr.refresh()

curses.wrapper(main)
