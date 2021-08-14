"""实用程序"""

import time

GLOBAL_DEBUG = True


def get_time():
    return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'


def print_by_time(msg):
    print(get_time() + str(msg))


class NetworkError(Exception):
    def __init__(self, arg):
        self.arg = arg
