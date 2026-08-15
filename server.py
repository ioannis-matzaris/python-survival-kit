"""Ο server του καταστήματος. Τρέξε: python3 server.py

Απαντάει σε ένα request και σταματάει. Απαντάει το ίδιο πράγμα σε κάθε
διαδρομή. Και όποιος του στείλει σκουπίδια, τον ρίχνει.
"""

import socket

HOST = "127.0.0.1"
PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

print(f"Ακούω στο http://{HOST}:{PORT}")

connection, _ = server.accept()
raw = connection.recv(4096).decode("utf-8")
method, path, version = raw.split("\r\n")[0].split(" ")

body = "εντάξει"
head = (
    "HTTP/1.1 200 OK\n"
    "Content-Type: text/plain\n"
    f"Content-Length: {len(body)}\n"
    "Connection: close\n\n"
)
connection.sendall(head.encode("utf-8") + body.encode("utf-8"))
connection.close()
