# -*- coding: utf-8 -*-
"""
Пример использования коннектора.
Смена пароля при первом подключении.
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
        print change_pass("ПАРОЛЬ","НОВЫЙ_ПАРОЛЬ")
        time.sleep(3)
    finally:
        print disconnect()
        uninitialize()
