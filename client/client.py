from socket import *
# from tkinter import *
from tkinter import messagebox
# from tkinter import ttk
from ctypes import windll
from utils import *
import re
import threading
from vslord_client import *


class CommunicateThread(threading.Thread):
    """负责与服务器的连接和通信,以及处理网络异常"""

    def __init__(self, master, server_addr=("127.0.0.1", 10001), try_time=5, *args, **kwargs):

        super(CommunicateThread, self).__init__(*args, **kwargs)
        self.master = master
        self.server_addr = server_addr
        self.try_time = try_time
        self._stop_event = threading.Event()
        self.connected = False
        self.socket = None

    def stop(self):
        self._stop_event.set()
        self.master.connection = None

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def run(self) -> None:
        """首先尝试连接服务器，成功以后，开始监听消息并保存"""
        self.try_connect()
        self.save_msg()

    def try_connect(self):
        while not self.connected and not self.stopped:
            try:
                self.socket = socket(AF_INET, SOCK_STREAM)
                self.socket.connect(self.server_addr)
            except Exception as error:
                print_by_time(error)  # 异常处理:捕获到的异常print出来
                self.socket.close()
                time.sleep(1)
                self.try_time -= 1
                if self.try_time < 0.5:
                    msg = "无法连接服务器, 请重试"
                    self.stop()  # 只要超过五次连接失败，就中止线程
                    raise NetworkError(msg)
                
            else:
                self.connected = True
                if GLOBAL_DEBUG:
                    print_by_time("成功连接服务器")

    def recv(self):  # 异常处理交给 save_msg 方法
        recv_msg = self.socket.recv(1024).decode('utf-8').strip()  # TODO 阻塞，导致无法关闭线程
        info_list = recv_msg.split(',')
        if GLOBAL_DEBUG:
            print_by_time("recieve from server: " + " ".join(info_list))
        return info_list

    def save_msg(self):
        """死循环 单独一个线程 记录从服务器端发来的信息
        """
        while True:
            if self.stopped:
                self.socket.close()
                return
            try:
                info_list = self.recv()
                if info_list == ['']:  # socket 的特性是如果一方关闭socket另一方会收到['']
                    self.connected = False
                    self.socket.close()
                    self.stop()
                    raise NetworkError("服务器端断开连接")
            except Exception as error:  # 处理socket.recv() 的异常
                self.socket.close()
                self.connected = False
                print_by_time(error)
                self.try_connect()
            else:
                if info_list[1] == "obey":
                    self.master.LOCK.acquire()
                    self.master.msg_to_obey.append(info_list)  # TODO 假定同时只有一个
                    self.master.LOCK.release()
                else:
                    self.master.recv_msg[info_list[0]] = info_list  # 保存来自服务器的消息
                    self.master.state[info_list[0]] = info_list[1]  # 根据消息提取出action的state，进行保存

    def wait_msg(self, action, timeout=5, step=0.05):
        """ 等待处理程序需要的消息(给定action或state的消息)的出现

        快速扫描 recv_msg
        如果在规定的时间内找到了需要的action对应的info_list返回
        如果美哟在规定的时间内找到，抛出异常

        :param action: 你需要的action
        :param timeout: 等待时间，超时抛出异常
        :param step: 扫描间隔
        :return: 你想要的 info_list
        """
        ddl = time.time() + timeout  # TODO 同一个action不会有多个消息，但是同一个state可能有多个消息

        while time.time() < ddl:
            if action in self.master.recv_msg:
                return self.master.recv_msg.pop(action)
            else:
                time.sleep(step)
        raise NetworkError("等待服务器消息超时(花费{}s)".format(timeout))  # 超时引发异常

    def send(self, msg):
        """发送给定格式的信息到服务器端

        无异常处理

        :param msg: 一个list 如 ["login", "username", "password"]
        """
        if GLOBAL_DEBUG == True:
            print_by_time("send to server: " + " ".join(msg))
        msg = ",".join(msg)  # 用","做分割是因为如果username中有空格不好办
        self.socket.send(msg.encode('utf-8'))

        # TODO 没有加入异常处理，因为如果无法发送信息，最大原因是对方关闭链接而这时savemsg方法早已捕获异常，connected 为 False。引用方应该确保在connected 为 True 的情况下调用


