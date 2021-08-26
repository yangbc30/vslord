import builtins
from threading import *
from tkinter import *
from tkinter import ttk

from rule import is_valid
from utils import *
from collections import OrderedDict
import ctypes


# 测试环境
class Client:
    state = {}
    msg_to_obey = []


###########
# Classes #
###########

class MyWidget:
    _master = None
    _owner = None
    _displaying = False

    def __init__(self, owner=None, *args, **kwargs):
        self.attachment = []
        self.appearance = None
        self.owner = owner

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):  # 不参与display
        if isinstance(self.owner, MyWidget):  # 如果前主人继承我的组件类（其中含有subordinate这个lst）把我在前主人的lst中删去
            self.owner.attachment.remove(self)
        self._owner = owner  # 修改owner
        if self.appearance:
            self.destory()
        if isinstance(self.owner, MyWidget):  # 重建从属关系，最后重新显示，显示的时候根据从属关系，建一个appr得到atta的master
            self.owner.attachment.append(self)

    @property
    def master(self):
        if type(self) is GameState:
            self._master = None
        assert self.owner.appearance, "上级还未创建appr {} {}".format(self.owner, self.owner.appearance)
        self._master = self.owner.appearance
        return self._master

    @property
    def displaying(self):
        return self._displaying

    @displaying.setter
    def displaying(self, value):
        assert value is True or value is False, "_displaying不支持的value"
        self._displaying = value

    # @timing
    def display(self):
        if self.appearance is None:  #
            self.set_appr()
        for widget in self.attachment:
            widget.display()
        self.place_atta()
        self.displaying = True

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

    def destory(self):
        self.appearance.destroy()
        self.appearance = None


class Timer(MyWidget):

    def display(self):
        pass


class Card(MyWidget):
    order_dict = {None: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11, 1: 12, 2: 13,
                  14: 14,
                  15: 15}

    def __init__(self, feature=(None, None), *args,
                 **kwargs):  # feature 为None显示扑克背面, (1, 0) 前一个代表大小, 后一个代表花色, 花色0: 红心, 1:方块, 2:梅花, 3:黑桃
        super(Card, self).__init__(*args, **kwargs)
        self.point, self.color = feature
        self.selected = False
        self.to_set_img = True

    @property
    def value(self):
        return self.order_dict[self.point]

    @property
    def mate_info(self):
        return self.point, self.color

    def select(self, event):
        if self.selected is False:
            event.widget.place(y=-20)
            self.selected = True
        else:
            event.widget.place(y=0)
            self.selected = False

    def set_appr(self):
        self.appearance = ttk.Label(master=self.master)
        if self.owner.can_select:
            self.appearance.bind("<Button-1>", self.select)
            # print(1)

    @property
    def img(self):
        if self.owner.anonymous is True:
            return CARD_IMG["None_None"].subsample(4, 4)
        else:
            return CARD_IMG["{}_{}".format(self.point, self.color)].subsample(4, 4)

    def set_img(self):
        if self.to_set_img is True:
            img = self.img
            self.appearance["image"] = img
            self.appearance.image = img
            self.to_set_img = False
        else:
            pass

    def place_atta(self):
        pass

    def __eq__(self, other):
        assert type(other) is Card
        if self.point == other.point and self.color == other.color:
            return True
        else:
            return False

    def __lt__(self, other):
        assert type(other) is Card

        return self.order_dict[self.point] < self.order_dict[other.point]

    def __gt__(self, other):
        return other < self

    def __str__(self):
        point_to_str = {None: "未知", 1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                        11: "J", 12: "Q", 13: "K", 14: "小猴", 15: "大猴"}
        color_to_str = {None: "", 0: "红心", 1: "方块", 2: "梅花", 3: "黑桃"}
        return "Card: {} {} ".format(color_to_str[self.color], point_to_str[self.point])


