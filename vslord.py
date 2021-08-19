from client import Client, LOCK
from threading import Thread
from tkinter import *

# 测试环境

CLIENT = Client()
CLIENT.username = "yangbc"
CLIENT.password = "yangbc"
CLIENT.mailbox = "2414836228@qq.com"
CLIENT.connect()
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
    _display = False
    _owner = None

    def __init__(self, owner=None, *args, **kwargs):
        self.appearance = None
        self.subordinate = []
        self.owner = owner

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        assert isinstance(self.owner, MyWidget)
        if isinstance(self.owner, MyWidget):  # 如果前主人继承我的组件类（其中含有subordinate这个lst）把我在前主人的lst中删去
            self.owner.subordinate.remove(self)
        self._owner = value  # 修改owner
        if isinstance(self.owner, MyWidget) and self.display:
            self.master = self.owner.appearance  # 换master
            self.owner.subordinate.append(self)
            assert isinstance(self.appearance, Widget)  # 改变本身widget的master
            self.appearance["master"] = self.master
            self.display = self.display
        else:
            self.master = None

    @property
    def display(self):
        return self._display

    @display.setter
    def display(self, value):
        assert value in [True, False], "set incorrect value for display"
        self._display = value
        if value == True:
            for widget in self.subordinate:
                widget.display = True  # 将self所有的附属组件展示出来
            if self.display:
                self.init_display()
        else:
            self.appearance.pack_forget()
            self.appearance.grid_forget()
            self.appearance.place_forget()

    def init_display(self):
        pass

    def pack(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget), "self.appearance 不是一个tkinter的widget"
        self.appearance.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget), "self.appearance 不是一个tkinter的widget"
        self.appearance.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        assert isinstance(self.appearance, Widget), "self.appearance 不是一个tkinter的widget"
        self.appearance.place(*args, **kwargs)

    def __add__(self, other):
        pass


class Timer:

    def __init__(self, owner):
        self.owner = owner

    def display(self):
        pass


class Card(MyWidget):

    def __init__(self, feature=(None, None), *args,
                 **kwargs):  # feature 为None显示扑克背面, (1, 0) 前一个代表大小, 后一个代表花色, 花色0: 红心, 1:方块, 2:梅花, 3:黑桃
        super(Card, self).__init__(*args, **kwargs)
        self.point, self.color = feature

    def init_display(self):
        img = PhotoImage(file="imgs/cards/{}.gif".format(self.point))
        self.appearance = Label(image=img)

    def __str__(self):
        point_to_str = {None: "未知", 1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                        11: "J", 12: "Q", 13: "K", 14: "小猴", 15: "大猴"}
        color_to_str = {None: "", 0: "红心", 1: "方块", 2: "梅花", 3: "黑桃"}
        return "Card: {} {} ".format(point_to_str[self.point], color_to_str[self.color])


class Cards(MyWidget):
    def __init__(self, cards=(), *args, **kwargs):  # cards = ((1, 0), (2, 0))
        super(Cards, self).__init__(*args, **kwargs)
        for card in cards:
            Card(feature=card, owner=self)

    @property
    def cards(self):
        return self.subordinate

    def init_display(self):
        self.appearance = Frame()
        for index, card in enumerate(self.cards):
            card.place(x=40 * index + 10, y=50)

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
    def cards(self):
        return self.subordinate[0]

    def init_display(self):
        self.appearance = Frame()
        self.cards.pack()

    def recieve_cards(self, cards):
        assert isinstance(cards, Cards)
        self.cards.__add__(cards)

    def __str__(self):
        return "Desk: {} ".format(self.cards)


class Info(MyWidget):
    def __init__(self, name, info, *args, **kwargs):
        super(Info, self).__init__(*args, **kwargs)
        self.name = name
        self.info = info

    def init_display(self):
        self.appearance = Frame()
        self.Label_01 = Label(master=self.appearance, text=self.name)
        self.Label_02 = Label(master=self.appearance, text=str(self.info))
        self.Label_01.pack()
        self.Label_02.pack()

    def __str__(self):
        return "Info: " + str({"name": self.name}.update(self.info)) + " "


class Player(MyWidget):
    def __init__(self, name, info, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.name = name
        Info(name=name, info=info, owner=self)
        Cards(cards=(), owner=self)

    @property
    def info(self):
        return self.subordinate[0]

    @property
    def cards(self):
        return self.subordinate[1]

    def init_display(self):
        self.appearance = Frame(master=self.master)
        self.info.pack()
        self.cards.pack()

    def recieve_cards(self, cards):
        assert isinstance(cards, Cards)
        self.cards.__add__(cards)

    def obey(self, info_list):
        pass

    def __str__(self):
        return "Player: " + str(self.info, self.cards)


class Me(Player):
    def __init__(self, *args, **kwargs):
        super(Me, self).__init__(*args, **kwargs)

    def display(self):
        pass


class GameState(MyWidget):
    """GameState 开启游戏，记录游戏信息，可供gui渲染
    """

    def __init__(self, me, player_info, display=True, *args, **kwargs):
        """保存gamestate基础信息, 初始化一些组件
        """
        super(GameState, self).__init__(*args, **kwargs)

        Me(name=me, info=player_info[me], owner=self)
        for name in player_info:
            if name != me:
                Player(name=name, info=player_info[name], owner=self)
        Desk(owner=self)

    @property
    def players(self):
        return_dict = {}
        for player in self.subordinate:
            if isinstance(player, Player):
                return_dict[player.name] = player
        return return_dict

    def start_game(self, display):
        """开始游戏。
        """
        thread_obey = Thread(target=self.let_obey)
        thread_obey.start()
        self.display = display
        thread_obey.join()

    def let_obey(self):
        """强迫玩家做出某些action
        """
        try:
            while True:
                for info_list in list(CLIENT.msg_to_obey):
                    player = self.players[info_list[2]]
                    player.obey(info_list)
                    # obey完action之后将该action踢出队列
                    LOCK.acquire()
                    CLIENT.msg_to_obey.remove(info_list)
                    LOCK.release()
                    # 修改值的时候加锁, save_msg有可能同时修改
        except Exception:  # TODO 异常处理
            return

    def init_display(self):
        """开启所有对象的display方法"""

        root = Tk()
        root.title("斗地主")
        self.appearance = root
        for obj in self.main_obj:
            obj.display(master=root)
        root.mainloop()
