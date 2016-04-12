# -*- coding: utf-8 -*-
"""
Модуль с основными командами Транзак Коннектора
(см. http://www.finam.ru/howtotrade/tconnector/).

.. note::
    Практически все команды асинхронны!
    Это означает что они возвращают структуру CmdResult, которая говорит лишь
    об успешности отправки команды на сервер, но не её исполнения там.
    Результат исполнения приходит позже в зарегистрированный командой *initialize()* хэндлер.
    Синхронные вспомогательные команды помечены отдельно.
"""
import ctypes, logging
import platform, os, sys
import lxml.etree as et
from structures import *
log = logging.getLogger("transaq.connector")

callback_func = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_char_p)
global_handler = None
path = ""
if __file__ is not None:
    path = os.path.dirname(__file__)
    if path != "":
        path += os.sep

txml_dll = ctypes.WinDLL(path + ("txmlconnector64.dll" if platform.machine() == 'AMD64' else 'txmlconnector.dll') )
connected = False
encoding = sys.stdout.encoding


@callback_func
def callback(msg):
    """
    Функция, вызываемая коннектором при входящих сообщениях.

    :param msg:
        Входящее сообщение Транзака.
    :return:
        True если все обработал.
    """
    obj = parse(msg.decode('utf8'))
    if isinstance(obj, Error):
        log.error(u"Траблы: %s" % obj.text)
        raise TransaqException(obj.text.encode(encoding))
    elif isinstance(obj, ServerStatus):
        log.info(u"Соединен с серваком: %s" % obj.connected)
        if obj.connected == 'error':
            log.warn(u"Ёпта, ошибка соединения: %s" % obj.text)
        log.debug(obj)
    else:
        log.info(u"Получил объект типа %s" % str(type(obj)))
        log.debug(obj)
    if global_handler:
        global_handler(obj)
    return True


class TransaqException(Exception):
    """
    Класс исключений, связанных с коннектором.
    """
    pass


def __get_message(ptr):
    # Достать сообщение из нативной памяти.
    msg = ctypes.string_at(ptr)
    txml_dll.FreeMemory(ptr)
    return unicode(msg, 'utf8')


def __elem(tag, text):
    # Создать элемент с заданным текстом.
    elem = et.Element(tag)
    elem.text = text
    return elem


def __send_command(cmd):
    # Отправить команду и проверить на ошибки.
    msg = __get_message(txml_dll.SendCommand(cmd))
    err = Error.parse(msg)
    if err.text:
        raise TransaqException(err.text.encode(encoding))
    else:
        return CmdResult.parse(msg)


def initialize(logdir, loglevel, msg_handler):
    """
    Инициализация коннектора (синхронная).

    :param logdir:
    :param loglevel:
    :param msg_handler:
    """
    global global_handler
    global_handler = msg_handler
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    err = txml_dll.Initialize(logdir + "\0", loglevel)
    if err != 0:
        msg = __get_message(err)
        raise TransaqException(Error.parse(msg).text.encode(encoding))
    if not txml_dll.SetCallback(callback):
        raise TransaqException(u"Коллбэк не установился")


def uninitialize():
    """
    Де-инициализация коннектора (синхронная).

    :return:
    """
    if connected:
        disconnect()
    err = txml_dll.UnInitialize()
    if err != 0:
        msg = __get_message(err)
        raise TransaqException(Error.parse(msg).text.encode(encoding))


def connect(login, password, server, min_delay=100):
    host, port = server.split(':')
    root = et.Element("command", {"id": "connect"})
    root.append(__elem("login", login))
    root.append(__elem("password", password))
    root.append(__elem("host", host))
    root.append(__elem("port", port))
    root.append(__elem("rqdelay", str(min_delay)))
    return __send_command(et.tostring(root, encoding="utf-8"))


def disconnect():
    global connected
    root = et.Element("command", {"id": "disconnect"})
    return __send_command(et.tostring(root, encoding="utf-8"))
    # connected = False


def server_status():
    root = et.Element("command", {"id": "server_status"})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_instruments():
    root = et.Element("command", {"id": "get_securities"})
    return __send_command(et.tostring(root, encoding="utf-8"))


def __subscribe_helper(board, tickers, cmd, mode):
    root = et.Element("command", {"id": cmd})
    trades = et.Element(mode)
    for t in tickers:
        sec = et.Element("security")
        sec.append(__elem("board", board))
        sec.append(__elem("seccode", t))
        trades.append(sec)
    root.append(trades)
    return __send_command(et.tostring(root, encoding="utf-8"))


