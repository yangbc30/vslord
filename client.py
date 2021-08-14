from socket import *
from threading import *
from tkinter import Frame, Button, Label, StringVar, Entry, messagebox, Tk
from utils import *
import re


class Client:
    """Client的method实现了所有对网络有关的封装，Client的instance记录下当前所有（有效的）信息
    """
    username = None
    password = None
    mailbox = None  # 当用户登录成功，注册成功时，对应的ui会记录用户用户名、密码、和邮箱（因为一个ui完成对应的任务后会自动销毁）
    threads = {}  # 保存线程，暂时无用
    recv_msg = {}  # 保存recv方法得到的消息，以action作为关键字 {"login": ["login", "error", "user_not_found"]}
    is_connected = False  # 记录当前是否已经连上服务器
    state = {}  # 记录收到消息中所有action的状态 {"register_step_1": "ok", ...}

    def __init__(self, server_addr=("127.0.0.1", 10001)):
        self.server_addr = server_addr  # 调试用端口（即本机的10001端口）端口冲突自行修改

    def connect(self):
        """负责与服务器的连接，连接成功则返回True则分出线程监听socket，连接失败则返回False交给引用方处理
        """
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket.connect(self.server_addr)
        except Exception as error:
            print_by_time(error)  # 异常处理:捕获到的异常print出来
            self.socket.close()
            self.is_connected = False
            return False
        t = Thread(target=self.save_msg)  # 分出线程监听socket
        t.start()
        self.threads["listen"] = t  # 将进程记录 TODO 后续进程多了，进程管理
        self.is_connected = True
        return True

    def recv(self):  # 异常处理交给 save_msg 方法
        recv_msg = self.socket.recv(1024).decode('utf-8').strip()
        info_list = recv_msg.split(',')
        if GLOBAL_DEBUG == True:
            print_by_time("recieve from server: " + " ".join(info_list))
        return info_list

    def save_msg(self):
        """死循环 单独一个线程 记录从服务器端发来的信息
        """
        while True:
            try:
                info_list = self.recv()
                if info_list == ['']:  # socket 的特性是如果一方关闭socket另一方会收到['']
                    raise NetworkError("服务器端断开连接")
            except NetworkError as error:  # 服务器端关闭socket，收不到消息，自然关闭socket
                print_by_time(error)
                self.socket.close()
                self.is_connected = False
                return  # 退出死循环，释放线程资源
            except Exception as error:  # 处理socket.recv() 的异常
                self.socket.close()
                self.is_connected = False
                print_by_time(error)
                return
            else:
                self.recv_msg[info_list[0]] = info_list  # 保存来自服务器的消息
                self.state[info_list[0]] = info_list[1]  # 根据消息提取出action的state，进行保存

    def wait_msg(self, key_word, timeout=5, step=0.05):
        """ 等待处理程序需要的消息的出现

        快速扫描 recv_msg
        如果在规定的时间内找到了需要的action对应的info_list返回
        如果美哟在规定的时间内找到，抛出异常

        :param key_word: 你需要的action
        :param timeout: 等待时间，超时抛出异常
        :param step: 扫描间隔
        :return: 你想要的 info_list
        """
        ddl = time.time() + timeout
        while time.time() < ddl:
            if key_word in self.recv_msg:
                return self.recv_msg[key_word]
            else:
                time.sleep(step)
        raise NetworkError("接受服务器消息超时(花费{}s)".format(timeout))  # 超时引发异常

    def send(self, msg):
        """发送给定格式的信息到服务器端

        无异常处理

        :param msg: 一个list 如 ["login", "username", "password"]
        """
        if GLOBAL_DEBUG == True:
            print_by_time("send to server: " + " ".join(msg))
        msg = ",".join(msg)  # 用","做分割是因为如果username中有空格不好办
        self.socket.send(msg.encode('utf-8'))

        # TODO 没有加入异常处理，因为如果无法发送信息，最大原因是对方关闭链接而这时savemsg方法早已捕获异常，is_connected 为 False。引用方应该确保在is_connected 为 True 的情况下调用


