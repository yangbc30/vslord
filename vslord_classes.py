

###########
# Classes #
###########

# 定义本程序所用到的类(除了Rule)

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



class Cards(Card):
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
    def __init__(self, cards, strategy):
        """
        cards - instance of Cards : 玩家手上握的牌
        strategy - function : 对应玩家的策略
        """
        self.cards = cards
        self.strategy = strategy

    def action(self, gamestate):
        """
        gamestate - instance of GameState : 当前游戏状态
        玩家根据当前游戏状态结合玩家的策略进行决策，返回一个instance of Cards 表示玩家打出的牌
        打出的牌是否合法另行判断
        """
        return self.strategy(gamestate)



class GameState:
    """
    储存游戏当前状态
    通过gamestate玩家可以确定出什么，并且可以按照gamestate渲染ui
    """
    def __init__(self, players, current_palyer, rule):
        """
        players - list : 储存参与游戏的所有玩家，按出牌顺序储存
        rule - instance of Rule : 代表不同的游戏规则
        开始一盘游戏
        """
        time = 0  # 经过的时间 一开始设为0
        self.players = players
        self.current_player = current_palyer
        # self.next_player =
        self.rule = rule()  # 创建rule的一个instance
        self.cards_used = Cards()  # 游戏中所有用过的牌
        self.current_cards = Cards()  # 上家打的牌


        # 后续还要加很多attributes

