from socket import *
from threading import *
import time
from tkinter import Frame, Button, Label, StringVar, Entry, messagebox, Tk

GLOBAL_DEBUG = True


def get_time():
    return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'


def print_by_time(msg):
    print(get_time() + str(msg))


class NetworkError(Exception):
    def __init__(self, arg):
        self.arg = arg


class Client:
    """
    Client负责做与游戏无关的与服务器的交互
    """
    username = None
    password = None # 登录以及注册成功后进行修改
    server_addr = ('127.0.0.1', 10001)
    threads = {}
    recv_msg = {}

    def __init__(self):
        pass

    def connect(self):
        """包含在登录的步骤中，成功返回True则分出线程监听，失败返回False交给引用方处理
        """
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket.connect(self.server_addr)
        except Exception as error:
            if GLOBAL_DEBUG is True:
                print_by_time(error)
            self.socket.close()
            return False
        t = Thread(target=self.save_msg)  # 分出线程
        t.start()
        return True

    def recv(self):  # 异常处理交给 self.save_msg 方法
        recv_msg = self.socket.recv(1024).decode('utf-8').strip()
        info_list = recv_msg.split(',')
        if GLOBAL_DEBUG == True:
            print_by_time("recieve from server: " + " ".join(info_list))
        return info_list

    def save_msg(self):
        while True:
            try:
                info_list = self.recv()
                if info_list == ['']:
                    raise NetworkError("服务器端断开连接")
            except NetworkError as error:
                print_by_time(error)
                self.socket.close()
                return  # 中断线程
            except Exception as error:  # 处理socket.recv() 的异常
                print_by_time(error)
            else:
                self.recv_msg[info_list[0]] = info_list

    def wait_msg(self, key_word, timeout=5, step=0.05):
        """等待处理程序需要的消息的出现
        """
        ddl = time.time() + timeout
        while time.time() < ddl:
            if key_word in self.recv_msg:
                return self.recv_msg[key_word]
            else:
                time.sleep(step)
        raise NetworkError("接受服务器消息超时(花费{}s)".format(timeout))  # 超时引发异常

    def send(self, msg):  # msg 是一个list 如 ["login", "username", "password"]
        """
        >>> msg = ["login", "username", "password"]
        >>> ",".join(msg)
        'login,username,password'
        >>> " ".join(msg)
        'login username password'
        """
        if GLOBAL_DEBUG == True:
            print_by_time("send to server: " + " ".join(msg))
        msg = ",".join(msg)  # 用","做分割是因为如果username中有空格不好办
        self.socket.send(msg.encode('utf-8'))

        # 异常处理交给引用方


class Login(Frame):
    """第一个gui界面，负责用户登录和注册的step_1
    """

    def __init__(self, master, *args, **kwargs):
        super(Login, self).__init__(master=master, *args, **kwargs)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.label_1 = Label(master=self, text="用户名")
        self.label_2 = Label(master=self, text="密码")
        self.label_1.grid(row=0, column=0)
        self.label_2.grid(row=1, column=0)

        self.v1 = StringVar()
        self.v2 = StringVar()
        self.entry_1 = Entry(master=self, textvariable=self.v1)
        self.entry_2 = Entry(master=self, textvariable=self.v2, show='*')
        self.entry_1.grid(row=0, column=1, columnspan=2)
        self.entry_2.grid(row=1, column=1, columnspan=2)

        self.button_1 = Button(master=self, text="登录", command=self.login)
        self.button_2 = Button(master=self, text="注册", command=self.register_step_1)
        self.button_1.grid(row=2, column=1)
        self.button_2.grid(row=2, column=2)

    def login(self):
        if CLIENT.connect() is False:
            messagebox.showerror(message="Cannot connect server, please check your network then retry.",
                                 title="connection error")
        else:
            action = "login"
            username = self.v1.get()
            password = self.v2.get()
            msg = [action, username, password]
            CLIENT.send(msg)
            try:
                info_list = CLIENT.wait_msg(key_word=action)
            except NetworkError as error:
                print_by_time(error)
                messagebox.showerror(message=str(error), title="timeout error")
                return # 退回gui eventloop 相当于恢复原来的状态

            if info_list[0] == action:
                if info_list[1] == "ok":
                    if GLOBAL_DEBUG is True:
                        print("login success")
                        CLIENT.username = username
                        CLIENT.password = password
                    # 进入游戏大厅
                else:
                    if GLOBAL_DEBUG is True:
                        print(info_list[2])
                    messagebox.showerror(message=info_list[2], title="login error")

    def check_username(self, username):
        """如果合适返回True，否则提示错误信息，返回False交给引用方处理
        6~18位字符，只能包含英文字母，数字，下划线。
        """
        ok = True
        length = len(username)
        if length > 18 or length < 6:
            ok = False
        for i in username:
            if not (i.isdigit() or i.isalpha() or i == '_'):
                ok = False
        if ok is False:
            messagebox.showerror(title="用户名错误", message="用户名为6~18位字符，只能包含英文字母，数字，下划线")
        return ok

    def check_password(self, password):
        """如果合适返回True，否则提示错误信息，返回False交给引用方处理
        6~18位字符，只能包含英文字母，数字。
        """
        ok = True
        length = len(password)
        if length > 18 or length < 6:
            ok = False
        for i in password:
            if not (i.isdigit() or i.isalpha()):
                ok = False
        if ok is False:
            messagebox.showerror(title="密码错误", message="密码为6~18位字符，只能包含英文字母，数字")
        return ok

    def register_step_1(self):
        action = "register"
        progress = "step_1"
        username = self.v1.get()
        password = self.v2.get()

        if self.check_username(username) is False or self.check_password(password) is False:
            return # 返回到mainloop
        else:
            msg = [action, progress, username, password]
            CLIENT.send(msg) # 查询数据库，密码是否已经存在
            try:
                info_list = CLIENT.wait_msg(action)
            except NetworkError as error:
                print_by_time(error)
                messagebox.showerror(message=str(error), title="timeout error")
                return
            else:
                assert info_list[1] == progress, "消息错乱"
                if info_list[2] == "continue":
                    CLIENT.username = username
                    CLIENT.password = password
                    self.destroy()
                    Register(master=ROOT)
                    # 进入注册的第二步
                else:
                    pass  # TODO 打印错误，return 回mainloop


class Register(Frame):
    def __init__(self, master, *args, **kwargs):
        super(Register, self).__init__(master=master, *args, **kwargs)
        # TODO



if __name__ == '__main__':
    ROOT = Tk() # 全局变量
    # ROOT.geometry("400x300")
    ROOT.title("登录")
    CLIENT = Client()  # 创建一个client对象，负责处理底层数据传输，为全局变量
    login_ui = Login(master=ROOT)  # 对于每个ui，client都相当于底层逻辑
    ROOT.mainloop()
