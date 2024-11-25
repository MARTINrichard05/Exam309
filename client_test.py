import socket
import time

address = "127.0.0.1"
port = 4200

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((address, port))
for i in range(10):
    client.send(b"Hello world!")
    time.sleep(1)
client.send(b"deco-server")
client.close()
