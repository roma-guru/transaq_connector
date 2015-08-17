# -*- coding: utf-8 -*-
"""
Модуль со структурными классами Transaq XML Коннектора.
Всем основным xml структурам сопоставлены питоновые объекты.

@author: Roma
"""
from eulxml.xmlmap import *
from eulxml.xmlmap.fields import Field, DateTimeMapper
import sys, inspect, logging

log = logging.getLogger('transaq.structures')
# Формат дат/времени используемый Транзаком
timeformat = "%d.%m.%Y %H:%M:%S"
# Кодировка для вывода, cp866 - виндовая консоль, utf8 - нормальная консоль
encoding = 'utf8'
# Список классов, ленивая инициализация при парсинге
_my_classes = []


def parse(xml):
    """
    Общая функция парсинга xml-структур.

    Параметры:
        xml - any supported xml
    Возврат:
        obj - mapped python object
    """
    global _my_classes
    # Корневой тег достанем
    root = parseString(xml).tag
    # Пройдемся по всем классам модуля и найдем подходящий
    if not len(_my_classes):
        _my_classes = filter(lambda o: inspect.isclass(o) and issubclass(o, MyXmlObject),
                             sys.modules[__name__].__dict__.values())
    for cls in _my_classes:
        if root == cls.ROOT_NAME:
            return cls.parse(xml)
    # Лабуда какая-то пришла
    log.error(u"Неподдерживаемый xml, не распарсился нихрена! Типа %s" % xml[:10])
    log.debug(xml)
    return None


# Вспомогательные классы
class NullableDateTimeMapper(DateTimeMapper):
    """
    Оберточный класс вокруг DateTimeMapper,
        возвращающий None для заданных значений, а не вываливающий исключение при обработке даты.
    """
    nones = ['0']

    def to_python(self, node):
        if node is None:
            return None
        if isinstance(node, basestring):
            rep = node
        else:
            rep = self.XPATH(node)
        if rep in self.nones:
            return None
        else:
            return super(NullableDateTimeMapper, self).to_python(node)


class MyXmlObject(XmlObject):
    """
    Расширение eulxml.XmlObject с методом само-парсинга и наглядным представлением.
    """

    @classmethod
    def parse(cls, xml):
        return load_xmlobject_from_string(xml, cls)

    def __repr__(self):
        cls = self.__class__
        fields = []
        for (name, val) in filter(lambda (name, val): isinstance(val, Field), inspect.getmembers(cls)):
            val = self.__getattribute__(name)
            if isinstance(val, unicode):
                val = val.encode(encoding)
            if val:
                fields.append("%s=%s" % (name, str(val)))
        return "%s(%s)" % (cls.__name__, ', '.join(fields))


class Entity(MyXmlObject):
    """
    Абстрактный класс сущностей, имеет идентификатор.
    """
    # Entity id, unique in the same class
    id = IntegerField('@id')

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id


class Packet(MyXmlObject):
    """
    Абстрактный пакет сущностей присланный серваком.
    """
    items = []


class Error(MyXmlObject):
    """
    Ошибка.
    """
    ROOT_NAME = 'error'
    text = StringField('text()')


class CmdResult(MyXmlObject):
    """
    Результат отправки команды (но не исполнения на серваке).
    """
    ROOT_NAME = 'result'
    success = SimpleBooleanField('@success', 'true', 'false')
    text = StringField('message')
    id = IntegerField('@transactionid')


# Классы xml структур Транзака
class HistoryCandle(Entity):
    """
    Свечки OHLCV (open,high,low,close).
    """
    ROOT_NAME = 'candle'
    date = DateTimeField('@date', timeformat)
    id = hash(date)
    open = FloatField('@open')
    high = FloatField('@high')
    low = FloatField('@low')
    close = FloatField('@close')
    volume = IntegerField('@volume')
    # только ФОРТС
    open_interest = IntegerField('@oi')


