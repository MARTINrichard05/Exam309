from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
from threading import Thread
import socket
import sys
import time


class Server:
    def __init__(self, address : str ="0.0.0.0", port : int = 4200, max_clients : int = 5): # le port que M.Drouhin a choisi
        self.__clients = []
        self.__address = address
        self.__port = port
        self.__max_clients = max_clients

        self.__ClientlistenerThread = None
        self.__MsglistenerThread = None

        self.__running = False

    def start(self):
        self.__ClientlistenerThread = Thread(target=self.__startup)
        self.__MsglistenerThread = Thread(target=self.__msg_listener)
        self.__running = True
        self.__ClientlistenerThread.start()
        self.__MsglistenerThread.start()


    def __msg_listener(self):
        while self.running:
            for client in self.__clients:
                try:
                    msg = client.recv(1024)
                    if msg:
                        print(msg)
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    print("Client disconnected")
                    self.__clients.remove(client)
                    client.close()


    def stop(self):
        self.__running = False
        try :
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except OSError:
            pass # Le socket à crashé, donc est fermé
        self.__ClientlistenerThread.join()
        print("Server stopped")

    def __listen_for_new_clients(self):
        print("Listening for new clients")
        while self.running:
            if len(self.__clients) >= self.__max_clients:
                time.sleep(0.02)
                continue
            try :
                client, addr = self.__socket.accept()
            except OSError:
                continue
            client.setblocking(False)
            self.__clients.append(client)
            print(f"New client: {addr}")

    def __start_listener(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.__address, self.__port))
        self.__socket.listen()
        self.__listen_for_new_clients()

    def __startup(self):
        self.__start_listener()
        self.__socket.close()



    @property
    def running(self):
        return self.__running

    @property
    def address(self):
        return self.__address
    @address.setter
    def address(self, value):
        self.__address = value

    @property
    def port(self):
        return self.__port
    @port.setter
    def port(self, value : int):

        self.__port = value

    @property
    def max_clients(self):
        return self.__max_clients
    @max_clients.setter
    def max_clients(self, value : int):
        self.__max_clients = value

class App:
    def __init__(self):
        self.__server = Server()
        self.__app = QApplication(sys.argv)
        self.__root = QWidget()
        self.__root.resize(500, 800)
        self.__root.setWindowTitle("Hello world!")
        self.__grid = QGridLayout()
        self.__root.setLayout(self.__grid)
        self.__initWidgets()

    def run(self):
        self.__root.show()
        sys.exit(self.__app.exec())

    def __initWidgets(self):
        self.__portline = QLineEdit()
        self.__portline.setText("4200")

        self.__addressline = QLineEdit()
        self.__addressline.setText("0.0.0.0")

        self.__maxclientsline = QLineEdit()
        self.__maxclientsline.setText("5")

        self.__startstop = QPushButton("Démmarrage du serveur")
        self.__startstop.clicked.connect(self.startstop)

        self.__grid.addWidget(QLabel("Port:"), 0, 0)
        self.__grid.addWidget(self.__portline, 0, 1)

        self.__grid.addWidget(QLabel("Address:"), 1, 0)
        self.__grid.addWidget(self.__addressline, 1, 1)

        self.__grid.addWidget(self.__startstop, 2, 0, 1, 2)

    def __refresh_server_params(self):
        self.__server.address = self.__addressline.text()

        try:
            self.__server.port = int(self.__portline.text())
        except ValueError:
            self.__portline.setText("4200")
            self.__server.port = 4200

        try:
            self.__server.max_clients = int(self.__maxclientsline.text())
        except ValueError:
            self.__maxclientsline.setText("5")
            self.__server.max_clients = 5


    def startstop(self):
        if self.__server.running:
            self.__server.stop()
            self.__startstop.setText("Démmarrage du serveur")

        else:
            self.__refresh_server_params()
            self.__server.start()
            self.__startstop.setText("Arrêt du serveur")



if __name__ == "__main__":
    app = App()
    app.run()