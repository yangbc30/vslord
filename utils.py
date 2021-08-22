"""实用程序"""

import time
import random
GLOBAL_DEBUG = True


def get_time():
    return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'


def print_by_time(msg):
    """将信息以[时间] + []

    :param msg: 一切有str方法的对象
    """
    print(get_time() + str(msg))


def timing(func):
    def wrapper(*args, **kwargs):
        t_begin = time.time()
        ret = func(*args, **kwargs)
        t_end = time.time()
        print(func.__name__ + " consume " + str(t_end - t_begin))
        return ret
    return wrapper


class NetworkError(Exception):
    def __init__(self, arg):
        self.arg = arg


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


def test_cards(card_set, n=10):
    card_dealer = CardDealer(card_set)
    cards = []
    for i in range(n):
        cards.append(next(card_dealer))
    return tuple(cards)

