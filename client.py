from socket import *
from threading import *
from tkinter import Frame, Button, Label, StringVar, Entry, messagebox, Tk
from utils import *
import re


class Client:
    """
    Client负责做与游戏无关的与服务器的交互
    """
    username = None
    password = None  # 登录以及注册成功后进行修改
    mailbox = None
    server_addr = ('127.0.0.1', 10001)
    threads = {}
    recv_msg = {}
    is_connected = False
    state = {}  # 保存当前状态

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
            self.is_connected = False
            return False
        t = Thread(target=self.save_msg)  # 分出线程
        t.start()
        self.is_connected = True
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
                self.is_connected = False
                return  # 中断线程
            except Exception as error:  # 处理socket.recv() 的异常
                self.socket.close()
                self.is_connected = False
                print_by_time(error)
                return
            else:
                self.recv_msg[info_list[0]] = info_list
                self.state[info_list[0]] = info_list[1]

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
    """第一个gui界面，负责用户login和register的第一步
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
        if CLIENT.is_connected is False:
            if CLIENT.connect() is False:
                messagebox.showerror(message="无法连接服务器",
                                     title="连接错误")
            return  # 返回mainloop

        action = "login"
        username = self.v1.get()
        password = self.v2.get()
        msg = [action, username, password]
        CLIENT.send(msg)
        try:
            info_list = CLIENT.wait_msg(key_word=action)
        except NetworkError as error:
            print_by_time(error)
            messagebox.showerror(message=str(error), title="连接超时")
            return  # 退回mainloop 相当于恢复原来的状态

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
        if CLIENT.is_connected is False:
            if CLIENT.connect() is False:
                messagebox.showerror(message="无法连接服务器",
                                     title="连接错误")
            return  # 返回mainloop

        action = "register_step_1"
        username = self.v1.get()
        password = self.v2.get()

        if self.check_username(username) is False or self.check_password(password) is False:
            return  # 返回mainloop
        else:
            msg = [action, username, password]
            CLIENT.send(msg)  # 查询数据库，密码是否已经存在
            try:
                info_list = CLIENT.wait_msg(action)
            except NetworkError as error:
                print_by_time(error)
                messagebox.showerror(title="连接超时", message=str(error))
                return
            else:
                if info_list[1] == "ok":
                    CLIENT.username = username
                    CLIENT.password = password
                    self.destroy()
                    Register(master=ROOT)
                    # 进入注册的第二步
                else:
                    error = info_list[2]
                    if error == "username_used":
                        messagebox.showerror(title="用户名错误", message="这个用户名太好以至于已经被使用过了！")
                        return
                    # 添加其他错误


class Register(Frame):
    """完成register的第二步和第三步

    """

    def __init__(self, master, *args, **kwargs):
        super(Register, self).__init__(master=master, *args, **kwargs)
        self.pack()
        self.create_widgets()
        # TODO

    def create_widgets(self):
        self.label_1 = Label(master=self, text="邮箱")
        self.label_2 = Label(master=self, text="验证码")
        self.label_1.grid(row=0, column=0)
        self.label_2.grid(row=1, column=0)

        self.v1 = StringVar()
        self.v2 = StringVar()
        self.entry_1 = Entry(master=self, textvariable=self.v1)
        self.entry_2 = Entry(master=self, textvariable=self.v2)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)

        self.button_1 = Button(master=self, text="获取", command=self.register_step_2)
        self.button_2 = Button(master=self, text="注册", command=self.register_step_3)
        self.button_1.grid(row=1, column=2)
        self.button_2.grid(row=2, column=1)

    def check_mailbox(self, mailbox):
        """合法返回True，非法messagebox提示，返回False
        >>> root = Tk()
        >>> register = Register(master=root)
        >>> register.check_mailbox("2414836228@qq.com")
        True
        >>> register.check_mailbox("baidu.com")
        False
        """
        pattern = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
        if re.match(pattern, mailbox) is not None:
            return True
        else:
            messagebox.showerror(title="邮箱错误", message="邮箱格式错误")
            return False

    def register_step_2(self):
        action = "register_step_2"
        mailbox = self.v1.get()
        if self.check_mailbox(mailbox) is False:
            return  # 返回mainloop
        else:
            msg = [action, mailbox]
            CLIENT.send(msg)
            try:
                info_list = CLIENT.wait_msg(key_word=action)
            except NetworkError as error:
                print_by_time(error)
                messagebox.showerror(message=str(error), title="连接超时")
                return  # 退回mainloop 相当于恢复原来的状态
            if info_list[1] == "ok":
                # 记录信息，进入下一步
                self.mailbox = mailbox
                return  # 返回mainloop 等待用户点击注册
            else:
                error = info_list[2]  # 处理错误代码
                if error == "mailbox_used":
                    messagebox.showerror(title="邮箱错误", message="这个邮箱名已被人使用")
                    return  # 返回mainloop 重试
                if error == "cannot_send_mail":
                    messagebox.showerror(title="SMTP错误", message="服务器无法发送验证邮件")
                    return  # 返回mainloop 重试
                if error == "cannot_send_mail":
                    messagebox.showerror(title="服务器错误", message="服务器数据库查询错误")
                    return  # 返回mainloop 重试

    def register_step_3(self):
        pre_action = "register_step_2"
        action = "register_step_3"
        if CLIENT.state[pre_action] != "ok":
            messagebox.showerror(title="注册错误", message="请先获取填写验证码")
            return  # 返回mainloop 重试

        code = self.v2.get()
        msg = [action, code]
        CLIENT.send(msg)
        try:
            info_list = CLIENT.wait_msg(key_word=action)
        except NetworkError as error:
            print_by_time(error)
            messagebox.showerror(message=str(error), title="连接超时")
            return  # 退回mainloop 相当于恢复原来的状态

        if info_list[1] == "ok":
            CLIENT.state["login"] = "ok"
            self.destroy()
            messagebox.showinfo(title="注册成功", message="已自动登录进入游戏")
            # TODO 进入游戏
        else:
            error = info_list[2]
            if error == "wrong code":
                messagebox.showerror(title="验证码错误", message="验证码错误请重试")
                return  # 返回mainloop 重试


if __name__ == '__main__':
    ROOT = Tk()  # 全局变量
    # ROOT.geometry("400x300")
    ROOT.title("登录")
    CLIENT = Client()  # 创建一个client对象，负责处理底层数据传输，为全局变量
    login_ui = Login(master=ROOT)  # 对于每个ui，client都相当于底层逻辑
    ROOT.mainloop()
