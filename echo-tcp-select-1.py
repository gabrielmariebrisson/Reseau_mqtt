#!/usr/bin/python3
import socket
import select

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 7777))
s.listen(1)
l = []

while True:
    r, _, _ = select.select(l + [s], [], [])
    for s2 in r:
        if s2 == s:
            s3, a = s.accept()
            print("new client:", a)
            l = l + [s3]
        else:
            msg = s2.recv(1500)
            if len(msg) == 0:
                print("client disconnected")
                s2.close()
                l.remove(s2)
                continue
            s2.sendall(msg)