def subscribe_ticks(board, tickers):
    return __subscribe_helper(board, tickers, "subscribe", "alltrades")


def unsubscribe_ticks(board, tickers):
    return __subscribe_helper(board, tickers, "unsubscribe", "alltrades")


def subscribe_quotations(board, tickers):
    return __subscribe_helper(board, tickers, "subscribe", "quotations")


def unsubscribe_quotations(board, tickers):
    return __subscribe_helper(board, tickers, "unsubscribe", "quotations")


def subscribe_bidasks(board, tickers):
    return __subscribe_helper(board, tickers, "subscribe", "quotes")


def unsubscribe_bidasks(board, tickers):
    return __subscribe_helper(board, tickers, "unsubscribe", "quotes")


def new_order(board, ticker, client, buysell, quantity, price=0,
              bymarket=True, usecredit=True):
    # Add hidden, unfilled, nosplit
    root = et.Element("command", {"id": "neworder"})
    sec = et.Element("security")
    sec.append(__elem("board", board))
    sec.append(__elem("seccode", ticker))
    root.append(sec)
    root.append(__elem("client", client))
    root.append(__elem("buysell", buysell.upper()))
    root.append(__elem("quantity", str(quantity)))
    if not bymarket:
        root.append(__elem("price", str(price)))
    else:
        root.append(et.Element("bymarket"))
    if usecredit:
        root.append(et.Element("usecredit"))
    return __send_command(et.tostring(root, encoding="utf-8"))


def new_stoploss(board, ticker, client, buysell, quantity, trigger_price, price=0,
                 bymarket=True, usecredit=True, linked_order=None, valid_for=None):
    root = et.Element("command", {"id": "newstoporder"})
    sec = et.Element("security")
    sec.append(__elem("board", board))
    sec.append(__elem("seccode", ticker))
    root.append(sec)
    root.append(__elem("client", client))
    root.append(__elem("buysell", buysell.upper()))
    if linked_order:
        root.append(__elem("linkedorderno", str(linked_order)))
    if valid_for:
        root.append(__elem("validfor", valid_for.strftime(timeformat)))

    sl = et.Element("stoploss")
    sl.append(__elem("quantity", str(quantity)))
    sl.append(__elem("activationprice", str(trigger_price)))
    if not bymarket:
        sl.append(__elem("orderprice", str(price)))
    else:
        sl.append(et.Element("bymarket"))
    if usecredit:
        sl.append(et.Element("usecredit"))

    root.append(sl)
    return __send_command(et.tostring(root, encoding="utf-8"))


def new_takeprofit(board, ticker, client, buysell, quantity, trigger_price,
                   correction=0, use_credit=True, linked_order=None, valid_for=None):
    root = et.Element("command", {"id": "newstoporder"})
    sec = et.Element("security")
    sec.append(__elem("board", board))
    sec.append(__elem("seccode", ticker))
    root.append(sec)
    root.append(__elem("client", client))
    root.append(__elem("buysell", buysell.upper()))
    if linked_order:
        root.append(__elem("linkedorderno", str(linked_order)))
    if valid_for:
        root.append(__elem("validfor", valid_for.strftime(timeformat)))

    tp = et.Element("takeprofit")
    tp.append(__elem("quantity", str(quantity)))
    tp.append(__elem("activationprice", str(trigger_price)))
    tp.append(et.Element("bymarket"))
    if use_credit:
        tp.append(et.Element("usecredit"))
    if correction:
        tp.append(__elem("correction", str(correction)))
    root.append(tp)
    return __send_command(et.tostring(root, encoding="utf-8"))


def cancel_order(id):
    root = et.Element("command", {"id": "cancelorder"})
    root.append(__elem("transactionid", str(id)))
    return __send_command(et.tostring(root, encoding="utf-8"))


def cancel_stoploss(id):
    root = et.Element("command", {"id": "cancelstoporder"})
    root.append(__elem("transactionid", str(id)))
    return __send_command(et.tostring(root, encoding="utf-8"))


def cancel_takeprofit(id):
    cancel_stoploss(id)


