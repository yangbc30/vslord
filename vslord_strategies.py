from vslord_classes import *

##############
# strategies #
##############

# 策略，就像星际开房间组队，这个位置是人类玩家还是电脑，联机还是不连机是电脑的话又是什么难度的
# 但是strategy的功能都是通过当前形式做出一个出牌的选择，如果是本机上的人类玩家直接读取键盘
# 如果是联机玩家，对方读取键盘，通过网络发送过来，如果是电脑就要写ai程序

def strategy_0(gamestate):
    """
    本机玩家，从键盘中读取
    """
    pass  # ToDo

def strategy_1(gamestate):
    """
    联机玩家，从网络接口中读取数据
    """
    pass  # ToDo

def vslord_ai(gamestate):
    """
    电脑策略
    """
    pass  # ToDo