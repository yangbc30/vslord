from socket import *
import time


class Client:
    """
    Client负责做与游戏无关的与服务器的交互
    """
    server_addr = ('127.0.0.1', 10001)
    debug = True

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket.connect(self.server_addr)
        except Exception:
            print("Cannot connect server")
            self.socket.close()
            return False
        return True

    def get_time(self):
        return '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+']'

    def send(self, msg):
        if self.debug == True:
            print(self.get_time() + "send to server: " + msg)
        self.socket.send(msg.encode('utf-8'))

    def recv(self):
        recv_msg = self.socket.recv(1024).decode('utf-8').strip()
        info_list = recv_msg.split(' ')
        if self.debug == True:
            print(self.get_time() + "recieve from server: ", recv_msg)
        return info_list


    def login(self):
        if self.connect() == True:
            msg = "login {} {}".format(self.username, self.password)
            self.send(msg)
            info_list = self.recv()
            if info_list[0] == 'login':
                if info_list[1] == 'ok':
                    print("login success")
                else:
                    print(info_list[2])
        time.sleep(2)



if __name__ == '__main__':

    client = Client(username="yangbc", password="yangbc")
    client.login()
    client2 = Client(username="zls", password="zls")
    client2.login()
    client3 = Client(username='yuanye', password="yuanye")
    client3.login()


