#!/usr/bin/python

import sys
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from types import SimpleNamespace

POLL_INTERVAL = 0.9
MSGLEN = 80


def main():
    addr_components = sys.argv[1].split(':')
    addr = addr_components[0], int(addr_components[1])
    start_server(addr)


def start_server(addr):
    with socket(AF_INET, SOCK_STREAM) as lsock:
        lsock.bind(addr)
        lsock.listen()
        while True:
            print('waiting for connection')
            rsock, raddr = lsock.accept()  # block until new connection
            print(f'accepted connection from {raddr}')
            Thread(
                target=service_connection,
                args=(rsock, raddr)
            ).start()


def service_connection(sock, addr):
    try:
        data = SimpleNamespace(
            proceed=True,
            result=None,
            addr=addr,
            buf=b''
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
        print(f'connection to {addr} closed by client')


def handle_read(sock, data):
    msg = sock.recv(MSGLEN)
    print(f'recieved message from {data.addr}: {msg}')
    data.buf += bytearray('OK', 'utf8')


def handle_write(sock, data):
    bytes_sent = sock.send(data.buf)
    data.buf = data.buf[:bytes_sent]


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('keyboard interrupt; exiting')