class Login(Frame):
    """运行程序默认创建的第一个ui，实现的action： login, register_step_1

    ui 和 功能同步实现
    """

    def __init__(self, master, *args, **kwargs):
        super(Login, self).__init__(master=master, *args, **kwargs)
        self.pack()  # 在root中布局自身
        self.create_widgets()  # 生成小部件

    def create_widgets(self):
        self.label_1 = Label(master=self, text="用户名")  # 创建小部件实例（标签）
        self.label_2 = Label(master=self, text="密码")
        self.label_1.grid(row=0, column=0)  # 在master=Frame中进行部署
        self.label_2.grid(row=1, column=0)

        self.v1 = StringVar()  # Tkinter 封装的字符串类，相当于创建一个空字符串对象
        self.v2 = StringVar()
        self.entry_1 = Entry(master=self, textvariable=self.v1)  # 创建小部件实例（输入框），设置将输入字符串赋给 v1
        self.entry_2 = Entry(master=self, textvariable=self.v2, show='*')
        self.entry_1.grid(row=0, column=1, columnspan=2)  # 部署
        self.entry_2.grid(row=1, column=1, columnspan=2)

        self.button_1 = Button(master=self, text="登录", command=self.login)  # 创建小部件（按钮） command 表示点击后会调用的函数
        self.button_2 = Button(master=self, text="注册", command=self.register_step_1)
        self.button_1.grid(row=2, column=1)  # 部署
        self.button_2.grid(row=2, column=2)

    def login(self):
        """点击”登录“按钮后执行 完成login的逻辑
        """
        if CLIENT.is_connected is False:  # 查看是否已经连接
            if CLIENT.connect() is False:  # 判断是否连接成功
                messagebox.showerror(message="无法连接服务器",
                                     title="连接错误")
            return  # 返回mainloop 用户可重新点击重新尝试连接

        action = "login"
        username = self.v1.get()
        password = self.v2.get()  # 获取Tkinter 中 StringVar 类对象的值记用 get 方法
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
                if GLOBAL_DEBUG is True:  # 提示性的消息debug时print 异常消息都要print
                    print_by_time("login success")
                CLIENT.username = username  # 登录 成功 后才能修改Client中的值
                CLIENT.password = password
                # TODO 进入游戏大厅
            else:
                if GLOBAL_DEBUG is True:
                    print_by_time(info_list[2])
                messagebox.showerror(message=info_list[2], title="login error")  # 所有服务器端来的 error 代码都用messagebox处理

    def check_username(self, username):
        """在客户端判断用户名是否符合基本规范

        如果合适返回True，否则提示错误信息，返回False交给引用方处理
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
        """在客户端判断密码是否符合基本规范

        如果合适返回True，否则提示错误信息，返回False交给引用方处理
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
        if CLIENT.is_connected is False:  # 同 login 开头
            if CLIENT.connect() is False:
                messagebox.showerror(message="无法连接服务器",
                                     title="连接错误")
            return  # 返回mainloop

        action = "register_step_1"
        username = self.v1.get()  # 获取用户输入值
        password = self.v2.get()

        if self.check_username(username) is False or self.check_password(password) is False:
            return  # 返回mainloop
        else:
            msg = [action, username, password]
            CLIENT.send(msg)  # 查询数据库，看用户名是否已经存在，如果存在，服务器端暂时保存用户名和密码
            try:
                info_list = CLIENT.wait_msg(action)
            except NetworkError as error:
                print_by_time(error)
                messagebox.showerror(title="连接超时", message=str(error))
                return  # 返回mainloop
            else:
                if info_list[1] == "ok":
                    CLIENT.username = username  # 注册第一步成功，客户端暂时保存用户名密码
                    CLIENT.password = password
                    self.destroy()  # 注册第一步完成，这个ui已经完成使命，销毁
                    Register(master=ROOT)  # 创建register_step_2 的ui 进入注册的第二步
                else:
                    error = info_list[2]  # 处理错误代码
                    if error == "username_used":
                        messagebox.showerror(title="用户名错误", message="这个用户名太好以至于已经被使用过了！")
                        return  # 返回mainloop


class Register(Frame):
    """完成register_step_1 后自动启动，负责register的第二步和第三步
    """

    def __init__(self, master, *args, **kwargs):
        super(Register, self).__init__(master=master, *args, **kwargs)
        self.pack()
        self.create_widgets()

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

        self.button_1 = Button(master=self, text="获取", command=self.register_step_2)  # 点击进入相应函数
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
            return  # 返回mainloop 重新填写用户名
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
                self.mailbox = mailbox  # 记录信息，进入下一步
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
            return  # 退回mainloop 重试

        if info_list[1] == "ok":
            CLIENT.state["login"] = "ok"
            self.destroy()
            messagebox.showinfo(title="注册成功", message="已自动登录进入游戏")
            # TODO 进入游戏大厅
        else:
            error = info_list[2]
            if error == "wrong code":
                messagebox.showerror(title="验证码错误", message="验证码错误请重试")
                return  # 返回mainloop 重试


if __name__ == '__main__':
    LOCK = Lock()  # 线程锁 全局变量 多线程修改数据用 TODO 加入线程锁
    ROOT = Tk()  # 根界面 全局变量
    # ROOT.geometry("400x300")
    ROOT.title("登录")
    CLIENT = Client()  # 创建一个client对象，负责处理底层数据传输和状态记录，为全局变量
    login_ui = Login(master=ROOT)  # 默认创建登录界面
    ROOT.mainloop()  # 开始实践循环，捕获event