class Cards(MyWidget):
    class_name = "Cards"

    def __init__(self, cards=(), can_select=False, anonymous=True, *args, **kwargs):  # cards = ((1, 0), (2, 0))
        super(Cards, self).__init__(*args, **kwargs)
        self.can_select = can_select
        self.anonymous = anonymous
        # print(self.can_select)
        for card in cards:
            Card(feature=card, owner=self)
        self.sort_cards()

    @property
    def mate_info(self):  # 生成该牌堆的元数据
        lst = []
        for card in self.card_list:
            lst.append(card.mate_info)
        return tuple(lst)

    @property
    def card_list(self):  # 一个Card对象的list
        return self.attachment

    @property
    def cards_selected(self):
        assert self.can_select
        lst = []
        for card in self.card_list:
            if card.selected is True:
                lst.append(card.mate_info)
        return ValidCards(tuple(lst))

    def set_appr(self):
        self.appearance = ttk.Frame(master=self.master)
        # self.appearance = ttk.Frame(master=self.master, bg="grey")

    def place_atta(self):
        x_border = 0.1
        y_border = 0.1
        num = len(self.card_list)
        if num == 0:
            step = 0
            x_border = 0.4
        else:
            step = 0.8 / num
        for index, card in builtins.enumerate(self.card_list):
            card.set_img()
            card.place(relx=step * index + x_border, rely=y_border)

    @staticmethod
    def swap_card(a, b):
        assert type(a) is Card and type(b) is Card
        a.point, b.point = b.point, a.point
        a.color, b.color = b.color, a.color
        a.selected, b.selected = b.selected, a.selected
        a.to_set_img, b.to_set_img = True, True

    # @timing
    def sort_cards(self):  # 不参与display
        num = len(self.card_list)
        for i in range(num - 1):
            for j in range(num - 1 - i):
                if self.card_list[j] > self.card_list[j + 1]:
                    Cards.swap_card(self.card_list[j], self.card_list[j + 1])

    def __add__(self, other):
        assert isinstance(other, Cards), "只能用Cards加Cards"
        for card in list(other.card_list):
            card.owner = self
        if self.anonymous is False:
            self.sort_cards()
        if self.displaying is True:
            self.display()

    def __sub__(self, other):
        assert isinstance(other, Cards), "只能用Cards加Cards"
        for card in list(self.card_list):
            if card in other.card_list:
                card.owner = "Trash"
        if self.displaying is True:
            self.display()

    def __str__(self):
        return self.class_name + ": " + str([str(card) for card in self.card_list]) + " "


class ValidCards(Cards):
    class_name = "ValidCards"

    def __init__(self, *args, **kwargs):
        super(ValidCards, self).__init__(anonymous=False, *args, **kwargs)
        self.valid = False
        self.pattern = None
        self.value = None
        self.validate()  # 创建时判断是否合法（不比大小）

    def validate(self, current_cards=None):
        is_valid(self, current_cards)
        print("是否合法", self.valid, self.pattern, self.value)

    @property
    def feature_dict(self):  # 这个牌堆的特征，key=value，mate_info=times，按照time优先，point其次，由大到小
        dict_1 = {}
        for card in self.card_list:
            if card.value in dict_1:
                dict_1[card.value] += 1
            else:
                dict_1[card.value] = 1

        dict_2 = OrderedDict()

        for i in range(len(dict_1)):
            curr_value = 0
            curr_times = 0
            for value in dict_1:
                if dict_1[value] > curr_times:
                    curr_times = dict_1[value]
                    curr_value = value
                elif dict_1[value] == curr_times:
                    if value > curr_value:
                        curr_value = value
            dict_1.pop(curr_value)
            dict_2[curr_value] = curr_times

        return dict_2

    @property
    def feature_str(self):  # 这个牌堆的特征“3322”
        s = ""
        for value in list(self.feature_dict.values()):
            s += str(value)
        return s

    def __add__(self, other):
        super(ValidCards, self).__add__(other)
        self.validate()

    def __sub__(self, other):
        super(ValidCards, self).__sub__(other)
        self.validate()


class Info(MyWidget):
    def __init__(self, name, info, *args, **kwargs):
        super(Info, self).__init__(*args, **kwargs)
        self.name = name
        self.info = info

    def set_appr(self):
        self.appearance = ttk.Frame(master=self.master)
        self.Label_01 = ttk.Label(master=self.appearance, text=self.name)
        self.Label_02 = ttk.Label(master=self.appearance, text=str(self.info))
        self.Label_01.pack()
        self.Label_02.pack()

    def place_atta(self):
        pass

    def __str__(self):
        str_dict = {"name": self.name}
        str_dict.update(self.info)
        return "Info: " + str(str_dict) + " "


class Obeyer(MyWidget):
    def obey(self, info_lst):
        pass

    @property
    def cards(self):
        return Cards()

    def receive_cards(self, cards):
        self.cards.__add__(cards)

    def remove_cards(self, cards):
        self.cards.__sub__(cards)


class Desk(Obeyer):

    def __init__(self, *args, **kwargs):
        super(Desk, self).__init__(*args, **kwargs)
        ValidCards(cards=(), owner=self)

    @property
    def current_cards(self):
        return self.attachment[0]

    @current_cards.setter
    def current_cards(self, value):
        self.remove_cards(self.current_cards)
        self.receive_cards(value)

    @property
    def cards(self):  # 一个Cards对象
        return self.attachment[0]

    def set_appr(self):
        self.appearance = ttk.Frame(master=self.master)

    def place_atta(self):
        self.cards.place(x=0, y=100, relwidth=1, relheight=1)

    def __str__(self):
        return "Desk: {} ".format(self.cards)


