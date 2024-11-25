from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from threading import Thread
import socket
import sys
import time

# github : https://github.com/MARTINrichard05/Exam309

class Server:
    def __init__(self, address : str ="0.0.0.0", port : int = 4200, max_clients : int = 5): # le port que M.Drouhin a choisi
        self.__clients = []
        self.__address = address
        self.__port = port
        self.__max_clients = max_clients

        self.__ClientlistenerThread = None
        self.__MsglistenerThread = None
        
        self.__msg_buffer = []

        self.__running = False

    def __log(self, msg):
        self.__msg_buffer.append(msg)
        # print(msg)
        
        

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
                        self.__log(f"Message > {msg.decode()}")
                        if msg.decode() == "deco-server":
                            self.__clients.remove(client)
                            client.close()
                            self.__log("Client disconnected")
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    self.__log("Client disconnected")
                    self.__clients.remove(client)
                    client.close()


    def stop(self):
        self.__log("Stopping server")
        self.__running = False
        self.__log("Waiting for message listener to stop")
        self.__MsglistenerThread.join()
        self.__log("Message listener stopped")
        self.__log("Closing clients")
        for client in self.__clients:
            client.close()
            self.__log("Client Deleted")
        try :
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except OSError:
            pass # Le socket à crashé, donc est fermé
        # self.__ClientlistenerThread.join()
        self.__log("Server stopped")

    def __listen_for_new_clients(self):
        self.__log("Listening for new clients")
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
            self.__log(f"New client: {addr}")

    def __start_listener(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            self.__socket.bind((self.__address, self.__port))
        except OSError:
            self.__log("Addresse déja utilisée, veuillez changer le port ou l'addresse et réessayer")
        self.__socket.listen()
        self.__listen_for_new_clients()

    def __startup(self):
        self.__start_listener()
        self.__socket.close()

    def last_msg(self):
        if self.__msg_buffer:
            return self.__msg_buffer.pop(0)
        return None



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
        self.__logsThread = Thread(target=self.loop)
        self.running = True

    def run(self):
        self.__root.show()
        self.__logsThread.start()
        code = self.__app.exec()
        self.running = False
        self.__logsThread.join()
        sys.exit(code)


    def __log(self, msg):
        self.__logs.append(str(msg))

    def __initWidgets(self):
        self.__portline = QLineEdit()
        self.__portline.setText("4200")

        self.__addressline = QLineEdit()
        self.__addressline.setText("0.0.0.0")

        self.__maxclientsline = QLineEdit()
        self.__maxclientsline.setText("5")

        self.__logs = QTextEdit()
        self.__logs.setReadOnly(True)


        self.__startstop = QPushButton("Démmarrage du serveur")
        self.__startstop.clicked.connect(self.startstop)

        self.__grid.addWidget(QLabel("Port:"), 0, 0)
        self.__grid.addWidget(self.__portline, 0, 1)

        self.__grid.addWidget(QLabel("Address:"), 1, 0)
        self.__grid.addWidget(self.__addressline, 1, 1)

        self.__grid.addWidget(QLabel("Max clients:"), 2, 0)
        self.__grid.addWidget(self.__maxclientsline, 2, 1)

        self.__grid.addWidget(self.__startstop, 3, 0, 1, 2)
        self.__grid.addWidget(self.__logs, 4, 0, 1, 2)

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

    def __refresh_logs(self):
        msg = self.__server.last_msg()
        if msg:
            self.__logs.append(msg)

    def loop(self):
        while self.running:
            self.__refresh_logs()
            self.__app.processEvents()



    def startstop(self):
        if self.__server.running:
            self.__log("On demande au serveur de s'arrêter")
            self.__server.stop()
            self.__startstop.setText("Démmarrage du serveur")
            self.__server = Server()

        else:
            self.__refresh_server_params()
            self.__server.start()
            self.__startstop.setText("Arrêt du serveur")
            self.__log("Serveur démarré")





if __name__ == "__main__":
    app = App()
    app.run()