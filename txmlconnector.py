# -*- coding: utf-8 -*-
"""
Модуль с основными командами Транзак Коннектора.

@author: Roma
"""
import ctypes, logging
import lxml.etree as et
from txmlstructures import *
log = logging.getLogger("transaq.connector")


def callback(msg):
    """
    Функция, вызываемая коннектором при входящих сообщениях.
    :param msg: входящее сообщение Транзака
    :return: True если все обработал
    """
    obj = parse(msg)
    if isinstance(obj, Error):
        log.error(u"Чета не то ваще: %s" % obj.text)
        raise TransaqException(obj.text)
    elif isinstance(obj, ServerStatus):
        log.info(u"Соединен с серваком: %s" % obj.connected)
        if obj.connected == 'error':
            log.warn(u"Ёпта, ошибка соединения: %s" % obj.text)
        log.debug(obj)
    elif isinstance(obj, ClientAccount):
        log.info(u"Подключил аккаунт: %s", obj.id)
        if not obj.active:
            log.warn(u"Гады, аккаунт удаляют!")
        log.debug(obj)
    elif isinstance(obj, BoardPacket):
        log.info(u"Получил список борд(режимов)")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, MarketPacket):
        log.info(u"Получил список рынков")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, CandleKindPacket):
        log.info(u"Получил список интервалов свечек")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, SecurityPacket):
        log.info(u"Получил список инструментиков")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, SecurityPitPacket):
        log.info(u"Получил список инструментиков")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, CreditAbility):
        log.info(u"Получил статус кредитов")
        log.debug(obj)
    elif isinstance(obj, PositionPacket):
        log.info(u"Получил список позиций")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, ClientPortfolio):
        log.info(u"Получил свой портфель Т+")
        if len(obj.items): log.debug(obj)
    elif isinstance(obj, ClientOrderPacket):
        log.info(u"Получил список текущих заявочек")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, ClientTradePacket):
        log.info(u"Получил список своих совершенных сделок")
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, HistoryCandlePacket):
        log.info(u"Получил исторические свечки по инструменту %s" % obj.seccode)
        if len(obj.items): log.debug(obj.items[0])
    elif isinstance(obj, ClientLimitsForts):
        log.info(u"Получил лимиты ФОРТС")
        log.debug(obj)
    elif isinstance(obj, ClientLimitsTPlus):
        log.info(u"Получил лимиты Т+")
        log.debug(obj)
    else:
        log.warn(u"Получил какую-то мутную тему (типа %s)" % str(type(obj)))
    if global_handler:
        global_handler(obj)
    return True


callback_func = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_char_p)
callback_func = callback_func(callback)
global_handler = None
txml_dll = ctypes.WinDLL("txmlconnector64.dll")
connected = False


class TransaqException(Exception):
    pass


def __get_message(ptr):
    msg = ctypes.string_at(ptr)
    txml_dll.FreeMemory(ptr)
    return msg


def __elem(tag, text):
    elem = et.Element(tag)
    elem.text = text
    return elem


def __send_command(cmd):
    msg = __get_message(txml_dll.SendCommand(cmd))
    err = Error.parse(msg)
    if err.text:
        raise TransaqException(err.text)
    else:
        return CmdResult.parse(msg)


def initialize(logdir, loglevel, msg_handler):
    global global_handler
    global_handler = msg_handler
    err = txml_dll.Initialize(logdir + "\0", loglevel)
    if err != 0:
        msg = __get_message(err)
        raise TransaqException(Error.parse(msg))
    if not txml_dll.SetCallback(callback_func):
        raise TransaqException("Callback was not installed")


def uninitialize():
    if connected:
        disconnect()
    err = txml_dll.UnInitialize()
    if err != 0:
        msg = __get_message(err)
        raise TransaqException(Error.parse(msg))


def connect(login, password, server, min_delay=100):
    host, port = server.split(':')
    root = et.Element("command", {"id": "connect"})
    root.append(__elem("login", login))
    root.append(__elem("password", password))
    root.append(__elem("host", host))
    root.append(__elem("port", port))
    # root.append(__elem("loglevel", str(loglevel)))
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
    root = et.Element("command", {"id": "get_markets"})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_history(board, seccode, period, count, reset=True):
    root = et.Element("command", {"id": "gethistorydata"})
    sec = et.Element("security")
    sec.append(__elem("board", board))
    sec.append(__elem("seccode", seccode))
    root.append(sec)
    root.append(__elem("period", str(period)))
    root.append(__elem("count", str(count)))
    root.append(__elem("reset", "true" if reset else "false"))
    return __send_command(et.tostring(root, encoding="utf-8"))


def new_condorder(board, ticker, client, buysell, quantity, price,
                  cond_type, cond_val, valid_after, valid_before,
                  bymarket=True, usecredit=True):
    root = et.Element("command", {"id": "newcondorder"})
    return NotImplemented


# Forts only
def get_forts_position(client):
    root = et.Element("command", {"id": "get_forts_position", "client": client})
    return __send_command(et.tostring(root, encoding="utf-8"))


# Forts only
def get_limits_forts(client):
    root = et.Element("command", {"id": "get_client_limits", "client": client})
    return __send_command(et.tostring(root, encoding="utf-8"))


def get_servtime_diff():
    return NotImplemented


def change_pass(oldpass, newpass):
    return NotImplemented


def get_version():
    # Needs new struct connector_version
    return NotImplemented


def get_sec_info(market, seccode):
    return NotImplemented


# Fort only? Not sure
def move_order(id, price, quantity=0, moveflag=0):
    root = et.Element("command", {"id": "moveorder"})
    root.append(__elem("transactionid", str(id)))
    root.append(__elem("price", str(price)))
    root.append(__elem("quantity", str(quantity)))
    root.append(__elem("moveflag", str(moveflag)))
    return __send_command(et.tostring(root, encoding="utf-8"))


# What diff with get_client_limits?
def get_limits_tplus(client, securities):
    root = et.Element("command", {"id": "get_max_buy_sell_tplus", "client": client})
    for (market, code) in securities:
        sec = et.Element("security")
        sec.append(__elem("market", str(market)))
        sec.append(__elem("seccode", code))
        root.append(sec)
    return __send_command(et.tostring(root, encoding="utf-8"))


# Not used
def get_portfolio_mct(client):
    return NotImplemented