class Player(Obeyer):
    def __init__(self, name, info, can_select=False, anonymous=True, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.name = name
        Info(name=name, info=info, owner=self)
        Cards(cards=(), can_select=can_select, anonymous=anonymous, owner=self)

    @property
    def info(self):  # 一个Info对象
        return self.attachment[0]

    @property
    def cards(self):  # 一个Cards对象
        return self.attachment[1]

    def set_appr(self):
        self.appearance = ttk.Frame(master=self.master)

    def place_atta(self):
        self.info.pack()
        self.cards.place(x=0, y=100, relwidth=1, relheight=1)

    def __str__(self):
        return "Player: " + str(self.info, self.cards)


class ActionBar(MyWidget):
    def __init__(self, *args, **kwargs):
        super(ActionBar, self).__init__(*args, **kwargs)

    def set_appr(self):
        self.appearance = ttk.Frame(master=self.master)
        button_1 = ttk.Button(master=self.appearance, text="不要", command=self.owner.pass_round)
        button_2 = ttk.Button(master=self.appearance, text="出牌", command=self.owner.drop_cards_request)
        button_1.pack()
        button_2.pack()

    def place_atta(self):
        pass


class Me(Player):
    def __init__(self, client=None, *args, **kwargs):
        super(Me, self).__init__(can_select=True, anonymous=False, *args, **kwargs)
        ActionBar(owner=self)
        self.client = client

    @property
    def selected_cards(self):
        return self.cards.cards_selected

    @property
    def action_bar(self):
        return self.attachment[2]

    def place_atta(self):
        super(Me, self).place_atta()
        self.action_bar.pack()

    def pass_round(self):
        action_name = "pass_round"
        print("不要")
        # action = Action(self.owner, action_name)

    def drop_cards_request(self):
        cards = self.selected_cards  # ValidCards类型
        cards.validate(self.owner.current_cards)
        print("上家牌：", str(self.owner.current_cards))
        print("出牌", str(cards))

        if cards.valid:
            self.owner.current_cards = cards

    def drop_cards_implement(self):
        pass


class GameState(MyWidget):
    """GameState 开启游戏，记录游戏信息，可供gui渲染
    """

    def __init__(self, me, player_info, current_player, client, *args, **kwargs):
        """保存gamestate基础信息, 初始化一些组件
        """
        super(GameState, self).__init__(*args, **kwargs)

        Me(name=me, info=player_info[me], owner=self, client=client)
        for name in player_info:
            if name != me:
                Player(name=name, info=player_info[name], owner=self)
        Desk(owner=self)
        self.me = me
        self.current_player = current_player
        self._current_cards = None
        self.client = client

    def send(self, msg):
        pass

        # Card(feature=(1, 1), owner=self)

    @property
    def desk(self):
        return self.attachment[3]

    @property
    def current_cards(self):
        return self.desk.current_cards

    @current_cards.setter
    def current_cards(self, value):
        self.desk.current_cards = value

    @property
    def player_dict(self):
        player_dict = {}
        for player in self.attachment:
            if isinstance(player, Player):
                player_dict[player.name] = player
        return player_dict

    def start_game(self, display=False, master=None):
        """开始游戏。
        """
        thread_obey = Thread(target=self.let_obey)
        thread_obey.start()
        if display is True:
            self.root = master
            self.start_gui()
        # thread_obey.join()

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
        assert type(self.root) is Tk
        for w in self.root.winfo_children():
            w.destroy()

        self.root.title("斗地主")
        self.root.geometry("1000x800")
        self.appearance = self.root

    # @timing
    def place_atta(self):
        # self.attachment[0].config(bg="green")
        self.attachment[0].place(relx=0.3, rely=0.5, relwidth=0.4, relheight=0.5)
        # self.attachment[1].config(bg="red")
        self.attachment[1].place(relx=0, rely=0, relwidth=0.3, relheight=0.5)
        # self.attachment[2].config(bg="red")
        self.attachment[2].place(relx=0.7, rely=0, relwidth=0.3, relheight=0.5)
        # self.attachment[3].config(bg="yellow")
        self.attachment[3].place(relx=0.3, rely=0, relwidth=0.4, relheight=0.5)
        # print(self.attachment[0].cards.appearance)

        self.attachment[0].receive_cards(Cards(test_cards(CARDS, 25)))
        # self.attachment[1].receive_cards(Cards(test_cards(CARDS, 18)))
        # self.attachment[2].receive_cards(Cards(test_cards(CARDS, 54)))
        self.desk.receive_cards(Cards(cards=((1, 1),)))

        self.attachment[3].remove_cards(Cards(((1, 1),)))  # test drop cards or card

    def start_gui(self):
        global CARDS
        CARDS = tuple([(point, color) for point in range(1, 14) for color in range(4)] + [(14, None), (15, None)])
        global CARD_IMG
        CARD_IMG = {"{}_{}".format(point, color): PhotoImage(file="imgs/cards/{}_{}.png".format(point, color)) for
                    point, color in list(CARDS) + [(None, None)]}
        self.display()
        self.appearance.mainloop()


if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    LOCK = Lock()
    CLIENT = Client()
    CLIENT.player_info = {
        "yangbc": {"points": 1000},
        "yuanye": {"points": 1000},
        "lvyaqiao": {"points": 1000},
    }
    root = Tk()
    gamestate = GameState("yangbc", CLIENT.player_info, current_player="yangbc", client=CLIENT)
    gamestate.start_game(display=True, master=root)
