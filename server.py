from vslord_classes import *
from vslord_rules import *
from vslord_strategies import *
from socket import *

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("127.0.0.1", serverPort))

serverSocket.listen(3)


transportSocket, address = serverSocket.accept()
message = transportSocket.recv(1024)