class Client:
    """Client的method实现了所有对网络有关的封装，Client的instance记录下当前所有（有效的）信息
    """

    def __init__(self, server_addr=("127.0.0.1", 10001)):
        self.server_addr = server_addr  # 调试用端口（即本机的10001端口）端口冲突自行修改

        self.username = None
        self.password = None
        self.connection = None
        self.mailbox = None  # 当用户登录成功，注册成功时，对应的ui会记录用户用户名、密码、和邮箱（因为一个ui完成对应的任务后会自动销毁）

        self.threads = {}  # 保存线程，暂时无用
        self.state = {}  # 记录收到消息中所有action的状态 {"register_step_1": "ok", ...}
        self.player_info = {}  # 记录所有玩家信息 {"yuanye": {...}}
        self.recv_msg = {}  # 保存recv方法得到的消息，以action作为关键字 {"login": ["login", "error", "user_not_found"]}
        self.msg_to_obey = []  # 保存等待遵守的action [["give_cards_to", "force", "yangbc", "Cards"], ...]
        self.roomate_info = {}  # 保存当前房间所有人的信息 {
                                #     "yangbc": {"points": 1000},
                                #     "yuanye": {"points": 1000},
                                #     "lvyaqiao": {"points": 1000},
                                # }

        self.LOCK = threading.Lock()  # 线程锁 全局变量 多线程修改数据用 TODO 加入线程锁
        self.connect(server_addr=server_addr, try_time=5)

    @property
    def connected(self):
        if self.connection is not None:
            return self.connection.connected
        else:
            return False

    def connect(self, *args, **kwargs):  # TODO 断线重连
        """创建线程进行communicate
        """
        t = CommunicateThread(master=self, *args, **kwargs)
        self.connection = t
        self.threads["connection"] = t  # 将进程记录 TODO 线程管理
        try:
            t.start()
        except NetworkError as e:
            print_by_time(e)
            messagebox.showerror(title="连接异常", message=str(e))

    def disconnect(self):
        assert self.connection
        self.connection.stop()

    def wait_msg(self, *args, **kwargs):
        if self.connected:
            return self.connection.wait_msg(*args, **kwargs)
        else:
            self.connect()
            raise NetworkError("尝试重新连接服务器")

    def send(self, *args, **kwargs):
        if self.connected:
            return self.connection.send(*args, **kwargs)
        else:
            self.connect()
            raise NetworkError("尝试重新连接服务器")


