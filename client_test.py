import socket

address = "127.0.0.1"
port = 4200

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((address, port))
client.send(b"Hello world!")
client.send(b"EXIT")
client.close()