class HistoryCandlePacket(Packet):
    """
    Пакет свечек |||.
    """
    ROOT_NAME = 'candles'
    secid = IntegerField('@secid')
    board = StringField('@board')
    seccode = StringField('@seccode')
    status = IntegerField('@status')
    period = IntegerField('@period')
    items = NodeListField('candle', HistoryCandle)


class ServerStatus(Entity):
    """
    Состояние соединения.
    """
    ROOT_NAME = 'server_status'
    connected = StringField('@connected', choices=['true', 'false', 'error'])
    timezone = StringField('@server_tz')
    # Атрибут recover – необязательный параметр. Его наличие означает, что
    # коннектор пытается восстановить потерянное соединение с сервером
    recover = SimpleBooleanField('@recover', 'true', None)
    text = StringField('text()')

    def __repr__(self):
        if self.connected != 'error':
            return "ServerStatus(id=%d,tz=%s,conn=%s)" % \
                   (self.id, self.timezone, self.connected)
        else:
            return "ServerStatus(ERROR, text=%s)" % self.text.encode(encoding)


class ClientAccount(Entity):
    """
    Данные клиентсткого аккаунта.
    """
    ROOT_NAME = 'client'
    id = StringField('@id')
    active = SimpleBooleanField('@remove', 'false', 'true')
    # Возможные типы клиента: spot (кассовый), leverage (плечевой), margin_level (маржинальный)
    type = StringField('type', choices=['spot', 'leverage', 'margin_level'])
    # Валюта  фондового  портфеля
    currency = StringField('currency', choices=['NA', 'RUB', 'EUR', 'USD'])
    # Поля ml_overnight и ml_intraday присылаются только для плечевых клиентов.
    # Выражаются в виде десятичной дроби и показывают величину плеча.
    ml_intraday = FloatField('ml_intraday')
    ml_overnight = FloatField('ml_overnight')
    # Поля ml_restrict, ml_call и ml_close присылаются только для маржинальных клиентов
    ml_restrict = FloatField('ml_restrict')
    ml_call = FloatField('ml_call')
    ml_close = FloatField('ml_close')


class Market(Entity):
    """
    Названия рынков: ММВБ, ФОРТС...
    """
    ROOT_NAME = 'market'
    name = StringField('text()')


class MarketPacket(Packet):
    """
    Пакет с доступными рынками.
    """
    ROOT_NAME = 'markets'
    items = NodeListField('market', Market)


class CandleKind(Entity):
    """
    Периоды свечек.
    """
    ROOT_NAME = 'kind'
    id = IntegerField('id')
    name = StringField('name')
    period = IntegerField('period')


class CandleKindPacket(Packet):
    """
    Пакет с доступными периодами.
    """
    ROOT_NAME = 'candlekinds'
    items = NodeListField('kind', CandleKind)


class Security(Entity):
    """
    Ценная бумага.
    """
    ROOT_NAME = 'security'
    id = secid = IntegerField('@secid')
    active = SimpleBooleanField('@active', 'true', 'false')
    seccode = StringField('seccode')
    sectype = StringField('sectype')
    board = StringField('board')
    market = IntegerField('market')
    name = StringField('shortname')
    decimals = IntegerField('decimals')
    minstep = FloatField('minstep')
    lotsize = IntegerField('lotsize')
    point_cost = FloatField('point_cost')
    timezone = StringField('sec_tz')
    # Bool flags
    credit_allowed = SimpleBooleanField('opmask/@usecredit', 'yes', 'no')
    bymarket_allowed = SimpleBooleanField('opmask/@bymarket', 'yes', 'no')
    nosplit_allowed = SimpleBooleanField('opmask/@nosplit', 'yes', 'no')
    immediate_allowed = SimpleBooleanField('opmask/@immorcancel', 'yes', 'no')
    cancelbalance_allowed = SimpleBooleanField('opmask/@cancelbalance', 'yes', 'no')
    # Doc says secid is not reliable
    def __eq__(self, other):
        return (type(self) == type(other)
                and self.market == other.market and self.seccode == other.seccode)


class SecurityPacket(Packet):
    ROOT_NAME = 'securities'
    items = NodeListField('security', Security)


## Info updates, to be done
class SecInfo(Entity):
    pass


