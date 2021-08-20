from client import Client
from threading import *
from tkinter import *

# 测试环境
LOCK = Lock()
CLIENT = Client()
CLIENT.username = "yangbc"
CLIENT.password = "yangbc"
CLIENT.mailbox = "2414836228@qq.com"
CLIENT.state["login"] = "ok"
CLIENT.player_info = {
    "yangbc": {"points": 1000},
    "yuanye": {"points": 1000},
    "lvyaqiao": {"points": 1000},
}



print("ok")


###########
# Classes #
###########

class MyWidget:
    _master = None
    _owner = None
    _display = False

    def __init__(self, owner=None, *args, **kwargs):
        self.attachment = []
        self.owner = owner
        self.appearance = None

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if isinstance(self.owner, MyWidget):  # 如果前主人继承我的组件类（其中含有subordinate这个lst）把我在前主人的lst中删去
            self.owner.attachment.remove(self)
        self._owner = value  # 修改owner
        if isinstance(self.owner, MyWidget):  # 重建从属关系，最后重新显示，显示的时候根据从属关系，建一个appr得到atta的master
            self.owner.attachment.append(self)
            if self._display:
                self.display()
        else:
            self.master = None

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, value):
        self._master = value

    def _set_master(self):
        if isinstance(self, GameState):
            self.master = None
        elif isinstance(self, MyWidget):
            self.master = self.owner.appearance
        else:
            print("set master error")

    def display(self):
        self._set_master()
        self.set_appr()
        for widget in self.attachment:
            widget.display()
        self.place_atta()
        self._display = True

    def set_appr(self):  # 附属的外貌在init中已经创建，但是需要创建本身的外貌
        pass

    def place_atta(self):  # 一个组件可以摆放附属的位置
        pass

    def forget(self):  # 将一个组件隐藏
        self.appearance.pack_forget()
        self.appearance.grid_forget()
        self.appearance.place_forget()

    def pack(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget), "self.appearance 不是一个tkinter的widget"
        self.appearance.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget), "self.appearance 不是一个tkinter的widget"
        self.appearance.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget), "self.appearance 不是一个tkinter的widget"
        self.appearance.place(*args, **kwargs)

    def config(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget)
        self.appearance.config(*args, **kwargs)

    def __add__(self, other):
        pass


class Timer(MyWidget):

    def display(self):
        pass


class Card(MyWidget):

    def __init__(self, feature=(None, None), *args,
                 **kwargs):  # feature 为None显示扑克背面, (1, 0) 前一个代表大小, 后一个代表花色, 花色0: 红心, 1:方块, 2:梅花, 3:黑桃
        super(Card, self).__init__(*args, **kwargs)
        self.point, self.color = feature

    def set_appr(self):
        img = PhotoImage(file="imgs/cards/{}.gif".format(self.point))
        self.appearance = Label(master=self.master, image=img)
        self.appearance.image = img
        # self.appearance = Label(master=self.master, text="11 ")

    def place_atta(self):
        pass

    def __str__(self):
        point_to_str = {None: "未知", 1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                        11: "J", 12: "Q", 13: "K", 14: "小猴", 15: "大猴"}
        color_to_str = {None: "", 0: "红心", 1: "方块", 2: "梅花", 3: "黑桃"}
        return "Card: {} {} ".format(color_to_str[self.color], point_to_str[self.point])


class Cards(MyWidget):
    def __init__(self, cards=(), *args, **kwargs):  # cards = ((1, 0), (2, 0))
        super(Cards, self).__init__(*args, **kwargs)
        for card in cards:
            Card(feature=card, owner=self)

    @property
    def cards(self):  # 一个Card对象的list
        return self.attachment

    def set_appr(self):
        self.appearance = Frame(master=self.master)

    def place_atta(self):
        for card in self.cards:
            card.pack()

    def __add__(self, other):
        assert isinstance(other, Cards)
        for card in other.cards:
            card.owner = self

    def __str__(self):
        return "Cards: " + str(self.cards) + " "


