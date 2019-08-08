#!/usr/bin/python

import os
import sys
from socket import socket, AF_INET, SOCK_STREAM
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from types import SimpleNamespace
from conf import (POLL_INTERVAL, MSGLEN,
                  DEFAULT_ADDR, ENCODING)

def main():
    addr_components = os.environ.get('ADDR', DEFAULT_ADDR).split(':')
    addr = addr_components[0], int(addr_components[1])
    msgs = [bytes(msg, ENCODING) for msg in sys.stdin]
    payload = b''.join(msgs)
    sel = DefaultSelector()
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect(addr)
        sock.setblocking(False)
        data = SimpleNamespace(buf=payload, proceed=True)
        sel.register(sock, EVENT_READ | EVENT_WRITE, data)
        while data.proceed:
            for key, mask in sel.select(timeout=POLL_INTERVAL):
                if mask & EVENT_READ:
                    handle_read(sock, data)
                if mask & EVENT_WRITE:
                    handle_write(sock, data)


def handle_read(sock, data):
    msg = sock.recv(MSGLEN)
    print(msg.decode(ENCODING))
    data.proceed = False


def handle_write(sock, data):
    if len(data.buf) > 0:
        bytes_sent = sock.send(data.buf)
        data.buf = data.buf[bytes_sent:]


if __name__ == '__main__':
    try:
        main()
    except ConnectionResetError:
        print('connection reset by remote; exiting')
    except KeyboardInterrupt:
        print('keyboard interrupt; exiting')
