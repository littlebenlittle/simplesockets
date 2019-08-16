#!/usr/bin/python3

import sys
import os
from io import StringIO
from socket import socket, AF_INET, SOCK_STREAM
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from types import SimpleNamespace
from conf import (POLL_INTERVAL, MSGLEN,
                  DEFAULT_ADDR, ENCODING)


def main():
    if not os.path.exists('/app/docker-lock'):
        print('Do not use this outside of a container!!')
        sys.exit(1)
    addr_components = os.environ.get('ADDR', DEFAULT_ADDR).split(':')
    addr = addr_components[0], int(addr_components[1])
    start_server(addr)


def start_server(addr):
    with socket(AF_INET, SOCK_STREAM) as lsock:
        lsock.bind(addr)
        lsock.listen()
        print(f'listening on {addr}')
        while True:
            rsock, raddr = lsock.accept()  # block until new connection
            # print(f'accepted connection from {raddr}')
            pid = os.fork()
            if pid == 0:
                service_connection(rsock, raddr)


def service_connection(sock, addr):
    try:
        data = SimpleNamespace(
            proceed=True,
            result=None,
            addr=addr,
            buf=b'',
            g=dict()
        )
        sel = DefaultSelector()
        sel.register(sock, EVENT_READ | EVENT_WRITE, data)
        while data.proceed:
            for key, mask in sel.select(timeout=POLL_INTERVAL):
                if mask & EVENT_READ:
                    handle_read(sock, data)
                if mask & EVENT_WRITE:
                    handle_write(sock, data)
        return data.result
    except (BrokenPipeError, ConnectionResetError):
        # print(f'connection to {addr} closed by remote')
        pass


def handle_read(sock, data):
    msg = sock.recv(MSGLEN)
    # print(f'recieved message from {data.addr}: {msg}')
    try:
        for line in msg.split(b'\n'):
            if line in (b'\n', b'', b'\r', b'\r\n'):
                continue
            tmp = sys.stdout
            outp = sys.stdout = StringIO()
            print('>>> ' + line.decode(ENCODING).strip())
            exec(line, data.g)
            sys.stdout = tmp
            result = outp.getvalue()
            if result not in ('\n', '', '\r', '\r\n'):
                print(f'{result}'.strip('\n'))
            data.buf += bytes(result+'\n', ENCODING)
    except Exception as e:
        print(str(e))
        data.buf = bytes(str(e.args), ENCODING)


def handle_write(sock, data):
    if len(data.buf) > 0:
        bytes_sent = sock.send(data.buf)
        data.buf = data.buf[bytes_sent:]


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
