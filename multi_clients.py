import time
from multiprocessing import Process

def start_new_client():
    import client_test


def start():
    clients = []
    for i in range(4):
        client = Process(target=start_new_client)
        client.start()
        clients.append(client)
        time.sleep(0.1)
    for client in clients:
        client.join()

if __name__ == "__main__":
    start()