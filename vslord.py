from vslord_classes import *
from vslord_rules import *
from vslord_strategies import *
from vslord_gui import *



########
# Main #
########

# 主程序
def play(gamestate):
    """
    上家出完牌后下一个人开始出牌
    判断出的牌是否合法
    判断是否胜利
    出牌后修改gamestate
    """
    pass  # ToDo



###########
# Example #
###########



# 创建玩家
player0 = Player(Cards(), strategy_0)
player1 = Player(Cards(), strategy_1)
player2 = Player(Cards(), strategy_1)

# 开始游戏
gamestate = GameState([player0, player1, player2], player0, Vslord_Rule)


# 玩家开始操作 要同时执行
player0.action(gamestate)
player1.action(gamestate)
player2.action(gamestate)
"""
# 开始渲染
gui(gamestate)

# 发牌等
gamestate.rule.preparation()

# 打牌
while True:
    play(gamestate)
    
"""