class Desk(MyWidget):

    def __init__(self, *args, **kwargs):
        super(Desk, self).__init__(*args, **kwargs)
        Cards(cards=(), owner=self)

    @property
    def cards(self):  # 一个Cards对象
        return self.attachment[0]

    def set_appr(self):
        self.appearance = Frame(master=self.master)

    def place_atta(self):
        self.cards.pack()

    def receive_cards(self, cards):
        assert isinstance(cards, Cards)
        self.cards.__add__(cards)

    def __str__(self):
        return "Desk: {} ".format(self.cards)


class Info(MyWidget):
    def __init__(self, name, info, *args, **kwargs):
        super(Info, self).__init__(*args, **kwargs)
        self.name = name
        self.info = info

    def set_appr(self):
        self.appearance = Frame(master=self.master)
        self.Label_01 = Label(master=self.appearance, text=self.name)
        self.Label_02 = Label(master=self.appearance, text=str(self.info))
        self.Label_01.pack()
        self.Label_02.pack()

    def place_atta(self):
        pass

    def __str__(self):
        str_dict = {"name": self.name}
        str_dict.update(self.info)
        return "Info: " + str(str_dict) + " "


class Player(MyWidget):
    def __init__(self, name, info, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.name = name
        Info(name=name, info=info, owner=self)
        Cards(cards=(), owner=self)

    @property
    def info(self):  # 一个Info对象
        return self.attachment[0]

    @property
    def cards(self):  # 一个Cards对象
        return self.attachment[1]

    def set_appr(self):
        self.appearance = Frame(master=self.master, bg="red")

    def place_atta(self):
        self.info.pack()
        self.cards.pack()

    def receive_cards(self, cards):
        assert isinstance(cards, Cards)
        self.cards.__add__(cards)

    def obey(self, info_list):
        pass

    def __str__(self):
        return "Player: " + str(self.info, self.cards)


class Me(Player):
    def __init__(self, *args, **kwargs):
        super(Me, self).__init__(*args, **kwargs)


class GameState(MyWidget):
    """GameState 开启游戏，记录游戏信息，可供gui渲染
    """

    def __init__(self, me, player_info, *args, **kwargs):
        """保存gamestate基础信息, 初始化一些组件
        """
        super(GameState, self).__init__(*args, **kwargs)

        Me(name=me, info=player_info[me], owner=self)
        for name in player_info:
            if name != me:
                Player(name=name, info=player_info[name], owner=self)
        Desk(owner=self)
        self.me = me

        Card(feature=(1, 1), owner=self)

    @property
    def player_dict(self):
        player_dict = {}
        for player in self.attachment:
            if isinstance(player, Player):
                player_dict[player.name] = player
        return player_dict

    def start_game(self, display):
        """开始游戏。
        """
        thread_obey = Thread(target=self.let_obey)
        thread_obey.start()
        if display is True:
            self.display()
        thread_obey.join()

    def let_obey(self):
        """强迫玩家做出某些action
        """
        try:
            while True:
                for info_list in list(CLIENT.msg_to_obey):
                    player = self.player_dict[info_list[2]]
                    player.obey(info_list)
                    # obey完action之后将该action踢出队列
                    LOCK.acquire()
                    CLIENT.msg_to_obey.remove(info_list)
                    LOCK.release()
                    # 修改值的时候加锁, save_msg有可能同时修改
        except Exception:  # TODO 异常处理
            return

    def set_appr(self):
        """开启所有对象的display方法"""
        root = Tk()
        root.title("斗地主")
        # root.geometry("1000x800")
        self.appearance = root

    def place_atta(self):
        self.attachment[0].config(bg="green")
        self.attachment[0].place(relx=0.3, rely=0.5, relwidth=0.4, relheight=0.5)
        self.attachment[1].config(bg="red")
        self.attachment[1].place(relx=0, rely=0, relwidth=0.3, relheight=0.5)
        self.attachment[2].config(bg="red")
        self.attachment[2].place(relx=0.7, rely=0, relwidth=0.3, relheight=0.5)
        self.attachment[3].config(bg="yellow")
        self.attachment[3].place(relx=0.3, rely=0, relwidth=0.4, relheight=0.5)
        cards = Cards(cards=((1, 2), (2, 2)), owner=self.attachment[3])
        self.attachment[3].receive_cards(cards)
        self.appearance.mainloop()


gamestate = GameState("yangbc", CLIENT.player_info).start_game(display=True)