class SecInfoUpdate(Entity):
    pass


## Quotation stats subscription
class Quotation(Entity):
    ROOT_NAME = 'quotation'
    id = secid = IntegerField('@secid')
    board = StringField('board')
    seccode = StringField('seccode')
    point_cost = FloatField('point_cost')
    # Coupon dividend
    accrued = FloatField('accruedintvalue')
    open = FloatField('open')
    waprice = FloatField('waprice')
    bid_depth = IntegerField('biddepth')
    demand = IntegerField('biddeptht')
    numbids = IntegerField('numbids')
    offer_depth = IntegerField('offerdepth')
    suply = IntegerField('offerdeptht')
    numoffers = IntegerField('numoffers')
    best_bid = FloatField('bid')
    best_offer = FloatField('offer')
    numtrades = IntegerField('numtrades')
    volume_today = IntegerField('voltoday')
    # Forts only
    open_positions = IntegerField('openpositions')
    delta_positions = IntegerField('deltapositions')
    last_price = FloatField('last')
    last_time = DateTimeField('time', timeformat)
    last_quantity = IntegerField('quantity')
    # Price delta to prev. day
    change = FloatField('change')
    # Price delta to weighted avg of prev. day
    change_wa = FloatField('priceminusprevwaprice')
    # Total turnover
    value_today = FloatField('valtoday')
    yld = FloatField('yield')
    yld_wa = FloatField('yieldatwaprice')
    market_price_today = FloatField('marketpricetoday')
    highest_bid = FloatField('highbid')
    lowest_offer = FloatField('lowoffer')
    high = FloatField('high')
    low = FloatField('low')
    close = FloatField('closeprice')
    close_yld = FloatField('closeyield')
    status = StringField('status')
    trade_status = StringField('tradingstatus')
    buy_deposit = FloatField('buydeposit')
    sell_deposit = FloatField('selldeposit')
    volatility = FloatField('volatility')
    # Wtf is this?
    theory_price = FloatField('theoreticalprice')


class QuotationPacket(Packet):
    ROOT_NAME = 'quotations'
    items = NodeListField('quotation', Quotation)


## All trades subsription
class Trade(Entity):
    ROOT_NAME = 'trade'
    secid = IntegerField('@secid')
    board = StringField('board')
    seccode = StringField('seccode')
    id = trade_no = IntegerField('tradeno')
    time = DateTimeField('time', timeformat)
    price = FloatField('price')
    quantity = IntegerField('quantity')
    buysell = StringField('buysell', choices=['B', 'S'])
    open_interest = IntegerField('openinterest')
    trade_period = StringField('period', choices=['O', 'N', 'C', 'F', 'B', 'T', 'L'])


class TradePacket(Packet):
    ROOT_NAME = 'alltrades'
    items = NodeListField('trade', Trade)


## All orders subscription
class Quote(Entity):
    ROOT_NAME = 'quote'
    id = secid = IntegerField('@secid')
    board = StringField('board')
    seccode = StringField('seccode')
    price = FloatField('price')
    source = StringField('source')
    yld = IntegerField('yield')
    buy = IntegerField('buy')
    sell = IntegerField('sell')


class QuotePacket(Packet):
    ROOT_NAME = 'quotes'
    items = NodeListField('quote', Quote)


## Main part: Orders
class BaseOrder(Entity):
    id = IntegerField('@transactionid')
    order_no = IntegerField('orderno')
    secid = IntegerField('secid')
    board = StringField('board')
    seccode = StringField('seccode')
    price = FloatField('price')
    time = DateTimeField('time', timeformat)
    client = StringField('client')
    status = StringField('status')
    buysell = StringField('buysell', choices=['B', 'S'])
    exp_date = DateTimeField('expdate', timeformat)
    broker_ref = StringField('brokerref')
    accept_time = DateTimeField('accepttime', timeformat)
    valid_before = DateTimeField('validbefore', timeformat)
    quantity = IntegerField('quantity')
    withdraw_time = DateTimeField('withdrawtime', timeformat)
    withdraw_time.mapper = NullableDateTimeMapper(timeformat)
    result = StringField('result')


