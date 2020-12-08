import socket

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s1.connect(('127.0.0.1', 12345))

s1.send(b'Linoy Davari Yael Simhis')

data = s1.recv(100)
print("Server sent: ", data)

s1.close()

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s2.connect(('127.0.0.1', 12345))

s2.send(b'318416344 209009604')

data = s2.recv(100)
print("Server sent: ", data)

s2.close()