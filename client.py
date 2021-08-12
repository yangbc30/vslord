from socket import *
from threading import *
import time



class Client:
    """
    Client负责做与游戏无关的与服务器的交互
    """
    server_addr = ('127.0.0.1', 10001)
    threads = {}
    debug = True

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def process_msg(self):
        while True:
            info_list = self.recv()

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket.connect(self.server_addr)
        except Exception:
            print("Cannot connect server")
            self.socket.close()
            return False
        t = Thread(target=self.process_msg)
        t.start()
        return True

    def get_time(self):
        return '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+']'

    def send(self, msg): # msg 是一个list 如 ["login", "username", "password"]
        """
        >>> msg = ["login", "username", "password"]
        >>> ",".join(msg)
        'login,username,password'
        >>> " ".join(msg)
        'login username password'
        """
        if self.debug == True:
            print(self.get_time() + "send to server: " + " ".join(msg))
        msg = ",".join(msg) # 用","做分割是因为如果username中有空格不好办
        self.socket.send(msg.encode('utf-8'))

    def recv(self):
        recv_msg = self.socket.recv(1024).decode('utf-8').strip()
        info_list = recv_msg.split(',')
        if self.debug == True:
            print(self.get_time() + "recieve from server: ", " ".join(info_list))
        return info_list


    def login(self):
        if self.connect() is True:
            msg = ["login", self.username, self.password]
            self.send(msg)
            info_list = self.recv()
            if info_list[0] == 'login':
                if info_list[1] == 'ok':
                    print("login success")
                    # 分出一个线程监听socket端口
                else:
                    print(info_list[2])
        # time.sleep(2)

    def register(self, mail_box="2414836228@qq.com", process="step_1"):
        request = "register"
        if process == "step_1":
            msg = [request, process, mail_box]
            self.send(msg)





if __name__ == '__main__':

    client = Client(username="yangbc", password="yangbc")
    client.login()
    # client2 = Client(username="zls", password="zls")
    # client2.login()
    # client3 = Client(username='lvyaqiao', password="lvyaqiao")
    # client3.login()


