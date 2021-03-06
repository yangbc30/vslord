###########
# Actions #
###########

# 牌类游戏都是由每个玩家的action构成的，action包括一开始的拿牌，顺牌，选牌，出牌等等，甚至开房间，开始游戏都可以说是action
# 只要游戏一开始，所有玩家都可以提出action的请求，而不是只局限于一个玩家可以出牌的时间。比如三个人ABC斗地主，该A出牌，但是B可以选他下一轮要出的牌，尽管这不是他的出牌时间
# 玩家在开始游戏之后都可以提出action的请求，有的请求合法，有的请求不合法，比如A出牌的时候，B提出了出牌这个action的请求，这个显然是不合法的（根据action.is_valid(gamestate)判断
# 合法的action显然会产生一些影响，比如选牌会改变player的数据，ui也会相应渲染选牌的效果，出牌会改变gamestate中记录的上家出牌数据，ui渲染
# 既然action改变了gamestate，就要对每个玩家的gamestate进行同步，同步的方法就是向需要同步的玩家发送自己的action让对方重演gamestate中发生的变化
# 也有的action比较特殊，比如选牌就不用同步，因为这是要对对手保密的信息

class Action:

    def __init__(self, gamestate, action_name, **kwargs):
        self.gamestate = gamestate
        self.name = action_name
        self.parameters = kwargs
        self.parse_action()

    def parse_action(self):
        if self.name == "pass_round":
            assert len(self.parameters) == 0
            self.is_valid_pass_round()

    def is_valid_pass_round(self):
        if self.gamestate.current_player == self.gamestate.me:
            return True

    def request(self):
        msg = list(self.name, )
        self.gamestate.send()

    def is_valid(self):
        """
        返回这个action在这个gamestate下由这个player给出合不合法
        True or False
        """
        pass

    def effect(self):
        """
        这个action对gamestate的修改

        """
        pass

    def display(self):
        """
        将这个action渲染出来
        """
        pass

    def sync(self):
        """
        将这个action与其他玩家同步
        """
        pass

