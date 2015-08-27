# -*- coding: utf-8 -*-
"""
Пример использования коннектора.
"""
from commands import *
import time


def handle_txml_message(msg):
    print msg


if __name__ == '__main__':
    try:
        initialize("Logs", 3, handle_txml_message)
        print connect("ЛОГИН", "ПАРОЛЬ", "78.41.194.46:3950")
        time.sleep(3)
        print get_history('TQBR', 'GAZP', 2, count=10)
        time.sleep(3)
    finally:
        print disconnect()
        uninitialize()