class Order(BaseOrder):
    ROOT_NAME = 'order'
    origin_order_no = IntegerField('origin_orderno')
    # Order cost
    value = FloatField('value')
    accrued_int = FloatField('accruedint')
    settle_code = StringField('settlecode')
    balance = IntegerField('balance')
    hidden = IntegerField('hidden')
    yld = IntegerField('yield')
    condition = StringField('condition')
    condition_value = FloatField('conditionvalue')
    valid_after = DateTimeField('valid_after', timeformat)
    max_commission = FloatField('maxcomission')


class StopOrder(BaseOrder):
    ROOT_NAME = 'stoporder'
    order_no = IntegerField('activeorderno')
    canceller = StringField('canceller')
    alltrade_no = IntegerField('alltradeno')
    author = StringField('author')
    linked_order_no = IntegerField('linkedorderno')
    # stops are delayed
    time = None


class StopLoss(StopOrder):
    use_credit = SimpleBooleanField('stoploss/@usecredit', 'yes', 'no')
    activation_price = FloatField('stoploss/activationprice')
    bymarket = ItemField('bymarket')
    guard_time = DateTimeField('stoploss/guardtime', timeformat)
    # Overrides
    broker_ref = StringField('stoploss/brokerref')
    quantity = IntegerField('stoploss/quantity')
    price = FloatField('stoploss/orderprice')


class TakeProfit(StopOrder):
    activation_price = FloatField('takeprofit/activationprice')
    guard_time = DateTimeField('takeprofit/guardtime', timeformat)
    extremum = FloatField('takeprofit/extremum')
    level = FloatField('takeprofit/level')
    correction = FloatField('takeprofit/correction')
    guard_spread = FloatField('takeprofit/guardspread')
    # Overrides
    broker_ref = StringField('takeprofit/brokerref')
    quantity = IntegerField('takeprofit/quantity')


class ClientOrderPacket(Packet):
    ROOT_NAME = 'orders'

    @classmethod
    def parse(cls, xml):
        result = ClientOrderPacket()
        result.items = []
        root = parseString(xml)
        assert root.tag == ClientOrderPacket.ROOT_NAME
        for child in root:
            if child.tag == Order.ROOT_NAME:
                result.items.append(Order(child))
            elif child.tag == StopOrder.ROOT_NAME:
                for subchild in child:
                    if subchild.tag == 'stoploss':
                        result.items.append(StopLoss(child))
                    elif subchild.tag == 'takeprofit':
                        result.items.append(TakeProfit(child))
        return result


## Matched trades
class ClientTrade(Entity):
    ROOT_NAME = 'trade'
    secid = IntegerField('secid')
    id = trade_no = IntegerField('tradeno')
    order_no = IntegerField('orderno')
    board = StringField('board')
    seccode = StringField('seccode')
    client = StringField('client')
    buysell = StringField('buysell', choices=['B', 'S'])
    time = DateTimeField('time', timeformat)
    broker_ref = StringField('brokerref')
    value = FloatField('value')
    commission = FloatField('comission')
    price = FloatField('price')
    items = IntegerField('items')
    quantity = IntegerField('quantity')
    yld = IntegerField('yield')
    accrued_int = FloatField('accruedint')
    trade_type = StringField('tradetype', choices=['T', 'N', 'R', 'P'])
    settle_code = StringField('settlecode')
    current_position = IntegerField('currentpos')


class ClientTradePacket(Packet):
    ROOT_NAME = 'trades'
    items = NodeListField('trade', ClientTrade)


## Market position
class ClientPosition(Entity):
    id = client = StringField('client')
    market = IntegerField('market')
    register = StringField('register')
    name = StringField('shortname')
    asset = StringField('asset')
    saldo_in = FloatField('saldoin')
    saldo = FloatField('saldo')
    bought = FloatField('bought')
    sold = FloatField('sold')
    order_buy = FloatField('ordbuy')
    order_sell = FloatField('ordsell')


