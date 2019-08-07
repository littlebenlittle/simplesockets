#!/usr/bin/python

import sys
from socket import socket, AF_INET, SOCK_STREAM
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from types import SimpleNamespace

POLL_INTERVAL = 0.9
MSGLEN = 80


def main():
    sel = DefaultSelector()
    addr_components = sys.argv[1].split(':')
    addr = addr_components[0], int(addr_components[1])
    msgs = [bytes(msg, 'utf8') for msg in sys.stdin]
    msgs.reverse()
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect(addr)
        sock.setblocking(False)
        data = SimpleNamespace(msgs=msgs, inb=b'', outb=b'START')
        sel.register(sock, EVENT_READ | EVENT_WRITE, data)
        keep_going = True
        while keep_going:
            keep_going = handle_connection(sel)


def handle_connection(sel):
    for key, mask in sel.select(timeout=POLL_INTERVAL):
        if mask & EVENT_READ:
            msg = key.fileobj.recv(MSGLEN)
            if msg:
                key.data.inb += msg
                if msg == b'DONE':
                    print('exiting')
                    return False
        if mask & EVENT_WRITE:
            if len(key.data.msgs) == 0:
                key.fileobj.sendall(b'DONE')
                return False
            if key.data.inb == b'OK':
                print('got the OK')
                key.data.inb = b''
                key.data.outb = key.data.msgs.pop()
            bytes_sent = key.fileobj.send(key.data.outb)
            key.data.outb = key.data.outb[bytes_sent:]
    return True


if __name__ == '__main__':
    try:
        main()
    except ConnectionResetError:
        print('connection reset by remote; exiting')
    except KeyboardInterrupt:
        print('keyboard interrupt; exiting')
