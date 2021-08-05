from vslord_strategies import *
from socket import *


###########
# Classes #
###########


class Connection:

    def __init__(self, serverName, serverPort):
        """
        创建tcp链接
        """
        self.playerSocket = socket(AF_INET, SOCK_STREAM)
        self.playerSocket.connect((serverName, serverPort))

    def send_to_server(self, message):
        """
        发送表示action的字符串到服务器
        """
        self.playerSocket.send(message.encode())

    def receive_from_server(self):
        """
        接收服务器字符串
        """
        return self.playerSocket.recv(1024).decode()


class Room:
    """

    """

    def __init__(self, room_name, loacal_player, room_owner, rule):
        self.local_player = loacal_player
        self.room_name = room_name
        self.room_owner = room_owner
        self.players = [room_owner]
        self.rule = rule
        self.prepared = False

    def add_player(self, player_name):
        self.players.append(Player("%s" % (player_name)))  # 根据player的name创建player instance然后加入room

    def get_prepared(self):
        self.prepared = True

    def start_game(self):
        GameState(self.players, self.local_player, self.rule).simulate()
        # for player in self.players:
        #    player.action(gamestate)
        #    player.obey(gamestate)
        #    异步执行


class Card:
    """
    一个牌
    具有有能够唯一确定这张牌的特征
    """

    def __init__(self, attribute):
        """
        attribute - list : 这张牌是什么牌 比如梅花五attribute = 【“♣”， “5”】
        """
        self.attribute = attribute


class Cards:
    """
    一些牌，可以是一个玩家手上握的牌，也可以是一个玩家当前打出的牌，也可以是所有被打出的牌
    可以一开始就具有一些牌，也可以后来加入一个或者一些牌
    """

    def __init__(self, cards=[]):
        """
        cards - list : 初始有几张牌, cards中每个元素都是card的一个instance
        """
        self.cards = cards

    def add_cards(self, cards):
        """
        cards - instance of Cards : 添加一些牌
        """
        self.cards = self.cards + cards.cards

    def add_card(self, card):
        """
        card - instance of Card : 添加一个牌
        """
        self.cards = self.cards.append(card)

    def get_random_card(self):
        """
        牌堆中随机给出一个牌，发牌时用
        """
        pass  # ToDo


class Player:
    """
    表示一个玩家
    具有该玩家的strategy，该玩家的手上握的牌
    玩家可以出牌
    """

    def __init__(self, name, strategy=interactive_strategy, connection=None):
        """
        cards - instance of Cards : 玩家手上握的牌
        strategy - function : 对应玩家的策略
        """
        self.connection = connection
        self.cards = None
        self.name = name
        self.connection = None
        self.strategy = strategy

    def login(self):
        password = input("your password :")
        self.connection.send_to_server("password: %s" % password)
        # ToDo 完善验证密码协议

    def action(self, gamestate):
        """
        gamestate - instance of GameState : 当前游戏状态
        玩家根据当前游戏状态结合玩家的策略进行决策，返回一个instance of Action表示玩家想要做出一个操作
        """
        while True:
            action = eval(self.strategy(gamestate))
            if action.is_valid() == True:
                action.effect()  # 这个操作对gamestate的影响
                action.display()  # 这个操作显示在屏幕上

    def obey(self, gamestate, action_str):
        """
        服从服务器的指令
        """
        action = eval(action_str)
        action.effect()
        action.display()


class GameState:
    """
    储存游戏当前状态
    通过gamestate玩家可以确定出什么，并且可以按照gamestate渲染ui
    """

    def __init__(self, players, local_player, rule):
        """
        players - list : 储存参与游戏的所有玩家，按出牌顺序储存
        rule - instance of Rule : 代表不同的游戏规则
        开始一盘游戏
        """
        time = 0  # 经过的时间 一开始设为0
        self.players = players
        self.local_player = local_player
        # self.next_player =
        self.cards_used = Cards()  # 游戏中所有用过的牌
        self.current_cards = Cards()  # 上家打的牌

    def simulate(self):
        """
        开始游戏
        """
        while True:
            action_to_obey = self.local_player.connection.receive_from_server()
            # player.obey(action_to_obey)
        # self.local_player.action()
        # ToDo 异步