class MoneyPosition(ClientPosition):
    ROOT_NAME = 'money_position'
    # Let id=0 for money
    id = 0
    market = IntegerListField('markets/market')
    order_buy_cond = FloatField('ordbuycond')
    commission = FloatField('comission')
    ord_sell = 0


class SecurityPosition(ClientPosition):
    ROOT_NAME = 'sec_position'
    id = secid = IntegerField('secid')
    seccode = asset = StringField('seccode')
    saldo_min = FloatField('saldomin')


# To be done
class ClientPositionForts(Entity):
    pass


class ClientMoneyForts(ClientPositionForts):
    pass


class SpotLimits(ClientPositionForts):
    pass


class FortCollaterals(ClientPositionForts):
    pass


class PositionPacket(Packet):
    ROOT_NAME = 'positions'

    @classmethod
    def parse(cls, xml):
        result = PositionPacket()
        result.items = []
        root = parseString(xml)
        assert root.tag == PositionPacket.ROOT_NAME
        for child in root:
            if child.tag == 'money_position':
                result.items.append(MoneyPosition(child))
            elif child.tag == 'sec_position':
                result.items.append(SecurityPosition(child))
        return result


# Forts only, to be done
class ClientLimitsForts(Entity):
    ROOT_NAME = 'clientlimits'
    id = client = StringField('@client')
    cbplimit = FloatField('cbplimit')
    cbplused = FloatField('cbplused')
    cbplplanned = FloatField('cbplplanned')
    fob_varmargin = FloatField('fob_varmargin')
    coverage = FloatField('coverage')
    liquidity_c = FloatField('liquidity_c')
    profit = FloatField('profit')
    money_current = FloatField('money_current')
    money_reserve = FloatField('money_reserve')
    money_free = FloatField('money_free')
    options_premium = FloatField('options_premium')
    exchange_fee = FloatField('exchange_fee')
    forts_varmargin = FloatField('forts_varmargin')
    varmargin = FloatField('varmargin')
    pclmargin = FloatField('pclmargin')
    options_vm = FloatField('options_vm')
    spot_buy_limit = FloatField('spot_buy_limit')
    used_spot_buy_limit = FloatField('used_spot_buy_limit')
    collat_current = FloatField('collat_current')
    collat_free = FloatField('collat_free')


## T+ Portfolio, ugly but important
class ClientPortfolio(Entity):
    ROOT_NAME = 'portfolio_tplus'
    id = client = StringField('@client')
    coverage_fact = FloatField('coverage_fact')
    coverage_plan = FloatField('coverage_plan')
    coverage_crit = FloatField('coverage_crit')
    open_equity = FloatField('open_equity')
    equity = FloatField('equity')
    cover = FloatField('cover')
    init_margin = FloatField('init_margin')
    pnl_income = FloatField('pnl_income')
    pnl_intraday = FloatField('pnl_intraday')
    leverage = FloatField('leverage')
    margin_level = FloatField('margin_level')

    class _Money(MyXmlObject):
        open_balance = FloatField('open_balance')
        bought = FloatField('bought')
        sold = FloatField('sold')
        settled = FloatField('settled')
        balance = FloatField('balance')
        tax = FloatField('tax')

        class _ValuePart(MyXmlObject):
            register = StringField('@register')
            open_balance = FloatField('open_balance')
            bought = FloatField('bought')
            sold = FloatField('sold')
            settled = FloatField('settled')
            balance = FloatField('balance')

        value_parts = NodeListField('value_part', _ValuePart)

    money = NodeField('money', _Money)

    class _Security(MyXmlObject):
        secid = IntegerField('@secid')
        market = IntegerField('market')
        seccode = StringField('seccode')
        price = FloatField('price')
        open_balance = IntegerField('open_balance')
        bought = IntegerField('bought')
        sold = IntegerField('sold')
        balance = IntegerField('balance')
        buying = IntegerField('buying')
        selling = IntegerField('selling')
        cover = FloatField('cover')
        init_margin = FloatField('init_margin')
        riskrate_long = FloatField('riskrate_long')
        riskrate_short = FloatField('riskrate_short')
        pnl_income = FloatField('pnl_income')
        pnl_intraday = FloatField('pnl_intraday')
        max_buy = IntegerField('maxbuy')
        max_sell = IntegerField('maxsell')

        class _ValuePart(MyXmlObject):
            register = StringField('@register')
            open_balance = IntegerField('open_balance')
            bought = IntegerField('bought')
            sold = IntegerField('sold')
            settled = IntegerField('settled')
            balance = IntegerField('balance')
            buying = IntegerField('buying')
            selling = IntegerField('selling')

        value_parts = NodeListField('value_part', _ValuePart)

    securities = NodeListField('security', _Security)