class Login(ttk.Frame):
    """运行程序默认创建的第一个ui，实现的action： login, register_step_1

    ui 和 功能同步实现
    """

    def __init__(self, master, client):
        super(Login, self).__init__(master=master, padding="5 5 5 5")
        self.grid(row=0, column=0, sticky=(N, S, W, E))  # 在root中布局自身
        self.master = master
        self.client = client
        self.valid_name = False
        self.valid_pswd = False

        self.create_widgets()  # 生成小部件

    def check_username(self, username, op):
        """在客户端判断用户名是否符合基本规范

        如果合适返回True，否则提示错误信息，返回False交给引用方处理
        6~18位字符，只能包含英文字母，数字，下划线。
        """
        msg = "请输入6~18位字符，只能包含英文字母，数字，下划线"
        self.errmsg.set("")
        valid = re.match(r"^[a-zA-Z0-9_]{6,18}$", username) is not None

        self.valid_name = valid
        self.button_2.state(["!disabled"] if self.valid_name and self.valid_pswd else ["disabled"])
        self.button_1.state(["!disabled"] if self.valid_name and self.valid_pswd else ["disabled"])

        if op == "key":
            ok_so_far = re.match(r"^[a-zA-Z0-9_]{0,18}$", username) is not None
            if not ok_so_far:
                self.errmsg.set(msg)
            return ok_so_far
        elif op == "focusout":
            if not valid:
                self.errmsg.set(msg)
            return valid
        else:
            print("没有捕获到的event: ", op)
            return True

    def check_password(self, password, op):
        """在客户端判断密码是否符合基本规范

        如果合适返回True，否则提示错误信息，返回False交给引用方处理
        6~18位字符，只能包含英文字母，数字。
        """

        msg = "请输入6~18位字符，只能包含英文字母，数字"
        self.errmsg.set("")
        valid = re.match(r"^[a-zA-Z0-9]{6,18}$", password) is not None

        self.valid_pswd = valid
        self.button_2.state(["!disabled"] if self.valid_name and self.valid_pswd else ["disabled"])
        self.button_1.state(["!disabled"] if self.valid_name and self.valid_pswd else ["disabled"])

        if op == "key":
            ok_so_far = re.match(r"^[a-zA-Z0-9]{0,18}$", password) is not None
            if not ok_so_far:
                self.errmsg.set(msg)
            return ok_so_far
        elif op == "focusout":
            if not valid:
                self.errmsg.set(msg)
            return valid
        else:
            print("没有捕获到的event: ", op)
            return True

    def remember(self):
        try:
            f = open("my_info.txt", "r")
            info_dict = eval(f.read())
            if info_dict["remember"] is True:
                self.is_remember.set(True)
                self.v1.set(info_dict["username"])
                self.v2.set(info_dict["password"])

        except IOError:
            try:
                f = open("my_info.txt", "w")
                init_str = "{'remember': False, 'username': '', 'password': ''}"
                f.write(init_str)
            except Exception as error:
                self.errmsg.set(str(error))

    def set_remember(self):
        if self.is_remember.get() is False:
            with open("my_info.txt", "w") as f:
                init_str = "{'remember': False, 'username': '', 'password': ''}"
                f.write(init_str)
        else:
            with open("my_info.txt", "w") as f:
                info_dict = {'remember': True, 'username': self.v1.get(), 'password': self.v2.get()}
                f.write(str(info_dict))

    def create_widgets(self):
        self.errmsg = StringVar(value="")
        self.label_error = ttk.Label(master=self, textvariable=self.errmsg, font='TkSmallCaptionFont', foreground='red')
        self.label_error.grid(row=3, columnspan=3)

        self.label_1 = ttk.Label(master=self, text="用户名")  # 创建小部件实例（标签）
        self.label_2 = ttk.Label(master=self, text="密码")
        self.label_1.grid(row=0, column=0)  # 在master=Frame中进行部署
        self.label_2.grid(row=1, column=0)

        self.v1 = StringVar(value="")  # Tkinter 封装的字符串类，相当于创建一个空字符串对象
        self.v2 = StringVar(value="")

        check_username_wrapper = (self.master.register(self.check_username), "%P", "%V")
        self.entry_1 = ttk.Entry(master=self, textvariable=self.v1, validate='all',
                                 validatecommand=check_username_wrapper)  # 创建小部件实例（输入框），设置将输入字符串赋给 v1

        check_password_wrapper = (self.master.register(self.check_password), "%P", "%V")
        self.entry_2 = ttk.Entry(master=self, textvariable=self.v2, show='*', validate='all',
                                 validatecommand=check_password_wrapper)
        self.entry_1.grid(row=0, column=1, columnspan=2, sticky=EW)  # 部署
        self.entry_2.grid(row=1, column=1, columnspan=2, sticky=EW)

        self.button_1 = ttk.Button(master=self, text="登录", command=self.login)  # 创建小部件（按钮） command 表示点击后会调用的函数
        self.button_2 = ttk.Button(master=self, text="注册", command=self.register_step_1)

        self.button_1.grid(row=2, column=1)  # 部署
        self.button_2.grid(row=2, column=2)

        self.is_remember = BooleanVar(value=False)
        self.remember()
        self.check_button_1 = ttk.Checkbutton(master=self, text="记住账户", variable=self.is_remember, onvalue=True,
                                              offvalue=False, command=self.set_remember)
        self.check_button_1.grid(row=1, column=3)

        self.check_password(self.v2.get(), "focusout")
        self.check_username(self.v1.get(), "focusout")

        self.entry_1.focus()
        # self.master.bind("<Return>", lambda e: self.login())  # 快捷键

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def login(self):
        """点击”登录“按钮后执行 完成login的逻辑
        """
        action = "login"
        username = self.v1.get()
        password = self.v2.get()  # 获取Tkinter 中 StringVar 类对象的值记用 get 方法
        msg = [action, username, password]
        try:
            self.client.send(msg)
            info_list = self.client.wait_msg(action=action)
            print_by_time(info_list)
        except NetworkError as error:
            print_by_time(error)
            return  # 退回mainloop 相当于恢复原来的状态

        if info_list[0] == action:
            if info_list[1] == "ok":
                if GLOBAL_DEBUG is True:  # 提示性的消息debug时print 异常消息都要print
                    print_by_time("login success")
                self.client.username = username  # 登录 成功 后才能修改Client中的值
                self.client.password = password
                # TODO 进入游戏大厅

                def test_env():
                    self.client.roomate_info = {
                        "111111": {"points": 1000},
                        "yuanye": {"points": 1000},
                        "lvyaqiao": {"points": 1000},
                    }
                    GameState(self.client.username, self.client.roomate_info, self.client.username, client=self.client).start_game(display=True, master=self.master)

                test_env()
            else:
                if GLOBAL_DEBUG is True:
                    print_by_time(info_list[2])
                messagebox.showerror(message=info_list[2], title="login error")  # 所有服务器端来的 error 代码都用messagebox处理

    def register_step_1(self):

        action = "register_step_1"
        username = self.v1.get()  # 获取用户输入值
        password = self.v2.get()

        msg = [action, username, password]

        try:
            self.client.send(msg)  # 查询数据库，看用户名是否已经存在，如果存在，服务器端暂时保存用户名和密码
            info_list = self.client.wait_msg(action)
        except NetworkError as error:
            print_by_time(error)
            messagebox.showerror(title="连接超时", message=str(error))
            return  # 返回mainloop
        else:
            if info_list[1] == "ok":
                self.client.username = username  # 注册第一步成功，客户端暂时保存用户名密码
                self.client.password = password
                self.destroy()  # 注册第一步完成，这个ui已经完成使命，销毁
                Register(master=self.master, client=self.client)  # 创建register_step_2 的ui 进入注册的第二步
            else:
                error = info_list[2]  # 处理错误代码
                if error == "username_used":
                    messagebox.showerror(title="用户名错误", message="这个用户名太好以至于已经被使用过了！")
                    return  # 返回mainloop


