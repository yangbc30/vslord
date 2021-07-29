from vslord_classes import *


#########
# Rules #
#########

# 定义不同游戏的规则

class Rule:
    """
    一个牌类游戏的规则
    有所有牌型
    all_cards =
    有前期准备工作（发牌，地主牌）
    有出牌是否合法的判断函数
    有出牌的效果
    有胜利和失败的条件
    """
    def preparation(self, gamestate):
        """
        发牌，留地主牌
        """
        pass

    def is_valid(self, cards, gamestate):
        """
        cards - instance of Cards : 玩家决策出的想要出的牌
        判断出牌是否合法
        """
        pass

    def effect(self, cards, gamestate):
        """
        cards - instance of Cards : 玩家合法的出牌
        不同的牌型有不同的效果 比如uno换方向
        """
        pass

    def win_or_loss(self, gamestate):
        """
        gamestate : 玩家出牌，改变之后的游戏状态
        判断输赢
        """
        pass

class Vslord_Rule(Rule):
    """
    继承Rule
    斗地主游戏的规则
    """
    all_cards = Cards([])  # ToDo

    def preparation(self, gamestate):
        """
        发牌，留地主牌
        """
        pass  # ToDo

    def is_valid(self, cards, gamestate):
        """
        cards - instance of Cards : 玩家决策出的想要出的牌
        判断出牌是否合法
        """
        pass  # ToDo

    def effect(self, cards, gamestate):
        """
        cards -instance of Cards : 玩家合法的出牌
        不同的牌型有不同的效果 比如uno换方向
        """
        pass  # ToDo

    def win_or_loss(self, gamestate):
        """
        gamestate : 玩家出牌，改变之后的游戏状态
        判断输赢
        """
        pass  # ToDo



class Uno_Rule(Rule):
    pass  # ToDo