## Some utility objects (non-entities)
class CreditAbility(MyXmlObject):
    ROOT_NAME = 'overnight'
    overnight = SimpleBooleanField('@status', 'true', 'false')
    intraday = SimpleBooleanField('@status', 'false', 'true')


class MarketOrderAbility(MyXmlObject):
    ROOT_NAME = 'marketord'
    secid = IntegerField('@secid')
    seccode = StringField('@seccode')
    permitted = SimpleBooleanField('@permit', 'yes', 'no')


# Deprecated
class ClientLimitsT0(MyXmlObject):
    ROOT_NAME = 'leverage_control'
    client = StringField('@client')
    leverage_fact = FloatField('@leverage_fact')
    leverage_plan = FloatField('@leverage_plan')

    class Security(MyXmlObject):
        secid = IntegerField('@secid')
        board = StringField('@board')
        seccode = StringField('@seccode')
        max_buy = IntegerField('@maxbuy')
        max_sell = IntegerField('@maxsell')

    securities = NodeListField('security', Security)


# Duplication of Trade class for some reason
class HistoryTick(Trade):
    ROOT_NAME = 'tick'
    secid = IntegerField('secid')
    time = DateTimeField('trade_time', timeformat)


class HistoryTickPacket(Packet):
    ROOT_NAME = 'ticks'
    items = NodeListField('tick', HistoryTick)


## Boards aka regimes
class Board(Entity):
    ROOT_NAME = 'board'
    id = StringField('@id')
    name = StringField('name')
    market = IntegerField('market')
    type = IntegerField('type')

    def __str__(self):
        return self.name.encode(encoding)

    __repr__ = __str__


class BoardPacket(Packet):
    ROOT_NAME = 'boards'
    items = NodeListField('board', Board)


## Duplication of Security class for some reason
class SecurityPit(MyXmlObject):
    ROOT_NAME = 'pit'
    board = StringField('@board')
    seccode = StringField('@seccode')
    market = IntegerField('market')
    decimals = IntegerField('decimals')
    minstep = FloatField('minstep')
    lotsize = IntegerField('lotsize')
    point_cost = FloatField('point_cost')


class SecurityPitPacket(Packet):
    ROOT_NAME = 'pits'
    items = NodeListField('pit', SecurityPit)


## Max buy/sell for any instrument
class ClientLimitsTPlus(Entity):
    ROOT_NAME = 'max_buy_sell_tplus'
    id = client = StringField('@client')

    class Security(MyXmlObject):
        secid = IntegerField('@secid')
        market = IntegerField('market')
        seccode = StringField('seccode')
        max_buy = IntegerField('maxbuy')
        max_sell = IntegerField('maxsell')

    # many or just one?
    securities = NodeListField('security', Security)


## Transaq has IM!
class TextMessage(Entity):
    ROOT_NAME = 'message'
    id = date = DateTimeField('date', timeformat)
    urgent = SimpleBooleanField('urgent', 'Y', 'N')
    sender = StringField('from')
    text = StringField('text')


class TextMessagePacket(Packet):
    ROOT_NAME = 'messages'
    items = NodeListField('message', TextMessage)


## MMA Account (Whotrades), not used
class ClientPortfolioMCT(MyXmlObject):
    pass


## News objects, not used
class NewsHeader(MyXmlObject):
    pass


class NewsBody(MyXmlObject):
    pass
