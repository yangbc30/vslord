"""实用程序"""

import time

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