def get_portfolio(client):
    root = et.Element("command", {"id": "get_portfolio", "client": client})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_markets():
    """
    Получить список рынков.

    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "get_markets"})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_history(board, seccode, period, count, reset=True):
    """
    Выдать последние N свечей заданного периода, по заданному инструменту.

    :param board:
        Идентификатор режима торгов.
    :param seccode:
        Код инструмента.
    :param period:
        Идентификатор периода.
    :param count:
        Количество свечей.
    :param reset:
        Параметр reset="true" говорит, что нужно выдавать самые свежие данные, в
        противном случае будут выданы свечи в продолжение предыдущего запроса.
    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "gethistorydata"})
    sec = et.Element("security")
    sec.append(__elem("board", board))
    sec.append(__elem("seccode", seccode))
    root.append(sec)
    root.append(__elem("period", str(period)))
    root.append(__elem("count", str(count)))
    root.append(__elem("reset", "true" if reset else "false"))
    return __send_command(et.tostring(root, encoding="utf-8"))


# TODO Доделать условные заявки
def new_condorder(board, ticker, client, buysell, quantity, price,
                  cond_type, cond_val, valid_after, valid_before,
                  bymarket=True, usecredit=True):
    """
    Новая условная заявка.

    :param board:
    :param ticker:
    :param client:
    :param buysell:
    :param quantity:
    :param price:
    :param cond_type:
    :param cond_val:
    :param valid_after:
    :param valid_before:
    :param bymarket:
    :param usecredit:
    :return:
    """
    root = et.Element("command", {"id": "newcondorder"})
    return NotImplemented


def get_forts_position(client):
    """
    Запрос позиций клиента по FORTS.

    :param client:
        Идентификатор клиента.
    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "get_forts_position", "client": client})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_limits_forts(client):
    """
    Запрос лимитов клиента ФОРТС.

    :param client:
        Идентификатор клиента.
    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "get_client_limits", "client": client})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_servtime_diff():
    """
    Получить разницу между серверным временем и временем на компьютере пользователя (синхронная).

    :return:
        Результат команды с разницей времени.
    """
    return NotImplemented


def change_pass(oldpass, newpass):
    """
    Смена пароля (синхронная).

    :param oldpass:
        Старый пароль.
    :param newpass:
        Новый пароль.
    :return:
        Результат команды.
    """
    root = et.Element("command", {"id": "change_pass", "oldpass": oldpass, "newpass": newpass})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_version():
    """
    Получить версию коннектора (синхронная).

    :return:
        Версия коннектора.
    """
    root = et.Element("command", {"id": "get_connector_version"})
    return ConnectorVersion.parse(__get_message(txml_dll.SendCommand(et.tostring(root, encoding="utf-8")))).version


def get_sec_info(market, seccode):
    """
    Запрос на получение информации по инструменту.

    :param market:
        Внутренний код рынка.
    :param seccode:
        Код инструмента.
    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "get_securities_info"})
    sec = et.Element("security")
    sec.append(__elem("market", str(market)))
    sec.append(__elem("seccode", seccode))
    root.append(sec)
    return __send_command(et.tostring(root, encoding="utf-8"))


def move_order(id, price, quantity=0, moveflag=0):
    """
    Отредактировать заявку.

    :param id:
        Идентификатор заменяемой заявки FORTS.
    :param price:
        Цена.
    :param quantity:
        Количество, лотов.
    :param moveflag:
        0: не менять количество;
        1: изменить количество;
        2: при несовпадении количества с текущим – снять заявку.
    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "moveorder"})
    root.append(__elem("transactionid", str(id)))
    root.append(__elem("price", str(price)))
    root.append(__elem("quantity", str(quantity)))
    root.append(__elem("moveflag", str(moveflag)))
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_limits_tplus(client, securities):
    """
    Получить лимиты Т+.

    :param client:
        Идентификатор клиента.
    :param securities:
        Список пар (market, seccode) на которые нужны лимиты.
    :return:
        Результат отправки команды.
    """
    root = et.Element("command", {"id": "get_max_buy_sell_tplus", "client": client})
    for (market, code) in securities:
        sec = et.Element("security")
        sec.append(__elem("market", str(market)))
        sec.append(__elem("seccode", code))
        root.append(sec)
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_portfolio_mct(client):
    """
    Получить портфель МСТ/ММА. Не реализован пока.

    :param client:
        Идентификатор клиента.
    :return:
        Результат отправки команды.
    """
    return NotImplemented

def get_united_portfolio(client, union=None):
    """
    Получить единый портфель.
    В команде необходимо задать только один из параметров (client или union).

    :param client:
        Идентификатор клиента.
    :param union:
        Идентификатор юниона.
    :return:
        Результат отправки команды.
    """
    params = {"id": "get_united_portfolio"}
    if client is not None:
        params["client"] = client
    elif union is not None:
        params["union"] = union
    else:
        raise ValueError("please specify client OR union")
    root = et.Element("command", params)
    return __send_command(et.tostring(root, encoding="utf-8"))