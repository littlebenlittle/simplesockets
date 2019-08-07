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
    with socket(AF_INET, SOCK_STREAM) as lsock:
        lsock.bind(addr)
        lsock.listen()
        rsock, raddr = lsock.accept()  # block until new connection
        print(f'Accepted new connection from {raddr}')
    rsock.setblocking(False)
    data = SimpleNamespace(inb=b'', outb=b'')
    sel.register(rsock, EVENT_READ | EVENT_WRITE, data)
    keep_going = True
    with rsock:
        while keep_going:
            keep_going = handle_connection(sel)


def handle_connection(sel):
    for key, mask in sel.select(timeout=POLL_INTERVAL):
        if mask & EVENT_READ:
            msg = key.fileobj.recv(MSGLEN)
            print(f'Received msg: {msg}')
            if msg == b'DONE':
                print(f'inb = {key.data.inb}')
                return False
            key.data.inb += msg
            key.data.outb = b'OK'
        if mask & EVENT_WRITE:
            if len(key.data.outb) > 0:
                print(f'sending {key.data.outb}')
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
