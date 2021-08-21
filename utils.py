"""实用程序"""

import time
import random
import vslord
GLOBAL_DEBUG = True


def get_time():
    return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'


def print_by_time(msg):
    """将信息以[时间] + []

    :param msg: 一切有str方法的对象
    """
    print(get_time() + str(msg))


class NetworkError(Exception):
    def __init__(self, arg):
        self.arg = arg


CARDS = tuple([(point, color) for point in range(1, 14) for color in range(4)] + [(14, None), (15, None)])

# print(CARDS)


class CardDealer:
    def __init__(self, cards):
        self.cards = list(cards)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.cards) == 0:
            raise StopIteration
        else:
            card = random.choice(self.cards)
            self.cards.remove(card)
            return card


def test_cards(n=10):
    card_dealer = CardDealer(CARDS)
    cards = []
    for i in range(n):
        cards.append(next(card_dealer))
    return vslord.Cards(cards=tuple(cards))