class Register(ttk.Frame):
    """完成register_step_1 后自动启动，负责register的第二步和第三步
    """

    def __init__(self, master, client):
        super(Register, self).__init__(master=master, padding="5 5 5 5")
        self.grid(row=0, column=0, sticky=(N, S, W, E))
        self.master = master
        self.client = client

        self.create_widgets()

    def check_mailbox(self, mailbox, op):
        """合法返回True，非法messagebox提示，返回False
        """
        msg = "邮箱格式错误"
        self.errmsg.set("")
        valid = re.match(r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$", mailbox) is not None
        self.button_1.state(["!disabled"] if valid else ["disabled"])
        if valid is False and op == "focusout":
            return False
        else:
            return True

    def check_code(self, code, op):
        """检查验证码"""
        msg = "验证码为四位数字"
        self.errmsg.set("")
        valid = re.match(r"^[0-9]{4}$", code) is not None
        print(valid)
        self.button_2.state(["!disabled"] if valid else ["disabled"])
        if op == "key":
            ok_so_far = re.match(r"^[0-9]{1,4}$", code) is not None
            if not ok_so_far:
                self.errmsg.set(msg)
            return ok_so_far
        elif op == "focusout":
            if not valid:
                self.errmsg.set(msg)
            return valid
        else:
            print("没有捕获到的event: ", op)
            return True

    def create_widgets(self):
        self.errmsg = StringVar(value="")
        self.label_error = ttk.Label(master=self, textvariable=self.errmsg, font='TkSmallCaptionFont', foreground='red')

        self.label_1 = ttk.Label(master=self, text="邮箱")
        self.label_2 = ttk.Label(master=self, text="验证码")
        self.label_1.grid(row=0, column=0)
        self.label_2.grid(row=1, column=0)

        self.v1 = StringVar(value="")
        self.v2 = StringVar(value="")
        check_mailbox_wrapper = (self.master.register(self.check_mailbox), "%P", "%V")
        check_code_wrapper = (self.master.register(self.check_code), "%P", "%V")
        self.entry_1 = ttk.Entry(master=self, textvariable=self.v1, validate="all",
                                 validatecommand=check_mailbox_wrapper)
        self.entry_2 = ttk.Entry(master=self, textvariable=self.v2, validate="all", validatecommand=check_code_wrapper)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)

        self.button_1 = ttk.Button(master=self, text="获取", command=self.register_step_2)  # 点击进入相应函数
        self.button_2 = ttk.Button(master=self, text="注册", command=self.register_step_3)
        self.button_1.grid(row=1, column=2, sticky=(E, W))
        self.button_2.grid(row=2, column=1, sticky=(E, W))

        self.button_1.state(["disabled"])
        self.button_2.state(["disabled"])
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def register_step_2(self):
        action = "register_step_2"
        mailbox = self.v1.get()
        print(mailbox)

        msg = [action, mailbox]
        try:
            self.client.send(msg)
            info_list = self.client.wait_msg(action=action)
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
        if self.client.state[pre_action] != "ok":
            messagebox.showerror(title="注册错误", message="请先获取填写验证码")
            return  # 返回mainloop 重试

        code = self.v2.get()
        msg = [action, code]
        try:
            self.client.send(msg)
            info_list = self.client.wait_msg(action=action)
        except NetworkError as error:
            print_by_time(error)
            messagebox.showerror(message=str(error), title="连接超时")
            return  # 退回mainloop 重试

        if info_list[1] == "ok":
            self.client.state["login"] = "ok"
            self.destroy()
            messagebox.showinfo(title="注册成功", message="已自动登录进入游戏")
            # TODO 进入游戏大厅
        else:
            error = info_list[2]
            if error == "wrong_code":
                messagebox.showerror(title="验证码错误", message="验证码错误请重试")
                return  # 返回mainloop 重试


def main():
    windll.shcore.SetProcessDpiAwareness(1)
    client = Client()  # 创建一个client对象，负责处理底层数据传输和状态记录，为全局变量

    root = Tk()  # 根界面 全局变量
    # ROOT.geometry("400x300")
    root.title("登录")
    Login(master=root, client=client)  # 默认创建登录界面
    root.mainloop()  # 开始事件循环，捕获event
    client.disconnect()
    print("断开连接")

if __name__ == '__main__':
    main()
