from socket import *
from threading import Thread
import sqlite3
import os, sys
import time

def msg_eval(message):
    """
    将从socket中接受到的字符串解析成代码
    """
    words = message.split()
    if words[0] == "login":
        assert len(words) == 3, "login error"
        username = words[1]
        passwrod = words[2]



class Server:
    """
    服务器，通过端口创建，接受到tcp请求创建client，并且接受client的请求
    """
    debug = True
    clients = {}
    threads = {}

    def __init__(self, maxClient=3 ,server_addr=('127.0.0.1',10001), database="user.db"):
        self.server_addr = server_addr
        self.maxClient = maxClient
        self.serverSocket = socket()
        self.serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.serverSocket.bind(self.server_addr)

    def get_time(self):
        return '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+']'


    def send_to(self, socket, msg):
        if self.debug == True:
            print(self.get_time() + "send to client: " + msg)
        socket.send(msg.encode('utf-8'))

    def recv_from(self, socket):
        recv_msg = socket.recv(1024).decode('utf-8').strip()
        info_list = recv_msg.split(' ')
        if self.debug == True:
            print(self.get_time() + "recieve from client: ", recv_msg)
        return info_list

    def start(self):
        self.serverSocket.listen(self.maxClient)
        print(self.get_time(), '系统等待连接')
        while True:

            conn, addr = self.serverSocket.accept()

            t = Thread(target=self.do_request, args=(conn, ))
            t.start()
            self.threads[conn] = t
            for c in self.threads:
                if c._closed is True:
                    self.threads[c].join()

    def do_request(self, conn):
        """

        """
        while True:
            try:
                info_list = self.recv_from(conn)
            except OSError:
                print("系统已关闭端口")
                return

            if info_list == ['']:
                conn.close()
                print('断开连接')

            if info_list[0] == 'login':
                username = info_list[1]
                password = info_list[2]

                db = sqlite3.connect("user.db")
                cursor = db.cursor()
                cursor.execute("select password from user where username = '{}'".format(username) )
                query_result = cursor.fetchall()   #  [('yangbc',)]
                cursor.close()
                db.commit()
                db.close()

                if query_result == []:
                    msg = "login error user_not_found"
                    self.send_to(conn, msg)
                    conn.close()
                else:
                    password_queried = query_result[0][0]
                    if  password == password_queried:
                        msg = "login ok"
                        self.send_to(conn, msg)
                    else:
                        msg = "login error password_not_correct"
                        self.send_to(conn, msg)
                        conn.close()




class Client:
    """
    接受到一个tcp请求创建一个用户，同时创建一个线程
    不断监听用户的connection处理接收到的内容
    """
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address


if __name__ == '__main__':
    server = Server()
    server.start()



