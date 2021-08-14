from socket import *
from threading import *
import sqlite3
# import os
# import sys
import random
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from utils import *


class Server:
    """
    服务器，通过端口创建，接受到tcp请求创建client，并且接受client的请求
    """
    clients = {}
    threads = {}

    def __init__(self, maxClient=3, server_addr=('127.0.0.1', 10001)):
        self.server_addr = server_addr
        self.maxClient = maxClient
        self.lock = Lock()
        try:
            self.serverSocket = socket()
            self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.serverSocket.bind(self.server_addr)
        except Exception as error:
            print_by_time(error)

    def start(self):
        self.serverSocket.listen(self.maxClient)
        if GLOBAL_DEBUG is True:
            print_by_time("系统等待连接")
        while True:
            conn, addr = self.serverSocket.accept()

            t = Node(conn, self)
            t.start()
            self.threads[conn] = t
            for c in self.threads:
                if c._closed is True:  # thread._closed 是啥 TODO
                    self.threads[c].join()


class Node(Thread):
    """Sever中接受了客户端的一个tcp连接请求，建立tcp连接，对于服务器，将客户端抽象为一个节点，分配一个线程处理这个节点发出的信息
    """
    sender_mailbox = "201870105@smail.nju.edu.cn"
    sender_nickname = "Game Vslord"
    sender_password = "Yangbc30"
    mail_title = "Verify your email for Vslord"
    nickname = "Player"
    database = "user.db"
    state = {}  # 表示对应用户当前的状态 如{"login":"ok"}

    username = None
    password = None
    mailbox = None
    code = None

    def __init__(self, conn, server):
        super().__init__()
        self.socket = conn
        self.server = server

    def send(self, msg_list):  # send 不需要异常处理，因为如果对方端口关闭，会自动给我发送['']此时recv的异常处理使端口关闭
        if GLOBAL_DEBUG is True:
            print_by_time("send to client: " + " ".join(msg_list))
        msg = ",".join(msg_list)
        self.socket.send(msg.encode('utf-8'))
        self.state[msg_list[0]] = msg_list[1]  # 保存状态

    def recv(self):  # 异常交给Node.run处理
        recv_msg = self.socket.recv(1024).decode('utf-8').strip()
        info_list = recv_msg.split(',')
        if GLOBAL_DEBUG is True:
            print_by_time("recieve from client: " + " ".join(info_list))
        return info_list

    def sql(self, command):
        """传入符合规范的sql命令字符串记得最后加分号命令全部大写，然后修改/或查询结果

        修改成功 -> 返回True
        查询成功 -> 返回查询结果 形式为一个列表，每个元素都是元组，每个元组代表一行结果 [('yangbc',), ('yuanye',), ('lvyaqiao',)]
        失败 -> 打印相应错误的字符串
        >>> node = Node(socket(), Server())

        >>> node.sql("SELECT sender_password FROM user;")
        [('yangbc',), ('yuanye',), ('lvyaqiao',), ('zls',)]
        >>> node.sql("SELECT sender_password FROM user WHERE username = 'yangbc';")
        [('yangbc',)]
        >>> node.sql("SELECT sender_password FROM user WHERE username = 'asdf';")
        []
        """
        assert sqlite3.complete_statement(command), "invalid sql command"  # 检查输入的命令是否是合法的sql
        db = sqlite3.connect(self.database)
        cursor = db.cursor()
        command = command.strip()
        try:
            cursor.execute(command)

            if command.lstrip().startswith("SELECT"):
                return cursor.fetchall()  #

        except sqlite3.Error as error:
            print_by_time(str(error))
            return False  # TODO 引用方异常处理
        finally:
            cursor.close()
            db.commit()
            db.close()
        return True  # 如果command不以SELECT开头，并且执行成功，返回True

    def send_mail(self, reciever_mailbox="2414836228@qq.com",
                  reciever_nickname="yuanye"):  # 2414836228@qq.com, 20087000@smail.nju.edu.cn
        """
        >>> node = Node(socket(), Server())
        >>> true_or_false, code_or_error = node.send_mail()
        >>> true_or_false
        True
        """

        code = str(random.randrange(1000, 9999))
        msg = MIMEText("验证码: " + code, 'plain', 'utf-8')
        msg['From'] = formataddr((self.sender_nickname, self.sender_mailbox))
        msg['To'] = formataddr((reciever_nickname, reciever_mailbox))
        msg['Subject'] = self.mail_title
        try:
            with smtplib.SMTP_SSL("smtp.exmail.qq.com", 465) as server:  # 因为连接smtp服务器后总要有sever.quit()，直接简写with
                server.login(self.sender_mailbox, self.sender_password)
                server.sendmail(self.sender_mailbox, [reciever_mailbox], msg.as_string())

        except Exception as error:
            print_by_time(error)
            return False, str(error)  # 如果smtp报错，将报错发回
        else:
            return True, code  # 无异常，表示邮件发送成功，返回验证码，给do_request进行比对

    def run(self):
        """Node 继承Thread类，继承Thread的类自动调用run方法
        """

        while True:
            try:
                info_list = self.recv()
                if info_list == ['']:  # 如果说服务器端套间字不断收到['']，说明客户端已经断开连接，这时通信中止，服务器端也应当关闭套间字
                    raise NetworkError
            except OSError as error:
                print_by_time("服务器端断开连接" + str(error))
                return
            except NetworkError as error:
                print_by_time("客户端断开连接" + str(error))
                self.socket.close()
                return

            self.process_msg(info_list, len(info_list))

    def process_msg(self, info_list, info_len):
        """根据run中不断获取的客户端信息，服务器端进行反馈

        """
        action = info_list[0]

        if action == "login":
            username = info_list[1]
            password = info_list[2]

            query_result = self.sql("SELECT password FROM user WHERE username = '{}';".format(username))

            if query_result == []:
                msg = [action, "error", "user_not_found"]
                self.send(msg)
                self.socket.close()
            else:
                password_queried = query_result[0][0]
                if password == password_queried:
                    msg = [action, "ok"]
                    self.send(msg)
                    # 登录成功
                    self.username = username  # 将username存入Node类中

                    self.server.lock.acquire()
                    self.server.clients[username] = Node
                    self.server.lock.release()
                    # 将client加入clients字典中，多线程共享
                else:
                    msg = [action, "error", "password_not_correct"]
                    self.send(msg)
                    self.socket.close()

        if action == "register_step_1":

            username = info_list[1]
            password = info_list[2]
            query_result = self.sql("SELECT username FROM user WHERE username = '{}';".format(username))
            if query_result == []:  # username 唯一，合法，保存数据
                self.username = username
                self.password = password
                msg = [action, "ok"]
                self.send(msg)
            else:  # username 不唯一，不合法，发送错误代码
                msg = [action, "error", "username_used"]
                self.send(msg)

        if action == "register_step_2":
            reciever_box = info_list[1]  # 根据协议解析box
            query_result = self.sql("SELECT * FROM user WHERE mailbox = '{}';".format(
                reciever_box))  # 如果在数据库中已经存在这个邮箱（self.sql 返回一个非空list），提示客户端邮箱已注册
            if isinstance(query_result, list):
                if len(query_result) != 0:
                    msg = [action, "error", "mailbox_used"]
                    self.send(msg)
                else:
                    true_or_false, code_or_error = self.send_mail(reciever_box, self.nickname)
                    if true_or_false is True:
                        msg = [action, "ok"]
                        self.send(msg)
                        self.code = code_or_error  # 将验证码进行记录，下一次客户端发送验证码时进行比对
                        self.mailbox = reciever_box  # 将邮箱进行记录，如果第二部验证码正确，录入注册信息

                    else:
                        msg = [action, "error", "cannot_send_mail", code_or_error]  # SMTP 发生错误
                        self.send(msg)
            else:
                msg = [action, "error", "sql_error", query_result]
                self.send(msg)

        if action == "register_step_3":
            code = info_list[1]
            if code == self.code:
                msg = [action, "ok"]
                self.state["login"] = "ok"  # 验证码填写正确的同时就登录上了
                self.send(msg)
                assert self.sql(
                    "INSERT INTO user(username, password, mailbox ) VALUES ('{}', '{}', '{}');".format(self.username,
                                                                                                       self.password,
                                                                                                       self.mailbox)), "sql insert error"
            else:
                msg = [action, "error", "wrong_code"]
                self.send(msg)


if __name__ == '__main__':
    server = Server()
    server.start()
